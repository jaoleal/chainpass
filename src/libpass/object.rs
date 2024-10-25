
use aes::cipher::KeyInit;
use aes_gcm::{aead::Aead, Aes256Gcm};
use aes_gcm_siv::{aead::AeadMut, Nonce};
use bdk::bitcoin::hashes::{ripemd160, Hash};

use anyhow::Result;
/// Any data that can be reduced to a single key-value pair can be composed as a KVObject.
/// This trait contains the necessary methods to convert the data into Bitcoin script and set a fee for it.
/// Outputing the partial transaction.
pub struct KVObject(pub [u8; 80]);

impl KVObject {
    pub fn decrypt(key: &[u8; 32], blob: &[u8]) -> Result<KVObject> {
        let cipher = Aes256Gcm::new_from_slice(key).unwrap();
        let hash160_key = ripemd160::Hash::hash(key);

        let nonce_bytes: [u8; 12] = [
            hash160_key[0],
            hash160_key[1],
            hash160_key[2],
            hash160_key[3],
            hash160_key[4],
            hash160_key[5],
            hash160_key[6],
            hash160_key[7],
            hash160_key[8],
            hash160_key[9],
            hash160_key[10],
            hash160_key[11],
        ];
        let nonce = Nonce::from_slice(&nonce_bytes);
        let mut ret: [u8; 80] = [0u8; 80];
        ret.copy_from_slice(&cipher.decrypt(nonce, blob).unwrap());
        Ok(KVObject(ret))
    }

    /// Concat, Encrypt, Compress(if needed) and return the raw bytes.
    pub fn encrypt_data(&self, key: &[u8; 32]) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
        let mut data = Vec::new();
        data.extend_from_slice(&self.0.clone());

        let cipher = Aes256Gcm::new_from_slice(key).unwrap();

        let hash160_key = ripemd160::Hash::hash(key);

        let nonce_bytes: [u8; 12] = [
            hash160_key[0],
            hash160_key[1],
            hash160_key[2],
            hash160_key[3],
            hash160_key[4],
            hash160_key[5],
            hash160_key[6],
            hash160_key[7],
            hash160_key[8],
            hash160_key[9],
            hash160_key[10],
            hash160_key[11],
        ];
        let nonce = Nonce::from_slice(&nonce_bytes);

        // Encrypt the data
        let ciphertext = cipher
            .encrypt(nonce, data.as_slice())
            .map_err(|e| format!("Encryption failed: {}", e))?;

        // Combine nonce and ciphertext for the final output
        // Format: [12 bytes nonce][...ciphertext]
        let mut output = Vec::with_capacity(ciphertext.len());
        output.extend_from_slice(&ciphertext);
        Ok(output)
    }
}
