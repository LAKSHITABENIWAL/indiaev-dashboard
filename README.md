# indiaev-dashboard
# India EV Market Dashboard

An interactive Streamlit dashboard to analyze and visualize the growth of the electric vehicle (EV) market in India (2001–2024). This project provides insights into sales trends, manufacturer performance, infrastructure, policy impact, and future forecasts using real data and advanced analytics.

Key metrics and trends in EV sales, revenue, and growth rates
Interactive visualizations including line charts, bar charts, pie charts, and maps
Manufacturer and state-wise analysis of EV adoption and infrastructure
Forecasting tools using machine learning and time series models to predict future EV sales
Policy impact analysis to show how government initiatives (like FAME-II) have influenced EV adoption
Customizable UI with light/dark mode and modern sidebar navigation
---

## 🚗 Features

- **Dashboard:** Key metrics, sales trends, and revenue estimates for different EV categories.
- **Visualizations:** Interactive charts for sales, manufacturer analysis, state-wise adoption, vehicle class insights, and more.
- **Forecast:** Predict future EV sales using machine learning and time series models (Linear Regression, Random Forest, Neural Network, ARIMA, Prophet).
- **Summary:** Executive summary of India's EV market evolution, key segments, and future outlook.
- **EV Policy Impact:** Visualizes the effect of major government policies (like FAME-II) on EV adoption.
- **Dark/Light Mode:** Modern UI with sidebar navigation and theme toggle.

---

## 📊 Tech Stack

- [Streamlit](https://streamlit.io/) (dashboard & UI)
- [Pandas](https://pandas.pydata.org/) (data analysis)
- [Plotly](https://plotly.com/python/) (interactive charts)
- [Scikit-learn](https://scikit-learn.org/) (ML models)
- [Prophet](https://facebook.github.io/prophet/) & [ARIMA](https://www.statsmodels.org/) (time series forecasting)
- [GeoJSON](https://geojson.org/) (state-wise mapping)

---

## 📁 Data Sources

- EV manufacturer and sales data (CSV)
- Public charging station data (CSV)
- Vehicle registration data (CSV)
- India state boundaries (GeoJSON)

---

## 🚀 How to Run Locally

1. **Clone the repo:**
    ```sh
    git clone https://github.com/YOUR_USERNAME/indiaev-dashboard.git
    cd indiaev-dashboard
    ```

2. **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Add data files:**
    - Place `ev_maker.csv`, `ev_sales.csv`, `OperationalPC.csv`, `vehicleclass.csv`, and `india_state.geojson` in the project folder.

4. **Run the app:**
    ```sh
    streamlit run app.py
    ```

---

## 🌐 Deploy on Streamlit Cloud

1. Push your code to GitHub.
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud), sign in, and create a new app from your repo.
3. Set `app.py` as the main file and deploy!

---

## 📸 Screenshots

![Dashboard Screenshot](https://user-images.githubusercontent.com/your-screenshot.png)

---

## ✍️ Author

- [Your Name](https://github.com/YOUR_USERNAME)

---

## 📄 License

This project is for educational and demonstration purposes.

---

## ⭐️ Acknowledgements

- Open-source datasets and the Streamlit community.
