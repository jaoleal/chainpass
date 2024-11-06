import struct
import hashlib as h
def invert_bytes(data):
    for i in range(0, len(data), 2):
        data = data[:i] + data[i+1] + data[i] + data[i+2:]
    data = data[::-1]
    return data
def compact_size(integer):
    if integer < 253:
        return struct.pack('<B', integer)
    elif integer < 65535:
        return b'\xfd' + struct.pack('<H', integer)
    elif integer < 4294967295:
        return b'\xfe' + struct.pack('<I', integer)
    else:
        return b'\xff' + struct.pack('<Q', integer)

def check_segwit(input_obj, is_list=False):
    if is_list:
        for input in input_obj:
            if "witness" in input:
                return True
        return False
    elif "witness" in input_obj:
        return True
    return False

def get_message(tx_data, hashtype, input_index):
    print(hashtype)
    version = struct.pack('<I', tx_data['version'])
    is_segwit = check_segwit(tx_data["vin"], True)
    input_count = bytearray(compact_size(len(tx_data['vin'])))
    output_count = bytearray(compact_size(len(tx_data['vout'])))
    # Serialize the inputs
    inputs = input_count
    for input_obj in tx_data['vin']:
        prevout_id = bytes.fromhex(invert_bytes(input_obj['txid']))
        vout = struct.pack('<I', input_obj['vout'])
        if tx_data['vin'].index(input_obj) == input_index:
            script_size = compact_size(len(bytes.fromhex(input_obj['prevout']['scriptpubkey'])))
            script = bytes.fromhex(input_obj['prevout']['scriptpubkey'])
        else:
            if "scriptsig" in input_obj:
                script_size = compact_size(len(bytes.fromhex(input_obj['scriptsig'])))
                script = bytes.fromhex(input_obj['scriptsig'])
            else:
                script_size = b'\x00'
                script = b''
        if not (hashtype == b'\x02' or hashtype == b'\x03'):
            sequence = struct.pack('<I', input_obj['sequence'])
            if tx_data['vin'].index(input_obj) == input_index:
                sequence = struct.pack('<I', input_obj['sequence'])
            else:
                sequence = struct.pack('<I', 0)
        
        inputs.extend(prevout_id)
        inputs.extend(vout)
        inputs.extend(script_size)
        inputs.extend(script)
        inputs.extend(sequence)


    outputs = output_count
    # Serialize the outputs
    for output_obj in tx_data['vout']:
        value = struct.pack('<Q', int(output_obj['value']))
        script_size = compact_size(len(bytes.fromhex(output_obj['scriptpubkey'])))
        script = bytes.fromhex(output_obj['scriptpubkey'])
        outputs.extend(value) 
        outputs.extend(script_size)
        outputs.extend(script)

    if hashtype == b'\x03' or hashtype == b'\x83':
        outputs = b''
        for output_obj in range(len(tx_data['vout'])):
            if not hashtype == b'\x83':
                value = struct.pack('<Q', int(output_obj['value']))
                script_size = compact_size(0)
                script = b''
                outputs.extend(value) 
                outputs.extend(script_size)
                outputs.extend(script)
            if tx_data['vout'].index(output_obj) == input_index:
                value = struct.pack('<Q', int(tx_data['vout'][output_obj]['value']))
                script_size = compact_size(len(bytes.fromhex(tx_data['vout'][output_obj]['scriptpubkey'])))
                script = bytes.fromhex(tx_data['vout'][output_obj]['scriptpubkey'])
                outputs.extend(value) 
                outputs.extend(script_size)
                outputs.extend(script)
                break

    # Serialize the locktime
    locktime = bytearray(struct.pack('<I', tx_data['locktime']))
    witness = bytearray()
    for input_obj in tx_data['vin']:
        if check_segwit(input_obj):
            witness.extend(compact_size(len(input_obj['witness'])))
            for w in input_obj['witness']:
                witness.extend(compact_size(len(bytes.fromhex(w))))
                witness.extend(bytes.fromhex(w))
        elif is_segwit:
            witness.extend(b'\x00')


    sighash =  hashtype + b'\x00\x00\x00'


    message_components = bytearray()
    if hashtype == b'\x01' or hashtype == b'\x81' or hashtype == b'\x82' or hashtype == b'\x83':

        if hashtype == b'\x81' or hashtype == b'\x82' or hashtype == b'\x83':

            inputs = b''
            input_obj = tx_data['vin'][input_index]
            prevout_id = bytes.fromhex(invert_bytes(input_obj['txid']))
            vout = struct.pack('<I', input_obj['vout'])
            script_size = compact_size(len(bytes.fromhex(input_obj['prevout']['scriptpubkey'])))
            script = bytes.fromhex(input_obj['prevout']['scriptpubkey'])
            if "scriptsig" in input_obj:
                script_size = compact_size(len(bytes.fromhex(input_obj['scriptsig'])))
                script = bytes.fromhex(input_obj['scriptsig'])
            else:
                script_size = b'\x00'
                script = b''
    
            sequence = struct.pack('<I', input_obj['sequence'])
            inputs.extend(prevout_id)
            inputs.extend(vout)
            inputs.extend(script_size)
            inputs.extend(script)
            inputs.extend(sequence)


        if hashtype == b'\x82':
            outputs = b'0x00'
            message_components = version + inputs + outputs + locktime + sighash
        else:
            print("here")
            message_components = version + inputs + outputs + locktime + sighash 
    elif hashtype == b'\x02':
        message_components = version + inputs + locktime + sighash
    if is_segwit:
        #if is segwit, concatenate the marker and flag to the version
        marker = bytes.fromhex("0001")
        return  h.sha256(h.sha256(version  + marker + inputs + witness + locktime).digest()).digest()
    return  h.sha256(h.sha256(message_components).digest()).digest()


def serialize_tx_data(tx_data):
    version = struct.pack('<I', tx_data['version'])
    is_segwit = check_segwit(tx_data["vin"], True)
    input_count = bytearray(compact_size(len(tx_data['vin'])))
    output_count = bytearray(compact_size(len(tx_data['vout'])))
    # Serialize the inputs
    inputs = input_count
    for input_obj in tx_data['vin']:
        prevout_id = bytes.fromhex(invert_bytes(input_obj['txid']))
        vout = struct.pack('<I', input_obj['vout'])
        if "scriptsig" in input_obj:
            script_size = compact_size(len(bytes.fromhex(input_obj['scriptsig'])))
            script = bytes.fromhex(input_obj['scriptsig'])
        else:
            script_size = b'\x00'
            script = b''
        sequence = struct.pack('<I', input_obj['sequence'])
        inputs.extend(prevout_id)
        inputs.extend(vout)
        inputs.extend(script_size)
        inputs.extend(script)
        inputs.extend(sequence)



    outputs = output_count
    # Serialize the outputs
    for output_obj in tx_data['vout']:
        value = struct.pack('<Q', int(output_obj['value']))
        script_size = compact_size(len(bytes.fromhex(output_obj['scriptpubkey'])))
        script = bytes.fromhex(output_obj['scriptpubkey'])
        outputs.extend(value) 
        outputs.extend(script_size)
        outputs.extend(script)
    # Serialize the locktime
    locktime = bytearray(struct.pack('<I', tx_data['locktime']))

    # Concatenate all serialized parts
    serialized_tx_data = bytearray()
    serialized_tx_data.extend(inputs) 
    serialized_tx_data.extend(outputs)
    witness = bytearray()
    for input_obj in tx_data['vin']:
        if check_segwit(input_obj):
            witness.extend(compact_size(len(input_obj['witness'])))
            for w in input_obj['witness']:
                witness.extend(compact_size(len(bytes.fromhex(w))))
                witness.extend(bytes.fromhex(w))
        elif is_segwit:
            witness.extend(b'\x00')
    if is_segwit:
        #if is segwit, concatenate the marker and flag to the version
        marker = bytes.fromhex("0001")
        return is_segwit, version, marker, serialized_tx_data, witness, locktime
    return is_segwit, version, serialized_tx_data, witness, locktime
