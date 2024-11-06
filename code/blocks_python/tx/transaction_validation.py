import hashlib
import ecdsa
import tx.transactions as tx
import tx.serialization as ser
from ecdsa.util import sigdecode_der 
#verify the data type for the transaction fields

def validate_tx_script(tx_filename, input_index = 0):
    tx_info = tx.get_tx_info(tx_filename + ".json")
    if not tx_syntax_validation(tx_info):
        print("Error validating tx syntax")
        return False
    input_obj = tx_info['vin'][input_index]
    #check if input is witness
    if "witness" in input_obj:
        witness_script = str()
        for element in input_obj['witness']:
            witness_script =  witness_script + element + " "
        script = witness_script + input_obj['prevout']['scriptpubkey_asm']
    else:
        script = input_obj['scriptsig_asm'] + " " + input_obj['prevout']['scriptpubkey_asm']
    script = script.split(' ')
    return execute_script([], script, 0, tx_filename, input_index)

def get_tx_message(tx_filename, hash_type, input_index = 0):
    tx_info = tx.get_tx_info(tx_filename + ".json")
    return ser.get_message(tx_info, hash_type, input_index)

def tx_syntax_validation(tx):
    #check if the tx has the required fields
    required_fields = ['locktime', 'version', 'vin', 'vout']
    for required_field in required_fields:
        if not required_field in tx:
            return False
    if not (len(tx['vin']) > 0 and len(tx['vout']) > 0):
        return False
    for input in tx['vin']:
        if not "prevout" in input:
            return False
        if not "scriptpubkey" in input['prevout']:
            return False
        if not "scriptsig" in input and not "witness" in input:
            return False
    for output in tx['vout']:
        if not "scriptpubkey" in output:
            return False
        if not "value" in output:
            return False
    return True

def hash160(data):
    return hashlib.new('ripemd160', hashlib.sha256(bytes.fromhex(data)).digest()).digest().hex()

def check_signature(pubkey, signature, message):
    print(pubkey.hex())
    print(signature.hex())
    print(message.hex())
    # Perform ECDSA signature verification
    pubkey = ecdsa.VerifyingKey.from_string(pubkey, curve=ecdsa.SECP256k1)
    return pubkey.verify(signature,message, sigdecode=sigdecode_der)

def execute_script(stack, script, index = 0, tx_filename = None, input_index = 0):
    #script has to be a list with every element being a string
    # script = unlocking_script_asm + " " + locking_script_asm
    # script = script.split(' ')
    # and the stack has to be a list
    # stack = []
    # the function will recursively run until the script is empty returning the result of the validation
    # the code works on pushing the next element. and will jump the element if is not an opcode
    # the opcodes that will be implemented is just the ones present in the mempool.
    # 'OP_HASH160'
    # 'OP_PUSHBYTES'
    # 'OP_DUP'
    # 'OP_CHECKSIG'
    # 'OP_PUSHDATA'
    # 'OP_EQUALVERIFY'
    # 'OP_EQUAL'
    # 'OP_0'
    # 'OP_PUSHNUM_1'

    if "OP" in script[index]:
        opcode = script.pop(0)
        index -= 1
      
        if 'OP_PUSHBYTES' in opcode or 'OP_PUSHDATA' in opcode:
            # since the opcode is a push we dont need the amount of bytes, just a push of the data due to how it will be input
            stack.append(script.pop(0))
        elif 'OP_HASH160' in opcode:
            # double hash160 the previous element
            stack.append(hash160(stack.pop()))
        elif "OP_DUP" in opcode:
            # duplicate the last element
            cp = stack[-1]
            stack.append(cp)
        elif 'OP_EQUALVERIFY' in opcode:
            if stack.pop() != stack.pop():
                stack.append(False)
        elif 'OP_EQUAL' in opcode:
            stack.append(stack.pop() == stack.pop())
        elif 'OP_0' in opcode:
            stack.append(0)
        elif 'OP_PUSHNUM_1' in opcode:
            stack.append(1)
    else:   
        stack.append(script.pop(0))
        index -= 1
    if (len(stack) == 0 or False in stack):
        return False
    elif (len(stack) > 0 or True in stack) and len(script) == 0:
        return True
    else:
        return execute_script(stack, script, index + 1, tx_filename, input_index) 