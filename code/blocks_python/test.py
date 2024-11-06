import json
import tx.transactions as txmod
import tx.transaction_validation as txval
import tx.serialization as txser
import blockbuilder as bbmod
import hashlib as h

def test_witness_script():
  tx_filename =  "00a5be9434f4d97613391cdce760293fd142786a00952ed4edfd66dd19c5c23a"
  assert txval.validate_tx_script(tx_filename) == True

def test_checksig_with_serialization():
  tx_filename = "0a8b21af1cfcc26774df1f513a72cd362a14f5a598ec39d915323078efb5a240"
  assert txval.validate_tx_script(tx_filename) == True

def test_script_no_checksig():
  script = "1 OP_DUP"
  script = script.split(" ")
  assert txval.execute_script([], script) == True
  script = "12 OP_HASH160"
  script = script.split(" ")
  assert txval.execute_script([], script) == True
  script = "OP_PUSHBYTES 21 OP_HASH160".split(" ")
  assert txval.execute_script([], script) == True
  script = "1 1 OP_EQUAL".split(" ")
  assert txval.execute_script([], script) == True
  script = "1 2 OP_EQUALVERIFY".split(" ")
  assert txval.execute_script([], script) == False
  script = "1 1 OP_EQUALVERIFY".split(" ")
  assert txval.execute_script([], script) == False
  script = "OP_0".split(" ")
  #in this specific case, python considers 0 false (i dont know why)
  assert txval.execute_script([], script) == False
  script = "OP_PUSHNUM_1".split(" ")
  assert txval.execute_script([], script) == True
  script = "OP_PUSHNUM_1 OP_PUSHNUM_1 OP_EQUAL".split(" ")
  assert txval.execute_script([], script) == True


def test_witness_commitment():
    entries = ["82f9f96db7bdbb9e70626747632e373b34eefd50d613dfea7092744169591b6e","7cb2a4f55245bae141a5d6ad51c08d7a9fdf2c2b905e4d97639ed80b82e69800","a9e537569db3c64340ed5abcdd983e9bb1b6ad6f90c93bc80d31c5cc0490bcea","4ab3cc4296fee78153d60d2884323a84260157db0b83a72309272f109ad9dd32","c2aedaae370101d6ca170f206e74222ae934afefe0e621b79b6290b919526563","2d5eb3d5dd4df76bf88f2f89c49c98be5552c7800c9ce20bb60a5496a23ec25f","7e4a05a078f4d7afcd686d117e319f8f14d69be43a0609bb9a9cb36a75a88abb"]
    for i in range(len(entries)):
       entries[i] = bytes.fromhex(txser.invert_bytes(entries[i]))
    witness_root = bbmod.merkle_root(entries, False)
    assert witness_root.hex() == "8835c8a2f6d1d85b9a3eaa3922d196f91356542417c9a3e849e41ef8ab3c616f"

def test_wtxid():
    entry = "00a5be9434f4d97613391cdce760293fd142786a00952ed4edfd66dd19c5c23a"
    tx_info = txmod.get_tx_info(entry + ".json")
    ser = txser.serialize_tx_data(tx_info)
    if ser[0]:
      ser_hex = ser[1].hex() + ser[2].hex() + ser[3].hex() + ser[4].hex() + ser[5].hex()
    else:
      ser_hex = ser[1].hex() + ser[2].hex() + ser[4].hex()
    hash2 = h.sha256(h.sha256(bytes.fromhex(ser_hex)).digest()).digest()
    hash = txser.invert_bytes(hash2.hex())
    assert hash == "5a1e17d86dabca58285dd00be376bf2d3242acf887e8bcbcda90b7217d3fb6b0"

def test_serialization():
    #this is the test for a non-segwit transaction
    entry = "0a70cacb1ac276056e57ebfb0587d2091563e098c618eebf4ed205d123a3e8c4"
    tx_info = txmod.get_tx_info(entry + ".json")
    ser = txser.serialize_tx_data(tx_info)
    if ser[0]:
      ser_hex = ser[1].hex() + ser[3].hex() + ser[4].hex()
    else: 
      ser_hex = ser[1].hex() + ser[2].hex() + ser[4].hex()
    hash2 = h.sha256(h.sha256(bytes.fromhex(ser_hex)).digest()).digest()
    hash = txser.invert_bytes(hash2.hex())
    hash = h.sha256(bytes.fromhex(hash)).digest()
    hash = hash.hex()
    
    assert hash == entry
    #this test covers the a segwit one
    entry = "00a5be9434f4d97613391cdce760293fd142786a00952ed4edfd66dd19c5c23a"
    tx_info = txmod.get_tx_info(entry + ".json")
    ser = txser.serialize_tx_data(tx_info)
    if ser[0]:
      ser_hex = ser[1].hex() + ser[3].hex() + ser[5].hex()
    else:
      ser_hex = ser[1].hex() + ser[2].hex() + ser[4].hex()
    hash2 = h.sha256(h.sha256(bytes.fromhex(ser_hex)).digest()).digest()
    hash = txser.invert_bytes(hash2.hex())
    print(hash)
    assert hash == "bec11fb2fd836e5fb28996a8ae2008d59142f781bfbfa70a31447af315e89aec"
    hash = h.sha256(bytes.fromhex(hash)).digest()
    hash = hash.hex()
    assert hash == entry

def test_get_tx_info():
    tx_id = "0a3fd98f8b3d89d2080489d75029ebaed0c8c631d061c2e9e90957a40e99eb4c.json"
    info = txmod.get_tx_info(tx_id)
    assert info == json.loads("""{
  "version": 2,
  "locktime": 834637,
  "vin": [
    {
      "txid": "b9b515b6171b47940809366f5d58591a56063db03fc39f678a03cb2b455f9428",
      "vout": 0,
      "prevout": {
        "scriptpubkey": "0014371e036c75b663254314287faa19c7b3f6c35e8a",
        "scriptpubkey_asm": "OP_0 OP_PUSHBYTES_20 371e036c75b663254314287faa19c7b3f6c35e8a",
        "scriptpubkey_type": "v0_p2wpkh",
        "scriptpubkey_address": "bc1qxu0qxmr4ke3j2sc59pl65xw8k0mvxh52kt0x5m",
        "value": 293400650
      },
      "scriptsig": "",
      "scriptsig_asm": "",
      "witness": [
        "304402207ed00dfbbf904a6f24d43725fe3cd9d8fec2f5b6f6a7ac7b1e0816e39266ff7602200966bdee875f64538a655dd2a0bc548c3deb5fd717ec3e9e107d1233533cc23a01",
        "021160ee898d5480f4a193254338a6f289ab33a56ed639ca0b1504c9acffdf4fda"
      ],
      "is_coinbase": false,
      "sequence": 4294967294
    }
  ],
  "vout": [
    {
      "scriptpubkey": "00140d1c76c89fbba64867349c1ad0f3313e6b4b7d36",
      "scriptpubkey_asm": "OP_0 OP_PUSHBYTES_20 0d1c76c89fbba64867349c1ad0f3313e6b4b7d36",
      "scriptpubkey_type": "v0_p2wpkh",
      "scriptpubkey_address": "bc1qp5w8djylhwnysee5nsddpue38e45klfk893yee",
      "value": 4402400
    },
    {
      "scriptpubkey": "001414989c53e65d603069bf506996f24f45f4a12107",
      "scriptpubkey_asm": "OP_0 OP_PUSHBYTES_20 14989c53e65d603069bf506996f24f45f4a12107",
      "scriptpubkey_type": "v0_p2wpkh",
      "scriptpubkey_address": "bc1qzjvfc5lxt4srq6dl2p5eduj0gh62zgg8mqeurg",
      "value": 288994794
    }
  ]
}""")
