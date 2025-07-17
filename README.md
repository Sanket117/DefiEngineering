```markdown
# Aave V2 Wallet Credit Scoring

## Overview
This project develops a machine learning model to assign credit scores (0–1000) to wallets interacting with the Aave V2 protocol on Polygon, based on transaction data (~87MB JSON). Higher scores indicate reliable behavior (e.g., timely repayments, low risk), while lower scores reflect risky or exploitative behavior (e.g., frequent liquidations).

## Method
We use unsupervised learning (K-Means clustering) to group wallets by transaction behavior, followed by a scoring mechanism. Features include transaction counts, USD-normalized volumes, repayment ratios, and risk indicators. The model’s clustering quality is validated using the silhouette score.

## Architecture
- **Input**: JSON file (`data/user-wallet-transactions.json`) with fields like `userWallet`, `action`, `timestamp`, and `actionData` (amount, assetSymbol, assetPriceUSD).
- **Processing**:
  1. Load JSON and normalize amounts to USD using token decimals (6 for USDC, 18 for WMATIC/DAI) and `assetPriceUSD`.
  2. Engineer features per wallet: transaction counts (deposits, borrows, repays, redeems, liquidations), USD volumes, ratios (repay-to-borrow, borrow-to-deposit), wallet age, and transaction frequency.
  3. Scale features using `StandardScaler`.
  4. Cluster wallets into 5 groups using K-Means (tunable via silhouette score).
  5. Assign scores: Reliable clusters (800–1000), moderate (400–800), risky (0–400), with adjustments based on repayment and risk features.
  6. Save scores to `wallet_scores.csv` and generate a score distribution chart (`score_distribution.json` and optional PNG).
- **Libraries**: `pandas`, `scikit-learn`, `numpy`, `matplotlib`.

## Processing Flow
1. Parse JSON into a DataFrame.
2. Convert transaction amounts to USD, handling token decimals and errors.
3. Aggregate features by `userWallet` (e.g., total deposits, repay-to-borrow ratio).
4. Normalize features and apply K-Means clustering.
5. Assign scores based on cluster and feature adjustments.
6. Output scores and visualize distribution.

## Extensibility
- Add features: Collateral ratios, interest rate analysis.
- Switch to supervised learning with labeled data.
- Optimize for larger datasets using `dask` or `pyspark`.

## Validation
- **Clustering Quality**: Silhouette score (printed during execution) measures clustering coherence (0.5–1.0 is good).
- **Score Logic**: Manual inspection of high/low-score wallets confirms alignment with behavior (e.g., high repayment → high score, liquidations → low score).
- **Robustness**: Tested on data subsets for consistency.

## Setup
1. Install dependencies: `pip install -r requirements.txt`.
2. Place `user-wallet-transactions.json` in `data/`.
3. Run: `python score_wallets.py`.

## Notes
- Handles missing/malformed data in `actionData` fields.
- Uses `include_groups=False` in pandas `apply` to avoid FutureWarnings.
```