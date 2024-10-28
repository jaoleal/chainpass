# The official repository of the Chainpass PoC

Chainpass exposes the possibility of storage of passwords on publick blockchains like the Bitcoin one.

## HOW

From a extended keypair, just like normal wallets that controls satoshis, we can derive keys just like specified on [Bip32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki).

Given an index, from the extended keypair, we can derive a private key and a public key and use their data to indexate and secure a cryptographic blob containining any piece of data inside the blockchain.

Details apart, a login-password String converted to bytes are used on the [AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) encryption function, using the private key as secret for the output and a ripemd160 of the private key as nounce.

The according publick key is then used to derive a bitcoin address which needed to be funded which a suficcient amount to pay for the vbytes that the transaction have.

Then, the transaction is constructed spending the address and only outputting an `op_return` with the encrypted data. We can track where the cryptographic blob is by the transaction that spend the address we funded earlier.

## The output of chainpass

Chainpass still limited on its functions, but its core its already working.

Everything is mocked and already in chainpass, just because i hadn`t time to develop IO with protect agains invariants (someone using it wrong).

install with
```bash
cargo install --path .#while in the repo of the app.
```

Run with
```bash
chainpass -g true # if you`re running directly the binary
#or
cargo run -- -g true
```

```bash
# this beta will auto generate login-password
Generating a login-password...

# result
Generated login is: joyful91
Generated password is: cactuskeyboardicecreamdrumbookwormpuzzlelanternbutterflystonestonechairl

Done!
# This warn is normal since well only use the test key
No valid key provided. Using test one

# bc1... is the fund address of the test key.
Please fund this address: |bc1qp30e58hrp0etgsl2q9y4tar26a93nwc0ym53vx| with enough sats to pay for the transaction vbytes

# raw hex
Transaction Hex: 020000000100000000000000000000000000000000000000000000000000000000000000000000000000fdffffff010000000000000000636a4c60e23cef4bff389159d5034f341c207d245cbffbeab1f2ec8999108aabb067c8ebc23cd2fc6f57e723969ea5d12c9b9dc8037d67de7f6adf7bd8b92718472248a5076aaa309bcd2a4741da6f297c3b6563896a85cafe74c93df6b66fca0b0f828300000000
```

now, you can use the hex encoded transaction (0200...) as input to
```Bash
chainpass -d #hex

#or

cargo run -- -d #hex
```
