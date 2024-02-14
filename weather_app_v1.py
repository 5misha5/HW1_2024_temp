import datetime as dt
import json

import requests
from flask import Flask, jsonify, request

# create your API token, and set it up in Postman collection as part of the Body section
API_TOKEN = "lemme_die"
# you can get API keys for free here - https://api-ninjas.com/api/jokes
RSA_KEY = "6BPQZ42RRLRQ94DGYZC4DWPDN"

app = Flask(__name__)


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


def get_weather(location: str, date=str(dt.date.today())):
    url_base_url = "https://weather.visualcrossing.com"
    url_api = "VisualCrossingWebServices/rest/services/timeline"
    

    url = f"{url_base_url}/{url_api}/{location}/{date}?key={RSA_KEY}"

    response = requests.get(url)

    if response.status_code == requests.codes.ok:
        return json.loads(response.text)
    else:
        raise InvalidUsage(response.text, status_code=response.status_code)


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route("/")
def home_page():
    return "<p><h2>KMA L2: python Saas.</h2></p>"


@app.route("/content/api/v1/weather", methods=["POST"])
def weather_endpoint():
    json_data = request.get_json()

    if json_data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = json_data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    if json_data.get("location") is None:
        raise InvalidUsage("location is required", status_code=400)

    location = json_data.get("location")
    requester_name = "Noname" if json_data.get("requester_name") is None else json_data.get("requester_name")
    date = str(dt.date.today()) if json_data.get("date") is None else json_data.get("date")
     

    weather = get_weather(location=location, date=date)

    day_weather = weather["days"][0]

    result = {
        "requester_name": requester_name,
        "location": location,
        "date": day_weather["datetime"],
        "description": day_weather["description"],
        "cloudcover: ": day_weather["cloudcover"],
        "tempmax: ": day_weather["tempmax"],
        "tempmin: ": day_weather["tempmin"],
        "snow: ": day_weather["snow"],
        "sunrise: ": day_weather["sunrise"],
        "sunset: ": day_weather["sunset"],
    }

    return result

if __name__ == "__main__":
    print(get_weather("Kyiv", "2024-02-14"))
