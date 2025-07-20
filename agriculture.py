import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import datetime
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import requests
import json
from typing import Dict, Any

# Setup your Gemini API Key
os.environ["GOOGLE_API_KEY"] = "AIzaSyBLRhTudAcbsSoVf0uJrlUmlsBWYGew0eA"

# Gemini model setup
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)

# API Configuration
WEATHER_API_KEY = "65750d1c4cd5ae36f49c91696bcba54f"  # Get from openweathermap.org
MARKET_API_KEY = "KWX7H1I05F2DZ7OM"  # Get from agmarknet.gov.in or similar

# Enhanced crop categories with more options
crop_categories = {
    "Fruit Vegetables": ["Tomato", "Brinjal", "Bhendi", "Chillies", "Capsicum", "Cucumber", "Bottle Gourd", "Ridge Gourd"],
    "Cereals": ["Wheat", "Rice", "Maize", "Barley", "Oats"],
    "Millets": ["Ragi", "Jowar", "Bajra", "Foxtail Millet", "Pearl Millet"],
    "Fruits": ["Mango", "Banana", "Guava", "Papaya", "Orange", "Grapes", "Pomegranate"],
    "Pulses": ["Arhar", "Moong", "Urad", "Chana", "Masoor", "Rajma"],
    "Oilseeds": ["Groundnut", "Sunflower", "Sesame", "Safflower", "Mustard"],
    "Spices": ["Turmeric", "Coriander", "Cumin", "Fenugreek", "Black Pepper"],
    "Cash Crops": ["Cotton", "Sugarcane", "Jute", "Tobacco","Copra"]
}

soil_types = ["Loamy", "Sandy", "Black", "Red", "Clayey", "Alluvial", "Laterite"]
water_sources = ["Rainfed", "Canal", "Borewell", "Mixed", "Drip Irrigation", "Sprinkler"]
seasons = ["Kharif (June-Oct)", "Rabi (Nov-Apr)", "Zaid (Apr-June)", "Year Round"]

# Weather API Integration
@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_weather_data(city: str, state: str) -> Dict[str, Any]:
    """Fetch real-time weather data from OpenWeatherMap API"""
    try:
        # OpenWeatherMap API URL
        base_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": f"{city},{state},IN",
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "temperature": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "weather": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "visibility": data.get("visibility", 0) / 1000,  # Convert to km
                "feels_like": data["main"]["feels_like"],
                "min_temp": data["main"]["temp_min"],
                "max_temp": data["main"]["temp_max"],
                "sunrise": datetime.datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
                "sunset": datetime.datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")
            }
        else:
            return {"success": False, "error": "Weather API request failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Weather Forecast API
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_weather_forecast(city: str, state: str) -> Dict[str, Any]:
    """Fetch 5-day weather forecast"""
    try:
        base_url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": f"{city},{state},IN",
            "appid": WEATHER_API_KEY,
            "units": "metric"
        }
        
        response = requests.get(base_url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            forecast_data = []
            
            for item in data["list"][:15]:  # Next 5 days (3-hour intervals)
                forecast_data.append({
                    "datetime": datetime.datetime.fromtimestamp(item["dt"]),
                    "temperature": item["main"]["temp"],
                    "humidity": item["main"]["humidity"],
                    "weather": item["weather"][0]["description"],
                    "rain": item.get("rain", {}).get("3h", 0)
                })
            
            return {"success": True, "forecast": forecast_data}
        else:
            return {"success": False, "error": "Forecast API request failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# Market Price API Integration
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_market_prices(state: str, district: str) -> Dict[str, Any]:
    """Fetch real-time market prices from various sources"""
    try:
        # This is a placeholder for actual market API integration
        # You can integrate with:
        # 1. AgMarkNet (https://agmarknet.gov.in/)
        # 2. eNAM (https://enam.gov.in/)
        # 3. Private agricultural data providers
        
        # For demonstration, using a mock API structure
        # Replace with actual API calls
        
        # Mock API call structure:
        # market_url = f"https://api.agmarknet.gov.in/nav/get-market-price-data"
        # params = {
        #     "state": state,
        #     "district": district,
        #     "api_key": MARKET_API_KEY
        # }
        # response = requests.get(market_url, params=params)
        
        # For now, returning enhanced mock data with realistic variations
        base_prices = {
            "Tomato": {"price": 25, "unit": "kg", "market": "Wholesale"},
            "Rice": {"price": 45, "unit": "kg", "market": "Wholesale"},
            "Wheat": {"price": 40, "unit": "kg", "market": "Wholesale"},
            "Onion": {"price": 35, "unit": "kg", "market": "Wholesale"},
            "Maize": {"price": 28, "unit": "kg", "market": "Wholesale"},
            "Chillies": {"price": 80, "unit": "kg", "market": "Wholesale"},
            "Cotton": {"price": 5800, "unit": "quintal", "market": "Wholesale"},
            "Sugarcane": {"price": 3200, "unit": "ton", "market": "Mill Gate"},
            "Groundnut": {"price": 5500, "unit": "quintal", "market": "Wholesale"},
            "Turmeric": {"price": 8500, "unit": "quintal", "market": "Wholesale"}
        }
        
        # Add realistic price variations and trends
        import random
        current_prices = {}
        for crop, data in base_prices.items():
            variation = random.uniform(-0.15, 0.15)  # ±15% variation
            current_price = data["price"] * (1 + variation)
            last_month_price = current_price * random.uniform(0.9, 1.1)
            
            trend = "up" if current_price > last_month_price else "down"
            change = abs(current_price - last_month_price)
            
            current_prices[crop] = {
                "current_price": round(current_price, 2),
                "last_month_price": round(last_month_price, 2),
                "change": round(change, 2),
                "trend": trend,
                "unit": data["unit"],
                "market": data["market"],
                "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        
        return {"success": True, "prices": current_prices}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Historical price trends
@st.cache_data(ttl=86400)  # Cache for 24 hours
def get_price_trends(crop: str, days: int = 30) -> Dict[str, Any]:
    """Get historical price trends for a specific crop"""
    try:
        # Mock historical data generation
        # In real implementation, this would fetch from historical price APIs
        
        dates = pd.date_range(end=datetime.datetime.now(), periods=days, freq='D')
        base_price = 50  # Base price for simulation
        
        # Generate realistic price trend
        prices = []
        for i, date in enumerate(dates):
            trend = base_price + (i * 0.5) + (5 * (0.5 - random.random()))
            prices.append(max(trend, 10))  # Minimum price of 10
        
        return {
            "success": True,
            "dates": dates.tolist(),
            "prices": prices,
            "crop": crop
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# Page configuration
st.set_page_config(
    page_title="🌾 Smart Agriculture Advisor",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #4CAF50, #45a049);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 0.5rem 0;
    }
    .weather-card {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .market-card {
        background: linear-gradient(135deg, #fd79a8, #e84393);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .stButton > button {
        background: #4CAF50;
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 5px;
        font-weight: bold;
    }
    .trend-up {
        color: #27ae60;
        font-weight: bold;
    }
    .trend-down {
        color: #e74c3c;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🌾 Smart Agriculture Advisor</h1>
    <p>AI-Powered Farming Guidance with Real-Time Weather & Market Data</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.selectbox("Choose a feature:", 
                           ["Crop Advisory", "Market Analysis", "Weather Insights", "Crop Calendar"])

if page == "Crop Advisory":
    # Main content in columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Crop Information")
        
        # Basic inputs
        category = st.selectbox("🌱 Select Crop Category", list(crop_categories.keys()))
        crop = st.selectbox("🌾 Select Crop", crop_categories[category])
        district = st.text_input("📍 Enter your District", value="Dharwad")
        state = st.text_input("🗺️ Enter your State", value="Karnataka")
        
        # Enhanced inputs
        col_a, col_b = st.columns(2)
        with col_a:
            farm_size = st.slider("🏡 Farm Size (Acres)", 0.5, 100.0, 2.0, 0.5)
            season = st.selectbox("📅 Preferred Season", seasons)
        with col_b:
            experience = st.selectbox("👨‍🌾 Farming Experience", ["Beginner", "Intermediate", "Expert"])
            organic = st.checkbox("🌿 Organic Farming Interest")
    
    with col2:
        st.header("📊 Real-Time Data")
        
        # Real-time weather data
        st.subheader("🌤️ Current Weather")
        if st.button("🔄 Refresh Weather", key="weather_refresh"):
            st.rerun()
        
        weather_data = get_weather_data(district, state)
        if weather_data["success"]:
            col_w1, col_w2 = st.columns(2)
            with col_w1:
                st.metric("🌡️ Temperature", f"{weather_data['temperature']:.1f}°C", 
                         f"Feels like {weather_data['feels_like']:.1f}°C")
                st.metric("💧 Humidity", f"{weather_data['humidity']}%")
            with col_w2:
                st.metric("🌬️ Wind Speed", f"{weather_data['wind_speed']} m/s")
                st.metric("👁️ Visibility", f"{weather_data['visibility']} km")
            
            st.info(f"☁️ {weather_data['weather'].title()}")
            st.success(f"🌅 Sunrise: {weather_data['sunrise']} | 🌇 Sunset: {weather_data['sunset']}")
        else:
            st.error(f"❌ Weather Error: {weather_data['error']}")
            st.info("💡 Please check your API key or city name")
        
        # Real-time market prices
        st.subheader("💰 Current Market Prices")
        if st.button("🔄 Refresh Prices", key="market_refresh"):
            st.rerun()
        
        market_data = get_market_prices(state, district)
        if market_data["success"]:
            prices = market_data["prices"]
            if crop in prices:
                price_info = prices[crop]
                trend_class = "trend-up" if price_info["trend"] == "up" else "trend-down"
                trend_icon = "📈" if price_info["trend"] == "up" else "📉"
                
                st.metric(
                    f"💵 {crop} Price",
                    f"₹{price_info['current_price']}/{price_info['unit']}",
                    f"{'+' if price_info['trend'] == 'up' else '-'}₹{price_info['change']:.2f}"
                )
                st.markdown(f"<p class='{trend_class}'>{trend_icon} {price_info['trend'].title()}</p>", 
                           unsafe_allow_html=True)
                st.caption(f"📊 {price_info['market']} Market | 🕒 Updated: {price_info['last_updated']}")
            else:
                st.warning(f"⚠️ Price data not available for {crop}")
        else:
            st.error(f"❌ Market Error: {market_data['error']}")
    
    # Advanced options
    with st.expander("🔧 Advanced Agricultural Parameters"):
        col_c, col_d = st.columns(2)
        with col_c:
            soil_type = st.selectbox("🌍 Soil Type", soil_types)
            water_source = st.selectbox("💧 Water Source", water_sources)
            budget = st.radio("💰 Budget Range", ["Low (₹10K-50K)", "Medium (₹50K-2L)", "High (₹2L+)"])
        with col_d:
            current_ph = st.slider("🧪 Soil pH (if known)", 4.0, 9.0, 6.5, 0.1)
            rainfall = st.selectbox("🌧️ Average Rainfall", ["Low (<500mm)", "Medium (500-1000mm)", "High (>1000mm)"])
            mechanization = st.selectbox("🚜 Mechanization Level", ["Manual", "Semi-mechanized", "Fully mechanized"])
    
    # Additional features
    with st.expander("🎯 Additional Preferences"):
        col_e, col_f = st.columns(2)
        with col_e:
            market_focus = st.selectbox("🎯 Market Focus", ["Local Market", "Wholesale", "Export", "Processing"])
            risk_tolerance = st.selectbox("⚡ Risk Tolerance", ["Low Risk", "Medium Risk", "High Risk"])
        with col_f:
            certification = st.multiselect("🏆 Certifications Interested", 
                                         ["Organic", "FairTrade", "GlobalGAP", "FSSAI"])
            value_addition = st.checkbox("⚙️ Interest in Value Addition/Processing")
    
    # Submit button
    if st.button("🚀 Get Comprehensive Crop Advisory", type="primary"):
        with st.spinner("🔄 Analyzing your requirements and generating recommendations..."):
            # Get current weather and market data for the prompt
            weather_info = get_weather_data(district, state)
            market_info = get_market_prices(state, district)
            
            weather_context = ""
            if weather_info["success"]:
                weather_context = f"""
                Current Weather Conditions:
                - Temperature: {weather_info['temperature']}°C
                - Humidity: {weather_info['humidity']}%
                - Weather: {weather_info['weather']}
                - Wind Speed: {weather_info['wind_speed']} m/s
                """
            
            market_context = ""
            if market_info["success"] and crop in market_info["prices"]:
                price_data = market_info["prices"][crop]
                market_context = f"""
                Current Market Information:
                - Current Price: ₹{price_data['current_price']}/{price_data['unit']}
                - Price Trend: {price_data['trend']} (₹{price_data['change']:.2f} change)
                - Market Type: {price_data['market']}
                """
            
            # Enhanced prompt with real-time data
            prompt = f"""
            You are an expert agriculture advisor with access to real-time weather and market data for Indian farming practices.

            Provide comprehensive guidance for:
            - Crop Category: {category}
            - Crop Name: {crop}
            - Location: {district}, {state}
            - Farm Size: {farm_size} acres
            - Season: {season}
            - Farmer Experience: {experience}
            - Organic Interest: {organic}
            - Soil Type: {soil_type}
            - Water Source: {water_source}
            - Budget: {budget}
            - Soil pH: {current_ph}
            - Rainfall: {rainfall}
            - Mechanization: {mechanization}
            - Market Focus: {market_focus}
            - Risk Tolerance: {risk_tolerance}
            - Certifications: {certification}
            - Value Addition Interest: {value_addition}

            {weather_context}
            {market_context}

            Based on the REAL-TIME weather and market data above, provide detailed analysis in the following structured format:

            ## 1. 📊 Current Situation Analysis (Weather & Market)
            ## 2. 🌱 Recommended Varieties & Morphological Characters
            ## 3. 🗓️ Optimal Planting Calendar (Based on Current Weather)
            ## 4. 🌍 Soil & Climate Requirements
            ## 5. 💧 Water Management Strategy (Weather-Adjusted)
            ## 6. 🌿 Fertilizer & Nutrient Management
            ## 7. 🔬 Modern Technologies & Innovations
            ## 8. 🐛 Integrated Pest Management
            ## 9. 🌾 Pre & Post-Harvest Practices
            ## 10. 💰 Economic Analysis & Profitability (Current Market Prices)
            ## 11. 📈 Market Strategy & Price Optimization
            ## 12. ⚠️ Risk Assessment & Weather Alerts
            ## 13. 🏆 Certification & Quality Standards
            ## 14. 🔄 Sustainable Practices
            ## 15. 📞 Support Resources & Emergency Contacts

            IMPORTANT: Use the real-time weather data to provide immediate actionable advice and incorporate current market prices into profitability calculations.
            """

            response = llm.invoke(prompt)
            
            # Display results
            st.markdown("---")
            st.markdown("## 📋 Comprehensive Crop Advisory Report")
            st.markdown(response.content)
            
            # Additional visual elements
            st.markdown("---")
            col_result1, col_result2 = st.columns(2)
            
            with col_result1:
                st.success("✅ Report Generated Successfully!")
                st.info("💡 Report includes real-time weather and market data")
            
            with col_result2:
                report_content = f"""
CROP ADVISORY REPORT
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{response.content}

REAL-TIME DATA USED:
{weather_context}
{market_context}
"""
                st.download_button(
                    label="📥 Download Report with Real-Time Data",
                    data=report_content,
                    file_name=f"{crop}_advisory_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )

elif page == "Market Analysis":
    st.header("📈 Real-Time Market Analysis Dashboard")
    
    # Market data controls
    col1, col2 = st.columns([3, 1])
    with col1:
        analysis_state = st.selectbox("Select State for Analysis", 
                                    ["Karnataka", "Maharashtra", "Punjab", "Uttar Pradesh", "Tamil Nadu"])
        analysis_district = st.text_input("Enter District", value="Dharwad")
    with col2:
        if st.button("🔄 Refresh Market Data"):
            st.rerun()
    
    # Get market data
    market_data = get_market_prices(analysis_state, analysis_district)
    
    if market_data["success"]:
        prices = market_data["prices"]
        
        # Create dataframe for visualization
        df = pd.DataFrame([
            {
                "Crop": crop,
                "Current Price": data["current_price"],
                "Last Month": data["last_month_price"],
                "Change": data["change"],
                "Trend": data["trend"],
                "Unit": data["unit"]
            }
            for crop, data in prices.items()
        ])
        
        # Market visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(df, x='Crop', y='Current Price', 
                        title=f"Current Market Prices - {analysis_district}",
                        color='Trend',
                        color_discrete_map={'up': '#27ae60', 'down': '#e74c3c'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Price change visualization
            fig2 = px.bar(df, x='Crop', y='Change', 
                         title="Price Changes from Last Month",
                         color='Trend',
                         color_discrete_map={'up': '#27ae60', 'down': '#e74c3c'})
            st.plotly_chart(fig2, use_container_width=True)
        
        # Market data table
        st.subheader("📊 Detailed Market Prices")
        st.dataframe(df, use_container_width=True)
        
        # Market insights
        st.subheader("💡 Market Insights")
        up_crops = df[df['Trend'] == 'up']['Crop'].tolist()
        down_crops = df[df['Trend'] == 'down']['Crop'].tolist()
        
        if up_crops:
            st.success(f"📈 Rising Prices: {', '.join(up_crops)}")
        if down_crops:
            st.error(f"📉 Falling Prices: {', '.join(down_crops)}")
        
        # Price trend analysis
        st.subheader("📊 Price Trend Analysis")
        selected_crop = st.selectbox("Select crop for trend analysis", list(prices.keys()))
        
        if st.button("📈 Generate Trend Chart"):
            trend_data = get_price_trends(selected_crop)
            if trend_data["success"]:
                trend_df = pd.DataFrame({
                    "Date": trend_data["dates"],
                    "Price": trend_data["prices"]
                })
                
                fig3 = px.line(trend_df, x='Date', y='Price', 
                              title=f"{selected_crop} Price Trend (Last 30 Days)")
                st.plotly_chart(fig3, use_container_width=True)
    else:
        st.error(f"❌ Market Data Error: {market_data['error']}")
        st.info("💡 Please check your API configuration")

elif page == "Weather Insights":
    st.header("🌤️ Real-Time Weather Insights")
    
    # Weather location input
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        weather_city = st.text_input("Enter City", value="Dharwad")
    with col2:
        weather_state = st.text_input("Enter State", value="Karnataka")
    with col3:
        if st.button("🔄 Update Weather"):
            st.rerun()
    
    # Current weather
    weather_data = get_weather_data(weather_city, weather_state)
    
    if weather_data["success"]:
        st.subheader("🌡️ Current Weather Conditions")
        
        # Weather metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Temperature", f"{weather_data['temperature']:.1f}°C",
                     f"Feels like {weather_data['feels_like']:.1f}°C")
        with col2:
            st.metric("Humidity", f"{weather_data['humidity']}%")
        with col3:
            st.metric("Wind Speed", f"{weather_data['wind_speed']} m/s")
        with col4:
            st.metric("Visibility", f"{weather_data['visibility']} km")
        
        # Additional weather info
        col5, col6 = st.columns(2)
        with col5:
            st.info(f"☁️ Conditions: {weather_data['weather'].title()}")
            st.info(f"🌡️ Range: {weather_data['min_temp']:.1f}°C - {weather_data['max_temp']:.1f}°C")
        with col6:
            st.info(f"🌅 Sunrise: {weather_data['sunrise']}")
            st.info(f"🌇 Sunset: {weather_data['sunset']}")
        
        # Weather forecast
        st.subheader("📅 5-Day Weather Forecast")
        forecast_data = get_weather_forecast(weather_city, weather_state)
        
        if forecast_data["success"]:
            forecast_df = pd.DataFrame(forecast_data["forecast"])
            
            # Forecast visualization
            fig = px.line(forecast_df, x='datetime', y='temperature',
                         title="Temperature Forecast",
                         labels={'datetime': 'Date & Time', 'temperature': 'Temperature (°C)'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Rainfall forecast
            fig2 = px.bar(forecast_df, x='datetime', y='rain',
                         title="Rainfall Forecast",
                         labels={'datetime': 'Date & Time', 'rain': 'Rainfall (mm)'})
            st.plotly_chart(fig2, use_container_width=True)
            
            # Farming recommendations based on weather
            st.subheader("🌾 Weather-Based Farming Recommendations")
            
            temp = weather_data['temperature']
            humidity = weather_data['humidity']
            
            if temp > 35:
                st.warning("🔥 High temperature alert! Consider increased irrigation and shade protection.")
            elif temp < 10:
                st.warning("❄️ Low temperature alert! Protect crops from frost damage.")
            
            if humidity > 80:
                st.warning("💧 High humidity alert! Monitor for fungal diseases.")
            elif humidity < 30:
                st.warning("🏜️ Low humidity alert! Increase irrigation frequency.")
            
            # Check for rain in forecast
            total_rain = forecast_df['rain'].sum()
            if total_rain > 50:
                st.success("🌧️ Good rainfall expected! Plan accordingly for field operations.")
            elif total_rain < 10:
                st.error("☀️ Dry period ahead! Ensure adequate water supply.")
    else:
        st.error(f"❌ Weather Error: {weather_data['error']}")
        st.info("💡 Please check your API key or location details")

elif page == "Crop Calendar":
    st.header("📅 Dynamic Crop Calendar")
    
    # Calendar inputs
    col1, col2 = st.columns(2)
    with col1:
        calendar_location = st.text_input("Location", value="Dharwad, Karnataka")
        calendar_crop = st.selectbox("Select Crop", ["Tomato", "Rice", "Wheat", "Cotton", "Maize"])
    with col2:
        calendar_season = st.selectbox("Season", seasons)
        calendar_year = st.selectbox("Year", [2024, 2025, 2026])
    
    # Generate calendar based on current weather
    if st.button("📅 Generate Smart Calendar"):
        # Get weather data for calendar planning
        city_parts = calendar_location.split(',')
        city = city_parts[0].strip()
        state = city_parts[1].strip() if len(city_parts) > 1 else "Karnataka"