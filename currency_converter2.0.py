import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Currency Converter", layout="centered")

st.title("💱 Real-Time Currency Converter")

# Add some styling
st.markdown("""
    <style>
        .stTextInput input, .stNumberInput input {
            background-color: #f0f2f6;
            border-radius: 5px;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 10px 24px;
            width: 100%;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .success-box {
            padding: 15px;
            background-color: #e8f5e9;
            border-radius: 5px;
            border-left: 5px solid #4CAF50;
            margin: 10px 0;
        }
        .error-box {
            padding: 15px;
            background-color: #ffebee;
            border-radius: 5px;
            border-left: 5px solid #f44336;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for additional info
with st.sidebar:
    st.header("About")
    st.info("This app uses real-time exchange rates from the [exchangerate.host](https://exchangerate.host) API.")
    st.write("Enter a base currency, target currency, and amount to convert.")

# User input in columns for better layout
col1, col2 = st.columns(2)
with col1:
    base_currency = st.text_input("Base currency (e.g. USD):", value="USD", max_chars=3).upper()
with col2:
    target_currency = st.text_input("Target currency (e.g. KES):", value="KES", max_chars=3).upper()

amount = st.number_input("Amount to convert:", min_value=0.0, value=1.0, step=0.01)

if st.button("Convert Currency"):
    if not base_currency or not target_currency:
        st.error("Please enter both currencies.")
    elif base_currency == target_currency:
        st.error("Base and target currencies cannot be the same.")
    else:
        with st.spinner("Fetching exchange rate..."):
            try:
                # API request with date for caching
                url = f"https://api.exchangerate.host/convert?from={base_currency}&to={target_currency}&amount={amount}"
                response = requests.get(url)
                data = response.json()
                
                if "result" in data and data["success"]:
                    converted = data["result"]
                    rate = data["info"]["rate"]
                    date = datetime.fromtimestamp(data["info"]["timestamp"]).strftime('%Y-%m-%d %H:%M:%S')
                    
                    st.markdown(f"""
                    <div class="success-box">
                        <h3>Conversion Result</h3>
                        <p><strong>{amount:,.2f} {base_currency}</strong> = <strong>{converted:,.2f} {target_currency}</strong></p>
                        <p>Exchange rate: 1 {base_currency} = {rate:.6f} {target_currency}</p>
                        <p><small>Rates as of: {date}</small></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    error_msg = data.get("error", {}).get("info", "Failed to fetch conversion data.")
                    st.markdown(f"""
                    <div class="error-box">
                        <p>{error_msg}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("""
    <style>
        footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px;
        }
    </style>
    <footer>
        <p>Made with ❤️ by Francis Kamande</p>
    </footer>
""", unsafe_allow_html=True)