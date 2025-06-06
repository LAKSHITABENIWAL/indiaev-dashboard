import streamlit as st
import pandas as pd
import json
import plotly.express as px
import plotly.graph_objects as go
import warnings
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from statsmodels.tsa.arima.model import ARIMA
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
warnings.filterwarnings("ignore")
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=DeprecationWarning)
st.set_option("client.showErrorDetails", False)
st.set_page_config(page_title="India EV Market Dashboard", layout="wide")

# Load data with caching
@st.cache_data
def load_data():
    ev_maker = pd.read_csv("ev_maker.csv")
    ev_sales = pd.read_csv("ev_sales.csv")
    operational_pcs = pd.read_csv("OperationalPC.csv")
    vehicle_class = pd.read_csv("vehicleclass.csv")

    for year in range(2015, 2025):
        ev_sales[str(year)] = pd.to_numeric(ev_sales[str(year)], errors='coerce').fillna(0).astype(int)

    vehicle_class['Total Registration'] = vehicle_class['Total Registration'].astype(str).str.replace(',', '').astype(int)
    operational_pcs['State'] = operational_pcs['State'].str.upper()
    return ev_maker, ev_sales, operational_pcs, vehicle_class

@st.cache_data
def load_geojson():
    with open("india_state.geojson", "r") as f:
        india_geojson = json.load(f)
    for feature in india_geojson['features']:
        if 'NAME_1' in feature['properties']:
            feature['properties']['NAME_1'] = feature['properties']['NAME_1'].upper()
    return india_geojson

ev_maker, ev_sales, operational_pcs, vehicle_class = load_data()
india_geojson = load_geojson()

# === Sidebar UI ===
# CSS for button-style sidebar navigation + light mode base
sidebar_css = """
<style>
/* Main sidebar container */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a3a8f, #0d6e6e) !important;
    padding: 1.5rem 1rem !important;
    border-radius: 0 20px 20px 0 !important;
    box-shadow: 5px 0 15px rgba(0,0,0,0.1) !important;
}

/* Sidebar title */
.sidebar-title {
    font-size: 2rem !important;
    font-weight: 800 !important;
    background: linear-gradient(90deg, #FF9933, #FFFFFF, #138808) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    text-align: center !important;
    margin-bottom: 2rem !important;
    padding-bottom: 1rem !important;
    border-bottom: 2px solid rgba(255,255,255,0.1) !important;
    letter-spacing: 1px !important;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
}

/* Navigation buttons */
.sidebar-button {
    display: block !important;
    width: 100% !important;
    padding: 0.8rem 1.2rem !important;
    margin: 0.5rem 0 !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: white !important;
    background-color: rgba(255,255,255,0.1) !important;
    border: none !important;
    border-radius: 10px !important;
    cursor: pointer !important;
    text-align: left !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1) !important;
    position: relative !important;
    overflow: hidden !important;
}

.sidebar-button:hover {
    background-color: rgba(255,255,255,0.2) !important;
    transform: translateX(5px) !important;
    box-shadow: 0 4px 8px rgba(0,0,0,0.15) !important;
}

.sidebar-button.active {
    background: linear-gradient(90deg, #FF9933, #138808) !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(255,153,51,0.5) !important;
    font-weight: 700 !important;
    transform: translateX(5px) !important;
}

.sidebar-button.active:before {
    content: '' !important;
    position: absolute !important;
    left: 0 !important;
    top: 0 !important;
    height: 100% !important;
    width: 4px !important;
    background: white !important;
    border-radius: 10px 0 0 10px !important;
}

/* Dark mode toggle */
[data-testid="stSidebarUserContent"] {
    margin-top: 2rem !important;
    padding-top: 1.5rem !important;
    border-top: 2px solid rgba(255,255,255,0.1) !important;
}

[data-testid="stWidgetLabel"] {
    color: white !important;
    font-weight: 500 !important;
}

/* Icon styling */
.stCheckbox .st-cf {
    color: #FF9933 !important;
}

/* Responsive adjustments */
@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        padding: 1rem 0.5rem !important;
    }
    .sidebar-button {
        padding: 0.7rem 1rem !important;
        font-size: 0.9rem !important;
    }
    .sidebar-title {
        font-size: 1.5rem !important;
    }
}
</style>
"""

dark_mode_sidebar_css = """
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #121212, #1a1a2e) !important;
}

.sidebar-button {
    background-color: rgba(255,255,255,0.05) !important;
    color: #e0e0e0 !important;
}

.sidebar-button:hover {
    background-color: rgba(255,255,255,0.1) !important;
}

.sidebar-button.active {
    background: linear-gradient(90deg, #FF9933, #138808) !important;
    color: white !important;
}

[data-testid="stWidgetLabel"] {
    color: #e0e0e0 !important;
}
</style>
"""

dark_mode_css = """
<style>
/* Main content area */
.main .block-container {
    background-color: #1a1a2e !important;
    color: #e0e0e0 !important;
}

/* Text elements */
.main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {
    color: #ffffff !important;
}

.main p, .main span, .main div {
    color: #e0e0e0 !important;
}

/* Streamlit specific elements */
.stButton button {
    background-color: #2a2a3a !important;
    color: #ffffff !important;
    border: 1px solid #3a3a4a !important;
}

.stButton button:hover {
    background-color: #3a3a4a !important;
}

/* Select boxes and inputs */
.stSelectbox, .stTextInput, .stNumberInput {
    background-color: #2a2a3a !important;
    color: #ffffff !important;
}

/* Tables */
.stDataFrame {
    background-color: #2a2a3a !important;
    color: #ffffff !important;
}

/* Charts and plots */
.plotly-graph-div {
    background-color: #2a2a3a !important;
}

/* Metrics */
.stMetric {
    background-color: #2a2a3a !important;
    color: #ffffff !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background-color: #2a2a3a !important;
}

.stTabs [data-baseweb="tab"] {
    color: #ffffff !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background-color: #2a2a3a !important;
    color: #ffffff !important;
}

/* Dividers */
hr {
    border-color: #3a3a4a !important;
}

/* Links */
a {
    color: #4a9eff !important;
}

a:hover {
    color: #6bb5ff !important;
}

/* Code blocks */
.stCodeBlock {
    background-color: #2a2a3a !important;
}

/* Alerts and messages */
.stAlert {
    background-color: #2a2a3a !important;
    color: #ffffff !important;
}

/* Tooltips */
.tooltip {
    background-color: #2a2a3a !important;
    color: #ffffff !important;
}
</style>
"""

# Inject CSS
st.markdown(sidebar_css, unsafe_allow_html=True)

# Sidebar title
st.sidebar.markdown('<div class="sidebar-title">India EV Market</div>', unsafe_allow_html=True)

# Dark mode toggle with custom styling
dark_mode = st.sidebar.checkbox("🌙 Dark Mode", value=False, 
                              help="Toggle between light and dark mode")

if dark_mode:
    st.markdown(dark_mode_sidebar_css, unsafe_allow_html=True)
    st.markdown(dark_mode_css, unsafe_allow_html=True)

# Define pages
pages = ["About", "Dashboard", "Visualizations", "Forecast", "Summary", "EV Policy Impact"]

# Get current page from URL query params or default
query_params = st.experimental_get_query_params()
current_page = query_params.get("page", ["Dashboard"])[0]
if current_page not in pages:
    current_page = "Dashboard"

# Sidebar buttons with enhanced styling
for page in pages:
    active = "active" if page == current_page else ""
    # Use st.markdown to create clickable button-like divs
    st.sidebar.markdown(
        f'''
        <form action="" method="get" style="margin-bottom:0;">
            <input type="hidden" name="page" value="{page}">
            <button type="submit" class="sidebar-button {active}">
                {page}
            </button>
        </form>
        ''',
        unsafe_allow_html=True,
    )

def format_revenue(num):
    if num >= 1_000_000_000:
        return f"${num / 1_000_000_000:.2f}B"
    elif num >= 1_000_000:
        return f"${num / 1_000_000:.2f}M"
    else:
        return f"${num:,}"

if current_page == "Dashboard":
    # --- Dashboard page content ---
    st.markdown(
        """
        <h1 style="font-weight:900; text-align:center; 
        background: linear-gradient(90deg, #FF9933, #FFFFFF, #138808); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        user-select:none;">India Electric Vehicle Market</h1>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("### Overview & Key Metrics")

    vehicle_categories = ev_sales['Cat'].unique()
    selected_cat = st.selectbox("Select Vehicle Category", vehicle_categories)

    year_min, year_max = 2001, 2024
    selected_year_range = st.slider("Select Year Range", year_min, year_max, (2015, 2023))

    all_years = [str(y) for y in range(2001, 2025)]
    sales_years = [str(y) for y in range(2015, 2025)]

    filtered_sales = ev_sales[ev_sales['Cat'] == selected_cat]
    yearly_sales = pd.Series(0, index=all_years)
    for y in sales_years:
        if y in filtered_sales.columns:
            yearly_sales[y] = filtered_sales[y].sum()

    year_range_years = [str(y) for y in range(selected_year_range[0], selected_year_range[1] + 1)]
    selected_yearly_sales = yearly_sales.loc[year_range_years]

    total_sales = selected_yearly_sales.sum()
    avg_prices = {"3W": 1000, "2W": 750, "4W": 1500, "Heavy": 5000}
    prefix = selected_cat.split()[0]
    avg_price = avg_prices.get(prefix, 1_000_000)
    total_revenue = total_sales * avg_price
    formatted_revenue = format_revenue(total_revenue)
    yoy_growth = selected_yearly_sales.pct_change().fillna(0) * 100
    forecast_year = str(int(selected_yearly_sales.index[-1]) + 1)
    forecast_sales = max(0, selected_yearly_sales.iloc[-1] + (selected_yearly_sales.iloc[-1] - selected_yearly_sales.iloc[-2]) if len(selected_yearly_sales) > 1 else 0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Sales", f"{int(total_sales):,}")
    col2.metric("Estimated Revenue", formatted_revenue)
    col3.metric("Annual Growth Rate (YoY %)", f"{yoy_growth.iloc[-1]:.2f}%")
    col4.metric(f"Forecast Sales ({forecast_year})", f"{int(forecast_sales):,}")

    st.markdown("---")

    st.subheader("EV Sales Over Years")
    fig_sales = px.line(
        x=selected_yearly_sales.index,
        y=selected_yearly_sales.values,
        labels={"x": "Year", "y": "Units Sold"},
        title=f"EV Sales Over Years - {selected_cat}",
        markers=True,
        template="plotly_white"
    )
    st.plotly_chart(fig_sales, use_container_width=True)
    st.markdown("---")

    st.subheader("Market Analysis & Geographical Distribution")
    col_left, col_right = st.columns([1.5, 2.5])

    with col_left:
        st.markdown("#### Manufacturer Market Share")
        # Set a minimum year for the data (2015)
        min_year = 2015
        # Adjust the selected years to ensure they start from 2015
        adjusted_years = [str(year) for year in year_range_years if int(year) >= min_year]
        # If no years are above 2015, default to 2015
        if not adjusted_years:
            adjusted_years = [str(min_year)]
        # Calculating sales for selected years
        maker_sales = filtered_sales.groupby('Maker')[adjusted_years].sum()
        maker_selected_sales = maker_sales.sum(axis=1)
        maker_share = maker_selected_sales / maker_selected_sales.sum()
        # Categorizing manufacturers
        large_makers = maker_share[maker_share >= 0.05]
        others_share = maker_share[maker_share < 0.05].sum()
        # Creating the pie chart data
        maker_pie = pd.concat([large_makers, pd.Series({"Others": others_share})])
        # Plotting the pie chart
        fig_pie = px.pie(
            values=maker_pie.values,
            names=maker_pie.index,
            hole=0.4,
            template="plotly_white"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        st.markdown("#### Operational Public Charging Stations")
        
        # Create a row with two columns: one for dropdown and one for the OK button
        col1, col2 = st.columns([4, 1])
        
        with col1:
            state_filter = st.multiselect(
                "Select States to Highlight", 
                operational_pcs['State'].unique(),
                default=[]
            )
        
        with col2:
            show_map = st.button("OK", key="show_map")
    
        if show_map:
            filtered_pcs = operational_pcs[operational_pcs['State'].isin(state_filter)] if state_filter else operational_pcs
            fig_map = px.choropleth(
                filtered_pcs,
                geojson=india_geojson,
                locations='State',
                color='No. of Operational PCS',
                featureidkey='properties.NAME_1',
                hover_name='State',
                color_continuous_scale="Viridis",
                labels={'No. of Operational PCS': 'Operational PCS'},
                template="plotly_dark"
            )
            fig_map.update_geos(fitbounds="locations", visible=False)
            st.plotly_chart(fig_map, use_container_width=True) 
    st.markdown("---")
                                                                  
elif current_page == "Visualizations":
    st.title("EV Market and Infrastructure Visualizations")
    st.markdown("Explore various aspects of India's Electric Vehicle market through interactive visualizations")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "India EV Market Analysis", 
        "Manufacturer Analysis", 
        "Geographical Distribution", 
        "Vehicle Class Insights",
        "Sales Trends",
        "State Growth"  # New tab
    ])
    
    with tab5:
        st.header("Sales Trend Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Total EV Sales Growth")
            all_sales = ev_sales[[str(y) for y in range(2015, 2025)]].sum()
            fig1 = px.area(
                x=all_sales.index,
                y=all_sales.values,
                labels={"x": "Year", "y": "Total Units Sold"},
                title="Total EV Sales Growth (2015-2024)",
                template="plotly_white"
            )
            fig1.update_traces(line=dict(width=3), fill='tozeroy')
            st.plotly_chart(fig1, use_container_width=True)
            
        with col2:
            st.subheader("Category-wise Sales Comparison")
            cat_sales = ev_sales.groupby('Cat')[[str(y) for y in range(2015, 2025)]].sum().T
            fig2 = px.line(
                cat_sales,
                title="EV Sales by Vehicle Category (2015-2024)",
                markers=True,
                template="plotly_white"
            )
            fig2.update_layout(yaxis_title="Units Sold", xaxis_title="Year")
            st.plotly_chart(fig2, use_container_width=True)
        
        st.subheader("Top 10 EV Models by Sales")
        if 'Model' in ev_sales.columns:
            top_models = ev_sales.groupby('Model')[[str(y) for y in range(2020,2025)]].sum().sum(axis=1).nlargest(10)
        else:
            top_models = ev_sales.groupby('Maker')[[str(y) for y in range(2020,2025)]].sum().sum(axis=1).nlargest(10)
        fig3 = px.bar(
            top_models,
            orientation='h',
            title="Top 10 EV Models/Manufacturers by Sales (2020-2024)",
            labels={'value': 'Total Units Sold', 'index': 'Model' if 'Model' in ev_sales.columns else 'Manufacturer'},
            color=top_models.values,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with tab2:
        st.header("Manufacturer Analysis")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Top EV Manufacturers")
            top_makers = ev_sales.groupby('Maker')[[str(y) for y in range(2020, 2025)]].sum().sum(axis=1).nlargest(10)
            fig4 = px.bar(
                top_makers,
                orientation='h',
                title="Top 10 EV Manufacturers (2020-2024)",
                labels={'value': 'Total Units Sold', 'index': 'Manufacturer'},
                color=top_makers.values,
                color_continuous_scale='Viridis',
                template="plotly_white"
            )
            st.plotly_chart(fig4, use_container_width=True)
        with col2:
            st.subheader("Manufacturer Growth Trajectory")
            available_makers = sorted(list(set(ev_maker['EV Maker']).union(set(ev_sales['Maker']))))
            selected_makers = st.multiselect(
                "Select Manufacturers to Compare",
                available_makers,
                default=[]
            )
            
            if selected_makers:
                valid_makers = [maker for maker in selected_makers if maker in ev_sales['Maker'].values]
                
                if valid_makers:
                    maker_sales = ev_sales[ev_sales['Maker'].isin(valid_makers)]
                    maker_sales = maker_sales.groupby('Maker')[[str(y) for y in range(2015, 2025)]].sum().T
                    
                    fig5 = px.line(
                        maker_sales,
                        title="Sales Growth of Selected Manufacturers",
                        markers=True,
                        template="plotly_white"
                    )
                    fig5.update_layout(
                        yaxis_title="Units Sold", 
                        xaxis_title="Year",
                        legend_title="Manufacturer"
                    )
                    st.plotly_chart(fig5, use_container_width=True)
                else:
                    st.warning("Selected manufacturers not found in sales data")
            else:
                st.info("Please select manufacturers to compare")
        
        st.subheader("Manufacturer Geographical Distribution")
        maker_loc = ev_maker.groupby(['State', 'Place']).size().reset_index(name='Count')
        fig6 = px.treemap(
            maker_loc,
            path=['State', 'Place'],
            values='Count',
            title="EV Manufacturer Locations Across India",
            color='Count',
            color_continuous_scale='RdBu',
            template="plotly_white"
        )
        st.plotly_chart(fig6, use_container_width=True)
    
    with tab3:
        st.header("Geographical Distribution")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Public Charging Stations Distribution")
            fig7 = px.choropleth(
                operational_pcs,
                geojson=india_geojson,
                locations='State',
                color='No. of Operational PCS',
                featureidkey='properties.NAME_1',
                hover_name='State',
                color_continuous_scale="Viridis",
                title="Operational Public Charging Stations by State",
                template="plotly_white"
            )
            fig7.update_geos(fitbounds="locations", visible=False)
            st.plotly_chart(fig7, use_container_width=True)
            
        with col2:
            st.subheader("Top States for EV Infrastructure")
            top_states = operational_pcs.sort_values('No. of Operational PCS', ascending=False).head(10)
            fig8 = px.bar(
                top_states,
                x='State',
                y='No. of Operational PCS',
                color='No. of Operational PCS',
                title="Top 10 States by Charging Stations Count",
                template="plotly_white"
            )
            st.plotly_chart(fig8, use_container_width=True)
        
        st.subheader("EV Manufacturer Presence by State")
        state_makers = ev_maker.groupby('State').size().reset_index(name='Count')
        state_makers['State'] = state_makers['State'].str.upper()
        geojson_states = [f['properties']['NAME_1'].upper() for f in india_geojson['features']]
        state_makers = state_makers[state_makers['State'].isin(geojson_states)]
        
        if not state_makers.empty:
            fig9 = px.choropleth(
                state_makers,
                geojson=india_geojson,
                locations='State',
                color='Count',
                featureidkey='properties.NAME_1',
                hover_name='State',
                color_continuous_scale="Blues",
                title="Number of EV Manufacturers by State",
                template="plotly_white",
                range_color=[0, state_makers['Count'].max()]
            )
            fig9.update_geos(fitbounds="locations", visible=False)
            st.plotly_chart(fig9, use_container_width=True)
        else:
            st.warning("No matching state data found for the geojson")
    
    with tab4:
        st.header("Vehicle Class Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Vehicle Class Registration")
            if vehicle_class['Total Registration'].dtype == object:
                vehicle_class['Total Registration'] = vehicle_class['Total Registration'].str.replace(',', '').astype(int)
            else:
                vehicle_class['Total Registration'] = vehicle_class['Total Registration'].astype(int)
                
            fig10 = px.bar(
                vehicle_class.sort_values('Total Registration', ascending=False),
                x='Vehicle Class',
                y='Total Registration',
                color='Total Registration',
                title="Vehicle Registration by Class",
                template="plotly_white"
            )
            fig10.update_xaxes(tickangle=45)
            st.plotly_chart(fig10, use_container_width=True)
            
        with col2:
            st.subheader("EV Market Share by Category")
            total_ev_by_cat = ev_sales.groupby('Cat')[[str(y) for y in range(2020, 2025)]].sum().sum(axis=1)
            fig11 = px.pie(
                total_ev_by_cat,
                values=total_ev_by_cat.values,
                names=total_ev_by_cat.index,
                title="EV Market Share by Vehicle Category (2020-2024)",
                hole=0.4,
                template="plotly_white"
            )
            st.plotly_chart(fig11, use_container_width=True)
        
        st.subheader("Category-wise Yearly Growth")
        cat_growth = ev_sales.groupby('Cat')[[str(y) for y in range(2015, 2025)]].sum().T.pct_change().fillna(0) * 100
        fig12 = px.line(
            cat_growth,
            title="Yearly Growth Rate by Vehicle Category (%)",
            markers=True,
            template="plotly_white"
        )
        fig12.update_layout(yaxis_title="Growth Rate (%)", xaxis_title="Year")
        st.plotly_chart(fig12, use_container_width=True)
    with tab1:
        st.header("India EV Market Analysis")
    
        st.subheader("1. Market Size Over the Years")
        market_size = pd.Series([3.21, 9.3, 26.96, 78.2, 113.99], index=[2022, 2024, 2026, 2028, 2030])
        fig1 = px.line(market_size, title="India EV Market Size Forecast (2022-2030)", labels={'index': 'Year', 'value': 'Market Size (Billion USD)'})
        st.plotly_chart(fig1, use_container_width=True)
    
        st.subheader("2. EV Sales Over Years")
        sales_years = pd.Series([0.12, 0.33, 0.5, 0.98, 1.53, 1.02, 1.0], index=[2018, 2019, 2020, 2021, 2022, 2023, 2024])
        fig2 = px.bar(sales_years, title="Total EV Sales Growth (2018-2024)", labels={'index': 'Year', 'value': 'Sales (Millions)'})
        st.plotly_chart(fig2, use_container_width=True)
    
        st.subheader("3. Key Market Shares by State (2023)")
        state_data = pd.DataFrame({
            'State': ['Maharastra', 'Karnataka', 'Tamil Nadu', 'Gujarat', 'Rajasthan', 'Kerala', 'Delhi'],
            'Total Sales': [194343, 152680, 90288, 88615, 93767, 75800, 73676]
        })
        fig3 = px.bar(state_data, x='State', y='Total Sales', title="EV Sales by State (2023)")
        st.plotly_chart(fig3, use_container_width=True)
    
        st.subheader("4. Key Players in EV Market")
        player_data = pd.DataFrame({
            'Player': ['Ola', 'Others', 'Okinawa', 'TVS', 'Ather', 'Hero'],
            'Market Share (%)': [25.9, 22.1, 18.7, 14, 10.4, 8.9]
        })
        fig4 = px.pie(player_data, names='Player', values='Market Share (%)', title="EV Market Share by Key Players")
        st.plotly_chart(fig4, use_container_width=True)
    
        st.subheader("5. Growth Projections")
        forecast_data = pd.Series([3.95, 13.6, 27.7, 64.1, 140.6], index=[2025, 2028, 2032, 2035, 2038])
        fig5 = px.area(forecast_data, title="EV Sales Forecast (2025-2038)", labels={'index': 'Year', 'value': 'Sales (Millions)'})
        st.plotly_chart(fig5, use_container_width=True)
    
        st.subheader("6. Top States by EV Infrastructure (2024)")
        infra_data = pd.DataFrame({
            'State': ['Maharastra', 'Delhi', 'Karnataka', 'Kerala', 'Tamil Nadu', 'Uttar Pradesh'],
            'Charging Stations': [3079, 1886, 1051, 852, 643, 582]
        })
        fig6 = px.bar(infra_data, x='State', y='Charging Stations', title="EV Charging Infrastructure by State")
        st.plotly_chart(fig6, use_container_width=True)
    
        st.subheader("7. EV Sales by Category")
        category_data = pd.DataFrame({
            'Category': ['2-Wheeler', '3-Wheeler', '4-Wheeler'],
            'Sales (Millions)': [0.98, 0.5, 0.33]
        })
        fig7 = px.pie(category_data, names='Category', values='Sales (Millions)', title="EV Sales Distribution by Category (2023)")
        st.plotly_chart(fig7, use_container_width=True)
    
        st.subheader("8. SWOT Analysis")
        swot_data = pd.DataFrame({
            'Aspect': ['Strengths', 'Weaknesses', 'Opportunities', 'Threats'],
            'Details': ['Govt Support, Growing Demand', 'High Cost, Limited Range', 'Market Expansion, Innovation', 'Competition, Consumer Acceptance']
        })
        st.table(swot_data)

        st.subheader("9. India EV Policy Timeline")
        data = {
    'Year': [2001, 2010, 2011, 2012, 2013, 2015, 2018, 2019, 2020, 2024],
    'Event': [
        'First alternative fuels policy introduced',
        'MNRE launched incentives for electric vehicles',
        'NMEM established',
        'NEMMP 2020 approved with ₹14,000 Cr investment',
        'National Electric Mobility Mission Plan launched',
        'FAME-I introduced',
        'FAME-I extended, EV charging guidelines released',
        'FAME-II launched with ₹10,000 Cr budget',
        'Charging infrastructure expansion',
        'Comprehensive EV policy with incentives'
    ]
        }
        df = pd.DataFrame(data)
        df['Start'] = pd.to_datetime(df['Year'].astype(str) + '-01-01')
        df['End'] = df['Start'] + pd.DateOffset(months=6)
        fig = px.timeline(
    df,
    x_start='Start',
    x_end='End',
    y='Event',
    title='India EV Policy Milestones (2001-2024)',
    template='plotly_white'
)
        fig.update_yaxes(categoryorder="total ascending")
        fig.update_layout(height=600)
        st.plotly_chart(fig, use_container_width=True)


elif current_page == "Forecast":
    st.title("EV Market Forecast")
    st.markdown("Compare forecasting models and predict future EV adoption trends")
    
    pred_tab1, pred_tab2, pred_tab3,pred_tab4 = st.tabs([
        "Model Comparison", 
        "Advanced Time Series", 
        "Error Analysis",
        "Long-term Forecast"
    ])
    
    with pred_tab1:
        st.header("Model Comparison")
        st.markdown("Compare different forecasting models to identify the best approach")
        
        selected_cat = st.selectbox(
            "Select Vehicle Category", 
            ev_sales['Cat'].unique(),
            key="model_cat_select"
        )
        
        cat_data = ev_sales[ev_sales['Cat'] == selected_cat]
        yearly_sales = cat_data[[str(y) for y in range(2015, 2025)]].sum()
        years = pd.to_numeric(yearly_sales.index).to_numpy()
        sales = yearly_sales.values
        
        train_years, test_years = years[:-2].reshape(-1, 1), years[-2:].reshape(-1, 1)
        train_sales, test_sales = sales[:-2], sales[-2:]
        
        models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "Neural Network": MLPRegressor(hidden_layer_sizes=(50,), max_iter=1000, random_state=42)
        }
        
        results = []
        forecasts = {}
        
        for name, model in models.items():
            model.fit(train_years, train_sales)
            pred = model.predict(test_years)
            
            mae = mean_absolute_error(test_sales, pred)
            mse = mean_squared_error(test_sales, pred)
            rmse = np.sqrt(mse)  # Calculate RMSE from MSE
            r2 = r2_score(test_sales, pred)
            
            results.append({
                "Model": name,
                "MAE": mae,
                "RMSE": rmse,
                "R²": r2
            })
            
            forecasts[name] = model.predict(years.reshape(-1, 1))
        
        st.subheader("Model Performance Comparison")
        metrics_df = pd.DataFrame(results).sort_values("RMSE")
        st.dataframe(metrics_df.style.format({
            "MAE": "{:.1f}",
            "RMSE": "{:.1f}",
            "R²": "{:.3f}"
        }).highlight_min(subset=["MAE", "RMSE"], color='lightgreen')
                     .highlight_max(subset=["R²"], color='lightgreen'))
        
        st.subheader("Model Forecast vs Actual")
        fig_compare = go.Figure()
        
        fig_compare.add_trace(go.Scatter(
            x=years,
            y=sales,
            name='Actual',
            mode='lines+markers',
            line=dict(color='black', width=3)
        ))
        
        colors = ['#FF9933', '#138808', '#3366CC']
        for i, (name, pred) in enumerate(forecasts.items()):
            fig_compare.add_trace(go.Scatter(
                x=years,
                y=pred,
                name=name,
                mode='lines',
                line=dict(color=colors[i], width=2, dash='dot')
            ))
        
        fig_compare.update_layout(
            title=f"{selected_cat} - Model Comparison",
            xaxis_title="Year",
            yaxis_title="Units Sold",
            template="plotly_white"
        )
        st.plotly_chart(fig_compare, use_container_width=True)
        
        best_model_name = metrics_df.iloc[0]["Model"]
        best_model = models[best_model_name]
        st.success(f"Best model for {selected_cat}: **{best_model_name}** (lowest RMSE)")
    
    with pred_tab2:
        st.header("Advanced Time Series Models")
        st.markdown("Compare sophisticated time series models for improved forecasting accuracy")
        
        # Add ARIMA and Prophet models
        import warnings
        import pandas as pd
        import numpy as np
        from statsmodels.tsa.arima.model import ARIMA
        from prophet import Prophet
        
        warnings.filterwarnings("ignore")  # Suppress ARIMA and Prophet warnings
        
        selected_cat_ts = st.selectbox(
            "Select Vehicle Category", 
            ev_sales['Cat'].unique(),
            key="ts_cat_select"
        )
        
        cat_data_ts = ev_sales[ev_sales['Cat'] == selected_cat_ts]
        yearly_sales_ts = cat_data_ts[[str(y) for y in range(2015, 2025)]].sum()
        years_ts = pd.to_numeric(yearly_sales_ts.index).to_numpy()
        sales_ts = yearly_sales_ts.values
        
        # Prepare data for models
        train_idx = int(len(years_ts) * 0.7)  # 70% training, 30% testing
        train_years_ts, test_years_ts = years_ts[:train_idx], years_ts[train_idx:]
        train_sales_ts, test_sales_ts = sales_ts[:train_idx], sales_ts[train_idx:]
        
        # Results storage
        ts_results = []
        ts_forecasts = {}
        
        # ARIMA Model
        try:
            # Try different ARIMA orders and find the best one
            arima_orders = [(1,1,1), (1,1,0), (0,1,1), (2,1,0), (0,1,2)]
            best_aic = float('inf')
            best_order = None
            
            for order in arima_orders:
                try:
                    model = ARIMA(train_sales_ts, order=order)
                    model_fit = model.fit()
                    if model_fit.aic < best_aic:
                        best_aic = model_fit.aic
                        best_order = order
                except:
                    continue
            
            if best_order:
                # Use best ARIMA model
                st.info(f"Best ARIMA order: {best_order}")
                arima_model = ARIMA(train_sales_ts, order=best_order)
                arima_fit = arima_model.fit()
                
                # Forecast for test period
                arima_forecast = arima_fit.forecast(steps=len(test_years_ts))
                
                # Calculate metrics
                arima_mae = mean_absolute_error(test_sales_ts, arima_forecast)
                arima_mse = mean_squared_error(test_sales_ts, arima_forecast)
                arima_rmse = np.sqrt(arima_mse)
                
                # Store results
                ts_results.append({
                    "Model": "ARIMA",
                    "MAE": arima_mae,
                    "RMSE": arima_rmse,
                    "Parameters": f"Order={best_order}"
                })
                
                # Generate full forecast
                arima_full = ARIMA(sales_ts, order=best_order)
                arima_full_fit = arima_full.fit()
                arima_full_forecast = np.concatenate([sales_ts, arima_full_fit.forecast(steps=5)])
                ts_forecasts["ARIMA"] = arima_full_forecast
            else:
                st.warning("Could not find suitable ARIMA parameters. Skipping ARIMA model.")
        except Exception as e:
            st.warning(f"ARIMA model error: {str(e)}")
        
        # Prophet Model
        try:
            # Prepare data for Prophet
            prophet_data = pd.DataFrame({
                'ds': pd.to_datetime([f"{int(year)}-01-01" for year in years_ts]),
                'y': sales_ts
            })
            prophet_train = prophet_data.iloc[:train_idx]
            prophet_test = prophet_data.iloc[train_idx:]
            
            # Train Prophet model
            prophet_model = Prophet(yearly_seasonality=False, 
                                     seasonality_mode='multiplicative',
                                     interval_width=0.95)
            prophet_model.fit(prophet_train)
            
            # Make forecast on test set
            prophet_future = prophet_model.make_future_dataframe(periods=len(prophet_test), freq='YS')
            prophet_forecast = prophet_model.predict(prophet_future)
            
            # Extract test forecast
            prophet_preds = prophet_forecast['yhat'].values[train_idx:train_idx+len(test_years_ts)]
            
            # Calculate metrics
            prophet_mae = mean_absolute_error(test_sales_ts, prophet_preds)
            prophet_mse = mean_squared_error(test_sales_ts, prophet_preds)
            prophet_rmse = np.sqrt(prophet_mse)
            
            # Store results
            ts_results.append({
                "Model": "Prophet",
                "MAE": prophet_mae,
                "RMSE": prophet_rmse,
                "Parameters": "Default"
            })
            
            # Generate full forecast with 5 years future
            prophet_model_full = Prophet(yearly_seasonality=False, 
                                         seasonality_mode='multiplicative',
                                         interval_width=0.95)
            prophet_model_full.fit(prophet_data)
            prophet_future_full = prophet_model_full.make_future_dataframe(periods=5, freq='YS')
            prophet_forecast_full = prophet_model_full.predict(prophet_future_full)
            
            # Extract forecasts
            ts_forecasts["Prophet"] = prophet_forecast_full['yhat'].values
        except Exception as e:
            st.warning(f"Prophet model error: {str(e)}")
        
        # Include base models
        simple_models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42)
        }
        
        for name, model in simple_models.items():
            model.fit(train_years_ts.reshape(-1, 1), train_sales_ts)
            pred = model.predict(test_years_ts.reshape(-1, 1))
            
            mae = mean_absolute_error(test_sales_ts, pred)
            mse = mean_squared_error(test_sales_ts, pred)
            rmse = np.sqrt(mse)
            
            ts_results.append({
                "Model": name,
                "MAE": mae,
                "RMSE": rmse,
                "Parameters": "Standard"
            })
            
            # Generate full forecast
            full_model = simple_models[name]
            full_model.fit(years_ts.reshape(-1, 1), sales_ts)
            future_years = np.append(years_ts, [years_ts[-1] + i for i in range(1, 6)])
            ts_forecasts[name] = full_model.predict(future_years.reshape(-1, 1))
        
        # Display model comparison
        st.subheader("Advanced Model Comparison")
        ts_metrics_df = pd.DataFrame(ts_results).sort_values("RMSE")
        st.dataframe(ts_metrics_df.style.format({
            "MAE": "{:.1f}",
            "RMSE": "{:.1f}"
        }).highlight_min(subset=["MAE", "RMSE"], color='lightgreen'))
        
        # Display forecast visualization
        st.subheader("Forecast Comparison")
        
        future_years = np.append(years_ts, [years_ts[-1] + i for i in range(1, 6)])
        
        fig_ts = go.Figure()
        
        # Add actual data
        fig_ts.add_trace(go.Scatter(
            x=years_ts,
            y=sales_ts,
            name='Historical Data',
            mode='lines+markers',
            line=dict(color='black', width=3)
        ))
        
        # Add model forecasts
        colors = ['#FF9933', '#138808', '#3366CC', '#DC3912']
        i = 0
        
        for name, forecast in ts_forecasts.items():
            # Make sure forecast length matches future_years
            if len(forecast) > len(future_years):
                forecast = forecast[:len(future_years)]
            elif len(forecast) < len(future_years):
                # Pad with NaN if necessary
                forecast = np.append(forecast, [np.nan] * (len(future_years) - len(forecast)))
            
            fig_ts.add_trace(go.Scatter(
                x=future_years,
                y=forecast,
                name=f'{name} Forecast',
                mode='lines',
                line=dict(color=colors[i % len(colors)], width=2)
            ))
            i += 1
        
        # Add confidence intervals for Prophet
        if "Prophet" in ts_forecasts:
            prophet_lower = prophet_forecast_full['yhat_lower'].values
            prophet_upper = prophet_forecast_full['yhat_upper'].values
            
            fig_ts.add_trace(go.Scatter(
                x=np.concatenate([future_years, future_years[::-1]]),
                y=np.concatenate([prophet_upper, prophet_lower[::-1]]),
                fill='toself',
                fillcolor='rgba(255, 153, 51, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                name='Prophet 95% CI'
            ))
        
        fig_ts.update_layout(
            title=f"{selected_cat_ts} - Advanced Forecast Comparison (5-Year Horizon)",
            xaxis_title="Year",
            yaxis_title="Units Sold",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_ts, use_container_width=True)
        
        # Best model insights
        best_ts_model = ts_metrics_df.iloc[0]["Model"]
        st.success(f"Best time series model for {selected_cat_ts}: **{best_ts_model}** (lowest RMSE)")
        
        st.subheader("Model Insights")
        
        # Model-specific insights
        if best_ts_model == "ARIMA":
            st.markdown("""
            **ARIMA (AutoRegressive Integrated Moving Average)** excels at:
            - Capturing temporal dependencies in the data
            - Handling non-stationary time series through differencing
            - Providing confidence intervals for forecasts
            - Modeling seasonal patterns with seasonal variants (SARIMA)
            
            ARIMA is especially useful when the data shows clear autocorrelation patterns.
            """)
            
            # Display ARIMA components if available
            try:
                arima_decomp = arima_full_fit.plot_diagnostics(figsize=(10, 8))
                st.pyplot(arima_decomp.figure)
            except:
                st.info("ARIMA diagnostics not available")
                
        elif best_ts_model == "Prophet":
            st.markdown("""
            **Prophet** excels at:
            - Handling missing values and outliers robustly
            - Modeling seasonal patterns automatically (yearly, weekly, daily)
            - Capturing trend changes and non-linear growth
            - Incorporating holiday effects and external regressors
            - Providing uncertainty intervals
            
            Prophet is designed by Facebook for business forecasting and works well with time series that have seasonal patterns.
            """)
            
            # Display Prophet components
            try:
                prophet_fig1 = prophet_model_full.plot_components(prophet_forecast_full)
                st.pyplot(prophet_fig1)
            except:
                st.info("Prophet components not available")
                
        else:
            st.markdown(f"""
            **{best_ts_model}** performed best on this data, likely because:
            - It captures the underlying patterns in the EV sales data effectively
            - The complexity of the model matches the complexity of the data
            - It generalizes well to unseen data points
            """)

    with pred_tab3:
        st.header("Error Analysis")
        st.markdown("In-depth analysis of prediction errors to improve model accuracy")
        
        selected_cat_error = st.selectbox(
            "Select Vehicle Category", 
            ev_sales['Cat'].unique(),
            key="error_cat_select"
        )
        
        cat_data_error = ev_sales[ev_sales['Cat'] == selected_cat_error]
        yearly_sales_error = cat_data_error[[str(y) for y in range(2015, 2025)]].sum()
        years_error = pd.to_numeric(yearly_sales_error.index).to_numpy()
        sales_error = yearly_sales_error.values
        
        # Create train/test sets
        train_size = int(len(years_error) * 0.7)
        train_years_e = years_error[:train_size].reshape(-1, 1)
        train_sales_e = sales_error[:train_size]
        test_years_e = years_error[train_size:].reshape(-1, 1)
        test_sales_e = sales_error[train_size:]
        
        # Train models
        error_models = {
            "Linear Regression": LinearRegression(),
            "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
            "Neural Network": MLPRegressor(hidden_layer_sizes=(50,), max_iter=1000, random_state=42)
        }
        
        for name, model in error_models.items():
            model.fit(train_years_e, train_sales_e)
        
        # Create an empty DataFrame to store results
        error_df = pd.DataFrame({
            "Year": years_error[train_size:],
            "Actual": test_sales_e
        })
        
        # Add forecast and errors for each model
        for name, model in error_models.items():
            preds = model.predict(test_years_e)
            error_df[f"{name} Prediction"] = preds
            error_df[f"{name} Error"] = test_sales_e - preds
            error_df[f"{name} % Error"] = 100 * (test_sales_e - preds) / test_sales_e
        
        # Round the values for better display
        for col in error_df.columns:
            if "Error" in col and "%" not in col:
                error_df[col] = error_df[col].round(0).astype(int)
            elif "%" in col:
                error_df[col] = error_df[col].round(2)
            elif "Prediction" in col:
                error_df[col] = error_df[col].round(0).astype(int)
        
        # Display error analysis table
        st.subheader("Prediction Error Analysis")
        st.dataframe(error_df)
        
        # Error visualization
        st.subheader("Error Visualization")
        
        error_viz_type = st.radio(
            "Select Error Visualization",
            ["Absolute Error", "Percentage Error", "Error Distribution"]
        )
        
        if error_viz_type == "Absolute Error":
            error_cols = [col for col in error_df.columns if "Error" in col and "%" not in col]
            error_data = error_df[["Year"] + error_cols]
            
            fig_error = px.line(
                error_data, 
                x="Year", 
                y=error_cols,
                title=f"Absolute Prediction Error by Model - {selected_cat_error}",
                markers=True,
                template="plotly_white"
            )
            fig_error.update_layout(yaxis_title="Error (Units)")
            st.plotly_chart(fig_error, use_container_width=True)
            
        elif error_viz_type == "Percentage Error":
            pct_error_cols = [col for col in error_df.columns if "% Error" in col]
            pct_error_data = error_df[["Year"] + pct_error_cols]
            
            fig_pct_error = px.line(
                pct_error_data, 
                x="Year", 
                y=pct_error_cols,
                title=f"Percentage Prediction Error by Model - {selected_cat_error}",
                markers=True,
                template="plotly_white"
            )
            fig_pct_error.update_layout(yaxis_title="Error (%)")
            st.plotly_chart(fig_pct_error, use_container_width=True)
            
        else:  # Error Distribution
            error_cols = [col for col in error_df.columns if "Error" in col and "%" not in col]
            error_dist_data = pd.melt(
                error_df, 
                id_vars=["Year"], 
                value_vars=error_cols,
                var_name="Model", 
                value_name="Error"
            )
            
            fig_dist = px.box(
                error_dist_data, 
                x="Model", 
                y="Error",
                title=f"Error Distribution by Model - {selected_cat_error}",
                template="plotly_white",
                points="all"
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        
        # Error metrics by year
        st.subheader("Error Metrics by Year")
        
        selected_model = st.selectbox(
            "Select Model for Detailed Analysis",
            list(error_models.keys()),
            key="detailed_model_select"
        )
        
        year_metrics = []
        
        for idx, year in enumerate(years_error[train_size:]):
            actual = test_sales_e[idx]
            pred = error_df[f"{selected_model} Prediction"].iloc[idx]
            abs_error = abs(actual - pred)
            pct_error = 100 * abs_error / actual if actual != 0 else float('inf')
            
            year_metrics.append({
                "Year": int(year),
                "Actual Sales": int(actual),
                "Predicted Sales": int(pred),
                "Absolute Error": int(abs_error),
                "Percentage Error": round(pct_error, 2)
            })
        
        year_metrics_df = pd.DataFrame(year_metrics)
        
        st.dataframe(year_metrics_df.style.highlight_max(subset=["Percentage Error"], color='#FFCCCC')
                     .highlight_min(subset=["Percentage Error"], color='#CCFFCC'))
        
        # Guidance for improving forecasts
        st.subheader("Error Analysis Insights")
        
        high_error_years = year_metrics_df[year_metrics_df["Percentage Error"] > 10]["Year"].tolist()
        
        if high_error_years:
            st.warning(f"High prediction errors detected in years: {', '.join(map(str, high_error_years))}")
        else:
            st.success("Model performs well across all tested years.")   
    with pred_tab4:
        st.header("Long-Term Forecast")
        st.markdown("Generate and visualize long-term EV adoption forecast using the best model")
        
        # Select vehicle category
        selected_cat_lt = st.selectbox(
            "Select Vehicle Category", 
            ev_sales['Cat'].unique(),
            key="lt_cat_select"
        )
        
        # Select forecast horizon
        forecast_years = st.slider(
            "Select Forecast Horizon (Years)",
            min_value=5,
            max_value=20,
            value=10,
            step=5
        )
        
        # Get historical data
        cat_data_lt = ev_sales[ev_sales['Cat'] == selected_cat_lt]
        yearly_sales_lt = cat_data_lt[[str(y) for y in range(2015, 2025)]].sum()
        years_lt = pd.to_numeric(yearly_sales_lt.index).to_numpy()
        sales_lt = yearly_sales_lt.values
        
        # Determine the best model for this category based on historical data
        with st.spinner("Determining the best model for long-term forecasting..."):
            # Train and compare models
            lt_models = {
                "Linear Regression": LinearRegression(),
                "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
                "Neural Network": MLPRegressor(hidden_layer_sizes=(50,), max_iter=1000, random_state=42)
            }
            
            # Add time series models if possible
            try:
                # Add Prophet model
                prophet_data_lt = pd.DataFrame({
                    'ds': pd.to_datetime([f"{int(year)}-01-01" for year in years_lt]),
                    'y': sales_lt
                })
                prophet_model_lt = Prophet(yearly_seasonality=False, 
                                          seasonality_mode='multiplicative',
                                          interval_width=0.95)
                prophet_model_lt.fit(prophet_data_lt)
                
                # Try to add ARIMA model
                try:
                    # Find best ARIMA order
                    arima_orders = [(1,1,1), (1,1,0), (0,1,1), (2,1,0), (0,1,2)]
                    best_aic = float('inf')
                    best_order = None
                    
                    for order in arima_orders:
                        try:
                            model = ARIMA(sales_lt, order=order)
                            model_fit = model.fit()
                            if model_fit.aic < best_aic:
                                best_aic = model_fit.aic
                                best_order = order
                        except:
                            continue
                            
                    if best_order:
                        arima_model_lt = ARIMA(sales_lt, order=best_order)
                        arima_fit_lt = arima_model_lt.fit()
                except:
                    pass
            except:
                st.info("Advanced time series models not available. Using basic models only.")
            
            # Prepare train/test split for evaluation
            train_size_lt = int(len(years_lt) * 0.8)
            train_x = years_lt[:train_size_lt].reshape(-1, 1)
            train_y = sales_lt[:train_size_lt]
            test_x = years_lt[train_size_lt:].reshape(-1, 1)
            test_y = sales_lt[train_size_lt:]
            
            # Evaluate models
            model_results = []
            
            # Traditional models
            for name, model in lt_models.items():
                model.fit(train_x, train_y)
                test_pred = model.predict(test_x)
                rmse = np.sqrt(mean_squared_error(test_y, test_pred))
                model_results.append({"Model": name, "RMSE": rmse})
            
            # Prophet
            try:
                prophet_train = prophet_data_lt.iloc[:train_size_lt]
                prophet_model_eval = Prophet(yearly_seasonality=False, 
                                           seasonality_mode='multiplicative',
                                           interval_width=0.95)
                prophet_model_eval.fit(prophet_train)
                
                future = prophet_model_eval.make_future_dataframe(periods=len(test_x), freq='YS')
                forecast = prophet_model_eval.predict(future)
                prophet_pred = forecast['yhat'].values[-len(test_y):]
                prophet_rmse = np.sqrt(mean_squared_error(test_y, prophet_pred))
                model_results.append({"Model": "Prophet", "RMSE": prophet_rmse})
            except:
                pass
                
            # ARIMA
            try:
                if best_order:
                    arima_train = ARIMA(train_y, order=best_order)
                    arima_train_fit = arima_train.fit()
                    arima_pred = arima_train_fit.forecast(steps=len(test_y))
                    arima_rmse = np.sqrt(mean_squared_error(test_y, arima_pred))
                    model_results.append({"Model": "ARIMA", "RMSE": arima_rmse})
            except:
                pass
            
            # Find best model
            best_model_info = min(model_results, key=lambda x: x["RMSE"])
            best_model_name = best_model_info["Model"]
            
            st.success(f"Best model for {selected_cat_lt}: **{best_model_name}** (RMSE: {best_model_info['RMSE']:.2f})")
            
            # Generate future forecast
            future_years = np.arange(years_lt[-1] + 1, years_lt[-1] + 1 + forecast_years)
            all_years = np.concatenate([years_lt, future_years])
            
            # Make forecast
            if best_model_name == "Prophet":
                # Use Prophet for forecast
                future_df = prophet_model_lt.make_future_dataframe(periods=forecast_years, freq='YS')
                forecast_result = prophet_model_lt.predict(future_df)
                forecast_values = forecast_result['yhat'].values
                lower_bound = forecast_result['yhat_lower'].values
                upper_bound = forecast_result['yhat_upper'].values
                has_bounds = True
            elif best_model_name == "ARIMA":
                # Use ARIMA for forecast
                forecast_result = arima_fit_lt.forecast(steps=forecast_years)
                forecast_values = np.concatenate([sales_lt, forecast_result])
                has_bounds = False
            else:
                # Use traditional ML model
                selected_model = lt_models[best_model_name]
                selected_model.fit(years_lt.reshape(-1, 1), sales_lt)
                future_x = all_years.reshape(-1, 1)
                forecast_values = selected_model.predict(future_x)
                has_bounds = False
            
            # Visualize results
            st.subheader(f"{forecast_years}-Year Forecast for {selected_cat_lt}")
            
            fig_lt = go.Figure()
            
            # Add historical data
            fig_lt.add_trace(go.Scatter(
                x=years_lt,
                y=sales_lt,
                name='Historical Data',
                mode='lines+markers',
                line=dict(color='black', width=3)
            ))
            
            # Add forecast
            fig_lt.add_trace(go.Scatter(
                x=all_years,
                y=forecast_values,
                name=f'{best_model_name} Forecast',
                mode='lines',
                line=dict(color='#FF9933', width=2)
            ))
            
            # Add confidence intervals if available
            if has_bounds and best_model_name == "Prophet":
                fig_lt.add_trace(go.Scatter(
                    x=np.concatenate([all_years, all_years[::-1]]),
                    y=np.concatenate([upper_bound, lower_bound[::-1]]),
                    fill='toself',
                    fillcolor='rgba(255, 153, 51, 0.2)',
                    line=dict(color='rgba(255,255,255,0)'),
                    name='95% Confidence Interval'
                ))
            
            # Add vertical line to separate historical from forecast
            fig_lt.add_vline(x=years_lt[-1], line_dash="dash", line_color="gray")
            
            # Layout
            fig_lt.update_layout(
                title=f"{selected_cat_lt} - Long-Term EV Adoption Forecast",
                xaxis_title="Year",
                yaxis_title="Units Sold",
                template="plotly_white",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig_lt, use_container_width=True)
            
            # Display forecast data in tabular format
            forecast_df = pd.DataFrame({
                "Year": all_years,
                "Predicted Sales": np.round(forecast_values).astype(int)
            })
            forecast_df["Type"] = "Historical"
            forecast_df.loc[len(years_lt):, "Type"] = "Forecast"
            
            st.subheader("Forecast Data Table")
            st.dataframe(forecast_df.style.apply(
                lambda x: ['background-color: #f0f8ff' if v == "Forecast" else '' 
                          for v in x], 
                subset=["Type"]
            ))
            
            # Calculate growth metrics
            current_sales = sales_lt[-1]
            final_forecast = forecast_values[-1]
            total_growth = final_forecast - current_sales
            pct_growth = (final_forecast / current_sales - 1) * 100
            cagr = ((final_forecast / current_sales) ** (1 / forecast_years) - 1) * 100
            
            # Display metrics in columns
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label=f"Total Growth (Next {forecast_years} Years)",
                    value=f"{int(total_growth):,}",
                    delta=f"{pct_growth:.1f}%"
                )
            with col2:
                st.metric(
                    label="CAGR (Compound Annual Growth Rate)",
                    value=f"{cagr:.2f}%"
                )
            with col3:
                double_time = np.log(2) / np.log(1 + cagr/100) if cagr > 0 else float('inf')
                st.metric(
                    label="Market Doubling Time",
                    value=f"{double_time:.1f} years" if double_time < float('inf') else "N/A"
                )    
      
    

elif current_page == "About":
    st.title("📝 About the Project")
    
    # Project Overview with columns and emojis
    st.header("🚀 Project Overview")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3094/3094837.png", width=100)
    with col2:
        st.markdown("""
        **India EV Market Analysis (2001–2024)**  
        This interactive platform analyzes the evolution of India's electric vehicle market, 
        identifying key trends and presenting actionable insights through intuitive visualizations.
        """)
    
    st.markdown("---")
    
    # Tech Stack with badges
    st.subheader("🛠️ Technology Stack")
    tech_cols = st.columns(4)
    tech_cols[0].markdown("![Streamlit](https://img.shields.io/badge/-Streamlit-FF4B4B?logo=streamlit&logoColor=white)")
    tech_cols[1].markdown("![Pandas](https://img.shields.io/badge/-Pandas-150458?logo=pandas&logoColor=white)")
    tech_cols[2].markdown("![GeoPandas](https://img.shields.io/badge/-GeoPandas-3776AB?logo=python&logoColor=white)")
    tech_cols[3].markdown("![Plotly](https://img.shields.io/badge/-Plotly-3F4F75?logo=plotly&logoColor=white)")
    
    st.markdown("---")
    
    # Data Sources with expandable sections
    with st.expander("📂 Data Sources", expanded=True):
        cols = st.columns(3)
        cols[0].markdown("**EV Data**\n- Manufacturers\n- Sales figures")
        cols[1].markdown("**Infrastructure**\n- Charging stations\n- Vehicle registrations")
        cols[2].markdown("**Geospatial**\n- State boundaries\n- Market reports")
    
    st.markdown("---")
    
    # Policy Milestones with timeline
    st.subheader("🕰️ Key EV Policy Milestones (2001-2024)")
    tab1, tab2, tab3 = st.tabs(["Early Developments", "Growth Phase", "Acceleration"])
    
    with tab1:
        st.markdown("""
        **2001-2012**  
        - 🏁 **2001**: First alternative fuels policy introduced  
        - 🔋 **2010**: MNRE launched EV incentives  
        - 🚗 **2011**: National Mission for Electric Mobility  
        - 💰 **2012**: NEMMP 2020 approved (₹14,000 Cr)  
        """)
    
    with tab2:
        st.markdown("""
        **2013-2018**  
        - 📜 **2013**: National Electric Mobility Mission Plan  
        - 🏆 **2015**: FAME-I introduced  
        - ⏳ **2018**: FAME-I extended + charging guidelines  
        """)
    
    with tab3:
        st.markdown("""
        **2019-2024**  
        - 🚀 **2019**: FAME-II launched (₹10,000 Cr)  
        - ⚡ **2020**: Charging infrastructure expansion  
        - 🌟 **2024**: Comprehensive EV policy with incentives  
        """)
    
    st.markdown("---")
    
    # Market Analysis with metrics
    st.subheader("📈 Market Analysis")
    st.markdown("""
    The Indian EV market has shown exponential growth, projected to expand from **$3.21 billion (2022)** 
    to **$113.99 billion by 2030**.
    """)
    
    st.subheader("🏆 Major Players")
    player_cols = st.columns(3)
    player_cols[0].markdown("**2-Wheelers**\n- Ola\n- Okinawa\n- Ather")
    player_cols[1].markdown("**3-Wheelers**\n- YC\n- Saera\n- Mahindra")
    player_cols[2].markdown("**4-Wheelers**\n- Tata\n- MG\n- BYD")
    
    st.subheader("📍 Top Markets")
    st.markdown("Maharashtra | Karnataka | Tamil Nadu | Gujarat | Rajasthan | Kerala | Delhi", help="Leading states in EV adoption")
    
    st.markdown("---")
    
    # SWOT Analysis with colored cards
    st.subheader("🔍 SWOT Analysis")
    swot_cols = st.columns(4)
    
    with swot_cols[0]:
        with st.container(border=True):
            st.markdown("**💪 Strengths**")
            st.markdown("- Government support\n- Growing demand")
    
    with swot_cols[1]:
        with st.container(border=True):
            st.markdown("**🤕 Weaknesses**")
            st.markdown("- High costs\n- Limited charging")
    
    with swot_cols[2]:
        with st.container(border=True):
            st.markdown("**🌟 Opportunities**")
            st.markdown("- Market growth\n- Tech innovation")
    
    with swot_cols[3]:
        with st.container(border=True):
            st.markdown("**⚠️ Threats**")
            st.markdown("- Competition\n- Regulations")
    
    st.markdown("---", unsafe_allow_html=True)

elif current_page == "Summary":
    # Header with image and title
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/3350/3350290.png", width=80)  # EV icon
    with col2:
        st.title("India's Electric Vehicle Market")
        st.caption("A Transformative Journey (2001-2024)")

    st.markdown("---")
    
       
    # Market Evolution section with timeline
    st.header("📈 Market Evolution")
    with st.expander("View Policy Timeline", expanded=True):
        timeline_cols = st.columns(3)
        timeline_cols[0].markdown("**Early Foundations**\n(2001-2012)\n- First policies\n- NEMMP 2020")
        timeline_cols[1].markdown("**Growth Phase**\n(2013-2018)\n- FAME-I\n- Charging standards")
        timeline_cols[2].markdown("**Acceleration**\n(2019-2024)\n- FAME-II\n- $100B market potential")
    
    st.markdown("---")
    
    # Key Segments with icons and metrics
    st.header("🚗 Key Market Segments")
    seg_cols = st.columns(3)
    
    with seg_cols[0]:
        with st.container(border=True):
            st.markdown("**🛵 Two-Wheelers**")
            st.metric("Market Share", ">60%")
            st.markdown("- Ola Electric\n- Ather Energy\n- Okinawa")
    
    with seg_cols[1]:
        with st.container(border=True):
            st.markdown("**🛺 Three-Wheelers**")
            st.metric("Adoption Rate", "25% CAGR")
            st.markdown("- YC Electric\n- Mahindra\n- Saera")
    
    with seg_cols[2]:
        with st.container(border=True):
            st.markdown("**🚗 Four-Wheelers**")
            st.metric("Premium Segment", "Growing")
            st.markdown("- Tata Motors\n- MG Motor\n- BYD")
    
    st.markdown("---")
    
    # Geographic Trends with map suggestion
    st.header("🗺️ Geographic Trends")
    st.markdown("""
    **Leading States** (by EV adoption):
    """)
    geo_cols = st.columns(4)
    geo_cols[0].metric("Maharashtra", "#1")
    geo_cols[1].metric("Karnataka", "#2")
    geo_cols[2].metric("Tamil Nadu", "#3")
    geo_cols[3].metric("Gujarat", "#4")
    
    st.markdown("*For detailed regional analysis, visit the Insights page*")
    
    st.markdown("---")
    
    # Challenges & Opportunities with toggle
    st.header("⚖️ Challenges & Opportunities")
    tab1, tab2 = st.tabs(["Challenges", "Opportunities"])
    
    with tab1:
        st.markdown("""
        - **High upfront costs** compared to ICE vehicles
        - **Charging infrastructure** needs expansion
        - **Battery technology** limitations
        - **Consumer awareness** gaps
        """)
    
    with tab2:
        st.markdown("""
        - **$100B+** market potential by 2030
        - **Government incentives** continuing
        - **Local manufacturing** growth
        - **Renewable energy** integration
        """)
    
    st.markdown("---")
    
    # Future Outlook with callout
    st.header("🔮 Future Outlook")
    st.markdown("""
    <div style='background-color:#e8f8f5; padding:15px; border-radius:10px; border-left:5px solid #28b463;'>
    <h4 style='color:#28b463;margin-top:0;'>Projected Market Value: $113.99 Billion by 2030</h4>
    <p>India's EV market is poised to transform the transportation sector, potentially reducing CO₂ emissions by 37% from road transport by 2030.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
elif current_page == "EV Policy Impact":
    st.title("📜 EV Policy Impact")
    st.markdown("""
    Analyze how major government policies have influenced EV adoption in India.
    """)
    # Example: Show a bar chart of sales before and after FAME-II (2019)
    fame_year = 2019
    total_sales = ev_sales[[str(y) for y in range(2015, 2025)]].sum()
    before = total_sales[[str(y) for y in range(2015, fame_year)]].sum()
    after = total_sales[[str(y) for y in range(fame_year, 2025)]].sum()
    st.bar_chart(pd.DataFrame({
        "Period": ["Before FAME-II", "After FAME-II"],
        "Total Sales": [before, after]
    }).set_index("Period"))
    st.markdown("**Notice the significant increase in EV sales after the FAME-II policy was introduced in 2019.**")
