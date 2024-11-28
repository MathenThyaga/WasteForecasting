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

# Plot forecasted values with a thicker line and a standout color
fig.add_trace(go.Scatter(
    x=forecasted_data['ds'], 
    y=forecasted_data['yhat'], 
    mode='lines+markers', 
    name='Forecasted Values',
    line=dict(color='red', width=4, dash='dot'),
    marker=dict(size=6, color='red')  # Larger markers for better visibility
))

# Optionally add confidence intervals for forecasted values
fig.add_trace(go.Scatter(
    x=pd.concat([forecasted_data['ds'], forecasted_data['ds'][::-1]]),
    y=pd.concat([forecasted_data['yhat_upper'], forecasted_data['yhat_lower'][::-1]]),
    fill='toself',
    fillcolor='rgba(255, 99, 71, 0.2)',  # Light red fill for confidence intervals
    line=dict(color='rgba(255,255,255,0)'),
    showlegend=True,
    name='Confidence Interval'
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
