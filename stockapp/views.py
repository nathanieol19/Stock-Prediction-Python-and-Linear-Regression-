# Import necessary libraries
import yfinance as yf
import pandas as pd
import json
import requests
import matplotlib.pyplot as plt
from django.shortcuts import render
from django.http import HttpResponse
from io import BytesIO
import base64
import os
from sklearn.linear_model import LinearRegression

# Function to download Apple stock data
def download_apple_data():
    # URL for the Apple stock data in JSON format
    url = 'https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-PY0220EN-SkillsNetwork/data/apple.json'
    
    # Make a request to the URL
    response = requests.get(url)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Save the content to a local file named 'apple.json'
        with open('apple.json', 'wb') as f:
            f.write(response.content)
    else:
        # If the request fails, return None
        return None

# Django view function for the home page
def home(request):
    # Check if the request method is POST (form submission)
    if request.method == 'POST':
        # Retrieve the number of years from the submitted form data
        number_of_years = request.POST['number_of_years']
        number_of_years_str = number_of_years + "y"

        # Check if 'apple.json' exists, and if not, download it
        if not os.path.exists('apple.json'):
            download_apple_data()

        # Read the Apple stock information from 'apple.json'
        with open('apple.json') as json_file:
            apple_info = json.load(json_file)

        # Use yfinance to get historical stock data for Apple
        apple = yf.Ticker("AAPL")
        apple_share_price_data = apple.history(period=number_of_years_str)
        apple_share_price_data.reset_index(inplace=True)

        # Create a plot of opening prices
        plt.figure(figsize=(10, 5))
        plt.plot(apple_share_price_data["Date"], apple_share_price_data["Open"])
        plt.xlabel('Date')
        plt.ylabel('Opening Price')
        plt.title('Apple Stock Opening Price')
        plt.xticks(rotation=45)
        plt.grid(True)

        # Save the plot to a BytesIO object and encode it to base64
        plot_img = BytesIO()
        plt.savefig(plot_img, format='png')
        plot_img.seek(0)
        plot_base64 = base64.b64encode(plot_img.read()).decode()

        # Perform linear regression on opening and closing prices
        X = apple_share_price_data[['Open']]
        y = apple_share_price_data[['Close']]
        model = LinearRegression()
        model.fit(X, y)

        # Predict the closing price for a future date
        last_date = apple_share_price_data['Date'].max()
        future_date = last_date + pd.DateOffset(days=5)
        predicted_close_price = model.predict([[apple_share_price_data['Open'].iloc[-1]]])

        # Render the HTML template with plot and predicted close price
        return render(request, 'stockapp/index.html', {'plot': plot_base64, 'predicted_close_price': predicted_close_price[0]})

    # If the request method is not POST, render the HTML template with no plot
    return render(request, 'stockapp/index.html', {'plot': None})
