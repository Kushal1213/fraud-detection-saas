"""
Generate demo transaction data for testing the SaaS application.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_demo_transactions(n=100):
    """Generate synthetic transaction data for demo purposes."""
    
    np.random.seed(42)
    
    # Generate transaction IDs
    transaction_ids = [f"T{i:06d}" for i in range(1, n+1)]
    
    # Generate transaction timestamps (over past 30 days)
    start_date = datetime.now() - timedelta(days=30)
    transaction_dts = [(start_date + timedelta(hours=np.random.randint(0, 720))).timestamp() for _ in range(n)]
    
    # Generate transaction amounts (with some outliers)
    base_amounts = np.random.exponential(scale=100, size=n)
    amounts = np.where(np.random.random(n) < 0.1, base_amounts * 5, base_amounts)  # 10% outliers
    amounts = np.clip(amounts, 10, 5000)
    
    # Generate product codes
    product_codes = np.random.choice(['W', 'H', 'C', 'S', 'R'], size=n)
    
    # Generate card information
    card1 = np.random.randint(10000, 99999, size=n)
    card2 = np.random.randint(10000, 99999, size=n)
    card3 = np.random.randint(100, 999, size=n)
    card4 = np.random.randint(100, 999, size=n)
    card5 = np.random.randint(100, 999, size=n)
    card6 = np.random.randint(100, 999, size=n)
    
    # Generate address information
    addr1 = np.random.randint(100, 999, size=n)
    addr2 = np.random.randint(200, 999, size=n)
    dist1 = np.random.randint(10, 200, size=n)
    dist2 = np.random.randint(10, 200, size=n)
    
    # Generate email domains
    email_domains = np.random.choice(['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'], size=n)
    p_emaildomain = email_domains
    r_emaildomain = np.where(np.random.random(n) < 0.8, p_emaildomain, np.random.choice(['gmail.com', 'yahoo.com'], size=n))
    
    # Create DataFrame
    df = pd.DataFrame({
        'TransactionID': transaction_ids,
        'TransactionDT': transaction_dts,
        'TransactionAmt': amounts,
        'ProductCD': product_codes,
        'card1': card1,
        'card2': card2,
        'card3': card3,
        'card4': card4,
        'card5': card5,
        'card6': card6,
        'addr1': addr1,
        'addr2': addr2,
        'dist1': dist1,
        'dist2': dist2,
        'P_emaildomain': p_emaildomain,
        'R_emaildomain': r_emaildomain
    })
    
    return df

if __name__ == "__main__":
    # Generate demo data
    df = generate_demo_transactions(100)
    
    # Save to CSV
    output_path = "demo_transactions.csv"
    df.to_csv(output_path, index=False)
    print(f"Generated {len(df)} demo transactions and saved to {output_path}")
    print(f"\nFirst 5 rows:")
    print(df.head())
    print(f"\nData types:")
    print(df.dtypes)
