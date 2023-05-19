import creds
import pandas as pd
import streamlit as st
from datetime import date
import yfinance as yf


from prophet import Prophet
from prophet.plot import plot_plotly
from plotly import graph_objs as go

import firebase_admin
from firebase_admin import db
from firebase_admin import auth
from firebase_admin import credentials, firestore

############### FIREBASE INIT ###############################################################
cred = credentials.Certificate("equityinsight-c9145-firebase-adminsdk-ui9df-231da079b7.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

############### APPLICATION BODY ###########################################################
START = "2015-01-01"
TODAY = date.today().strftime("%Y-%m-%d")

st.image("equity.png", use_column_width=True)
st.info('The purpose of this application is to allow the user to select any of the top 10 performing stocks and look at current performance values but also a stock price prediction')

stocks = {
    'GOOG': 'Alphabet Inc. - Class C',
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'AMD': 'Advanced Micro Devices, Inc.',
    'NVDA': 'NVIDIA Corporation',
    'META': 'Facebook Inc.',
    'NFLX': 'Netflix',
    'AMZN': "Amazon"
}

st.markdown('#') 
############### USER REGISTRATION ###########################################################

st.header(':blue[User Registration]')
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Register"):
    # Create a test user
    try:
        user = auth.create_user(
            email=email,
            password=password,
        )
        st.success("Test user created successfully!")
        st.write("User ID:", user.uid)
    except Exception as e:
        st.error(f"Error creating test user: {e}")   
                 

st.markdown('#') 

##### PORTFOLIO CREATION ############################################################################
st.header(':blue[Portfolio Management]')

portfolio = []
user_id = st.text_input("Enter User ID:")
portfolio_name = st.text_input("Enter Portfolio Name:")

if st.button("Create Portfolio"):
    portfolio_ref = db.collection('portfolios').document(user_id)
    portfolio_data = {
        'name': portfolio_name,
        'stocks': [],
        'created_at': firestore.SERVER_TIMESTAMP
    }
    portfolio_ref.set(portfolio_data)
    st.success("Portfolio created successfully!")
st.markdown('###') 
################################################################################################


#Title
st.subheader('Currently Selected Stock Price and Symbol')

#show stock selection
select_stock = st.selectbox('Select stock you want to be added to your portfolio', stocks)

###########CURRENTLY SELECTED #####################################################
# Plot current price
st.subheader('Price/Symbol of Currently Selected Stock')


#get stock data from YahooFinance
data = yf.Ticker(select_stock)
history = data.history(period="1wk")

current_price = round(data.history(period='1d')['Close'].iloc[-1], 2)
st.write(f"Currently Selected:  **{select_stock}**")
st.write(f"Current Price:  **{current_price}**")


# Create a line graph using Plotly
fig1 = go.Figure(data=[go.Scatter(
    x=history.index,
    y=history['Close'],
    mode='lines',
    name=select_stock
)])

# Set the chart layout
fig1.update_layout(
    title=f"{select_stock} Stock Chart",
    xaxis_title="Date",
    yaxis_title="Price",
    template="plotly_white"  # Use the white theme for better visibility
)

st.plotly_chart(fig1)


########### ADD STOCK TO PORTFOLIO #####################################################
if "stock_amount" not in st.session_state:
    st.session_state.stock_amount = 0

stock_amount_input = st.number_input("Enter the amount of stock to add", min_value=0)
total_value = current_price * stock_amount_input
st.subheader(f"Total Value: {total_value}")

if st.button("Add Stock to Portfolio"):
    portfolio_ref = db.collection('portfolios').document(user_id)
    portfolio_ref.update({'stocks': firestore.ArrayUnion([select_stock])})
    portfolio_ref.update({'total_value': firestore.Increment(total_value)})  # Update total value
    st.session_state.stock_amount = stock_amount_input
    st.success("Stock added to portfolio!")
    
########## DISPLAY PORTFOLIO #####################################################            
st.header(':blue[Portfolio]')

if user_id:
    portfolio_ref = db.collection('portfolios').document(user_id)
    portfolio_data = portfolio_ref.get().to_dict()
    if portfolio_data:
        stocks = portfolio_data.get('stocks', [])
        for stock in stocks:
            st.write(f"Stock: {stock}")
            st.write(f"Number of Shares: {stock_amount_input}")
            
            # Fetch historical data for one week
            stock_data = yf.Ticker(stock)
            stock_history = stock_data.history(period='1mo')
            
            # Create a line graph using Plotly
            fig = go.Figure(data=go.Scatter(
                x=stock_history.index,
                y=stock_history['Close'],
                mode='lines',
                name='Close'
            ))

            # Set the chart layout
            fig.update_layout(
                title=f"{stock} Stock Chart",
                xaxis_title="Date",
                yaxis_title="Price",
                template="plotly_white"  # Use the white theme for better visibility
            )

            # Display the stock chart
            st.plotly_chart(fig)
            
    else:
        st.write("No portfolio found for the given User ID")
        
# Display total value        
if portfolio_name:
    total_value = portfolio_data.get('total_value', 0)
    st.subheader(f"Total Value: {total_value}")

################## REMOVE STOCK FROM PORTFOLIO ###########################################################

stocks_to_remove = st.multiselect("Select stocks to remove", stocks)

if st.button("Remove Selected Stocks from Portfolio"):
    portfolio_ref = db.collection('portfolios').document(user_id)
    for stock in stocks_to_remove:
        portfolio_ref.update({'stocks': firestore.ArrayRemove([stock])})
        # Retrieve the current price of the stock
        stock_data = yf.Ticker(stock)
        current_price = stock_data.history(period='1d')['Close'].iloc[-1]
        # Calculate the value to subtract from the total portfolio value
        stock_value = current_price * stock_amount_input
        portfolio_ref.update({'total_value': firestore.Increment(-stock_value)})  # Subtract stock value from total value
    st.success("Selected stocks removed from portfolio!")

# Remove the stock graphs from the portfolio display
for stock in stocks_to_remove:
    st.markdown(f"Removed {stock} from Portfolio")

st.markdown('###')
##### STOCK PRICE PREDITIONS ############################################################################

test_stocks = {
    'GOOG': 'Alphabet Inc. - Class C',
    'AAPL': 'Apple Inc.',
    'MSFT': 'Microsoft Corporation',
    'AMD': 'Advanced Micro Devices, Inc.',
    'NVDA': 'NVIDIA Corporation',
    'META': 'Facebook Inc.',
    'NFLX': 'Netflix',
    'AMZN': "Amazon"
}

st.header(":blue[Stock Price Predictions]")

selected_stock = st.selectbox('Select dataset for prediction', test_stocks)

n_years = st.slider('Years of prediction:', 1, 4)
period = n_years * 365

@st.cache_data
def load_data(ticker):
    data = yf.download(ticker, START, TODAY)
    data.reset_index(inplace=True)
    return data


data_load_state = st.text('Loading data...')
data = load_data(selected_stock)
data_load_state.text('Loading data... done!')

st.subheader('Raw data')
st.write(data.tail())

# Plot raw data
def plot_raw_data():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Open'], name="stock_open"))
    fig.add_trace(go.Scatter(x=data['Date'], y=data['Close'], name="stock_close"))
    fig.layout.update(title_text='Time Series data with Rangeslider', xaxis_rangeslider_visible=True)
    st.plotly_chart(fig)

plot_raw_data()

# Predict forecast with Prophet
df_train = data[['Date','Close']]
df_train = df_train.rename(columns={"Date": "ds", "Close": "y"})

m = Prophet()
m.fit(df_train)
future = m.make_future_dataframe(periods=period)
forecast = m.predict(future)

# Show and plot forecast
st.subheader('Forecast data')
st.write(forecast.tail())

st.write(f'Forecast plot for {n_years} years')
fig1 = plot_plotly(m, forecast)
st.plotly_chart(fig1)

st.write("Forecast components")
fig2 = m.plot_components(forecast)
st.write(fig2)\
    
st.markdown("---")
st.markdown("Developed by [Daniel Rodriguez]")
st.markdown("[GitHub Repository](https://github.com/your/repo)")