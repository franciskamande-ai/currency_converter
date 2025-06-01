import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="Currency Converter", layout="centered")

st.title("💱 Real-Time Currency Converter")

# API configuration
API_KEY = "caa4b53d5c599f5dd44a0700"
BASE_URL = f"https://v6.exchangerate-api.com/v6/{API_KEY}"

# Enhanced styling with clear visibility
st.markdown("""
    <style>
        /* Input fields with high contrast */
        .stTextInput input, .stNumberInput input {
            background-color: #f8f9fa;
            border: 1px solid #ced4da;
            border-radius: 5px;
            color: #212529 !important;
            padding: 8px 12px;
        }
        /* Input labels */
        .stTextInput label, .stNumberInput label {
            color: #495057 !important;
            font-weight: 500;
        }
        /* Button styling */
        .stButton button {
            background-color: #28a745;
            color: white !important;
            border-radius: 5px;
            padding: 10px 24px;
            width: 100%;
            font-weight: bold;
            border: none;
        }
        .stButton button:hover {
            background-color: #218838;
            color: white !important;
        }
        /* Result boxes */
        .success-box {
            padding: 15px;
            background-color: #e6f7ee;
            border-radius: 8px;
            border-left: 5px solid #28a745;
            margin: 15px 0;
            color: #155724;
        }
        .error-box {
            padding: 15px;
            background-color: #f8d7da;
            border-radius: 8px;
            border-left: 5px solid #dc3545;
            margin: 15px 0;
            color: #721c24;
        }
        /* Footer */
        footer {
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100%;
            background-color: #f8f9fa;
            text-align: center;
            padding: 10px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
        }
    </style>
""", unsafe_allow_html=True)

# Sidebar for additional info
with st.sidebar:
    st.header("ℹ️ About")
    st.info("""
    This app uses real-time exchange rates from ExchangeRate-API.
    Supported currencies: USD, EUR, GBP, JPY, KES, etc.
    """)
    st.write("Enter base currency, target currency, and amount to convert.")

# User input in columns
col1, col2 = st.columns(2)
with col1:
    base_currency = st.text_input("From currency (e.g. USD):", value="USD", max_chars=3).upper()
with col2:
    target_currency = st.text_input("To currency (e.g. KES):", value="KES", max_chars=3).upper()

amount = st.number_input("Amount to convert:", min_value=0.0, value=1.0, step=0.01, format="%.2f")

if st.button("🔁 Convert Currency"):
    if not base_currency or not target_currency:
        st.markdown("""
        <div class="error-box">
            <p>Please enter both currencies.</p>
        </div>
        """, unsafe_allow_html=True)
    elif base_currency == target_currency:
        st.markdown("""
        <div class="error-box">
            <p>Base and target currencies cannot be the same.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        with st.spinner("⏳ Fetching exchange rates..."):
            try:
                # First get all exchange rates for base currency
                url = f"{BASE_URL}/latest/{base_currency}"
                response = requests.get(url)
                data = response.json()
                
                if data.get("result") == "success":
                    rates = data.get("conversion_rates", {})
                    if target_currency in rates:
                        rate = rates[target_currency]
                        converted = amount * rate
                        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        
                        st.markdown(f"""
                        <div class="success-box">
                            <h3>💰 Conversion Result</h3>
                            <p><strong>{amount:,.2f} {base_currency} = {converted:,.2f} {target_currency}</strong></p>
                            <p>💱 Exchange rate: 1 {base_currency} = {rate:.6f} {target_currency}</p>
                            <p><small>🕒 Rates as of: {date}</small></p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="error-box">
                            <p>Currency {target_currency} not found in API response.</p>
                            <p>Available currencies: {', '.join(list(rates.keys())[:10])}...</p>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    error_type = data.get("error-type", "unknown")
                    st.markdown(f"""
                    <div class="error-box">
                        <p>API Error: {error_type.replace('-', ' ').title()}</p>
                        <p>Please check your currencies and try again.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
            except Exception as e:
                st.markdown(f"""
                <div class="error-box">
                    <p>Connection Error: {str(e)}</p>
                    <p>Please check your internet connection.</p>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("""
    <footer>
        <p>Made with ❤️ by Francis Kamande | ExchangeRate-API</p>
    </footer>
""", unsafe_allow_html=True)