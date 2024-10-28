use bitcoin::{
    absolute::LockTime, bip32::Xpriv, consensus::Encodable, hashes::Hash, hex::DisplayHex,
    key::Secp256k1, transaction::Version, Address, Amount, CompressedPublicKey, Network, OutPoint,
    PrivateKey, PublicKey, ScriptBuf, Sequence, Transaction, TxIn, TxOut, Txid, Witness,
};
use clap::{command, Parser};
use libpass::{
    object::KVObject,
    user::{create_op_return, get_obj_from_tx, UserContext},
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
}

pub fn main() {
    let cli = Cli::parse();

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
        println!("Generating a login-password");
        let mut rng = rand::thread_rng();
        let n = rng.gen_range(0..5);
        let l = format!("{}{}", LOGINS[n % 5], rng.gen_range(10..99));
        println!("Generated login is: {}", l);
        let p = PASSES[n % 5];
        println!("Generated password is: {}", p);
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
    let pk = PublicKey::from_private_key(&Secp256k1::new(), &sk);

    // Create a buffer for the KVObject
    let mut buffer = [0u8; 80];
    let login = login.unwrap_or_else(|| {
        panic!("Login should be generated or provided");
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
    println!("Fund this address: {}", address);

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

    // Decode the object from the transaction
    let decoded_obj = get_obj_from_tx(&transaction, secret_bytes).unwrap();
    println!(
        "Object from the transaction: {} - {}",
        decoded_obj.0, decoded_obj.1
    );
}
pub fn example() {
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
        key_pair: (
            Some(bdk::bitcoin::PrivateKey::from_str(sk.to_string().as_str()).unwrap()),
            bdk::bitcoin::PublicKey::from_str(pk.to_string().as_str()).unwrap(),
        ),
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
