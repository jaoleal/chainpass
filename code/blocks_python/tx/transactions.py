from hashlib import sha256
import json
import os
import sys
import tx.serialization as ser

#This function is used to get the txid of a transaction
#txid is a hash of everything in the transaction, except the witness data
def get_tx_id(tx_filename):
    tx_info = get_tx_info(tx_filename + ".json")
    tx_ser = ser.serialize_tx_data(tx_info)
    if tx_ser[0]:
      tx_ser_hex = tx_ser[1].hex() + tx_ser[3].hex() + tx_ser[5].hex()
    else:
      tx_ser_hex = tx_ser[1].hex() + tx_ser[2].hex() + tx_ser[4].hex()
    hash = sha256(sha256(bytes.fromhex(tx_ser_hex)).digest()).digest()
    return hash.hex()

#This function is used to get the wtxid of a transaction
#Wtxid is a hash of everything in the transaction, including the witness data
def get_wtxid(tx_filename):
    tx_info = get_tx_info(tx_filename + ".json")
    tx_ser = ser.serialize_tx_data(tx_info)
    tx_ser_hex = bytearray()
    for i in range(1, len(tx_ser)):
        tx_ser_hex.extend(tx_ser[i])
    hash = sha256(sha256(tx_ser_hex).digest()).digest()
    return hash.hex()

def valid_tx_values(tx_id):
    # get raw json data
    tx_info = get_tx_info(tx_id)

    #this block of code is just for calculating the fee.
    in_value = 0
    out_value = 0
    for in_values in tx_info["vin"]:    
       in_value += in_values["prevout"]["value"]
    for out_values in tx_info["vout"]:
        out_value += out_values["value"]
    fee = in_value - out_value

    return [fee, get_tx_size(tx_info), tx_id]

#will return the size of the serialized tx in bytes
#the regular transaction data is multiplied by 4 
#and the witness data remains the same as its byte size
def get_tx_size(tx_info):
    tx_ser = ser.serialize_tx_data(tx_info)
    if tx_ser[0]:
        default_data = tx_ser[1] + tx_ser[3] + tx_ser[5]
        witness_data = tx_ser[2] + tx_ser[4]
        return (sys.getsizeof(default_data) * 4) + sys.getsizeof(witness_data)
    else:
      return (sys.getsizeof(tx_ser[1] + tx_ser[2] + tx_ser[4]) * 4)
    
def get_tx_info(tx_filename):
    #will return the json raw data or False if 
    #if does not found it


    #if input of the function is "all" will return
    #all tx_filenames in the mempool
    if tx_filename == "all":
        return os.listdir("mempool/")
    path = "mempool/" + tx_filename
    if not (os.path.exists(path)):
        return False

    return json.load(open(path))