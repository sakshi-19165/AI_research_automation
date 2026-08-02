import requests


def fetch_weather():
    
    url = "https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278&current_weather=true"

    response = requests.get(url)
    data = response.json()  # Always returns a dictionary

    # Pull out current weather data
    current = data["current_weather"]

    print("Data is here ")
    print(f"Temperature : {current['temperature']}°C")
    print(f"Wind Speed  : {current['windspeed']} km/h")


if __name__ == "__main__":
    fetch_weather()