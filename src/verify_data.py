import sys
import os

# Arquivo responsável pela verificação dos dados
sys.path.append(os.getcwd())

from src.data_loader import load_taco_data, get_foods_from_df

csv_path = 'data/taco.csv'

print(f"Loading data from {csv_path}...")
try:
    df = load_taco_data(csv_path)
    print("Data loaded successfully!")
    print(f"Shape: {df.shape}")
    print("\nFirst 5 rows:")
    print(df.head())
    
    print("\nChecking for missing values:")
    print(df.isnull().sum())
    
    print("\nSample Food Objects:")
    foods = get_foods_from_df(df.head(20))
    for f in foods:
        print(f)
    
    print("\nCategories Found:")
    print(df['category'].unique())
        
except Exception as e:
    print(f"Error loading data: {e}")
    import traceback
    traceback.print_exc()
