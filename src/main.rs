use std::str::FromStr;

use bitcoin::{
    absolute::LockTime, bip32::Xpriv, consensus::Encodable, hashes::Hash, hex::DisplayHex,
    key::Secp256k1, script::PushBytes, transaction::Version, Address, Amount, CompressedPublicKey,
    Network, OutPoint, PublicKey, ScriptBuf, Sequence, Transaction, TxIn, TxOut, Txid, Witness,
};
use libpass::{
    object::KVObject,
    user::{create_op_return, get_obj_from_tx, UserContext},
};

pub mod libpass;

pub const TEST_KEYL: &str  = "xprv9s21ZrQH143K2JF8RafpqtKiTbsbaxEeUaMnNHsm5o6wCW3z8ySyH4UxFVSfZ8n7ESu7fgir8imbZKLYVBxFPND1pniTZ81vKfd45EHKX73";

// Chainpass is a simple app, given the private key, derive the next empty address (n + 1) n being the number of already
// indexed Objects.
//
// Any Key-Value item can be indexed as a KVObject.
//
// This special KVObject is encrypted with AES-GCM (using the sha512 of the secret key of the empty address) and compress the cyphertext to 80 bytes if
// needed.
//
// Then we request the user to fund the address we generated and produce a transaction that consumes the address and includes the processed object on
// a op_return.

pub fn main() {
    // Create a buffer
    let mut buffer = [0u8; 80];

    //desired test
    let key = "github22";
    let password = "passwordpasswordpasswordpasswordpasswordpasswordpasswordpasswordpassword";

    // the key bytes needs to be exactly 8 bytes (por enquanto)
    assert_eq!(key.as_bytes().len(), 8);

    // the password 72
    assert_eq!(password.as_bytes().len(), 72);

    buffer.copy_from_slice([key.as_bytes(), password.as_bytes()].concat().as_slice());

    let obj = KVObject(buffer);

    let secp = Secp256k1::new();
    let sk = Xpriv::from_str(TEST_KEYL)
        .expect("Valid key from string")
        .to_priv();
    let pk = PublicKey::from_private_key(&secp, &sk);

    // we instantiate a user with the index.
    let user = UserContext {
        key_pair: (Some(sk), pk),
        index: 0,
    };

    let mut secret_bytes: [u8; 32] = [0u8; 32];
    secret_bytes.copy_from_slice(sk.to_bytes().as_slice());

    let encrypted = obj.encrypt_data(&secret_bytes).unwrap();
    let encrypted = encrypted.as_slice();

    assert_eq!(
        buffer,
        KVObject::decrypt(&secret_bytes, encrypted).unwrap().0
    );

    let compressed_pk = CompressedPublicKey::from_private_key(&secp, &sk).unwrap();

    // Now just generate and address to fund and build a transaction to evaluate.
    let address = Address::p2wpkh(&compressed_pk, Network::Bitcoin);

    println!("Fund this address: {}", address);
    let transaction = Transaction {
        version: Version::TWO,
        lock_time: LockTime::ZERO,
        input: vec![TxIn {
            previous_output: OutPoint {
                txid: Txid::all_zeros(),
                vout: 0,
            },
            sequence: Sequence::ENABLE_RBF_NO_LOCKTIME,
            script_sig: ScriptBuf::new(),
            witness: Witness::default(),
        }],
        output: vec![TxOut {
            value: Amount::from_sat(0),
            script_pubkey: create_op_return(encrypted),
        }],
    };
    let mut buffer = Vec::<u8>::new();
    transaction.consensus_encode(&mut buffer).unwrap();
    println!("{}", buffer.to_lower_hex_string());

    let decoded_obj = get_obj_from_tx(&transaction, secret_bytes).unwrap();

    println!(
        "Object from the transaction: {} - {} ",
        decoded_obj.0, decoded_obj.1
    )
}
