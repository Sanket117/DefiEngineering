# Wallet Credit Score Analysis

## Score Distribution
The score distribution is visualized in a bar chart (`score_distribution.png` and `score_distribution.json`), showing the number of wallets in each 100-point range (0–100, 100–200, ..., 900–1000). The distribution is as follows:
- 0–100: 179 wallets
- 100–200: 4 wallets
- 200–300: 1 wallet
- 300–400: 1 wallet
- 400–500: 7 wallets
- 500–600: 357 wallets
- 600–700: 1900 wallets
- 700–800: 105 wallets
- 800–900: 765 wallets
- 900–1000: 164 wallets
Most wallets (1900 in 600–700) exhibit moderate to reliable behavior, with a significant peak at 600–700. A notable portion (765 in 800–900) reflects highly reliable usage, while a smaller group (179 in 0–100) indicates risky behavior. High scores (900–1000) are less common (164 wallets), suggesting rare exemplary behavior.

## Low-Score Wallets (0–400)
- **Characteristics**:
  - High `liquidation_to_total_ratio` (>0.1), indicating frequent liquidations.
  - Low `repay_to_borrow_ratio` (<0.5), suggesting unpaid debts.
  - High `borrow_to_deposit_ratio` (>2), indicating over-leveraging.
  - Short `wallet_age_days` (<30) and high `tx_frequency` (>10/day), suggesting bot-like or speculative behavior.
- **Example Behavior**: The 179 wallets in the 0–100 range, along with the few in 100–400, likely include those with rapid `redeemunderlying` after borrowing or multiple `liquidationcall` events, indicating risky or exploitative usage.

## High-Score Wallets (800–1000)
- **Characteristics**:
  - High `repay_to_borrow_ratio` (>0.9), indicating timely repayments.
  - Zero `has_liquidation`, showing no defaults.
  - Long `wallet_age_days` (>100) and low `borrow_to_deposit_ratio` (<1), suggesting stable, conservative usage.
  - High `total_deposit_usd` and consistent transaction patterns.
- **Example Behavior**: The 765 wallets in the 800–900 range and 164 in 900–1000 likely include those with regular `deposit` and `repay` actions, no liquidations, and diverse asset usage (e.g., USDC, WMATIC).

## Insights
- **Cluster Analysis**:
  - **Cluster 0 (Reliable)**: Likely corresponds to the 800–1000 range (929 wallets total), with high deposits, repayments, and wallet age; no liquidations.
  - **Cluster 4 (Risky)**: Likely includes the 0–100 range (179 wallets), with high borrows, liquidations, and short-term activity.
  - **Clusters 1–3**: Span the 400–700 range (2265 wallets), reflecting moderate behavior (e.g., partial repayments, occasional redeems).
- **Bot-Like Behavior**: The 179 wallets in 0–100 with high `tx_frequency` and low `wallet_age_days` suggest automated or exploitative activity.
- **Data Gaps**: The scarcity of `borrow` or `liquidationcall` actions (implied by low 0–400 counts) may skew scores higher. Additional data (e.g., collateral details) could refine risk assessment.
