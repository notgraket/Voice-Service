# notgraket
# Main script for the Voice Service
# Created: 2-8-2022
# Last Edit: 2-12-2022

from data_structures import *
from threading import Thread
import requests
from datetime import date, datetime

# Add your own OpenWeatherToken
OpenWeatherToken = ""

Recorder0 = AudioRecorder()
Parser0 = Recorder0.Parser
Dictionary0 = Dictionary()
GeneralInfo = Cache(maxsize=None)

# Change this to your own resources folder
TTS = TextToSpeech(directory = "C:\\Users\\<username>\Desktop\\Projects\\Voice Service\\Voice Service 1\\resources")



def command(keyword, arguments = []):
    def decorator(function):
        """Decorator for passing functions and arguments to a container"""
        container = Parser0.container
        container[keyword] = {
            "function" : function,
            "arguments" : len(arguments),
            "expected" : arguments
        }
        return function
    return decorator



def cache_general_info():
    """Caches general information for later use by commands"""
    if ("ipaddress" not in GeneralInfo) or ("geoinfo" not in GeneralInfo):
            ipaddress = requests.get("https://api.ipify.org?format=json").json()["ip"]
            geoinfo = requests.get(f"http://ip-api.com/json/{ipaddress}?fields=192").json()
            latlong = (geoinfo["lat"], geoinfo["lon"])
            GeneralInfo.add("ipaddress", ipaddress)        
            GeneralInfo.add("latlong", latlong)





@command(keyword = "hello")
def hello():
    """Prints 'Hello World!'"""
    """This is a test function"""
    print("Hello World!")





@command(keyword = "test")
def test():
    """Another test function"""
    print("This is a successful test!")





@command(keyword = "define", arguments = [str])
def define(word : str):
    """Defines a word"""
    word = Parser0.parse_arguments(word, 1)[0] # Get first argument
    Recorder0.Toggle_Recording() # Off
    Dictionary0.get_definition(word)
    Recorder0.Toggle_Recording() # On
    # This is to prevent the TTS from being recorded





@command(keyword = "get", arguments=[str])
def api_grab(api : str):
    print("called")
    api = Parser0.parse_arguments(api, 1)[0] # Get the first argument
    print(api)

    # Current temperature, cloud cover, and humidity
    if (api == "weather"):
        cache_general_info()
        
        lat, long = GeneralInfo["latlong"] # Tuple

        data = requests.get(f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&appid={OpenWeatherToken}&units=imperial").json()

        # Weather data
        current_temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        cloud_cover = data["weather"][0]["description"]
        humidity = data["main"]["humidity"]

        # Text To Speech
        text = f"""
        The current temperature is {current_temp} degrees Fahrenheit, but it feels like {feels_like} degrees.
        The cloud cover is {cloud_cover}, and humidity is at {humidity} percent.
        """
        TTS.say(text)

    # Date and time
    if (api == "date"):
        current_date = date.today().strftime("%B %d, %Y")
        current_time = datetime.now().strftime("%H:%M %p")
        text = f"Today's date is {current_date}, and it is currently {current_time}."
        TTS.say(text)





def main():
    Execute = Thread(target = Parser0.execute) # Executes oldest command in queue
    Record = Thread(target = Recorder0.record) # Records audio, inserts into queue
    Execute.start()
    Record.start()





if __name__ == "__main__":
    main()
