import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import argparse

# Page config
st.set_page_config(
    page_title="Lazada Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

parser = argparse.ArgumentParser(
        description="Dashboard for product data from Lazada Singapore"
    )
parser.add_argument(
        "--file_name",
        type=str,
        default='mobiles-tablets_products.csv',
        help="Filename of the data"
    )
args = parser.parse_args()

# Load the data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(f"output/{args.file_name}")
        # Clean and prepare data
        df.dropna(subset=['price'], inplace=True)
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['review_count'] = pd.to_numeric(df['review_count'], errors='coerce')
        df['discount_percentage'] = pd.to_numeric(df['discount_percentage'], errors='coerce')
        
        # Clean data
        df = df[df['price'].notnull() & (df['price'] > 0)]
        
        # Fill missing values
        df['location'] = df['location'].fillna('Unknown')
        df['review_count'] = df['review_count'].fillna(0)
        df['discount_percentage'] = df['discount_percentage'].fillna(0)
        
        return df
    except FileNotFoundError:
        st.error("CSV file not found. Please run the scraper first.")
        return pd.DataFrame()

# Load data
data = load_data()

if not data.empty:
    category = data['category'].unique()[0] if 'category' in data.columns else 'Products'
    
    # Header
    st.title(f"🛒 Lazada {category.title()} Analytics")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    st.markdown("---")
    
    # Create three columns for the charts
    col1, col2, col3 = st.columns(3)
    
    # Chart 1: Distribution by Location
    with col1:
        st.subheader("🌍 Distribution by Location")
        location_counts = data['location'].value_counts().head(10)
        fig_location = px.bar(
            x=location_counts.values,
            y=location_counts.index,
            orientation='h',
            title="Products by Location",
            labels={'x': 'Number of Products', 'y': 'Location'}
        )
        fig_location.update_layout(
            height=500,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        st.plotly_chart(fig_location, use_container_width=True)
    
    # Chart 2: Most Expensive 5 Products
    with col2:
        st.subheader("💰 Most Expensive 5 Products")
        top_expensive = data.nlargest(5, 'price')[['product_name', 'price', 'review_count']]
        
        # Create a bar chart for the most expensive products
        fig_expensive = px.bar(
            top_expensive,
            x='price',
            y='product_name',
            orientation='h',
            title="Top 5 Most Expensive Products",
            labels={'price': 'Price (SGD)', 'product_name': 'Product'},
            text='price'
        )
        fig_expensive.update_layout(
            height=500,
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        fig_expensive.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
        st.plotly_chart(fig_expensive, use_container_width=True)
        

    # Chart 3: Price Distribution
    with col3:
        st.subheader("📊 Price Distribution")
        fig_price_dist = px.histogram(
            data, 
            x='price', 
            nbins=25,
            title="Price Distribution",
            labels={'price': 'Price (SGD)', 'count': 'Number of Products'}
        )
        fig_price_dist.update_layout(
            height=500,
            showlegend=False
        )
        st.plotly_chart(fig_price_dist, use_container_width=True)
        
        # Show price statistics
        st.subheader("📈 Price Statistics")
        stats_df = pd.DataFrame({
            'Metric': ['Average', 'Median', 'Min', 'Max'],
            'Value': [
                f"${data['price'].mean():.2f}",
                f"${data['price'].median():.2f}",
                f"${data['price'].min():.2f}",
                f"${data['price'].max():.2f}"
                # f"${data['price'].std():.2f}"
            ]
        })
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Total Products:** {len(data):,} | **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

else:
    st.error("❌ No data available. Please run the scraper first to generate data.")
    st.markdown("""
    ### How to generate data:
    1. Run the scraper: `python main.py --category your-category`
    2. Wait for the scraping to complete
    3. Refresh this dashboard
    """)