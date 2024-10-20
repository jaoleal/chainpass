/// Any data that can be reduced to a single key-value pair can be composed as a KVObject.
/// This trait contains the necessary methods to convert the data into Bitcoin script and set a fee for it.
/// Outputing the partial transaction.

pub struct KVObject {
    pub key: String,
    pub value: String,
}

pub trait KVObjectApi<O = into<KVObject>> {
    fn to_script(&self) -> [u8];
    fn fee(&self) -> u64;
    fn to_tx(&self) -> Transaction;
}
