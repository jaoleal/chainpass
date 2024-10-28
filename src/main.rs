use bitcoin::{
    absolute::LockTime,
    bip32::Xpriv,
    consensus::{Decodable, Encodable},
    hashes::Hash,
    hex::DisplayHex,
    key::Secp256k1,
    transaction::Version,
    Address, Amount, CompressedPublicKey, Network, OutPoint, PrivateKey, PublicKey, ScriptBuf,
    Sequence, Transaction, TxIn, TxOut, Txid, Witness,
};
use clap::{command, Parser};
use libpass::{
    object::KVObject,
    user::{create_op_return, get_obj_from_tx},
};
use rand::Rng;
use std::str::FromStr;

pub mod libpass;

pub const PASSES: [&str; 5] = [
    "DLjTLmoWYbshrrTcNuugdadVATZCYZhoNBkxZWzaMbjxZjcvqLKCjjoRbQzdnWkzBTkNCCHk",
    "giraffechocolatetreeoceandancemirrorpencilbridgesunshinemusicheartheartl",
    "tigerflowersuitcasecloudrainbowpencilmountainbreezecandledoorchairchairl",
    "cactuskeyboardicecreamdrumbookwormpuzzlelanternbutterflystonestonechairl",
    "laptopoceanbubblechaircoffeestarfishbicyclemoonlightguitarfeathergrassrl",
];

pub const LOGINS: [&str; 5] = ["bright", "calmly", "elegant", "joyful", "noble"];

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

#[derive(Parser)]
#[command(version, about, long_about = None)]
pub struct Cli {
    #[arg(short, long, value_name = "KEY")]
    load_key: Option<String>,
    #[arg(short, long, value_name = "BOOL")]
    gen_object: Option<bool>,
    #[arg(short, long, value_name = "String")]
    decode_tx: Option<String>,
}

pub fn main() {
    let cli = Cli::parse();

    if let Some(hex) = cli.decode_tx {
        let mut secret_bytes: [u8; 32] = [0u8; 32];
        secret_bytes.copy_from_slice(
            PrivateKey::from_str(
                Xpriv::from_str(TEST_KEYL)
                    .unwrap()
                    .to_priv()
                    .to_string()
                    .as_str(),
            )
            .unwrap()
            .to_bytes()
            .as_slice(),
        );

        let str = hex.as_str();
        let tx = match hex::decode(&str) {
            Ok(t) => t,
            Err(_) => {
                println!("couldnt decode transaction");
                return;
            }
        };
        let tx = Transaction::consensus_decode(&mut tx.as_slice()).unwrap();
        println!("Using default key");

        let decoded_obj = get_obj_from_tx(&tx, secret_bytes).unwrap();
        println!(
            "Object from the transaction: {} - {} ",
            decoded_obj.0, decoded_obj.1
        );
        return;
    }

    let mut sk: Option<PrivateKey> = None;
    let mut pk: Option<PublicKey> = None;

    // Load key handler
    if let Some(s) = cli.load_key {
        let bytes = s.as_bytes();
        if let Ok(k) = PublicKey::from_slice(bytes) {
            pk = Some(k);
        } else {
            sk = Some(
                PrivateKey::from_slice(bytes, bitcoin::Network::Bitcoin).unwrap_or_else(|_| {
                    bitcoin::PrivateKey::from_slice(TEST_KEYL.as_bytes(), bitcoin::Network::Bitcoin)
                        .unwrap()
                }),
            );
        }
    }

    // Generate a login-password if requested
    let (login, password) = if cli.gen_object.unwrap_or(false) {
        println!("");
        println!("Generating a login-password...");
        println!("");
        let mut rng = rand::thread_rng();
        let n = rng.gen_range(0..5);
        let l = format!("{}{}", LOGINS[n % 5], rng.gen_range(10..99));
        println!("Generated login is: {}", l);
        let p = PASSES[n % 5];
        println!("Generated password is: {}", p);
        println!("");
        println!("Done!");
        (Some(l), Some(p))
    } else {
        (None, None)
    };

    if sk.is_none() && pk.is_none() {
        println!("No valid key provided. Using test one");
        sk = Some(
            PrivateKey::from_str(
                Xpriv::from_str(TEST_KEYL)
                    .unwrap()
                    .to_priv()
                    .to_string()
                    .as_str(),
            )
            .unwrap(),
        );
    }

    let sk = sk.unwrap();
    // Create a buffer for the KVObject
    let mut buffer = [0u8; 80];
    let login = login.unwrap_or_else(|| {
        panic!("Login should be generated or provided, for now use \" chainpass -g true \"");
    });
    let password = password.unwrap_or_else(|| {
        panic!("Password should be generated or provided");
    });

    buffer.copy_from_slice([login.as_bytes(), password.as_bytes()].concat().as_slice());
    let obj = KVObject(buffer);

    let mut secret_bytes: [u8; 32] = [0u8; 32];
    secret_bytes.copy_from_slice(sk.to_bytes().as_slice());

    // Encrypt the KVObject
    let encrypted = obj.encrypt_data(&secret_bytes).unwrap();
    let address = Address::p2wpkh(
        &CompressedPublicKey::from_private_key(&Secp256k1::new(), &sk).unwrap(),
        Network::Bitcoin,
    );
    println!("");
    println!(
        "Please fund this address: |{}| with enough sats to pay for the transaction vbytes",
        address
    );
    println!("");
    // Create the transaction
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
            value: Amount::from_sat(0), // You might want to adjust this based on your funding
            script_pubkey: create_op_return(&encrypted),
        }],
    };

    let mut buffer = Vec::<u8>::new();
    transaction.consensus_encode(&mut buffer).unwrap();
    println!("Transaction Hex: {}", buffer.to_lower_hex_string());
}
