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
def predict(data, device_name):
    # Prepare data for Prophet
    df_train = data[['Timestamp', 'Level']]
    df_train = df_train.rename(columns={"Timestamp": "ds", "Level": "y"})

    # Initialize and fit the model
    m = Prophet()
    m.fit(df_train)

    # Create a DataFrame for future predictions (7 days)
    future = m.make_future_dataframe(periods=7, freq='D')
    forecast = m.predict(future)

    # Display success message
    st.success("Forecasting done! Hooray!")

    # Display forecast results
    st.subheader(f'Waste Forecast for {device_name}')
    st.write(forecast[['ds', 'yhat']].tail(7).rename(columns={"ds": "Date", "yhat": "Predicted Waste Levels (cm)"}))
    
    # Show prediction graph
    fig1 = plot_plotly(m, forecast)
    st.plotly_chart(fig1)

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

    # Check if data is a dictionary with timestamps
    if isinstance(data, dict):
        try:
            data_df = pd.DataFrame([
                {
                    "Timestamp": pd.to_datetime(int(ts), unit='ms'), 
                    "Level": float(level_data['value']) if 'value' in level_data else None
                }
                for ts, level_data in data.items()
            ])
            data_df.dropna(subset=['Level'], inplace=True)  # Drop rows where Level is None
            return data_df
        except Exception as e:
            st.error(f"Data format error: {e}")
            return None
    elif isinstance(data, (int, float)):
        st.error("Expected timeseries data, but received a single value. Ensure your Firebase structure includes timestamps.")
        return None
    else:
        st.error("No data found or data format is unsupported.")
        return None

########### Streamlit app setup ################
st.set_page_config(layout='wide')
st.title('Waste Forecasting')

# Device Selection
selected_device_name = st.selectbox("Select a device", list(device_id_mapping.keys()))

# Begin forecast when user presses the button
if st.button("Forecast Now!"):
    with st.spinner("Fetching data and forecasting..."):
        device_id = device_id_mapping[selected_device_name]
        data = fetch_timeseries(device_id)
        
        if data is not None:
            predict(data, selected_device_name)
