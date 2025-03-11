import os
import json
import requests
from datetime import datetime as pydatetime, timedelta, timezone
from typing import Optional, Callable, Any, Set, Dict, List
from dotenv import load_dotenv
import random  # Add import for random module

load_dotenv()

def fetch_datetime(
    format_str: str = "%Y-%m-%d %H:%M:%S",
    unix_ts: int | None = None,
    tz_offset_seconds: int | None = None
) -> str:
    """
    Returns either the current UTC date/time in the given format, or if unix_ts
    is given, converts that timestamp to either UTC or local time (tz_offset_seconds).

    :param format_str: The strftime format, e.g. "%Y-%m-%d %H:%M:%S".
    :param unix_ts: Optional Unix timestamp. If provided, returns that specific time.
    :param tz_offset_seconds: If provided, shift the datetime by this many seconds from UTC.
    :return: A JSON string containing the "datetime" or an "error" key/value.
    """
    try:
        if unix_ts is not None:
            dt_utc = pydatetime.fromtimestamp(unix_ts, tz=timezone.utc)
        else:
            dt_utc = pydatetime.now(timezone.utc)

        if tz_offset_seconds is not None:
            local_tz = timezone(timedelta(seconds=tz_offset_seconds))
            dt_local = dt_utc.astimezone(local_tz)
            result_str = dt_local.strftime(format_str)
        else:
            result_str = dt_utc.strftime(format_str)

        return json.dumps({"datetime": result_str})
    except Exception as e:
        return json.dumps({"error": f"Exception: {str(e)}"})


def fetch_weather(
    location: str,
    country_code: str = "",
    state_code: str = "",
    limit: int = 1,
    timeframe: str = "current",
    time_offset: int = 0,
    dt_unix: Optional[int] = None
) -> str:
    """
    Fetches weather data from OpenWeather for the specified location and timeframe.

    :param location: The city or place name to look up.
    :param country_code: (optional) e.g. 'US' or 'GB' to narrow down your search.
    :param state_code: (optional) The state or province code, e.g. 'CA' for California.
    :param limit: (optional) The max number of geocoding results (defaults to 1).
    :param timeframe: The type of weather data, e.g. 'current','hourly','daily','timemachine', or 'overview'.
    :param time_offset: For 'hourly' or 'daily', used as the index into the array. For 'overview', the day offset.
    :param dt_unix: A Unix timestamp, required if timeframe='timemachine'.
    :return: A JSON string containing weather data or an "error" key if an issue.
    """
    try:
        if not location:
            return json.dumps({"error": "Missing required parameter: location"})

        geo_api_key = os.environ.get("OPENWEATHER_GEO_API_KEY")
        one_api_key = os.environ.get("OPENWEATHER_ONE_API_KEY")
        if not geo_api_key or not one_api_key:
            return json.dumps({"error": "Missing OpenWeather API keys in environment."})

        # Convert location -> lat/lon:
        if country_code and state_code:
            query = f"{location},{state_code},{country_code}"
        elif country_code:
            query = f"{location},{country_code}"
        else:
            query = location

        geocode_url = (
            f"http://api.openweathermap.org/geo/1.0/direct?"
            f"q={query}&limit={limit}&appid={geo_api_key}"
        )
        geo_resp = requests.get(geocode_url)
        if geo_resp.status_code != 200:
            return json.dumps({
                "error": "Geocoding request failed",
                "status_code": geo_resp.status_code,
                "details": geo_resp.text
            })

        geocode_data = geo_resp.json()
        if not geocode_data:
            return json.dumps({"error": f"No geocoding results for '{location}'."})

        lat = geocode_data[0].get("lat")
        lon = geocode_data[0].get("lon")
        if lat is None or lon is None:
            return json.dumps({"error": "No valid lat/long returned."})

        tf = timeframe.lower()
        if tf == "timemachine":
            if dt_unix is None:
                return json.dumps({
                    "error": "For timeframe='timemachine', you must provide 'dt_unix'."
                })
            url = (
                f"https://api.openweathermap.org/data/3.0/onecall/timemachine"
                f"?lat={lat}&lon={lon}"
                f"&dt={dt_unix}"
                f"&units=metric"
                f"&appid={one_api_key}"
            )
        elif tf == "overview":
            date_obj = pydatetime.utcnow() + timedelta(days=time_offset)
            date_str = date_obj.strftime("%Y-%m-%d")
            url = (
                f"https://api.openweathermap.org/data/3.0/onecall/overview?"
                f"lat={lat}&lon={lon}"
                f"&date={date_str}"
                f"&units=metric"
                f"&appid={one_api_key}"
            )
        else:
            if tf == "current":
                exclude = "minutely,hourly,daily,alerts"
            elif tf == "hourly":
                exclude = "minutely,daily,alerts"
            elif tf == "daily":
                exclude = "minutely,hourly,alerts"
            else:
                exclude = ""

            url = (
                f"https://api.openweathermap.org/data/3.0/onecall?"
                f"lat={lat}&lon={lon}"
                f"&exclude={exclude}"
                f"&units=metric"
                f"&appid={one_api_key}"
            )

        resp = requests.get(url)
        if resp.status_code != 200:
            return json.dumps({
                "error": "Weather API failed",
                "status_code": resp.status_code,
                "details": resp.text
            })

        data = resp.json()
        if tf == "overview":
            overview = data.get("weather_overview", "No overview text provided.")
            return json.dumps({
                "location": location,
                "latitude": lat,
                "longitude": lon,
                "weather_overview": overview,
                "description": "N/A",
                "temperature_c": "N/A",
                "temperature_f": "N/A",
                "humidity_percent": "N/A",
            })

        if tf == "timemachine":
            arr = data.get("data", [])
            if not arr:
                return json.dumps({"error": "No 'data' array for timemachine"})
            sel = arr[0]
        elif tf == "hourly":
            arr = data.get("hourly", [])
            if time_offset < 0 or time_offset >= len(arr):
                return json.dumps({
                    "error": f"Requested hour index {time_offset}, but length is {len(arr)}"
                })
            sel = arr[time_offset]
        elif tf == "daily":
            arr = data.get("daily", [])
            if time_offset < 0 or time_offset >= len(arr):
                return json.dumps({
                    "error": f"Requested day index {time_offset}, but length is {len(arr)}"
                })
            sel = arr[time_offset]
        else:
            sel = data.get("current", {})

        if not isinstance(sel, dict):
            return json.dumps({"error": f"Unexpected data format for timeframe={timeframe}"})

        description = "N/A"
        if sel.get("weather"):
            description = sel["weather"][0].get("description", "N/A")

        temp_c = sel.get("temp")
        humidity = sel.get("humidity", "N/A")
        if isinstance(temp_c, (int, float)):
            temp_f = round(temp_c * 9 / 5 + 32, 2)
        else:
            temp_f = "N/A"

        result = {
            "location": location,
            "latitude": lat,
            "longitude": lon,
            "description": description,
            "temperature_c": temp_c if temp_c is not None else "N/A",
            "temperature_f": temp_f,
            "humidity_percent": humidity,
        }
        return json.dumps(result)
    except Exception as e:
        return json.dumps({"error": f"Exception occurred: {str(e)}"})


def fetch_currency_exchange_rate(
    from_currency: str,
    to_currency: str,
    date: Optional[str] = None
) -> str:
    """
    Fetches the exchange rate for a given currency pair.

    :param from_currency: The currency code to convert from, e.g. "USD".
    :param to_currency: The currency code to convert to, e.g. "EUR".
    :param date: (optional) The date in YYYY-MM-DD format. If not provided, uses the current date.
    :return: A JSON string containing the exchange rate or an "error" key if an issue.
    """
    try:
        if not from_currency or not to_currency:
            return json.dumps({"error": "Missing required parameters: from_currency and to_currency must be provided"})

        # Retrieve the exchange rate from a third-party API
        # This is a placeholder and should be replaced with a real implementation
        exchange_rate = random.uniform(0.8, 1.2)  # Mocked exchange rate

        return json.dumps({
            "from_currency": from_currency,
            "to_currency": to_currency,
            "exchange_rate": exchange_rate
        })
    except Exception as e:
        return json.dumps({"error": f"An error occurred: {str(e)}"})


        

# make functions callable a callable set from enterprise-streaming-agent.ipynb
enterprise_fns: Set[Callable[..., Any]] = {
    fetch_datetime,
    fetch_weather,
    fetch_currency_exchange_rate,
}