pub struct Object {
    pub content: String,
}

impl Object {
    pub fn to_script(&self) -> [u8] {
        format!("", self.content)
    }
}
