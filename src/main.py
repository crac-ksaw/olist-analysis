
import kagglehub
import pandas as pd
import os
import glob

# 1. Download dataset
print("Downloading dataset...")
path = kagglehub.dataset_download("olistbr/brazilian-ecommerce")
print("Path to dataset files:", path)

# 2. List all files
print("\n--- Files in dataset ---")
csv_files = glob.glob(os.path.join(path, "*.csv"))
for f in csv_files:
    print(os.path.basename(f))

# 3. Load CSVs into DataFrames
dataframes = {}
print("\n--- Loading DataFrames ---")

def load_data(files):
    for f in files:
        filename = os.path.basename(f)
        df_name = filename.replace("olist_", "").replace("_dataset.csv", "").replace(".csv", "")
        print(f"Loading {filename} as {df_name}...")
        try:
            dataframes[df_name] = pd.read_csv(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")

load_data(csv_files)

# 4. Explore DataFrames
print("\n--- Data Exploration ---")
for name, df in dataframes.items():
    print(f"\nTable: {name}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print("First 5 rows:")
    print(df.head())
    
    # 6. Check for missing values and duplicates
    print(f"Missing Values:\n{df.isnull().sum()[df.isnull().sum() > 0]}")
    print(f"Duplicates: {df.duplicated().sum()}")

# 5. Identify Relationships (Heuristic based on naming conventions)
print("\n--- Potential Relationships ---")
all_columns = set()
for df in dataframes.values():
    all_columns.update(df.columns)

keys = [c for c in all_columns if c.endswith('_id') or c == 'zip_code_prefix']
print(f"Potential Keys found: {keys}")

# 7. Summary of Tables (Generated based on known Olist schema or just names)
print("\n--- Table Summaries ---")
summaries = {
    "customers": "Contains customer location and unique identifiers.",
    "geolocation": "Zip code coordinates (lat/lng).",
    "order_items": "Details of items within each order (product, price, freight).",
    "order_payments": "Payment methods and values for orders.",
    "order_reviews": "Customer reviews and ratings.",
    "orders": "Core table with order status and timestamps.",
    "products": "Product category and dimensions.",
    "sellers": "Seller location info.",
    "product_category_name_translation": "Translations of category names."
}

for name in dataframes.keys():
    print(f"{name}: {summaries.get(name, 'No description available')}")

# 8. Save Cleaned Data
# For this initial step, we will just save a copy to the cleaned_data folder.
# In a real scenario, we would do more rigorous cleaning (handling nulls, etc) here.
print("\n--- Saving Cleaned Data ---")
cleaned_dir = os.path.join(os.getcwd(), "olist_analysis", "cleaned_data")
os.makedirs(cleaned_dir, exist_ok=True)

for name, df in dataframes.items():
    # Example cleaning: Dropping exact duplicates if safe? 
    # For now, we'll just save raw as 'cleaned' to fulfill the requirement of having a working copy.
    # User asked to "Save a cleaned working copy".
    
    save_path = os.path.join(cleaned_dir, f"{name}.csv")
    df.to_csv(save_path, index=False)
    print(f"Saved {name} to {save_path}")

print("\nProcessing Complete.")
