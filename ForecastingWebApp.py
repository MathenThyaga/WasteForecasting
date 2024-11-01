import streamlit as st
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly
import json
import firebase_admin
from firebase_admin import credentials, db
from sklearn.metrics import mean_absolute_error, mean_squared_error
import math

# Initialize Firebase using Streamlit secrets
if not firebase_admin._apps:
    firebase_creds = dict(st.secrets["firebase"])
    cred = credentials.Certificate(firebase_creds)
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_creds["databaseURL"]
    })

# Device ID mapping (Firebase device names and IDs)
device_id_mapping = {
    "Level Sensor 1": "1",
    "Level Sensor 2": "2",
    "Level Sensor 3": "3",
    "Level Sensor 4": "4",
    "Level Sensor 5": "5",
    "Level Sensor 6": "6",
    "Level Sensor 7": "7",
    "Level Sensor 8": "8",
    "Level Sensor 9": "9",
    "Level Sensor 10": "10",
    "Level Sensor 11": "11",
    "Level Sensor 12": "12",
    "Level Sensor 13": "13"
}

# Function to run the forecast and plot graph
def predict(data, device_name, forecast_period):
    # Prepare data for Prophet
    df_train = data[['Timestamp', 'Level']]
    df_train = df_train.rename(columns={"Timestamp": "ds", "Level": "y"})

    # Initialize and fit the model
    m = Prophet()
    m.fit(df_train)

    # Create a DataFrame for future predictions
    future = m.make_future_dataframe(periods=forecast_period, freq='D')
    forecast = m.predict(future)

    # Display success message
    st.success("Forecasting done! Hooray!")

    # Display forecast results
    st.subheader(f'Waste Forecast for {device_name}')
    st.write(forecast[['ds', 'yhat']].tail(forecast_period).rename(columns={"ds": "Date", "yhat": "Predicted Waste Levels (cm)"}))
    
    # Show prediction graph with full width
    fig1 = plot_plotly(m, forecast)
    st.plotly_chart(fig1, use_container_width=True)

    # Calculate performance metrics
    y_true = data['Level']
    y_pred = forecast['yhat'][:len(y_true)]
    MAE = mean_absolute_error(y_true, y_pred)
    RMSE = math.sqrt(mean_squared_error(y_true, y_pred))

    st.subheader('Performance Metrics of the Forecast')
    st.write(f'Mean Absolute Error: {MAE}')
    st.write(f'Root Mean Squared Error: {RMSE}')

# Function to fetch timeseries data from Firebase Realtime Database
@st.cache_data
def fetch_timeseries(device_id):
    ref = db.reference(f'Devices/Level Sensor {device_id}/Level')
    data = ref.get()

    if isinstance(data, dict):
        try:
            # Extract each timestamp and the associated Level value
            data_df = pd.DataFrame([
                {"Timestamp": pd.to_datetime(int(ts), unit='ms'), "Level": float(level["Value"])}
                for ts, level in data.items() if "Value" in level
            ])
            # Check if we have enough data points
            if len(data_df) < 2:
                st.error("Not enough data points for forecasting. Please add more data for this device.")
                return None
            return data_df
        except Exception as e:
            st.error(f"Data format error: {e}")
            return None
    else:
        st.error("No data found or data format is unsupported.")
        return None

########### Streamlit app setup ################
st.set_page_config(layout='wide')
st.title('Waste Forecasting')

# Device Selection
selected_device_name = st.selectbox("Select a device", list(device_id_mapping.keys()))

# Forecast Period Selection
forecast_period = st.selectbox("Select forecast period", ["1 Week", "1 Month", "1 Year"])
period_mapping = {"1 Week": 7, "1 Month": 30, "1 Year": 365}
forecast_period_days = period_mapping[forecast_period]

# Begin forecast when user presses the button
if st.button("Forecast Now!"):
    with st.spinner("Fetching data and forecasting..."):
        device_id = device_id_mapping[selected_device_name]
        data = fetch_timeseries(device_id)
        
        if data is not None:
            st.write("Data to be used for forecasting:")
            st.dataframe(data)
            predict(data, selected_device_name, forecast_period_days)
