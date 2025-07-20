# Smart-Agriculture-Advisor
 Smart Agriculture Advisor – An AI-powered, real-time farming assistant for Indian farmers that provides crop advisory, dynamic market analysis, weather forecasting, and smart crop calendars using Google Gemini LLM, OpenWeatherMap, and visual dashboards built with Streamlit and Plotly
AI-Powered Decision Support System for Indian Farmers

This is a Streamlit-based Smart Agriculture Advisor that integrates real-time weather forecasting, dynamic market price monitoring, and LLM-powered crop advisory using Gemini 2.5 to support intelligent farming decisions in India.


Smart Agriculture Advisor is an intelligent, real-time farming decision support system built using Streamlit, LangChain with Gemini 2.5, and OpenWeatherMap APIs. Tailored for Indian farmers, it helps choose optimal crops, manage farm operations, and maximize profitability through:

    🌦️ Live Weather Monitoring (current & 5-day forecast)

    📉 Market Price Analysis with visual trends

    🌱 AI-generated Crop Advisory based on farmer inputs

    🗓️ Dynamic Crop Calendar adjusted for season, location & rainfall

------------------------------------------------------------

🔧 Features

| Feature                  | Description                                                                 |
|--------------------------|-----------------------------------------------------------------------------|
| 🌱 Crop Advisory         | Personalized recommendations based on weather, soil, market prices, land size, pH, and water source. |
| 💰 Market Analysis       | Real-time and historical crop price data with trend visualization and market insights. |
| 🌤️ Weather Insights      | 5-day weather forecast, real-time conditions, and climate-based recommendations for farming practices. |
| 📅 Dynamic Crop Calendar | Season and crop-specific calendar with weather-informed schedules and action points. |

------------------------------------------------------------

🚀 Tech Stack

- Frontend: Streamlit
- LLM: Google Gemini Pro (via langchain_google_genai)
- Weather API: OpenWeatherMap (Current + Forecast)
- Market Data: Simulated/Mocked (AgMarkNet/eNAM compatible)
- Visualization: Plotly
- Data Handling: Pandas

------------------------------------------------------------

🧠 How It Works

1. Users input details like crop category, farm size, soil type, season, and location.
2. The app fetches real-time weather and market price data.
3. A Gemini-powered LLM generates detailed crop advisory reports based on the user's context and live data.
4. Visualizations (bar and line charts) support market trend analysis and rainfall forecasting.

------------------------------------------------------------

📦 Installation

git clone https://github.com/yourusername/smart-agriculture-advisor.git
cd smart-agriculture-advisor
pip install -r requirements.txt

Create a .env file (or set environment variables) with:

GOOGLE_API_KEY=your_google_gemini_api_key
WEATHER_API_KEY=your_openweather_api_key
MARKET_API_KEY=your_market_api_key

------------------------------------------------------------

🏁 Run the App

streamlit run app.py

------------------------------------------------------------

📸 Screenshots

- Crop Advisory Report
- Market Price Trends
- Weather Insights

------------------------------------------------------------

🧪 Example Use Case

A farmer in Dharwad, Karnataka wants to grow Tomato on 2 acres during Kharif. The app:
- Fetches weather & market prices for Dharwad.
- Analyzes inputs (e.g., soil, water, season, pH).
- Uses Gemini to generate a 15-point comprehensive advisory with profitability analysis.

------------------------------------------------------------

✅ To-Do / Future Enhancements

- Integrate real AgMarkNet or eNAM APIs
- Add pest/disease prediction using image upload
- Include satellite imagery for NDVI/Soil Health Mapping
- Build WhatsApp or SMS Bot for rural farmers
- Deploy as a mobile/web PWA

------------------------------------------------------------

📄 License

MIT License – feel free to use, modify, and share!

------------------------------------------------------------

🤝 Acknowledgements

- LangChain
- Google Gemini API
- OpenWeatherMap
- AgMarkNet
- Indian farming community 🧑‍🌾 for inspiring this innovation
