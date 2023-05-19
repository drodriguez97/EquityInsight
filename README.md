# Equity Insight Application CS 4620

Submitted by: **Daniel Rodriguez**

The Equity Insight Application is a web-based tool designed to assist users in managing their investment portfolios and gaining insights into stock performance. The application allows users to register, create portfolios, add stocks to their portfolios, and view current stock prices and predictions.

## Video Walkthrough

Here's a walkthrough of implemented required features:

<img src='public\equity.gif' title='Video Walkthrough' width='' alt='Video Walkthrough' />

<!-- Replace this with whatever GIF tool you used! -->
GIF created with   
<!-- Recommended tools:
[Kap](https://getkap.co/) for macOS
[ScreenToGif](https://www.screentogif.com/) for Windows
[peek](https://github.com/phw/peek) for Linux. -->

## Key Features

- User Registration: Users can register with their email and password to access the application.
- Portfolio Management: Users can create portfolios, add stocks to their portfolios, and view the total value of their portfolios.
- Stock Selection: Users can select stocks from a predefined list and view their current prices and historical performance.
- Stock Price Predictions: Users can choose a stock and predict its future price using the Prophet library.
- Data Visualization: The application provides interactive charts to visualize stock prices and forecasted trends.

## Technologies Used

The Equity Insight Application is built using the following technologies:

- Python
- Streamlit: A Python library for building interactive web applications
- yfinance: A library for retrieving financial data from Yahoo Finance
- Prophet: A library for time series forecasting developed by Facebook
- Firebase: A cloud-based platform for building web and mobile applications

## Setup Instructions

To run the Equity Insight Application locally, follow these steps:

1. Clone the repository: `git clone https://github.com/drodriguez97/EquityInsight`
2. Obtain the necessary API keys and credentials for Firebase and Yahoo 
3. 2. Install the required dependencies: `pip install -r requirements.txt`Finance.
4. Replace the placeholders in the code with your API keys and credentials.
5. Run the application: `streamlit run main.py`

## Contributing

Contributions to the Equity Insight Application are welcome! If you find any bugs, have feature requests, or want to contribute improvements, please open an issue or submit a pull request.

## License

    Copyright [2023] [Daniel Rodriguez]

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.