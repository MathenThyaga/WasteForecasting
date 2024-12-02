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
            data_df = pd.DataFrame([{
                "Timestamp": pd.to_datetime(int(ts), unit='ms'), 
                "Level": float(level["Value"])
            } for ts, level in data.items() if "Value" in level])

            # Remove outliers and smooth noisy data
            q1 = data_df["Level"].quantile(0.25)
            q3 = data_df["Level"].quantile(0.75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            data_df = data_df[(data_df["Level"] >= max(0, lower_bound)) & (data_df["Level"] <= min(100, upper_bound))]
            # Smooth data using rolling average
            data_df["Level"] = data_df["Level"].rolling(window=5, min_periods=1).mean()

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

# Function to apply reset logic to forecasted values (as per your referenced code)
def apply_reset_logic(forecasted_values, reset_threshold=100):
    adjusted_values = []
    current_level = 0  # Starting point for level

    for value in forecasted_values:
        current_level += value
        if current_level >= reset_threshold:
            current_level = current_level - reset_threshold  # Reset if threshold exceeded
        adjusted_values.append(current_level)

    return adjusted_values

# Function to run the forecast, calculate metrics, and plot graph
def predict(data, device_name, forecast_period):
    # Prepare data for Prophet
    df_train = data[['Timestamp', 'Level']].rename(columns={"Timestamp": "ds", "Level": "y"})

    # Initialize and configure the Prophet model
    m = Prophet(
        seasonality_mode='multiplicative',  # Better for large fluctuations
        changepoint_prior_scale=0.1,  # Increased sensitivity to changes
        yearly_seasonality=True
    )
    m.add_seasonality(name='weekly', period=7, fourier_order=5)
    m.add_seasonality(name='daily', period=1, fourier_order=3)
    m.fit(df_train)

    # Create a DataFrame for future predictions
    future = m.make_future_dataframe(periods=forecast_period, freq='D')
    forecast = m.predict(future)

    # Calculate performance metrics
    y_true = df_train['y']
    y_pred = forecast.loc[:len(y_true) - 1, 'yhat']
    MAE = mean_absolute_error(y_true, y_pred)
    RMSE = math.sqrt(mean_squared_error(y_true, y_pred))

    # Display performance metrics
    st.subheader('Performance Metrics of the Forecast')
    st.write(f'Mean Absolute Error (MAE): {MAE:.2f}')
    st.write(f'Root Mean Squared Error (RMSE): {RMSE:.2f}')

    # Apply reset logic to forecasted values
    forecasted_values = forecast[forecast['ds'] > df_train['ds'].max()]['yhat'].tolist()
    adjusted_values = apply_reset_logic(forecasted_values)  # Apply reset logic here

    # Plot historical data
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_train['ds'],
        y=df_train['y'],
        mode='lines+markers',
        name='Historical Values',
        line=dict(color='blue'),
        marker=dict(size=4)
    ))

    # Plot adjusted forecasted data
    forecasted_dates = forecast[forecast['ds'] > df_train['ds'].max()]['ds']
    fig.add_trace(go.Scatter(
        x=forecasted_dates,
        y=adjusted_values,
        mode='lines+markers',
        name='Forecasted Values (With Reset Logic)',
        line=dict(color='black', width=4),
        marker=dict(size=6, color='black')
    ))

    # Update layout for clarity and y-axis range
    fig.update_layout(
        title=f"Waste Level Forecast for {device_name}",
        xaxis_title="Date",
        yaxis_title="Waste Levels (cm)",
        yaxis=dict(range=[0, 100]),  # Fix y-axis max at 100
        template="plotly_white",
        showlegend=True
    )

    # Show the plot
    st.plotly_chart(fig, use_container_width=True)

    # Display forecast results for the forecast period
    st.subheader(f'Waste Forecast for {device_name}')
    st.write(forecasted_dates)
    st.write(adjusted_values)

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
