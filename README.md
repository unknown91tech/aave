# Setup and Usage Guide

## Installation

1. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install required packages:
   ```bash
   pip install web3 python-dotenv
   ```

3. Set up your environment variables in the `aave_interaction.py` file:
   - `PRIVATE_KEY`: Your Ethereum wallet private key (without 0x prefix)

### Getting Sepolia USDC
1. You can get test USDC from various faucets or by swapping on Uniswap Sepolia
2. Some options:
   - Use [Aave's faucet](https://app.aave.com/faucet/) if available
   - Swap ETH for USDC on [Uniswap Sepolia](https://app.uniswap.org/)

## Running the Script

1. Make sure your virtual environment is activated
2. Run the script:
   ```bash
   python aave_interaction.py
   ```

3. The script will:
   - Connect to Sepolia via Infura
   - Approve USDC for Aave Pool
   - Deposit 0.1 USDC into Aave
   - Output transaction hashes that you can check on [Sepolia Etherscan](https://sepolia.etherscan.io/)



### Verifying Contract Addresses
The current addresses in the script should work for Sepolia testnet, but you can verify them:
- Check [Aave's documentation](https://docs.aave.com/developers/deployed-contracts/v3-testnet-addresses)
- Look up contract addresses on [Sepolia Etherscan](https://sepolia.etherscan.io/)

## Customizing the Script

### To change the deposit amount:
Modify the `amount_to_deposit` variable in the `main()` function:
```python
# Amount to approve and deposit (1 USDC, 6 decimals)
    usdc_amount = w3.to_wei(1, 'mwei')  # 1 USDC = 10^6 wei
```

### To use Holesky testnet instead:
Change the `TESTNET` variable from "sepolia" to "holesky" and update the contract addresses if needed:
```python
TESTNET = "holesky"
```
