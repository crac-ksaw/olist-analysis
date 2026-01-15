# 🇧🇷 Olist E-Commerce Sales & Customer Analysis

An end-to-end data analytics project exploring 100k+ orders from the Olist Brazilian E-Commerce dataset. This project moves from raw data processing to a production-grade analytics dashboard, designed to uncover actionable business insights.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B)
![Pandas](https://img.shields.io/badge/Pandas-Data-150458)

Click here to get to the site [Olist Interface](https://crac-ksaw-olist-analysis-srcdashboard-app-a6keww.streamlit.app)

## 🚀 What It Does Now (The Dashboard)

At the heart of this project is an interactive **Streamlit Dashboard** that serves as a tool for business stakeholders.

### Key Features
*   **English Normalization**: All product categories have been translated from Portuguese to English for international readability.
*   **Interactive Filtering**:
    *   **Time Travel**: Slice data by year using a range slider.
    *   **Category Drill-down**: Search and select specific product categories.
    *   **Customer Segmentation**: Toggle between *All*, *Repeat*, and *One-Time* customers.
*   **Executive KPIs**: Real-time cards for Revenue, Orders, Active Customers, and AOV.
*   **Visual Insights**:
    *   Monthly revenue trend analysis with seasonality peaks identified.
    *   Top 5 Category performance.
    *   Customer Retention breakdown (Repeat vs One-time).
    *   Top selling products list.

## 🛠 What We Did (The Process)

This project followed a rigorous data engineering and analysis workflow:

### 1. Data Acquisition & Setup
*   **Source**: Downloaded the [Olist Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) using `kagglehub`.
*   **Structure**: Established a professional directory structure separating `src` (code), `cleaned_data` (outputs), and `plots`.

### 2. Data Cleaning & Integration
*   **Loading**: Ingested 9 relational CSV files (Orders, Items, Products, Customers, Payments, etc.).
*   **Merging**: Constructed a unified "Gold Layer" dataset by joining tables on key identifiers (`order_id`, `product_id`, `customer_id`).
*   **Feature Engineering**:
    *   Derived date parts (Year, Month) for time-series analysis.
    *   Calculated Customer Order Frequency to flag **Repeat Customers**.
    *   Computed Total Revenue metrics.

### 3. Analysis & Refinement
*   **EDA**: Performed exploratory analysis to understand data shape, missing values, and business rules.
*   **Translation**: Mapped simplified English names to original Portuguese categories (e.g., `cama_mesa_banho` → `Bed Bath & Table`).
*   **Optimization**: Saved a final, feature-rich dataset (`final_sales_dataset.csv`) optimized for dashboard performance.

## 💻 How to Run

1.  **Install Dependencies**
    ```bash
    pip install pandas matplotlib seaborn plotly streamlit kagglehub
    ```

2.  **Run the Analysis Pipeline** (Optional, data is already cleaned)
    ```bash
    python olist_analysis/src/main.py            # Downloads & explores data
    python olist_analysis/src/sales_analysis.py  # Cleans & merges data
    ```

3.  **Launch the Dashboard**
    ```bash
    streamlit run olist_analysis/src/dashboard_app.py
    ```

## 📂 Project Structure

```
olist_analysis/
├── cleaned_data/              # Processed CSV files
│   ├── final_sales_dataset.csv
│   └── ...
├── plots/                     # Static visualizations
├── src/
│   ├── dashboard_app.py       # Streamlit Dashboard source
│   ├── main.py                # Data downloader & explorer
│   └── sales_analysis.py      # Data cleaning & merging logic
└── README.md                  # Project documentation
```

## 📸 App Screenshots

<img width="1862" height="862" alt="image" src="https://github.com/user-attachments/assets/277e4f62-1213-4267-9fe3-3f217e99cb43" />

With filters 
<img width="1864" height="844" alt="image" src="https://github.com/user-attachments/assets/ae5233e4-c942-4c45-a04a-84dd0ae6a663" />
<img width="1852" height="822" alt="image" src="https://github.com/user-attachments/assets/f381b218-0625-4b73-ac84-034d0cf8017d" />


