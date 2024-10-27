pub mod object;
pub mod user;

mod libpass {
    use anyhow::Result;
    use bdk::bitcoin::{PrivateKey, Transaction};
    use bitcoin::PublicKey;

    use super::object::*;

    use super::user;

    /// Utils like contanst and other stuff.
    mod utils {
        /// Actually this is the tip while the development of this app... i think its impossible to have chainpass objects before its own creation.
        pub const HEIGHT_GATE: u32 = 866_800;
    }
}
