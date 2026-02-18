from web3 import Web3
import json
import os

# Connect to Ganache
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

print(f"Connected: {web3.is_connected()}")
print(f"Accounts: {web3.eth.accounts}")

# Set default account (first account from Ganache)
account = web3.eth.accounts[0]
web3.eth.default_account = account

print(f"Using account: {account}")

# Read the contract
with open('RobotPayment.sol', 'r') as file:
    contract_source = file.read()

# For simplicity, let's compile with solcx
# Install: pip install py-solc-x
from solcx import compile_source, install_solc

# Install solc if not present
install_solc('0.8.0')

# Compile contract
compiled_sol = compile_source(contract_source)
contract_interface = compiled_sol['<stdin>:RobotPayment']

# Deploy contract
RobotPayment = web3.eth.contract(
    abi=contract_interface['abi'],
    bytecode=contract_interface['bin']
)

# Estimate gas
gas_estimate = web3.eth.estimate_gas({'from': account, 'data': contract_interface['bin']})
print(f"Gas estimate: {gas_estimate}")

# Deploy
tx_hash = RobotPayment.constructor().transact({'from': account, 'gas': gas_estimate})
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

print(f"Contract deployed at: {tx_receipt.contractAddress}")

# Save contract address to file
with open('contract_address.txt', 'w') as f:
    f.write(tx_receipt.contractAddress)

print("✅ Contract deployed successfully!")
print(f"Address saved to: contract_address.txt")