pub mod object;

mod libpass {
    use anyhow::Result;
    use bdk::bitcoin::{PrivateKey, Transaction};
    use bitcoin::PublicKey;

    use super::object::KVObject;

    /// Receives a [`KVObject`] and build a ACP(Anyone can pay) transaction with it.
    pub fn build_transaction_from_object(obj: &KVObject, k: PublicKey) -> Result<Transaction> {
        unimplemented!()
    }
    /// Interpretates the transaction and extract the compressed object.
    pub fn extract_object_from_transaction(tx: &Transaction, sk: PrivateKey) -> Result<KVObject> {
        unimplemented!()
    }
    /// Scans the given key
    pub fn scan_on_key(k: &PublicKey) -> Result<Vec<u32>> {
        unimplemented!()
    }

    /// Module to hold the methods for the user to interact with libpass.
    pub mod user_api {

        use anyhow::Result;
        use bdk::bitcoin::{PrivateKey, PublicKey};
        use bitcoin::OutPoint;

        use super::super::object::*;

        /// This struct should hold user data that we need to scan the addresses, build transactions and extracting [`KVObject`]s.
        pub struct UserContext {
            key_pair: (Option<PrivateKey>, PublicKey),
            utxos: Vec<OutPoint>,
            pub objects: Vec<KVObject>,
        }
        impl UserContext {}
        /// Creates a KVObject from a key and a value.
        pub fn create_object(key: String, value: String) -> Result<KVObject> {
            unimplemented!()
        }
    }
    /// Module to hold the methods for creating transactions and scripts.
    pub mod transaction_builder {
        use bitcoin::OutPoint;

        /// A template that holds any context data that needs to be present while building a transaction.
        //TODO: ADD ALL THE INFOS NEEDED TO BUILD A TRANSACTION THAT STORES THE KVOBJECT IN THE CHAIN.
        pub struct PreTx {
            utxo_to_spend: OutPoint,
        }
    }
    /// Utils like contanst and other stuff.
    pub mod utils {
        /// Actually this is the tip while the development of this app... i think its impossible to have chainpass objects before its own creation.
        pub const HEIGHT_GATE: u32 = 866_800;
    }
}
