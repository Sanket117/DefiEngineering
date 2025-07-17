import pandas as pd
import json
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Load JSON file
try:
    with open('data/user-wallet-transactions.json', 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
except FileNotFoundError:
    print("Error: 'data/user-wallet-transactions.json' not found.")
    exit(1)
except json.JSONDecodeError:
    print("Error: Invalid JSON format in 'data/user-wallet-transactions.json'.")
    exit(1)

# Normalize amount to USD
def normalize_amount(row):
    try:
        amount = int(row['actionData']['amount'])
        asset_symbol = row['actionData']['assetSymbol']
        decimals = 6 if asset_symbol in ['USDC'] else 18
        price_usd = float(row['actionData']['assetPriceUSD'])
        return (amount / 10**decimals) * price_usd
    except (KeyError, ValueError, TypeError):
        return 0.0  # Handle missing or malformed data

df['amount_usd'] = df.apply(normalize_amount, axis=1)

# Feature engineering
def engineer_features(df):
    if df.empty:
        print("Error: Input DataFrame is empty.")
        return pd.DataFrame()
    
    grouped = df.groupby('userWallet')
    features = pd.DataFrame({
        'num_deposits': grouped.apply(lambda x: (x['action'] == 'deposit').sum(), include_groups=False),
        'num_borrows': grouped.apply(lambda x: (x['action'] == 'borrow').sum(), include_groups=False),
        'num_repays': grouped.apply(lambda x: (x['action'] == 'repay').sum(), include_groups=False),
        'num_redeems': grouped.apply(lambda x: (x['action'] == 'redeemunderlying').sum(), include_groups=False),
        'num_liquidations': grouped.apply(lambda x: (x['action'] == 'liquidationcall').sum(), include_groups=False),
        'total_transactions': grouped.size(),
        'total_deposit_usd': grouped.apply(lambda x: x[x['action'] == 'deposit']['amount_usd'].sum(), include_groups=False),
        'total_borrow_usd': grouped.apply(lambda x: x[x['action'] == 'borrow']['amount_usd'].sum(), include_groups=False),
        'total_repay_usd': grouped.apply(lambda x: x[x['action'] == 'repay']['amount_usd'].sum(), include_groups=False),
        'total_redeem_usd': grouped.apply(lambda x: x[x['action'] == 'redeemunderlying']['amount_usd'].sum(), include_groups=False),
        'net_borrow_usd': grouped.apply(lambda x: x[x['action'] == 'borrow']['amount_usd'].sum() - 
                                       x[x['action'] == 'repay']['amount_usd'].sum(), include_groups=False),
        'repay_to_borrow_ratio': grouped.apply(lambda x: x[x['action'] == 'repay']['amount_usd'].sum() / 
                                              x[x['action'] == 'borrow']['amount_usd'].sum() if x[x['action'] == 'borrow']['amount_usd'].sum() > 0 else 0, 
                                              include_groups=False),
        'borrow_to_deposit_ratio': grouped.apply(lambda x: x[x['action'] == 'borrow']['amount_usd'].sum() / 
                                                x[x['action'] == 'deposit']['amount_usd'].sum() if x[x['action'] == 'deposit']['amount_usd'].sum() > 0 else 0, 
                                                include_groups=False),
        'redeem_to_deposit_ratio': grouped.apply(lambda x: x[x['action'] == 'redeemunderlying']['amount_usd'].sum() / 
                                                x[x['action'] == 'deposit']['amount_usd'].sum() if x[x['action'] == 'deposit']['amount_usd'].sum() > 0 else 0, 
                                                include_groups=False),
        'has_liquidation': grouped.apply(lambda x: (x['action'] == 'liquidationcall').any().astype(int), include_groups=False),
        'liquidation_to_total_ratio': grouped.apply(lambda x: (x['action'] == 'liquidationcall').sum() / x.size if x.size > 0 else 0, include_groups=False),
        'wallet_age_days': grouped['timestamp'].apply(lambda x: (x.max() - x.min()) / (24 * 3600)),
        'tx_frequency': grouped.apply(lambda x: x.size / ((x['timestamp'].max() - x['timestamp'].min()) / (24 * 3600)) if (x['timestamp'].max() - x['timestamp'].min()) > 0 else 0, include_groups=False),
        'num_unique_assets': grouped['actionData'].apply(lambda x: x.apply(lambda y: y['assetSymbol']).nunique()),
        'avg_transaction_usd': grouped['amount_usd'].mean()
    }).fillna(0)
    return features.reset_index()

features = engineer_features(df)
if features.empty:
    print("Error: No features generated. Exiting.")
    exit(1)



# Normalize features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(features.drop(columns=['userWallet']))

# Clustering
kmeans = KMeans(n_clusters=5, random_state=42)
features['cluster'] = kmeans.fit_predict(X_scaled)



# Assign scores
def assign_scores(features):
    scores = []
    for _, row in features.iterrows():
        cluster = row['cluster']
        base_score = {
            0: 800,  # Reliable: high repay, low liquidation
            1: 600,  # Moderate-high
            2: 400,  # Moderate
            3: 200,  # Moderate-low
            4: 0     # Risky: high liquidation, low repay
        }[cluster]
        # Adjust score based on key features
        adjustment = (row['repay_to_borrow_ratio'] * 100 - 
                      row['liquidation_to_total_ratio'] * 200 - 
                      row['borrow_to_deposit_ratio'] * 50 + 
                      row['wallet_age_days'] * 0.1)
        score = min(max(base_score + adjustment, 0), 1000)
        scores.append(score)
    features['score'] = scores
    return features

features = assign_scores(features)

# Save scores
features[['userWallet', 'score']].to_csv('wallet_scores.csv', index=False)

# Score distribution chart
score_ranges = pd.cut(features['score'], bins=range(0, 1100, 100), right=False)
score_dist = score_ranges.value_counts().sort_index()

chart = {
    "type": "bar",
    "data": {
        "labels": [f"{i}-{i+100}" for i in range(0, 1000, 100)],
        "datasets": [{
            "label": "Wallet Score Distribution",
            "data": score_dist.values.tolist(),
            "backgroundColor": ["#36A2EB", "#FF6384", "#FFCE56", "#4BC0C0", "#9966FF", 
                              "#FF9F40", "#66BB6A", "#EF5350", "#26A69A", "#AB47BC"],
            "borderColor": ["#2E86C1", "#E91E63", "#FFB300", "#26A69A", "#7B1FA2", 
                           "#F57C00", "#388E3C", "#C62828", "#00897B", "#8E24AA"],
            "borderWidth": 1
        }]
    },
    "options": {
        "scales": {
            "y": {
                "beginAtZero": True,
                "title": {
                    "display": True,
                    "text": "Number of Wallets"
                }
            },
            "x": {
                "title": {
                    "display": True,
                    "text": "Score Range"
                }
            }
        },
        "plugins": {
            "legend": {
                "display": False
            },
            "title": {
                "display": True,
                "text": "Wallet Credit Score Distribution"
            }
        }
    }
}

# Save chart configuration
with open('score_distribution.json', 'w') as f:
    json.dump(chart, f, indent=2)

# Plot for visualization (optional, for local testing)
plt.bar([f"{i}-{i+100}" for i in range(0, 1000, 100)], score_dist.values, 
        color=["#36A2EB", "#FF6384", "#FFCE56", "#4BC0C0", "#9966FF", 
               "#FF9F40", "#66BB6A", "#EF5350", "#26A69A", "#AB47BC"])
plt.xlabel('Score Range')
plt.ylabel('Number of Wallets')
plt.title('Wallet Credit Score Distribution')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('score_distribution.png')
plt.close()
