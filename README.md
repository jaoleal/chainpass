# The official repository of the Chainpass PoC

Chainpass exposes the possibility of storing passwords on publick blockchains like the Bitcoin one.

## HOW

From a extended keypair, just like normal wallets that controls satoshis, we can derive keys just like specified on [Bip32](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki).

Given an index, from the extended keypair, we can derive a private key and a publick key and use their data to indexate and secure a cryptographic blob containining any piece of data inside the blockchain.

Details apart, a login-password String converted to bytes are used on the [AES](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) encryption function, using the private key as secret for the output and a ripemd160 of the private key as nounce.

The according publick key is then used to derive a bitcoin address which needed to be funded which a suficcient amount to pay for the vbytes that the transaction have.

Then, the transaction is constructed spending the address and only outputting an `op_return` with the encrypted data. We can track where the cryptographic blob is by the transaction that spend the address we funded earlier.

## The output of chainpass

Chainpass still limited on its functions, but its core its already working.
