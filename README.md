## Assignment Objectives

The primary goal is to develop a scalable risk assessment model that can:
- Analyze wallet transaction histories from Compound V2/V3 protocols
- Extract meaningful behavioral features from on-chain data
- Generate reliable risk scores for lending and borrowing activities
- Provide transparent scoring methodology with clear justifications

## Technical Implementation

### Data Collection Method

The system utilizes the Etherscan API to retrieve comprehensive transaction data for each wallet address. The data collection process includes:

- **Transaction Retrieval**: Fetching complete transaction histories for all 100 wallet addresses
- **Protocol Filtering**: Identifying interactions specifically with Compound V2 and V3 contracts
- **Function Analysis**: Parsing transaction input data to classify specific DeFi actions (supply, borrow, repay, liquidation)
- **Data Validation**: Ensuring transaction integrity and filtering out failed transactions

### Feature Engineering

The risk assessment model incorporates 19 distinct features organized into several categories:

**Transaction Volume Metrics**
- Total transaction count and frequency patterns
- Action-specific counts (supplies, borrows, repayments, withdrawals)
- Gas usage patterns as indicators of user sophistication

**Behavioral Risk Indicators**
- Liquidation history and frequency
- Borrow-to-repay ratios indicating repayment reliability
- Supply-to-redeem ratios showing capital management patterns

**Activity Patterns**
- Wallet age and transaction frequency over time
- Recent activity levels and engagement consistency
- Protocol diversification across different Compound markets

**Risk Signals**
- Direct liquidation events (highest risk indicator)
- Poor repayment behavior patterns
- Extended periods of inactivity

### Scoring Methodology

The risk scoring algorithm employs a weighted point system starting from a neutral baseline of 500 points:

**Positive Score Factors (+points)**
- Transaction history depth (up to +200 points)
- Consistent repayment behavior (up to +150 points)
- Regular protocol engagement (+25-50 points)
- Portfolio diversification across markets (+15-30 points)
- Efficient gas usage patterns (+25 points)

**Negative Score Factors (-points)**
- Liquidation events (-400 points per occurrence)
- Poor repayment ratios (-100 points)
- Extended inactivity periods (-100 points)
- No transaction history (-300 points)

**Score Ranges**
- **High Risk (0-300)**: Wallets with liquidation history, poor repayment patterns, or no activity
- **Medium Risk (301-600)**: Wallets with mixed behavioral patterns or limited history
- **Low Risk (601-1000)**: Wallets demonstrating consistent, responsible DeFi usage

### Risk Indicator Justification

The selected risk indicators are based on established DeFi lending principles:

1. **Liquidation Events**: Direct evidence of over-leveraging and poor risk management
2. **Repayment Ratios**: Historical reliability in meeting debt obligations
3. **Activity Consistency**: Engaged users demonstrate better understanding of protocol risks
4. **Protocol Diversification**: Risk distribution across multiple markets indicates sophistication
5. **Transaction Patterns**: Regular, efficient interactions suggest experienced users

## Project Structure

```
wallet-risk-scoring/
├── main.py                     # Primary execution script
├── Wallet.csv                  # Input wallet addresses (100 wallets)
├── wallet_scores.csv           # Final output with risk scores
├── compound_transactions_raw.csv # Raw transaction data
├── wallet_features.csv         # Engineered features dataset
└── README.md                   # This documentation
```

## Usage Instructions

### Prerequisites
- Python 3.7+
- Required packages: pandas, requests, scikit-learn, numpy
- Valid Etherscan API key

### Execution Steps

1. **Setup Environment**
   ```bash
   pip install pandas requests scikit-learn numpy
   ```

2. **Configure API Access**
   - Update `ETHERSCAN_API_KEY` variable in main.py
   - Ensure wallet addresses are in Wallet.csv

3. **Run Analysis**
   ```bash
   python main.py
   ```

4. **Review Results**
   - Final scores: `wallet_scores.csv`
   - Feature analysis: `wallet_features.csv`
   - Raw data: `compound_transactions_raw.csv`

## Output Format

The final deliverable is a CSV file with the required structure:

| wallet_id | score |
|-----------|--------|
| 0xfaa0768bde629806739c3a4620656c5d26f44ef2 | 732 |
| 0x... | ... |

## Model Validation

The scoring system includes several validation mechanisms:
- Score normalization ensuring 0-1000 range compliance
- Default handling for wallets without transaction history
- Rate limiting for API calls to ensure data integrity
- Error handling for incomplete or corrupted transaction data

## Scalability Considerations

The system is designed for scalability through:
- Modular architecture separating data collection, feature engineering, and scoring
- Efficient API usage with built-in rate limiting
- Configurable parameters for different risk tolerance levels
- Extensible feature set for additional risk indicators

## Limitations and Future Improvements

**Current Limitations**
- Dependency on Etherscan API rate limits
- Focus limited to Compound protocol interactions
- Historical data analysis without predictive modeling

**Potential Enhancements**
- Integration with additional DeFi protocols (Aave, MakerDAO)
- Machine learning models for predictive risk assessment
- Real-time monitoring capabilities
- Cross-chain analysis integration

## Data Sources

- **Primary**: Etherscan API for Ethereum transaction data
- **Protocols**: Compound V2 and V3 smart contracts
- **Wallet Dataset**: 100 addresses provided via Google Sheets

This risk scoring system provides a robust foundation for DeFi lending risk assessment while maintaining transparency and scalability for future enhancements.
