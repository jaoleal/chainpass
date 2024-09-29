use chainpass::libpass::KVObject;

pub fn main() {
    let test = KVObject {
        key: "key".to_string(),
        value: "value".to_string(),
    };

    println!("{}", test.to_bytes())
}
