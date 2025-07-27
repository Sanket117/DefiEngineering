import pandas as pd
import json
import requests
import time
from datetime import datetime
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')

# Compound V2 Contract Addresses (Mainnet)
COMPOUND_V2_CONTRACTS = {
    'cDAI': '0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643',
    'cUSDC': '0x39AA39c021dfbaE8faC545936693aC917d5E7563',
    'cUSDT': '0xf650C3d88D12dB855b8bf7D11Be6C55A4e07dCC9',
    'cETH': '0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5',
    'cWBTC': '0xC11b1268C1A384e55C48c2391d8d480264A3A7F4',
    'cWBTC2': '0xccF4429DB6322D5C611ee964527D42E5d685DD6a',
    'cZRX': '0xB3319f5D18Bc0D84dD1b4825Dcde5d5f7266d407',
    'cBAT': '0x6C8c6b02E7b2BE14d4fA6022Dfd6d75921D90E4E',
    'cREP': '0x158079Ee67Fce2f58472A96584A73C7Ab9AC95c1',
    'cSAI': '0xF5DCe57282A584D2746FaF1593d3121Fcac444dC',
    'cCOMP': '0x70e36f6BF80a52b3B46b3aF8e106CC0ed743E8e4'
}

# Compound V3 USDC Contract (Mainnet)
COMPOUND_V3_CONTRACTS = {
    'cUSDCv3': '0xc3d688B66703497DAA19211EEdff47f25384cdc3'
}

# Combine all Compound contracts
ALL_COMPOUND_CONTRACTS = {**COMPOUND_V2_CONTRACTS, **COMPOUND_V3_CONTRACTS}

# Function signatures for Compound V2
COMPOUND_V2_FUNCTIONS = {
    'mint': '0xa0712d68',           # mint(uint256)
    'redeem': '0xdb006a75',        # redeem(uint256)
    'redeemUnderlying': '0x852a12e3',  # redeemUnderlying(uint256)
    'borrow': '0xc5ebeaec',        # borrow(uint256)
    'repayBorrow': '0x0e752702',   # repayBorrow(uint256)
    'repayBorrowBehalf': '0x2608f818',  # repayBorrowBehalf(address,uint256)
    'liquidateBorrow': '0xf5e3c462'     # liquidateBorrow(address,uint256,address)
}

# Function signatures for Compound V3
COMPOUND_V3_FUNCTIONS = {
    'supply': '0xf2b9fdb8',        # supply(address,uint256)
    'withdraw': '0xf3fef3a3',      # withdraw(address,uint256)
    'borrow': '0x4b8a3529',       # Different signature for V3
    'repay': '0x1ededc91'         # Different signature for V3
}

def load_wallet_addresses(csv_file_path):
    """Load wallet addresses from CSV file"""
    try:
        # Try different possible column names
        df = pd.read_csv(csv_file_path)
        
        wallet_column = 'wallet_id'
    
        
        # Extract wallet addresses and clean them
        wallet_addresses = df[wallet_column].astype(str).str.strip().str.lower()
        
        # Filter out any invalid addresses (should start with 0x and be 42 characters)
        valid_addresses = []
        for addr in wallet_addresses:
            if addr.startswith('0x') and len(addr) == 42:
                valid_addresses.append(addr)
            else:
                print(f"Skipping invalid address: {addr}")
        
        print(f"Loaded {len(valid_addresses)} valid wallet addresses from {csv_file_path}")
        return valid_addresses
        
    except Exception as e:
        print(f"Error loading wallet addresses from CSV: {e}")
        return []

class CompoundDataCollector:
    def __init__(self, etherscan_api_key):
        self.api_key = etherscan_api_key
        self.base_url = "https://api.etherscan.io/api"
        self.rate_limit_delay = 0.25  # 4 requests per second to be safe
        
    def get_wallet_transactions(self, wallet_address, start_block=0, end_block=99999999):
        """Fetch all transactions for a wallet address"""
        try:
            params = {
                'module': 'account',
                'action': 'txlist',
                'address': wallet_address,
                'startblock': start_block,
                'endblock': end_block,
                'page': 1,
                'offset': 10000,  # Max allowed by Etherscan
                'sort': 'asc',
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            time.sleep(self.rate_limit_delay)
            
            if response.status_code == 200:
                data = response.json()
                if data['status'] == '1':
                    return data['result']
                elif data['message'] == 'No transactions found':
                    return []
            print(f"API Error for {wallet_address}: {response.text}")
            return []
        except Exception as e:
            print(f"Error fetching transactions for {wallet_address}: {e}")
            return []
    
    def parse_compound_action(self, input_data, contract_address):
        """Parse the function signature to determine action type"""
        if len(input_data) < 10:
            return None
            
        function_sig = input_data[:10].lower()
        
        # Check if it's a V3 contract
        if contract_address.lower() in [addr.lower() for addr in COMPOUND_V3_CONTRACTS.values()]:
            if function_sig == COMPOUND_V3_FUNCTIONS['supply']:
                return 'supply'
            elif function_sig == COMPOUND_V3_FUNCTIONS['withdraw']:
                return 'withdraw'
            elif function_sig == COMPOUND_V3_FUNCTIONS['borrow']:
                return 'borrow'
            elif function_sig == COMPOUND_V3_FUNCTIONS['repay']:
                return 'repay'
        else:
            # V2 contract
            if function_sig == COMPOUND_V2_FUNCTIONS['mint']:
                return 'supply'  # mint = supply in V2
            elif function_sig in [COMPOUND_V2_FUNCTIONS['redeem'], COMPOUND_V2_FUNCTIONS['redeemUnderlying']]:
                return 'redeem'
            elif function_sig == COMPOUND_V2_FUNCTIONS['borrow']:
                return 'borrow'
            elif function_sig in [COMPOUND_V2_FUNCTIONS['repayBorrow'], COMPOUND_V2_FUNCTIONS['repayBorrowBehalf']]:
                return 'repay'
            elif function_sig == COMPOUND_V2_FUNCTIONS['liquidateBorrow']:
                return 'liquidation'
        
        return None
    
    def filter_compound_transactions(self, transactions):
        """Filter transactions to only include Compound protocol interactions"""
        compound_txs = []
        compound_addresses = set([addr.lower() for addr in ALL_COMPOUND_CONTRACTS.values()])
        
        for tx in transactions:
            # Check if transaction is to a Compound contract
            if tx['to'] and tx['to'].lower() in compound_addresses:
                # Parse function call
                action_type = self.parse_compound_action(tx['input'], tx['to'])
                if action_type:
                    # Determine contract type and token
                    contract_name = None
                    for name, addr in ALL_COMPOUND_CONTRACTS.items():
                        if addr.lower() == tx['to'].lower():
                            contract_name = name
                            break
                    
                    compound_tx = {
                        'userWallet': tx['from'].lower(),
                        'timestamp': int(tx['timeStamp']),
                        'action': action_type,
                        'contract_address': tx['to'].lower(),
                        'contract_name': contract_name,
                        'value_eth': float(tx['value']) / 1e18 if tx['value'] != '0' else 0,
                        'gas_used': int(tx['gasUsed']) if tx['gasUsed'] else 0,
                        'gas_price': int(tx['gasPrice']) if tx['gasPrice'] else 0,
                        'tx_hash': tx['hash'],
                        'block_number': int(tx['blockNumber']),
                        'is_error': tx['isError'] == '1'
                    }
                    compound_txs.append(compound_tx)
        
        return compound_txs
    
    def process_wallet_data(self, wallet_addresses):
        """Process all wallet addresses and return transaction data"""
        all_transactions = []
        
        print(f"Processing {len(wallet_addresses)} wallets...")
        
        for i, wallet in enumerate(wallet_addresses):
            print(f"Processing wallet {i+1}/{len(wallet_addresses)}: {wallet}")
            
            # Get transactions
            transactions = self.get_wallet_transactions(wallet.lower())
            
            if transactions:
                # Filter for Compound interactions
                compound_txs = self.filter_compound_transactions(transactions)
                all_transactions.extend(compound_txs)
                print(f"  Found {len(compound_txs)} Compound transactions")
            else:
                print(f"  No transactions found")
            
            # Rate limiting - be conservative
            time.sleep(self.rate_limit_delay)
        
        print(f"Total Compound transactions found: {len(all_transactions)}")
        return pd.DataFrame(all_transactions)

def engineer_compound_features(df, wallet_addresses):
    """Engineer features from Compound transaction data"""
    if df.empty:
        print("No transaction data available for feature engineering")
        # Create empty features for all wallets
        features = pd.DataFrame({
            'userWallet': wallet_addresses,
            'total_transactions': [0] * len(wallet_addresses),
            'num_supplies': [0] * len(wallet_addresses),
            'num_borrows': [0] * len(wallet_addresses),
            'num_repays': [0] * len(wallet_addresses),
            'num_redeems': [0] * len(wallet_addresses),
            'num_withdraws': [0] * len(wallet_addresses),
            'num_liquidations': [0] * len(wallet_addresses),
            'unique_contracts': [0] * len(wallet_addresses),
            'total_gas_used': [0] * len(wallet_addresses),
            'avg_gas_per_tx': [0] * len(wallet_addresses),
            'wallet_age_days': [0] * len(wallet_addresses),
            'tx_frequency_per_day': [0] * len(wallet_addresses),
            'has_liquidation': [0] * len(wallet_addresses),
            'liquidation_ratio': [0] * len(wallet_addresses),
            'borrow_repay_ratio': [0] * len(wallet_addresses),
            'supply_redeem_ratio': [0] * len(wallet_addresses),
            'diversification_score': [0] * len(wallet_addresses),
            'recent_activity': [99999] * len(wallet_addresses)  # Very high number for no activity
        })
        return features
    
    # Filter out failed transactions
    df = df[df['is_error'] == False].copy()
    
    if not df.empty:
        grouped = df.groupby('userWallet')
        
        features = pd.DataFrame({
            'userWallet': grouped.groups.keys(),
            'total_transactions': grouped.size(),
            'num_supplies': grouped.apply(lambda x: (x['action'] == 'supply').sum(), include_groups=False),
            'num_borrows': grouped.apply(lambda x: (x['action'] == 'borrow').sum(), include_groups=False),
            'num_repays': grouped.apply(lambda x: (x['action'] == 'repay').sum(), include_groups=False),
            'num_redeems': grouped.apply(lambda x: (x['action'] == 'redeem').sum(), include_groups=False),
            'num_withdraws': grouped.apply(lambda x: (x['action'] == 'withdraw').sum(), include_groups=False),
            'num_liquidations': grouped.apply(lambda x: (x['action'] == 'liquidation').sum(), include_groups=False),
            'unique_contracts': grouped['contract_name'].nunique(),
            'total_gas_used': grouped['gas_used'].sum(),
            'avg_gas_per_tx': grouped['gas_used'].mean(),
            'wallet_age_days': grouped['timestamp'].apply(lambda x: (x.max() - x.min()) / (24 * 3600) if len(x) > 1 else 0),
            'tx_frequency_per_day': grouped.apply(lambda x: len(x) / max(1, (x['timestamp'].max() - x['timestamp'].min()) / (24 * 3600)) if len(x) > 1 else 0, include_groups=False),
            'has_liquidation': grouped.apply(lambda x: (x['action'] == 'liquidation').any().astype(int), include_groups=False),
            'liquidation_ratio': grouped.apply(lambda x: (x['action'] == 'liquidation').sum() / len(x), include_groups=False),
            'borrow_repay_ratio': grouped.apply(lambda x: x[x['action'] == 'repay'].shape[0] / max(1, x[x['action'] == 'borrow'].shape[0]), include_groups=False),
            'supply_redeem_ratio': grouped.apply(lambda x: x[x['action'].isin(['redeem', 'withdraw'])].shape[0] / max(1, x[x['action'] == 'supply'].shape[0]), include_groups=False),
            'diversification_score': grouped['contract_name'].apply(lambda x: len(x.unique()) / len(x) if len(x) > 0 else 0),
            'recent_activity': grouped['timestamp'].apply(lambda x: (time.time() - x.max()) / (24 * 3600))  # Days since last activity
        }).fillna(0)
        
        features = features.reset_index(drop=True)
    else:
        # If no transactions found, create empty features
        features = pd.DataFrame({
            'userWallet': [],
            'total_transactions': [],
            'num_supplies': [],
            'num_borrows': [],
            'num_repays': [],
            'num_redeems': [],
            'num_withdraws': [],
            'num_liquidations': [],
            'unique_contracts': [],
            'total_gas_used': [],
            'avg_gas_per_tx': [],
            'wallet_age_days': [],
            'tx_frequency_per_day': [],
            'has_liquidation': [],
            'liquidation_ratio': [],
            'borrow_repay_ratio': [],
            'supply_redeem_ratio': [],
            'diversification_score': [],
            'recent_activity': []
        })
    
    # Ensure all wallets are included, even those with no transactions
    all_wallets_df = pd.DataFrame({'userWallet': wallet_addresses})
    features = all_wallets_df.merge(features, on='userWallet', how='left').fillna(0)
    
    # Set default values for wallets with no activity
    features.loc[features['recent_activity'] == 0, 'recent_activity'] = 99999
    
    return features

def calculate_risk_scores(features):
    """Calculate risk scores based on engineered features"""
    if features.empty:
        return features
    
    scores = []
    
    for _, row in features.iterrows():
        # Base score starts at 500 (neutral)
        score = 500
        
        # Transaction history bonus (up to +200 points)
        if row['total_transactions'] > 0:
            tx_bonus = min(100, row['total_transactions'] * 2)  # 2 points per transaction, max 100
            age_bonus = min(100, row['wallet_age_days'] * 0.5)  # 0.5 points per day, max 100
            score += tx_bonus + age_bonus
        else:
            # No transaction history = significant risk
            score -= 300
        
        # Liquidation penalty (severe)
        if row['has_liquidation']:
            score -= 400  # Heavy penalty for liquidations
        
        liquidation_penalty = row['liquidation_ratio'] * 300
        score -= liquidation_penalty
        
        # Borrow/Repay behavior (up to +/-150 points)
        if row['num_borrows'] > 0:
            if row['borrow_repay_ratio'] >= 1.0:
                score += 150  # Good repayment behavior
            elif row['borrow_repay_ratio'] >= 0.8:
                score += 100  # Decent repayment
            elif row['borrow_repay_ratio'] >= 0.5:
                score += 50   # Moderate repayment
            else:
                score -= 100  # Poor repayment history
        
        # Activity frequency bonus/penalty
        if row['tx_frequency_per_day'] > 1:
            score += 50   # Very active user
        elif row['tx_frequency_per_day'] > 0.1:
            score += 25   # Moderately active
        
        # Recent activity bonus
        if row['recent_activity'] < 30:  # Active in last 30 days
            score += 50
        elif row['recent_activity'] < 90:  # Active in last 90 days
            score += 25
        elif row['recent_activity'] > 365:  # Inactive for over a year
            score -= 100
        
        # Diversification bonus
        if row['unique_contracts'] > 3:
            score += 30
        elif row['unique_contracts'] > 1:
            score += 15
        
        # Gas efficiency (proxy for sophistication)
        if row['avg_gas_per_tx'] > 0:
            if row['avg_gas_per_tx'] < 100000:  # Efficient gas usage
                score += 25
            elif row['avg_gas_per_tx'] > 500000:  # Wasteful gas usage
                score -= 25
        
        # Ensure score is within bounds
        score = max(0, min(1000, score))
        scores.append(round(score))
    
    features['score'] = scores
    return features

def main():
    # Configuration
    ETHERSCAN_API_KEY = "A6PF7RSW8XNY8TM2DBA7BTTIJ1GW42NIVH"  
    WALLET_CSV_FILE = "Wallet.csv"  # Match your file name
    
    print(f"Starting main function at {datetime.now()}")
    print(f"\n0. Loading wallet addresses from {WALLET_CSV_FILE}...")
    try:
        wallet_addresses = load_wallet_addresses(WALLET_CSV_FILE)
        print(f"Loaded wallets: {wallet_addresses[:5]}...")  # First 5 wallets
    except Exception as e:
        print(f"Exception during wallet loading: {e}")
        return
    
    if not wallet_addresses:
        print("No valid wallet addresses found. Please check your CSV file.")
        return
    
    print("\n1. Initializing data collector...")
    collector = CompoundDataCollector(ETHERSCAN_API_KEY)
    print("\n2. Fetching transaction data from Compound protocols...")
    df = collector.process_wallet_data(wallet_addresses)
    print(f"DataFrame shape after fetching: {df.shape}")
    
    # Initialize data collector
    collector = CompoundDataCollector(ETHERSCAN_API_KEY)
    
    # Process all wallets
    print("\n1. Fetching transaction data from Compound protocols...")
    df = collector.process_wallet_data(wallet_addresses)
    
    # Save raw transaction data
    if not df.empty:
        df.to_csv('compound_transactions_raw.csv', index=False)
        print(f"Saved raw transaction data: {len(df)} transactions")
    
    # Engineer features
    print("\n2. Engineering risk assessment features...")
    features = engineer_compound_features(df, wallet_addresses)
    
    if not features.empty:
        # Save features
        features.to_csv('wallet_features.csv', index=False)
        print(f"Generated features for {len(features)} wallets")
        
        # Calculate risk scores
        print("\n3. Calculating risk scores...")
        features_with_scores = calculate_risk_scores(features)
        
        # Save final results in required format
        result_df = features_with_scores[['userWallet', 'score']].copy()
        result_df.columns = ['wallet_id', 'score']
        result_df.to_csv('wallet_scores.csv', index=False)
        
        print(f"\n=== RESULTS ===")
        print(f"Processed {len(result_df)} wallets")
        print(f"Score distribution:")
        print(f"  High Risk (0-300): {len(result_df[result_df['score'] <= 300])}")
        print(f"  Medium Risk (301-600): {len(result_df[(result_df['score'] > 300) & (result_df['score'] <= 600)])}")
        print(f"  Low Risk (601-1000): {len(result_df[result_df['score'] > 600])}")
        print(f"\nAverage score: {result_df['score'].mean():.1f}")
        print(f"Results saved to 'wallet_scores.csv'")
        
        # Show sample results
        print(f"\nSample results:")
        print(result_df.head(10).to_string(index=False))
        
    else:
        print("No features generated. Creating default scores...")
        # Create default scores for all wallets if no data found
        default_df = pd.DataFrame({
            'wallet_id': wallet_addresses,
            'score': [200] * len(wallet_addresses)  # Default low score for no activity
        })
        default_df.to_csv('wallet_scores.csv', index=False)
        print(f"Created default scores for {len(default_df)} wallets")

if __name__ == "__main__":
    main()