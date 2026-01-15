
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set Plot Style
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

CLEANED_DATA_DIR = os.path.join(os.getcwd(), "olist_analysis", "cleaned_data")
PLOTS_DIR = os.path.join(os.getcwd(), "olist_analysis", "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

def load_data():
    print("Loading data...")
    orders = pd.read_csv(os.path.join(CLEANED_DATA_DIR, "orders.csv"))
    items = pd.read_csv(os.path.join(CLEANED_DATA_DIR, "order_items.csv"))
    products = pd.read_csv(os.path.join(CLEANED_DATA_DIR, "products.csv"))
    customers = pd.read_csv(os.path.join(CLEANED_DATA_DIR, "customers.csv"))
    payments = pd.read_csv(os.path.join(CLEANED_DATA_DIR, "order_payments.csv"))
    return orders, items, products, customers, payments

def preprocess_data(orders, items, products, customers, payments):
    print("Preprocessing data...")
    # Convert dates
    orders['order_purchase_timestamp'] = pd.to_datetime(orders['order_purchase_timestamp'])
    
    # Merge tables
    # orders -> items (one-to-many)
    # items -> products (many-to-one)
    # orders -> customers (many-to-one) - Note: customer_id in orders maps to customer_id in customers table
    
    # 1. Merge Orders and Items
    merged_df = orders.merge(items, on='order_id', how='left')
    
    # 2. Merge with Products
    merged_df = merged_df.merge(products, on='product_id', how='left')
    
    # 3. Merge with Customers
    merged_df = merged_df.merge(customers, on='customer_id', how='left')
    
    # 4. Merge with Payments (Aggregating payments first to avoid duplication rows if multiple payments per order?)
    # Actually, simplistic usage: payments might have multiple rows per order. 
    # For Sales Analysis, we usually care about the order total.
    # The 'price' in order_items is per item. 'freight_value' is per item.
    # Let's verify revenue calculation using order_items price vs payments.
    # Approach: Use order_items for product sales analysis. Use payments for total GMV.
    # For this task, we will merge payments but be careful about duplicates if an order has multiple payments.
    # Let's checking if we need payment details or just total. 
    # Task asks to "Identify and load... payments" and "Create a unified sales DataFrame".
    # If we merge payments directly, we might duplicate item rows if there are multiple payments (e.g. voucher + credit card).
    # Safe bet: Calculate total payment per order and merge that.
    
    order_payments_agg = payments.groupby('order_id')['payment_value'].sum().reset_index()
    merged_df = merged_df.merge(order_payments_agg, on='order_id', how='left')
    
    return merged_df

def feature_engineering(df):
    print("Feature Engineering...")
    df['order_year'] = df['order_purchase_timestamp'].dt.year
    df['order_month'] = df['order_purchase_timestamp'].dt.strftime('%Y-%m') # YYYY-MM for sorting
    df['order_day'] = df['order_purchase_timestamp'].dt.day_name()
    
    # Revenue per line item is 'price'.
    # Validation: 'payment_value' should roughly equal sum(price + freight).
    
    # Customer Order Count (Frequency)
    customer_counts = df.groupby('customer_unique_id')['order_id'].nunique().reset_index()
    customer_counts.columns = ['customer_unique_id', 'customer_total_orders']
    
    df = df.merge(customer_counts, on='customer_unique_id', how='left')
    
    # Flag Repeat Customer
    df['customer_type'] = df['customer_total_orders'].apply(lambda x: 'Repeat' if x > 1 else 'One-time')
    
    return df

def sales_analysis(df):
    print("\n--- Sales Analysis ---")
    
    # Total Revenue (Sum of 'price' - strictly product revenue, excluding freight)
    total_revenue = df['price'].sum()
    total_orders = df['order_id'].nunique()
    
    print(f"Total Revenue (Product Sales): R$ {total_revenue:,.2f}")
    print(f"Total Orders: {total_orders}")
    
    print("\n[Insights]:")
    print(f"- The platform has generated R$ {total_revenue:,.2f} in product sales across {total_orders} orders.")
    
    # Monthly Sales Trend
    monthly_sales = df.groupby('order_month')['price'].sum().reset_index()
    
    # Plot Monthly Trend
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=monthly_sales, x='order_month', y='price', marker='o')
    plt.xticks(rotation=45)
    plt.title('Monthly Sales Trend')
    plt.ylabel('Revenue (R$)')
    plt.xlabel('Month')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "monthly_sales_trend.png"))
    print("Saved monthly_sales_trend.png")
    
    # Top 10 Products by Revenue
    top_products = df.groupby('product_id')['price'].sum().sort_values(ascending=False).head(10)
    print("\nTop 10 Products by Revenue:")
    print(top_products)
    
    # Top 10 Categories
    top_categories = df.groupby('product_category_name')['price'].sum().sort_values(ascending=False).head(10).reset_index()
    
    # Plot Top Categories
    plt.figure(figsize=(12, 6))
    sns.barplot(data=top_categories, x='price', y='product_category_name', palette='viridis')
    plt.title('Top 10 Product Categories by Revenue')
    plt.xlabel('Revenue (R$)')
    plt.ylabel('Category')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "top_10_categories.png"))
    print("Saved top_10_categories.png")
    
    print("\n[Insights]:")
    print(f"- The top category is '{top_categories.iloc[0]['product_category_name']}', driving significant revenue.")

def customer_analysis(df):
    print("\n--- Customer Analysis ---")
    
    unique_customers = df['customer_unique_id'].nunique()
    print(f"Number of Unique Customers: {unique_customers}")
    
    # Repeat vs One-time (based on Orders, not Line Items)
    # We need to drop duplicates per order to count customers correctly
    unique_orders = df.drop_duplicates(subset=['order_id'])
    
    cust_type_counts = unique_orders['customer_type'].value_counts()
    
    print("\nCustomer Distribution:")
    print(cust_type_counts)
    
    # Plot Customer Type
    plt.figure(figsize=(8, 8))
    plt.pie(cust_type_counts, labels=cust_type_counts.index, autopct='%1.1f%%', startangle=140, colors=['#ff9999','#66b3ff'])
    plt.title('Proportion of Repeat vs One-time Customers')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "customer_types_pie.png"))
    print("Saved customer_types_pie.png")
    
    # Average Order Value
    total_revenue_products = unique_orders['price'].sum() # Verify if this is correct aggregation.
    # Actually, df includes items. Summing 'price' in df gives total product revenue.
    # Summing 'payment_value' in unique_orders gives total GMV (inc freight).
    # Let's use Total Payment Value for AOV as it's what the customer pays.
    
    total_gmv = unique_orders['payment_value'].sum()
    aov = total_gmv / unique_orders.shape[0] # Total value / Total orders
    
    print(f"Average Order Value (AOV): R$ {aov:.2f}")
    
    print("\n[Insights]:")
    if cust_type_counts.get('Repeat', 0) / unique_customers < 0.1:
        print("- There is a very low repeat customer rate, indicating a business model driven by customer acquisition rather than retention.")
    else:
        print("- We see a healthy mix of repeat customers.")
    print(f"- On average, customers spend R$ {aov:.2f} per order.")

def main():
    orders, items, products, customers, payments = load_data()
    
    # Only keep delivered orders for sales analysis to be accurate?
    # Usually "delivered" or "shipped" implies revenue recognition.
    # Let's filter for simplicity unless user asked for all. User said "E-Commerce Sales", implies completed sales.
    orders = orders[orders['order_status'] == 'delivered']
    
    merged_df = preprocess_data(orders, items, products, customers, payments)
    merged_df = feature_engineering(merged_df)
    
    sales_analysis(merged_df)
    customer_analysis(merged_df)
    
    # Save Final Dataset
    save_path = os.path.join(CLEANED_DATA_DIR, "final_sales_dataset.csv")
    merged_df.to_csv(save_path, index=False)
    print(f"\nFinal dataset saved to {save_path}")

if __name__ == "__main__":
    main()
