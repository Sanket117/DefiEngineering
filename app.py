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

# Your 100 wallet addresses
WALLET_ADDRESSES = [
    "0x0039f22efb07a647557c7c5d17854cfd6d489ef3",
    "0x06b51c6882b27cb05e712185531c1f74996dd988",
    "0x0795732aacc448030ef374374eaae57d2965c16c",
    "0x0aaa79f1a86bc8136cd0d1ca0d51964f4e3766f9",
    "0x0fe383e5abc200055a7f391f94a5f5d1f844b9ae",
    "0x104ae61d8d487ad689969a17807ddc338b445416",
    "0x111c7208a7e2af345d36b6d4aace8740d61a3078",
    "0x124853fecb522c57d9bd5c21231058696ca6d596",
    "0x13b1c8b0e696aff8b4fee742119b549b605f3cbc",
    "0x1656f1886c5ab634ac19568cd571bc72f385fdf7",
    "0x1724e16cb8d0e2aa4d08035bc6b5c56b680a3b22",
    "0x19df3e87f73c4aaf4809295561465b993e102668",
    "0x1ab2ccad4fc97c9968ea87d4435326715be32872",
    "0x1c1b30ca93ef57452d53885d97a74f61daf2bf4f",
    "0x1e43dacdcf863676a6bec8f7d6896d6252fac669",
    "0x22d7510588d90ed5a87e0f838391aaafa707c34b",
    "0x24b3460622d835c56d9a4fe352966b9bdc6c20af",
    "0x26750f1f4277221bdb5f6991473c6ece8c821f9d",
    "0x27f72a000d8e9f324583f3a3491ea66998275b28",
    "0x2844658bf341db96aa247259824f42025e3bcec2",
    "0x2a2fde3e1beb508fcf7c137a1d5965f13a17825e",
    "0x330513970efd9e8dd606275fb4c50378989b3204",
    "0x3361bea43c2f5f963f81ac70f64e6fba1f1d2a97",
    "0x3867d222ba91236ad4d12c31056626f9e798629c",
    "0x3a44be4581137019f83021eeee72b7dc57756069",
    "0x3e69ad05716bdc834db72c4d6d44439a7c8a902b",
    "0x427f2ac5fdf4245e027d767e7c3ac272a1f40a65",
    "0x4814be124d7fe3b240eb46061f7ddfab468fe122",
    "0x4839e666e2baf12a51bf004392b35972eeddeabf",
    "0x4c4d05fe859279c91b074429b5fc451182cec745",
    "0x4d997c89bc659a3e8452038a8101161e7e7e53a7",
    "0x4db0a72edb5ea6c55df929f76e7d5bb14e389860",
    "0x4e61251336c32e4fe6bfd5fab014846599321389",
    "0x4e6e724f4163b24ffc7ffe662b5f6815b18b4210",
    "0x507b6c0d950702f066a9a1bd5e85206f87b065ba",
    "0x54e19653be9d4143b08994906be0e27555e8834d",
    "0x56ba823641bfc317afc8459bf27feed6eb9ff59f",
    "0x56cc2bffcb3f86a30c492f9d1a671a1f744d1d2f",
    "0x578cea5f899b0dfbf05c7fbcfda1a644b2a47787",
    "0x58c2a9099a03750e9842d3e9a7780cdd6aa70b86",
    "0x58d68d4bcf9725e40353379cec92b90332561683",
    "0x5e324b4a564512ea7c93088dba2f8c1bf046a3eb",
    "0x612a3500559be7be7703de6dc397afb541a16f7f",
    "0x623af911f493747c216ad389c7805a37019c662d",
    "0x6a2752a534faacaaa153bffbb973dd84e0e5497b",
    "0x6d69ca3711e504658977367e13c300ab198379f1",
    "0x6e355417f7f56e7927d1cd971f0b5a1e6d538487",
    "0x70c1864282599a762c674dd9d567b37e13bce755",
    "0x70d8e4ab175dfe0eab4e9a7f33e0a2d19f44001e",
    "0x7399dbeebe2f88bc6ac4e3fd7ddb836a4bce322f",
    "0x767055590c73b7d2aaa6219da13807c493f91a20",
    "0x7851bdfb64bbecfb40c030d722a1f147dff5db6a",
    "0x7b4636320daa0bc055368a4f9b9d01bd8ac51877",
    "0x7b57dbe2f2e4912a29754ff3e412ed9507fd8957",
    "0x7be3dfb5b6fcbae542ea85e76cc19916a20f6c1e",
    "0x7de76a449cf60ea3e111ff18b28e516d89532152",
    "0x7e3eab408b9c76a13305ef34606f17c16f7b33cc",
    "0x7f5e6a28afc9fb0aaf4259d4ff69991b88ebea47",
    "0x83ea74c67d393c6894c34c464657bda2183a2f1a",
    "0x8441fecef5cc6f697be2c4fc4a36feacede8df67",
    "0x854a873b8f9bfac36a5eb9c648e285a095a7478d",
    "0x8587d9f794f06d976c2ec1cfd523983b856f5ca9",
    "0x880a0af12da55df1197f41697c1a1b61670ed410",
    "0x8aaece100580b749a20f8ce30338c4e0770b65ed",
    "0x8be38ea2b22b706aef313c2de81f7d179024dd30",
    "0x8d900f213db5205c529aaba5d10e71a0ed2646db",
    "0x91919344c1dad09772d19ad8ad4f1bcd29c51f27",
    "0x93f0891bf71d8abed78e0de0885bd26355bb8b1d",
    "0x96479b087cb8f236a5e2dcbfc50ce63b2f421da6",
    "0x96bb4447a02b95f1d1e85374cffd565eb22ed2f8",
    "0x9a363adc5d382c04d36b09158286328f75672098",
    "0x9ad1331c5b6c5a641acffb32719c66a80c6e1a17",
    "0x9ba0d85f71e145ccf15225e59631e5a883d5d74a",
    "0x9e6ec4e98793970a1307262ba68d37594e58cd78",
    "0xa7e94d933eb0c439dda357f61244a485246e97b8",
    "0xa7f3c74f0255796fd5d3ddcf88db769f7a6bf46a",
    "0xa98dc64bb42575efec7d1e4560c029231ce5da51",
    "0xb271ff7090b39028eb6e711c3f89a3453d5861ee",
    "0xb475576594ae44e1f75f534f993cbb7673e4c8b6",
    "0xb57297c5d02def954794e593db93d0a302e43e5c",
    "0xbd4a00764217c13a246f86db58d74541a0c3972a",
    "0xc179d55f7e00e789915760f7d260a1bf6285278b",
    "0xc22b8e78394ce52e0034609a67ae3c959daa84bc",
    "0xcbbd9fe837a14258286bbf2e182cbc4e4518c5a3",
    "0xcecf5163bb057c1aff4963d9b9a7d2f0bf591710",
    "0xcf0033bf27804640e5339e06443e208db5870dd2",
    "0xd0df53e296c1e3115fccc3d7cdf4ba495e593b56",
    "0xd1a3888fd8f490367c6104e10b4154427c02dd9c",
    "0xd334d18fa6bada9a10f361bae42a019ce88a3c33",
    "0xd9d3930ffa343f5a0eec7606d045d0843d3a02b4",
    "0xdde73df7bd4d704a89ad8421402701b3a460c6e9",
    "0xde92d70253604fd8c5998c8ee3ed282a41b33b7f",
    "0xded1f838ae6aa5fcd0f13481b37ee88e5bdccb3d",
    "0xebb8629e8a3ec86cf90cb7600264415640834483",
    "0xeded1c8c0a0c532195b8432153f3bfa81dba2a90",
    "0xf10fd8921019615a856c1e95c7cd3632de34edc4",
    "0xf340b9f2098f80b86fbc5ede586c319473aa11f3",
    "0xf54f36bca969800fd7d63a68029561309938c09b",
    "0xf60304b534f74977e159b2e159e135475c245526",
    "0xf67e8e5805835465f7eba988259db882ab726800",
    "0xf7aa5d0752cfcd41b0a5945867d619a80c405e52",
    "0xf80a8b9cfff0febf49914c269fb8aead4a22f847",
    "0xfe5a05c0f8b24fca15a7306f6a4ebb7dcf2186ac"
]

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

def engineer_compound_features(df):
    """Engineer features from Compound transaction data"""
    if df.empty:
        print("No transaction data available for feature engineering")
        return pd.DataFrame()
    
    # Filter out failed transactions
    df = df[df['is_error'] == False].copy()
    
    # Create a complete list of all wallets (including those with no transactions)
    all_wallets = [addr.lower() for addr in WALLET_ADDRESSES]
    
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
        # If no transactions found, create empty features for all wallets
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
    all_wallets_df = pd.DataFrame({'userWallet': all_wallets})
    features = all_wallets_df.merge(features, on='userWallet', how='left').fillna(0)
    
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
    
    print("=== Compound Protocol Wallet Risk Scoring System ===")
    
    # Initialize data collector
    collector = CompoundDataCollector(ETHERSCAN_API_KEY)
    
    # Process all wallets
    print("\n1. Fetching transaction data from Compound protocols...")
    df = collector.process_wallet_data(WALLET_ADDRESSES)
    
    # Save raw transaction data
    if not df.empty:
        df.to_csv('compound_transactions_raw.csv', index=False)
        print(f"Saved raw transaction data: {len(df)} transactions")
    
    # Engineer features
    print("\n2. Engineering risk assessment features...")
    features = engineer_compound_features(df)
    
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
        default_df = p