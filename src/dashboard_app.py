import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Page Configuration ---
st.set_page_config(
    page_title="Olist Analytics | Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Styling ---
st.markdown("""
<style>
    /* General Font Styling */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', Roboto, sans-serif;
    }
    
    /* KPI Card Styling */
    .metric-card {
        background-color: #1E1E1E;
        color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        text-align: center;
        height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #4CAF50;
        margin-bottom: 5px;
    }
    .metric-label {
        font-size: 15px;
        color: #BBBBBB;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Insight Box Styling */
    .insight-box {
        background-color: #262730;
        border-left: 4px solid #4CAF50;
        padding: 15px;
        border-radius: 5px;
        margin-top: 15px;
        font-size: 15px;
        color: #E0E0E0;
    }
    .insight-title {
        font-weight: bold;
        color: #4CAF50;
        margin-bottom: 5px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #111;
    }
    
    /* Header Divider */
    hr {
        margin-top: 1rem;
        margin-bottom: 2rem;
        border: 0;
        border-top: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- Data Loading & Translation ---
# Use relative path based on script location for better portability (Streamlit Cloud)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "cleaned_data")
DATA_PATH = os.path.join(DATA_DIR, "final_sales_dataset.csv")
TRANS_PATH = os.path.join(DATA_DIR, "product_category_name_translation.csv")

@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        st.error(f"Data file not found at {DATA_PATH}.")
        return None
    
    df = pd.read_csv(DATA_PATH)
    
    # Datetime conversion
    if 'order_purchase_timestamp' in df.columns:
        df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    
    # Load Translations
    if os.path.exists(TRANS_PATH):
        trans_df = pd.read_csv(TRANS_PATH)
        # Create dictionary: {'beleza_saude': 'Beauty & Health'}
        # Clean up English names (replace _ with space, title case)
        trans_df['product_category_name_english'] = trans_df['product_category_name_english'].astype(str).str.replace('_', ' ').str.title()
        
        # Merge translation
        trans_map = dict(zip(trans_df['product_category_name'], trans_df['product_category_name_english']))
        
        # Apply mapping
        df['category_name_eng'] = df['product_category_name'].map(trans_map)
        
        # Fill missing values with original (cleaned) or 'Unknown'
        df['category_name_eng'] = df['category_name_eng'].fillna(
            df['product_category_name'].str.replace('_', ' ').str.title()
        ).fillna("Unknown Category")
    else:
        # Fallback if no translation file
        df['category_name_eng'] = df['product_category_name'].str.replace('_', ' ').str.title().fillna("Unknown Category")
        
    return df

df = load_data()

if df is not None:
    # --- Sidebar Filters ---
    st.sidebar.title("🔍 Filter Analysis")
    st.sidebar.markdown("Refine the data below.")
    
    # 1. Year Filter (Slider or List)
    years = sorted(df['order_year'].unique())
    min_year, max_year = min(years), max(years)
    
    st.sidebar.subheader("📅 Time Period")
    selected_year_range = st.sidebar.select_slider(
        "Select Year Range",
        options=years,
        value=(min_year, max_year),
        label_visibility="collapsed"
    )
    
    # 2. Category Filter (Expandable Search)
    st.sidebar.subheader("📦 Product Category")
    all_categories = sorted(df['category_name_eng'].unique().tolist())
    
    # Option to select all by default implicitly (if empty list)
    with st.sidebar.expander("Select Categories", expanded=False):
        selected_categories = st.multiselect(
            "Choose categories (Empty = All)",
            options=all_categories,
            default=[]
        )
            
    # 3. Customer Type Filter (Radio)
    st.sidebar.subheader("👥 Customer Segment")
    cust_type_option = st.sidebar.radio(
        "Show data for:",
        options=["All Customers", "Repeat Customers", "One-Time Customers"],
        index=0
    )
    
    # --- Filter Logic ---
    filtered_df = df[
        (df['order_year'] >= selected_year_range[0]) & 
        (df['order_year'] <= selected_year_range[1])
    ]
    
    if selected_categories:
        filtered_df = filtered_df[filtered_df['category_name_eng'].isin(selected_categories)]
        
    if cust_type_option == "Repeat Customers":
        filtered_df = filtered_df[filtered_df['customer_type'] == 'Repeat']
    elif cust_type_option == "One-Time Customers":
        filtered_df = filtered_df[filtered_df['customer_type'] == 'One-time']
    
    # --- Main Layout ---
    st.title("🇧🇷 Olist Business Analytics")
    st.markdown("### Executive Sales & Customer Performance Dashboard")
    st.markdown("Track key performance indicators and uncover trends in the Brazilian e-commerce market.")
    st.markdown("---")
    
    # --- KPIs Section ---
    total_revenue = filtered_df['price'].sum()
    total_orders = filtered_df['order_id'].nunique()
    total_customers = filtered_df['customer_unique_id'].nunique()
    aov = total_revenue / total_orders if total_orders > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Revenue</div>
            <div class="metric-value">R$ {total_revenue:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Orders</div>
            <div class="metric-value">{total_orders:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Active Customers</div>
            <div class="metric-value">{total_customers:,}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Avg Order Value</div>
            <div class="metric-value">R$ {aov:,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")

    # --- Insight Logic Helper ---
    def get_max_month(df):
        if df.empty: return "N/A"
        monthly = df.groupby('order_month')['price'].sum()
        return pd.to_datetime(monthly.idxmax() + '-01').strftime('%B %Y')
        
    top_cat_name = "N/A"
    if not filtered_df.empty:
        top_cat_name = filtered_df.groupby('category_name_eng')['price'].sum().idxmax()
    
    # --- Row 1: Trends & Categories ---
    c_left, c_right = st.columns((2, 1))
    
    with c_left:
        st.subheader("📈 Monthly Revenue Trajectory")
        monthly_sales = filtered_df.groupby('order_month')['price'].sum().reset_index()
        
        if not monthly_sales.empty:
            fig_trend = px.line(
                monthly_sales, 
                x='order_month', 
                y='price',
                markers=True,
                labels={'price': 'Revenue (R$)', 'order_month': 'Month'},
                color_discrete_sequence=['#00CC96']
            )
            fig_trend.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#333'),
                margin=dict(l=0, r=0, t=10, b=0),
                height=350
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # Insight Box
            peak_month = get_max_month(filtered_df)
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">Key Insight</div>
                Revenue peaked in <strong>{peak_month}</strong>. The overall trend indicates market behavior and seasonality. 
                Monitor these spikes to optimize inventory planning.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No data available for the selected range.")

    with c_right:
        st.subheader("🏆 Top 5 Categories")
        top_cats = filtered_df.groupby('category_name_eng')['price'].sum().nlargest(5).reset_index()
        
        if not top_cats.empty:
            fig_cat = px.bar(
                top_cats,
                x='price',
                y='category_name_eng',
                orientation='h',
                labels={'price': 'Revenue', 'category_name_eng': ''},
                color='price',
                color_continuous_scale='Viridis'
            )
            fig_cat.update_layout(
                yaxis={'categoryorder':'total ascending', 'automargin': True},
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                margin=dict(l=0, r=0, t=10, b=0),
                height=350,
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_cat, use_container_width=True)
            
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">Category Leader</div>
                <strong>{top_cat_name}</strong> is the highest performing category, driving a significant portion of total revenue.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No data.")

    st.markdown("---")

    # --- Row 2: Customer & Product Detail ---
    c_b1, c_b2 = st.columns((1, 2))
    
    with c_b1:
        st.subheader("👥 Retention Mix")
        # Calc strictly on filtered users
        filtered_users = filtered_df.drop_duplicates(subset=['customer_unique_id'])
        cust_dist = filtered_users['customer_type'].value_counts().reset_index()
        cust_dist.columns = ['Type', 'Count']
        
        if not cust_dist.empty:
            fig_pie = px.pie(
                cust_dist, 
                values='Count', 
                names='Type', 
                color='Type',
                color_discrete_map={'Repeat': '#EF553B', 'One-time': '#636EFA'},
                hole=0.5
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                margin=dict(t=20, b=20, l=0, r=0),
                height=300,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_pie, use_container_width=True)
            
            repeat_rate = (filtered_users['customer_type'] == 'Repeat').mean() * 100
            
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">Retention Rate</div>
                Only <strong>{repeat_rate:.1f}%</strong> of visible customers are repeat buyers. Implement loyalty programs to boost LTV.
            </div>
            """, unsafe_allow_html=True)

    with c_b2:
        st.subheader("🔥 Top 5 Revenue Drivers (Products)")
        
        # Aggregate by Product ID
        prod_perf = filtered_df.groupby(['product_id', 'category_name_eng'])['price'].sum().reset_index()
        top_products = prod_perf.nlargest(5, 'price')
        
        # Cleanup ID for display
        top_products['Product ID'] = top_products['product_id'].apply(lambda x: x[:8] + '...')
        
        if not top_products.empty:
            fig_prod = px.bar(
                top_products,
                x='Product ID',
                y='price',
                color='category_name_eng',
                labels={'price': 'Revenue (R$)', 'Product ID': 'Product (Short ID)', 'category_name_eng': 'Category'},
                text_auto='.2s'
            )
            fig_prod.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="white",
                margin=dict(l=0, r=0, t=10, b=0),
                height=300
            )
            st.plotly_chart(fig_prod, use_container_width=True)
            
            st.markdown(f"""
            <div class="insight-box">
                <div class="insight-title">Product Focus</div>
                These top 5 items are critical revenue generators. Ensure supply chain stability for these high-demand SKUs.
            </div>
            """, unsafe_allow_html=True)
            
else:
    st.error("Data could not be loaded. Please ensure the analysis script has run.")
