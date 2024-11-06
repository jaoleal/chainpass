import calendar
from hashlib import sha256
import time
from tx import tx_knapsack as knap_mod, transactions as tx_mod, serialization as ser, transaction_validation as tx_val
import blockbuilder as bb_mod

def main():
    #This is all the hard coded info
    version = "00000020"
    difficulty = "0000ffff00000000000000000000000000000000000000000000000000000000"
    previous_block = "0000000000000000000000000000000000000000000000000000000000000000"

    #gets the timestamp
    gmt = time.gmtime()
    timestamp = calendar.timegm(gmt)

    #converts difficulty to a hash object
    difficulty_hash = bytes.fromhex(difficulty)
    difficulty_hash = difficulty_hash.hex()

    #gets all the txs filenames in  ../../mempool
    entries = tx_mod.get_tx_info("all")
    #validate the entries
    valid_entries = list()
    for entry in entries:
        if tx_val.tx_syntax_validation(tx_mod.get_tx_info(entry)):
            valid_entries.append(entry)

    #gets some info about the txs, like fee, weight and the file name
    block_weight = 4000000
    block_header_weight = 320
    
    #gets the valid txs and their respective values
    transaction_values = list()
    for entry in valid_entries:
        transaction_values.append(tx_mod.valid_tx_values(entry))
    
    #gets the txs that will be included in the block using a knapsack 1-0 algorithm
    included_txsfilename, fee = knap_mod.tx_KISS(transaction_values, block_weight - block_header_weight)

    print("Transactions included fee: " + str(fee))

    #build the witness merkle root, starts with the first item being the coinbase as all 0's
    coinbasewtxid = bytes.fromhex("0000000000000000000000000000000000000000000000000000000000000000").hex()
    wtxids = [coinbasewtxid]
    for i  in range(len(included_txsfilename)):
        #loop to extract the wtxid from the included transactions
        wtxids.append(tx_mod.get_wtxid(included_txsfilename[i]))
    witnessroot = bb_mod.merkle_root(wtxids)
    print("Witness root builded")
    
    #build the coinbase the return is a tuple with the, respective, coinbase and the coinbaseid
    coinbase = bb_mod.build_coinbase_tx(fee, witnessroot)
    coinbasehex = coinbase[0]
    coinbasetxid = coinbase[1].hex()
    print("Coinbase builded")
    
    #build the merkle root starting wtihe the first item being the coinbase txid
    txids = [coinbasetxid]
    for i in range(len(included_txsfilename)):
        #loop to extract the txid from the included transactions
        txids.append(tx_mod.get_tx_id(included_txsfilename[i]))
    merkle_root = bb_mod.merkle_root(txids)
    merkle_root = merkle_root.hex()
    print("Merkle root builded")


    #inverting all the included txids, so it can be exposed as the real txid
    for i in range(len(txids)):
        txids[i] = ser.invert_bytes(txids[i])
    print("Txids builded")

    #get the actual timestamp
    timestamp = timestamp.to_bytes(4, byteorder='little')
    timestamp = timestamp.hex()
    
    #starts the nonce at 0
    # the nonce can be a integer between 0 and 4294967295
    # ocuping 4 bytes
    nonce = 0

    #build the bits and invert it
    bits = bb_mod.build_bits(difficulty)
    bits = ser.invert_bytes(bits)
    
    #start the mining process through a loop
    is_mined = False
    while not is_mined:
        #gets the hash of the actual nonce
        nonce_bytes = nonce.to_bytes(4, byteorder='little')
        nonce_bytes = nonce_bytes.hex()
        #concatenate all infos to build the block header
        block_header = str(version) + str(previous_block) + str(merkle_root) + str(timestamp) + str(bits) + str(nonce_bytes)
        block_header = bytes.fromhex(block_header)
        #double hash and invert to get block hash
        block_hash = sha256(sha256(block_header).digest()).digest()
        block_hash = block_hash.hex()
        block_hash_inverse = ser.invert_bytes(block_hash)
        #gets the serialized block header
        block_header = block_header.hex()
        if block_hash_inverse < difficulty_hash:
            is_mined = True
            #if the block hash is valid, build the block on ../../output.txt as SoB decided to be output
            f = open("../../output.txt", "w")
            f.write(block_header)
            f.write("\n")
            f.write(coinbasehex)
            f.write("\n")
            for tx in txids:
                f.write(tx)
                f.write("\n")
        else:
            # if the nonce is at maximum, get the actual timestamp
            # and restart the nonce
            if nonce + 1 >= 4294967295:
                nonce = 0
                gmt = time.gmtime()
                timestamp = calendar.timegm(gmt)
            else:
                nonce += 1

# a python strange thing to make the main function run
if __name__ == "__main__":
    main()