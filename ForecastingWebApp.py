import streamlit as st
import pandas as pd
from prophet import Prophet
import plotly.graph_objects as go
from firebase_admin import credentials, db
import firebase_admin
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
            # Remove outliers (values significantly above or below expected range)
            data_df = data_df[(data_df["Level"] >= 0) & (data_df["Level"] <= 100)]
            # Ensure enough data points are available
            if len(data_df) < 20:
                st.error("Not enough data points for accurate forecasting. Please add more data.")
                return None
            return data_df.sort_values("Timestamp")
        except Exception as e:
            st.error(f"Data format error: {e}")
            return None
    else:
        st.error("No data found or data format is unsupported.")
        return None

# Function to run the forecast and plot graph
def predict(data, device_name, forecast_period):
    # Prepare data for Prophet
    df_train = data[['Timestamp', 'Level']].rename(columns={"Timestamp": "ds", "Level": "y"})

    # Initialize and configure the Prophet model
    m = Prophet(
        seasonality_mode='multiplicative',  # Better for large fluctuations
        changepoint_prior_scale=0.5,  # Make trend detection more flexible
    )
    # Add custom weekly seasonality
    m.add_seasonality(name='weekly', period=7, fourier_order=3)
    m.fit(df_train)

    # Create a DataFrame for future predictions
    future = m.make_future_dataframe(periods=forecast_period, freq='D')
    forecast = m.predict(future)

    # Split data into historical and forecast
    historical_data = df_train
    forecasted_data = forecast[forecast['ds'] > historical_data['ds'].max()]

    # Calculate performance metrics
    y_true = historical_data['y']
    y_pred = forecast.loc[:len(y_true) - 1, 'yhat']
    MAE = mean_absolute_error(y_true, y_pred)
    RMSE = math.sqrt(mean_squared_error(y_true, y_pred))

    # Display performance metrics and warn if above threshold
    st.subheader('Performance Metrics of the Forecast')
    st.write(f'Mean Absolute Error (MAE): {MAE:.2f}')
    st.write(f'Root Mean Squared Error (RMSE): {RMSE:.2f}')
    if MAE > 20 or RMSE > 20:
        st.warning("The forecast error is above acceptable thresholds. Consider refining the data or model parameters.")

    # Plot historical values
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=historical_data['ds'], 
        y=historical_data['y'], 
        mode='lines+markers', 
        name='Historical Values',
        line=dict(color='blue'),
        marker=dict(size=4)
    ))

    # Plot forecasted values with a straight black line
    fig.add_trace(go.Scatter(
        x=forecasted_data['ds'], 
        y=forecasted_data['yhat'], 
        mode='lines+markers', 
        name='Forecasted Values',
        line=dict(color='black', width=4),
        marker=dict(size=6, color='black')
    ))

    # Update layout for clarity
    fig.update_layout(
        title=f"Waste Level Forecast for {device_name}",
        xaxis_title="Date",
        yaxis_title="Waste Levels (cm)",
        template="plotly_white",
        showlegend=True
    )

    # Show the plot
    st.plotly_chart(fig, use_container_width=True)

    # Display forecast results for the forecast period
    st.subheader(f'Waste Forecast for {device_name}')
    st.write(forecasted_data[['ds', 'yhat']].rename(columns={"ds": "Date", "yhat": "Predicted Waste Levels (cm)"}))

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
