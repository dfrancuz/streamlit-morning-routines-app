import os
import requests

# Function to get weather forecast for a given city
def get_forecast(city: str):
    api_key = os.environ.get("WEATHER_API_KEY")
    base_url = os.environ.get("WEATHER_BASE_URL")
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    return response.json()

# Function to get currency exchange rate between base and target currency
def get_exchange_rate(base_currency, target_currency):
    api_key = os.environ.get("CURRENCY_API_KEY")
    base_url = os.environ.get("CURRENCY_BASE_URL")
    complete_url = f'{base_url}/latest?apikey={api_key}&base_currency={base_currency}'
    response = requests.get(complete_url)
    data = response.json()

    if response.status_code == 200:
        if 'data' in data and target_currency in data['data']:
            exchange_rate = data['data'][target_currency]['value']
            return exchange_rate
    else:
        return None
