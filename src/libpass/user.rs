use std::fs;
use std::io::{self, Write};

/// Module to hold the methods for the user to interact with libpass.
use anyhow::Result;
use bdk::bitcoin::{PrivateKey, PublicKey};
use bitcoin::script::{Builder, PushBytesBuf};
use bitcoin::ScriptBuf;
use serde::{Deserialize, Serialize};

use super::object::KVObject;

#[derive(Serialize, Deserialize)]
/// This struct should hold user data that we need to scan the addresses, build transactions and extracting [`KVObject`]s.
pub struct UserContext {
    pub key_pair: (Option<PrivateKey>, PublicKey),
    pub index: u32,
}
impl UserContext {
    //returns (KVObject, (Opt<PK>, publickey)) for the according derivation.
    pub fn pair(&self, target: KVObject) -> Result<(KVObject, (Option<PrivateKey>, PublicKey))> {
        Ok((target, (self.key_pair)))
    }
    pub fn save(&self, filename: &str) -> io::Result<()> {
        let json = serde_json::to_string(self)?;
        let mut file = fs::File::create(filename)?;
        file.write_all(json.as_bytes())?;
        Ok(())
    }

    pub fn load(filename: &str) -> io::Result<Self> {
        let json = fs::read_to_string(filename)?;
        let context: UserContext = serde_json::from_str(&json)?;
        Ok(context)
    }
}
/// Creates a KVObject from a key and a value.
pub fn create_object(key: String, value: String) -> Result<KVObject> {
    let mut buffer = [0u8; 80];

    let key_bytes = key.as_bytes();

    let value_bytes = value.as_bytes();

    let blob = [key_bytes, value_bytes].concat();

    buffer.copy_from_slice(blob.as_slice());
    Ok(KVObject(buffer))
}

pub fn create_op_return(data: &[u8]) -> ScriptBuf {
    let mut push_bytes = PushBytesBuf::default();
    push_bytes
        .extend_from_slice(data)
        .expect("Data too long for push bytes");

    // Create a new script builder
    Builder::new()
        // Add OP_RETURN opcode
        .push_opcode(bitcoin::opcodes::all::OP_RETURN)
        // Push the data
        .push_slice(push_bytes)
        // Build the final script
        .into_script()
}
pub fn get_obj_from_tx(tx: &bitcoin::Transaction, sk: [u8; 32]) -> Result<(String, String)> {
    let mut buffer = Vec::new();

    for out in tx.output.iter() {
        if out.script_pubkey.is_op_return() {
            let object_slice = &out.script_pubkey.as_bytes()[3..];
            let mut t: Vec<u8> = Vec::with_capacity(object_slice.len());
            t.extend_from_slice(object_slice);
            buffer = t
        }
    }
    let decrypt = KVObject::decrypt(&sk, &buffer).unwrap().0;
    let mut k: [u8; 8] = [0u8; 8];
    let mut v: [u8; 72] = [0u8; 72];
    k.copy_from_slice(&decrypt[..8]);
    v.copy_from_slice(&decrypt[8..]);

    Ok((
        String::from_utf8(k.to_vec()).unwrap(),
        String::from_utf8(v.to_vec()).unwrap(),
    ))
}
