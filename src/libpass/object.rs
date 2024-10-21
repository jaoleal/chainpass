/// Any data that can be reduced to a single key-value pair can be composed as a KVObject.
/// This trait contains the necessary methods to convert the data into Bitcoin script and set a fee for it.
/// Outputing the partial transaction.

pub struct KVObject {
    pub key: String,
    pub value: String,
}

impl KVObject {
    pub fn encode_to_consensus(&self) -> Vec<u8> {
        let mut encoded = vec![];
        encoded.extend_from_slice(&self.key.as_bytes());
        encoded.extend_from_slice(&self.value.as_bytes());
        encoded
    }
}
