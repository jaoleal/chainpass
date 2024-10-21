use chainpass::libpass::object::KVObject;

pub const TEST_KEYL: &str  = "xprv9s21ZrQH143K2JF8RafpqtKiTbsbaxEeUaMnNHsm5o6wCW3z8ySyH4UxFVSfZ8n7ESu7fgir8imbZKLYVBxFPND1pniTZ81vKfd45EHKX73";
pub fn main() {
    let test = KVObject {
        key: "key".to_string(),
        value: "value".to_string(),
    };
    println!("{:?}", test.encode_to_consensus())
}
