import streamlit as st 
import pandas as pd
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# 1. Page Title & Layout 
st.set_page_config(page_title="Bike Sales Dashboard", layout="wide")
st.title("🚲 Bike Sales Analysis Dashboard")

# 2. Data Load 
@st.cache_data
def load_data():
    path = 'bike sales.csv.zip'
    data = pd.read_csv(path)
    data['Date'] = pd.to_datetime(data['Date'])
    return data


try:
    df = load_data()

    # 3. Sidebar Filters 
    st.sidebar.header("PICE Project Assignment")
    st.sidebar.subheader("Student Name: Phyu Sin Kyi, Batch(2026)")
    st.sidebar.write("Parami University")
    st.sidebar.markdown("---") 

    # Country Select Filter
    country_names = ['All'] + sorted(df['Country'].unique().tolist())
    selected_country_name = st.sidebar.selectbox("Select Country", options=country_names)

    # State Select Filter
    if selected_country_name != 'All':
        state_options = sorted(df[df['Country'] == selected_country_name]['State'].unique().tolist())
    else:
        state_options = sorted(df['State'].unique().tolist())
        
    state_names = ['All'] + state_options
    selected_state_name = st.sidebar.selectbox("Select State", options=state_names)

    # Category Select Filter
    category_names = ['All'] + sorted(df['Product_Category'].unique().tolist())
    selected_category_name = st.sidebar.selectbox("Select Category", options=category_names)

    # 4. Filter data
    filtered_df = df.copy()

    if selected_country_name != 'All':
        filtered_df = filtered_df[filtered_df['Country'] == selected_country_name]
        
    if selected_state_name != 'All':
        filtered_df = filtered_df[filtered_df['State'] == selected_state_name]
        
    if selected_category_name != 'All':
        filtered_df = filtered_df[filtered_df['Product_Category'] == selected_category_name]

    
    st.write(f"Total rows found: {filtered_df.shape[0]}")

    
    total_profit = filtered_df['Profit'].sum()
    total_cost = filtered_df['Cost'].sum()
    total_revenue = filtered_df['Revenue'].sum()

    avg_unit_price = filtered_df['Unit_Price'].mean()
    avg_unit_cost = filtered_df['Unit_Cost'].mean()
    total_quantity = filtered_df['Order_Quantity'].sum()

    # For the first three columns
    row1_col1, row1_col2, row1_col3 = st.columns(3)
    row1_col1.metric("Total Profit", f"${total_profit:,.2f}")
    row1_col2.metric("Total Cost", f"${total_cost:,.2f}")
    row1_col3.metric("Total Revenue", f"${total_revenue:,.2f}")

    st.markdown(" ") 

    # For the second three columns
    row2_col1, row2_col2, row2_col3 = st.columns(3)
    row2_col1.metric("Avg Unit Price", f"${avg_unit_price:,.2f}")
    row2_col2.metric("Avg Unit Cost", f"${avg_unit_cost:,.2f}")
    row2_col3.metric("Total Order Quantity", f"{total_quantity:,}")

    st.markdown("---")

    
    st.subheader("📊 Financial Trends & Demographics")

    # Monthly Revenue & Profit 
    monthly_trend = filtered_df.groupby(filtered_df['Date'].dt.to_period('M'))[['Revenue', 'Profit']].sum().reset_index()
    monthly_trend['Date'] = monthly_trend['Date'].dt.to_timestamp()

    fig1, ax1 = plt.subplots(figsize=(10, 3.5))
    sns.lineplot(data=monthly_trend, x='Date', y='Revenue', ax=ax1, marker='o', label='Revenue', color='#000080', linewidth=2)
    sns.lineplot(data=monthly_trend, x='Date', y='Profit', ax=ax1, marker='s', label='Profit', color='#10B981', linewidth=2)

    ax1.xaxis.set_major_locator(mdates.YearLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

    ax1.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    ax1.set_title("Monthly Revenue vs Profit Trend", fontsize=11, fontweight='bold')
    ax1.set_ylabel("Amount ($)")
    ax1.grid(True, linestyle='--', alpha=0.3)
    st.pyplot(fig1)
    plt.close()

    st.markdown("<br>", unsafe_allow_html=True) 

    # Product category and order quantity
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.write("**Top Selling Product Categories**")
        prod_sales = filtered_df.groupby('Product_Category')['Order_Quantity'].sum().reset_index().sort_values(by='Order_Quantity', ascending=True)
        
        category_colors = []
        for cat in prod_sales['Product_Category']:
            if str(cat).lower() == 'bikes':
                category_colors.append('#000080')
            elif str(cat).lower() == 'accessories':
                category_colors.append('#ADD8E6')
            elif str(cat).lower() == 'clothing':
                category_colors.append("#5A5A94")
            else:
                category_colors.append("#44525F")
                
        fig2, ax2 = plt.subplots(figsize=(5, 3.5))
        sns.barplot(data=prod_sales, x='Order_Quantity', y='Product_Category', ax=ax2, palette=category_colors)
        
        ax2.get_xaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
        ax2.set_xlabel("Total Quantity Sold")
        ax2.set_ylabel("")
        st.pyplot(fig2)
        plt.close()

    with chart_col2:
        st.write("**Sales Distribution by Gender**")
        gender_sales = filtered_df.groupby('Customer_Gender')['Revenue'].sum()
        
        fig3, ax3 = plt.subplots(figsize=(5, 3.5))
        my_pie_colors = sns.color_palette(['#FFB6C1', '#ADD8E6'])
        
        gender_sales.plot(
            kind='pie', 
            autopct='%1.1f%%', 
            ax=ax3, 
            colors=my_pie_colors, 
            startangle=90
        )
        ax3.set_ylabel('')
        st.pyplot(fig3)
        plt.close()

    # Age group
    st.markdown("<br>", unsafe_allow_html=True) 
    st.write("**Sales Count by Customer Age Group**")

    if 'Age_Group' in filtered_df.columns:
        age_sales = filtered_df['Age_Group'].value_counts().reset_index()
    else:
        bins = [0, 25, 34, 55, 120]
        labels = ['Youth (<25)', 'Young Adults (25-34)', 'Adults (35-55)', 'Seniors (>55)']
        filtered_df['Age_Group_Calc'] = pd.cut(filtered_df['Customer_Age'], bins=bins, labels=labels)
        age_sales = filtered_df['Age_Group_Calc'].value_counts().reset_index()
        
    age_sales.columns = ['Age_Group', 'Count']

    fig4, ax4 = plt.subplots(figsize=(10, 3.5)) 
    ax4.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    sns.barplot(data=age_sales, x='Age_Group', y='Count', ax=ax4, color='#8FAADC')

    ax4.set_title("Customer Distribution by Age Group", fontsize=11, fontweight='bold')
    ax4.set_xlabel("Age Group")
    ax4.set_ylabel("Number of Orders")
    ax4.grid(True, linestyle='--', alpha=0.3)
    st.pyplot(fig4)
    plt.close()

    # Unit Cost vs Unit Price 
    st.markdown("<br>", unsafe_allow_html=True)
    st.write("**Average Unit Cost vs Unit Price by Product Category**")

    cost_price_df = filtered_df.groupby('Product_Category')[['Unit_Cost', 'Unit_Price']].mean().reset_index()
    cost_price_melted = cost_price_df.melt(id_vars='Product_Category', value_vars=['Unit_Cost', 'Unit_Price'],
                                           var_name='Type', value_name='Amount')

    fig5, ax5 = plt.subplots(figsize=(10, 4))
    sns.barplot(data=cost_price_melted, x='Product_Category', y='Amount', hue='Type', ax=ax5, palette=['#ADD8E6', '#000080'])

    ax5.get_yaxis().set_major_formatter(plt.FuncFormatter(lambda x, loc: "${:,}".format(int(x))))
    ax5.set_title("Comparison of Average Unit Cost and Unit Price", fontsize=11, fontweight='bold')
    ax5.set_xlabel("Product Category")
    ax5.set_ylabel("Amount ($)")
    ax5.grid(True, linestyle='--', alpha=0.3)
    ax5.legend(title="")
    st.pyplot(fig5)
    plt.close()
    st.markdown("---")

    
    with st.expander("📋 View Filtered Sales Data"):
        st.dataframe(filtered_df, use_container_width=True)

except Exception as e:
    st.error(f"Error, Please check the code- {e}")

st.markdown(" ")
st.text("This is the conclusion of Bike Sales EDA process.")
