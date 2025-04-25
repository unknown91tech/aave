import json
from web3 import Web3
import os

# Configuration
INFURA_URL = "https://sepolia.infura.io/v3/d3826c909b504590bcfc68fda13432f3"  # Replace with your Infura Sepolia endpoint
PRIVATE_KEY = "your_private_key"  # Replace with your wallet's private key (from Coinbase/MetaMask)
WALLET_ADDRESS = "your_public_key"  # Replace with your wallet's public address

# Contract addresses (Sepolia testnet)
USDC_ADDRESS = "0x94a9D9AC8a22534E3FaCa9F4e7F2E2cf85d5E4C8"  # Correct USDC on Sepolia
AAVE_POOL_ADDRESS = "0x6Ae43d3271ff6888e7Fc43Fd7321a503ff738951"  # Aave V3 Pool on Sepolia


# Minimal ABI for USDC ERC20 (approve function)
USDC_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "spender", "type": "address"},
            {"name": "value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "account", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]

# Minimal ABI for Aave V3 Pool (deposit function)
AAVE_POOL_ABI = [
    {
        "inputs": [
            {"internalType": "address", "name": "asset", "type": "address"},
            {"internalType": "uint256", "name": "amount", "type": "uint256"},
            {"internalType": "address", "name": "onBehalfOf", "type": "address"},
            {"internalType": "uint16", "name": "referralCode", "type": "uint16"}
        ],
        "name": "deposit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Initialize web3
w3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Check connection
if not w3.is_connected():
    raise ConnectionError("Failed to connect to Sepolia testnet via Infura")

# Set default account
account = w3.eth.account.from_key(PRIVATE_KEY)
w3.eth.default_account = account.address

# Initialize contracts
usdc_contract = w3.eth.contract(address=USDC_ADDRESS, abi=USDC_ABI)
aave_pool_contract = w3.eth.contract(address=AAVE_POOL_ADDRESS, abi=AAVE_POOL_ABI)

def get_dynamic_gas_price():
    """Fetch current gas price and add a 20% buffer."""
    base_gas_price = w3.eth.gas_price
    return int(base_gas_price * 1.2)  # 20% higher than network average

def wait_for_transaction_receipt(tx_hash, max_attempts=5, timeout=300):
    """Wait for transaction receipt with retries."""
    for attempt in range(max_attempts):
        try:
            print(f"Attempt {attempt + 1}/{max_attempts} to fetch receipt for tx: {tx_hash.hex()}")
            receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
            return receipt
        except Exception as e:
            print(f"Retry {attempt + 1} failed: {str(e)}")
            if attempt == max_attempts - 1:
                raise Exception(f"Failed to fetch receipt after {max_attempts} attempts: {str(e)}")
            time.sleep(10)  # Wait before retrying
    return None

def approve_usdc(spender, amount):
    """
    Approve the Aave Pool to spend USDC on behalf of the wallet.
    :param spender: Address of the Aave Pool contract
    :param amount: Amount of USDC to approve (in wei)
    :return: Transaction hash
    """
    try:
        # Fetch nonce explicitly
        nonce = w3.eth.get_transaction_count(WALLET_ADDRESS, 'latest')
        print(f"Using nonce: {nonce}")

        # Build transaction
        tx = usdc_contract.functions.approve(spender, amount).build_transaction({
            'chainId': 11155111,  # Sepolia chain ID
            'gas': 150000,  # Increased gas limit
            'gasPrice': get_dynamic_gas_price(),
            'nonce': nonce,
        })

        # Sign transaction
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Approve transaction sent: {tx_hash.hex()}")

        # Wait for transaction receipt
        tx_receipt = wait_for_transaction_receipt(tx_hash)
        if tx_receipt.status == 1:
            print("Approve transaction successful")
            return tx_hash.hex()
        else:
            raise Exception("Approve transaction failed")
    except Exception as e:
        print(f"Error in approve_usdc: {str(e)}")
        raise

def deposit_to_aave(asset, amount, on_behalf_of):
    """
    Deposit USDC into Aave V3 Pool.
    :param asset: Address of the USDC token
    :param amount: Amount of USDC to deposit (in wei)
    :param on_behalf_of: Address to receive aTokens (usually the wallet address)
    :return: Transaction hash
    """
    try:
        # Fetch nonce explicitly
        nonce = w3.eth.get_transaction_count(WALLET_ADDRESS, 'latest')
        print(f"Using nonce: {nonce}")

        # Build transaction
        tx = aave_pool_contract.functions.deposit(
            asset,
            amount,
            on_behalf_of,
            0  # Referral code (0 for none)
        ).build_transaction({
            'chainId': 11155111,  # Sepolia chain ID
            'gas': 300000,
            'gasPrice': get_dynamic_gas_price(),
            'nonce': nonce,
        })

        # Sign transaction
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)

        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        print(f"Deposit transaction sent: {tx_hash.hex()}")

        # Wait for transaction receipt
        tx_receipt = wait_for_transaction_receipt(tx_hash)
        if tx_receipt.status == 1:
            print("Deposit transaction successful")
            return tx_hash.hex()
        else:
            raise Exception("Deposit transaction failed")
    except Exception as e:
        print(f"Error in deposit_to_aave: {str(e)}")
        raise

def check_balances():
    """Check ETH and USDC balances for debugging."""
    eth_balance = w3.eth.get_balance(WALLET_ADDRESS)
    print(f"ETH Balance: {w3.from_wei(eth_balance, 'ether')} ETH")
    
    # Add USDC balance check
    usdc_balance = usdc_contract.functions.balanceOf(WALLET_ADDRESS).call()
    print(f"USDC Balance: {usdc_balance / 10**6} USDC")

def main():
    # Amount to approve and deposit (1 USDC, 6 decimals)
    usdc_amount = w3.to_wei(1, 'mwei')  # 1 USDC = 10^6 wei

    try:
        # Check balances before starting
        print("Checking wallet balances...")
        check_balances()

        # Step 1: Approve Aave Pool to spend USDC
        print("Approving USDC for Aave Pool...")
        approve_tx_hash = approve_usdc(AAVE_POOL_ADDRESS, usdc_amount)
        print(f"Approve Tx Hash: {approve_tx_hash}")

        # Step 2: Deposit USDC into Aave Pool
        print("Depositing USDC to Aave Pool...")
        deposit_tx_hash = deposit_to_aave(USDC_ADDRESS, usdc_amount, WALLET_ADDRESS)
        print(f"Deposit Tx Hash: {deposit_tx_hash}")

    except Exception as e:
        print(f"Error in main: {str(e)}")

if __name__ == "__main__":
    main()
