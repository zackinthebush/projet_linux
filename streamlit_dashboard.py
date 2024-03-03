import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
from datetime import datetime
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
import plotly.graph_objs as go

# MongoDB setup (same as before)
client = MongoClient('localhost', 27017)
db = client['financial_data']
collection = db['cac_40_summary']
update_tracker = db['update_tracker']


def fetch_data():
    """
    Fetches data from MongoDB and returns it as a Pandas DataFrame.
    """
    data = collection.find()  # This fetches all documents in the collection
    df = pd.DataFrame(list(data))
    return df

def check_for_updates():
    """
    Checks if the data has been updated since the last fetch.
    """
    last_update = update_tracker.find_one(sort=[("timestamp", -1)])
    if last_update:
        last_update_time = last_update['timestamp']
        # Compare with the stored fetch timestamp
        last_fetch_time = st.session_state.get('last_fetch_time', datetime.min)
        return last_update_time > last_fetch_time
    return False

def plot_data(df):
    """
    Plots the data using Plotly.
    """
    # Ensure the DataFrame is sorted by date
    df.sort_values('file_date', inplace=True)
    
    # Plotting
    fig = px.line(df, x='file_date', y='average_close', title='CAC 40 Average Close Prices Over Time')
    return fig
    
def plot_decomposition(df, column='average_close', period=12):
    """
    Decomposes the time series and plots the components.
    :param df: DataFrame containing the time series data.
    :param column: The column name of the series to decompose.
    :param period: The number of observations per cycle (e.g., 12 for monthly data with yearly seasonality).
    """
    # Ensure the DataFrame is in proper format
    df['file_date'] = pd.to_datetime(df['file_date'])
    df.set_index('file_date', inplace=True, drop=False)
    df.sort_index(inplace=True)  # Sort by date if not already sorted

    # Check if there's enough data
    if len(df) < 2 * period:
        st.error(f"Not enough data for decomposition. Required: {2 * period}, Available: {len(df)}")
        return None

    # Decomposing
    decomposed = seasonal_decompose(df[column], model='additive', period=period)
    
    # Plotting
    trace1 = go.Scatter(x=decomposed.trend.index, y=decomposed.trend, mode='lines', name='Trend')
    trace2 = go.Scatter(x=decomposed.seasonal.index, y=decomposed.seasonal, mode='lines', name='Seasonal')
    trace3 = go.Scatter(x=decomposed.resid.index, y=decomposed.resid, mode='lines', name='Residual')
    
    fig = go.Figure(data=[trace1, trace2, trace3])
    fig.update_layout(title='Time Series Decomposition', xaxis_title='Date', yaxis_title=column)
    
    return fig

    
def plot_arima_forecast(df, column='average_close', p=1, d=1, q=1, steps=12):
    """
    Fits an ARIMA model and forecasts future values.
    :param df: DataFrame containing the time series data.
    :param column: The column name of the series to forecast.
    :param p: The order of the AR term.
    :param d: The order of differencing.
    :param q: The order of the MA term.
    :param steps: Number of steps ahead to forecast.
    """
    # Fit ARIMA model
    model = ARIMA(df[column], order=(p, d, q))
    results = model.fit()
    
    # Forecast
    forecast = results.forecast(steps=steps)
    
    # Plotting
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df[column], mode='lines', name='Actual'))
    fig.add_trace(go.Scatter(x=forecast.index, y=forecast, mode='lines', name='Forecast'))
    fig.update_layout(title='ARIMA Forecast', xaxis_title='Date', yaxis_title=column)
    
    return fig



# Streamlit app
def main():
    st.title('CAC 40 Data Visualization')
    
    # Check for updates and fetch data
    if 'df' not in st.session_state or check_for_updates():
        st.session_state.df = fetch_data()
        st.session_state.last_fetch_time = datetime.now()

    df = st.session_state.df
    
    if not df.empty:
        # Decomposition Plot
        if st.button('Show Decomposition'):
            fig_decomp = plot_decomposition(df)
            st.plotly_chart(fig_decomp)
        
        # ARIMA Forecast
        if st.button('Show ARIMA Forecast'):
            fig_arima = plot_arima_forecast(df)
            st.plotly_chart(fig_arima)
    else:
        st.write("No data available.")

if __name__ == "__main__":
    main()

    
   

