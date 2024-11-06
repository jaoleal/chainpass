import hashlib
import random
from datetime import datetime

# Simulating a UTXO structure
class UTXO:
    def __init__(self, tx_id, output_index, amount):
        self.tx_id = tx_id
        self.output_index = output_index
        self.amount = amount

    def __repr__(self):
        return f"UTXO(tx_id={self.tx_id}, output_index={self.output_index}, amount={self.amount})"

def generate_block(block_number, previous_block_hash, utxo_pool):
    """
    Generate a block that includes transactions. Each transaction spends UTXOs
    and creates new ones.
    """
    block_data = {
        'block_number': block_number,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'previous_block_hash': previous_block_hash,
        'nonce': random.randint(0, 1000000),  # Random nonce for simplicity
        'transactions': [],
    }

    total_utxos_spent = 0
    new_utxos = []

    # Generate a random number of transactions (between 1 and 5)
    for _ in range(random.randint(1, 5)):
        # For each transaction, we will spend UTXOs from the pool and create new ones
        inputs = []
        outputs = []

        # Spend a random number of UTXOs (between 1 and 3)
        num_inputs = random.randint(1, 3)
        for _ in range(num_inputs):
            if len(utxo_pool) > 0:
                utxo = random.choice(utxo_pool)
                inputs.append(utxo)
                utxo_pool.remove(utxo)  # Remove from pool as it's spent
                total_utxos_spent += utxo.amount

        # Generate outputs for the transaction (1 or 2 outputs)
        num_outputs = random.randint(1, 2)
        for i in range(num_outputs):
            amount = random.randint(1, 1000)
            outputs.append(amount)
            new_utxos.append(UTXO(f"tx_{block_number}_{_}_output_{i}", i, amount))

        transaction = {
            'inputs': inputs,
            'outputs': outputs
        }

        block_data['transactions'].append(transaction)

    # Simplified block hash using block contents
    block_string = str(block_data).encode('utf-8')
    block_hash = hashlib.sha256(block_string).hexdigest()

    block_data['block_hash'] = block_hash
    block_data['new_utxos'] = new_utxos  # Track the new UTXOs created by the block

    # Add the new UTXOs to the pool
    utxo_pool.extend(new_utxos)

    return block_data

def write_blocks_to_file(file_name, num_blocks):
    utxo_pool = []  # Initialize empty UTXO pool

    with open(file_name, 'w') as f:
        # Initial previous block hash (simulating genesis block)
        previous_block_hash = '0' * 64

        for block_number in range(1, num_blocks + 1):
            block_data = generate_block(block_number, previous_block_hash, utxo_pool)

            f.write(f"Block #{block_number}\n")
            f.write(f"Block Hash: {block_data['block_hash']}\n")
            f.write(f"Previous Block Hash: {block_data['previous_block_hash']}\n")
            f.write(f"Timestamp: {block_data['timestamp']}\n")
            f.write(f"Nonce: {block_data['nonce']}\n")
            f.write(f"Transactions:\n")
            for tx_idx, tx in enumerate(block_data['transactions']):
                f.write(f"  Transaction #{tx_idx + 1}:\n")
                f.write(f"    Inputs:\n")
                for input_utxo in tx['inputs']:
                    f.write(f"      - {input_utxo}\n")
                f.write(f"    Outputs: {tx['outputs']}\n")

            f.write(f"New UTXOs created by this block:\n")
            for utxo in block_data['new_utxos']:
                f.write(f"  - {utxo}\n")
            
            f.write("\n" + "="*50 + "\n\n")
            previous_block_hash = block_data['block_hash']

# Usage
file_name = "bitcoin_blocks_with_utxos.txt"
num_blocks = 5  # Generate 5 blocks
write_blocks_to_file(file_name, num_blocks)

print(f"Generated {num_blocks} Bitcoin-like blocks with UTXOs in {file_name}")
