import json
import urllib.request
import streamlit as st
import pandas as pd
import datetime
from streamlit import cache_data

# Streamlit app title and styling
st.set_page_config(page_title="FKN CURRENCY CONVERTER", layout="wide")
st.markdown("""
    <style>
    input {
        color: black !important;
    }
    .st-emotion-cache-1v0mbdj e115fcil1 img {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💱 FKN CURRENCY CONVERTER")

# --- Currency List ---
currency_list = [
    "USD", "KES", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "ZAR", "INR", 
    "CNY", "NZD", "SGD", "NGN", "GHS", "TZS", "UGX", "RUB", "BRL", "MXN"
]

# --- UI: Currency dropdowns and amount ---
col1, col2, col3 = st.columns(3)
with col1:
    base_currency = st.selectbox("Base currency:", currency_list, index=0)
with col2:
    target_currency = st.selectbox("Target currency:", currency_list, index=1)
with col3:
    amount = st.number_input("Amount to convert:", value=1.0, min_value=0.01)

# Cache historical data for 6 hours to avoid hitting API limits
@cache_data(ttl=21600)  # 6 hours in seconds
def get_historical_data(base, target, start_date, end_date):
    hist_url = f"http://api.exchangerate.host/timeframe?access_key=957c96b16d2a683a8592b2340d59afd0&source={base}&currencies={target}&start_date={start_date}&end_date={end_date}"
    
    try:
        with urllib.request.urlopen(hist_url) as response:
            data = json.loads(response.read())
            if data.get("success"):
                return data
            return None
    except:
        return None

# --- API for live conversion ---
if st.button("Convert"):
    api_url = f"https://v6.exchangerate-api.com/v6/caa4b53d5c599f5dd44a0700/latest/{base_currency}"

    try:
        with urllib.request.urlopen(api_url) as response:
            data = json.loads(response.read())

            if data["result"] == "success":
                rate = data["conversion_rates"].get(target_currency)
                if rate:
                    converted = round(amount * rate, 2)
                    st.success(f"✅ {amount} {base_currency} = {converted} {target_currency}")
                else:
                    st.error(f"❌ Target currency '{target_currency}' not found.")
            else:
                st.error("❌ API Error: " + str(data.get("error-type", "Unknown error")))
    except Exception as e:
        st.error(f"❌ Error: {e}")

# --- Sidebar for Historical Data and Stats ---
with st.sidebar:
    st.header("📉 Historical Insights")
    
    # Load cached data or show last successful fetch
    end_date = datetime.date.today()
    start_date = end_date - datetime.timedelta(days=365)
    
    with st.spinner("Loading historical data..."):
        hist_data = get_historical_data(base_currency, target_currency, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    
    if hist_data:
        rates = hist_data["quotes"]
        
        # Convert to pandas DataFrame
        df = pd.DataFrame.from_dict(rates, orient='index')
        df.index = pd.to_datetime(df.index)
        column_name = f"{base_currency}{target_currency}"
        df.columns = [target_currency]
        df.sort_index(inplace=True)

        # Calculate stats
        highest_rate = df[target_currency].max()
        highest_date = df[target_currency].idxmax().date()
        lowest_rate = df[target_currency].min()
        lowest_date = df[target_currency].idxmin().date()

        # Percentage changes with safety checks
        latest = df[target_currency].iloc[-1]
        day_ago = df[target_currency].iloc[-2] if len(df) > 1 else latest
        week_ago = df[target_currency].iloc[-7] if len(df) > 7 else latest
        month_ago = df[target_currency].iloc[-30] if len(df) > 30 else latest
        year_ago = df[target_currency].iloc[0]

        def safe_percent_change(new, old):
            return ((new - old) / old) * 100 if old != 0 else 0

        percent_day = safe_percent_change(latest, day_ago)
        percent_week = safe_percent_change(latest, week_ago)
        percent_month = safe_percent_change(latest, month_ago)
        percent_year = safe_percent_change(latest, year_ago)

        # Display stats
        st.subheader(f"💹 {base_currency} → {target_currency}")
        st.markdown(f"**Highest:** `{highest_rate:.4f}` on {highest_date}")
        st.markdown(f"**Lowest:** `{lowest_rate:.4f}` on {lowest_date}")
        st.markdown(f"**Current Rate:** `{latest:.4f}`")

        st.subheader("📊 % Change")
        cols = st.columns(2)
        cols[0].metric("1 Day", f"{percent_day:.2f}%")
        cols[1].metric("1 Week", f"{percent_week:.2f}%")
        cols[0].metric("1 Month", f"{percent_month:.2f}%")
        cols[1].metric("1 Year", f"{percent_year:.2f}%")

        # Improved chart visualization
        st.subheader("📈 1-Year Trend")
        
        # Resample to weekly data if too many points
        if len(df) > 100:
            chart_df = df.resample('W').mean()
        else:
            chart_df = df.copy()
            
        # Format y-axis to show reasonable decimal places
        min_rate = chart_df[target_currency].min()
        max_rate = chart_df[target_currency].max()
        y_range = max_rate - min_rate
        
        if y_range < 0.1:  # Small fluctuations
            st.line_chart(chart_df, y=target_currency, height=300, use_container_width=True)
        elif y_range < 1:  # Medium fluctuations
            st.line_chart(chart_df, y=target_currency, height=300, use_container_width=True)
        else:  # Large fluctuations
            st.line_chart(chart_df, y=target_currency, height=300, use_container_width=True)
            
    else:
        st.warning("⚠️ Historical data not available. Using cached data if possible.")
        # You could add logic here to load the last successful cached data

# Add some app 
# Add this at the bottom of your sidebar section (before the last line)
with st.sidebar:
    st.markdown("---")
    st.markdown("**Project by Francis Kamande**")
    st.markdown("*Currency Converter App*")
st.sidebar.markdown("---")
st.sidebar.markdown("**ℹ️ App Info**")
st.sidebar.markdown("- Data updates every 6 hours")
st.sidebar.markdown("- Rates are mid-market rates")
st.sidebar.markdown("- For demonstration purposes")
st.markdown("---")
st.caption("© 2024 | Developed by Francis Kamande")
