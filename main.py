import json
from typing import Any
import requests
import configparser

# config file for apikey security
def get_apikey():
    config = configparser.ConfigParser();
    config.read('app.config')
    apikey_from_file = config['secrets']['apikey']
    #print(apikey_from_file)
    return apikey_from_file

class NoSuchLocation(Exception):
    pass

class NotAZipCode(Exception):
    pass

apiKey = get_apikey()

def create_url(url_type, suffix_txt):
    if url_type == "location":
        return 'http://dataservice.accuweather.com/locations/v1/postal' \
                'codes/search?apikey=' + apiKey + "&q=" + suffix_txt
    if url_type == "conditions":
        returnVal = 'http://dataservice.accuweather.com/currentconditions/v1/' \
                '{}?apikey=' + apiKey
        return returnVal.format(suffix_txt)
    if url_type == "temp":
        returnVal = 'http://dataservice.accuweather.com/forecasts/v1/daily/5day/' \
                '963_PC?apikey=' + apiKey
        return returnVal
        

# We organize the code into functions to make it maintainable--per software *engineering*
# as opposed to software design
# Eventually convert this function to take both location and city
# Important Question: How do we get the user to find the right city by its name? Multiple questions? Multiple choice?
# And how much if the user is going to enter/query the same city twice, once for conditions and once more for five day
# temperature high's and low's?
# There are more than three Bostons, for instance, with at least two in the United States

def get_location(zipcode):
    # location_url = 'http://dataservice.accuweather.com/locations/v1/postal' \
    #               'codes/search?apikey=nQjG1eG3By20wnC8QxbDCEymZsajdQ2d&q=02703'
    zipcode_url = create_url("location", zipcode)
    response = requests.get(zipcode_url)
    print(response.status_code)

    # We make sure we can handle exceptions, such as a dirty zip code
    try:
        key = response.json()[0].get('Key') + "|" + response.json()[0]['EnglishName'] + ", " \
            + response.json()[0]['AdministrativeArea']['EnglishName'] + ", " \
            + response.json()[0]['Country']['EnglishName']
    except IndexError:
        raise NoSuchLocation()
    return key


def get_conditions(key, conditions_or_temp):
    # conditions_url = 'http://dataservice.accuweather.com/currentconditions/v1/' \
    #                 '{}?apikey=nQjG1eG3By20wnC8QxbDCEymZsajdQ2d'.format(key)
    url = create_url(conditions_or_temp, key[:key.find("|")])
    
    response = requests.get(url)
    json_version = response.json()
    city_name = key[key.find("|") + 1:]
    
    if conditions_or_temp == "conditions":
        print("Current Conditions for {0}: \n{1}\n".format(city_name, json_version[0].get('WeatherText')))
        
    if conditions_or_temp == "temp":
        jsonDailyForecastDict = json_version['DailyForecasts']
        dayCount = 0
        print("Five-Day Highs and Lows for " + city_name + ":")
        for day in jsonDailyForecastDict:
            dayCount += 1
            print("Day {0} ({1}) | Temps: Low - {2}F ; High - {3}F".format(dayCount, day['Date'][:10],
                                                                           day['Temperature']['Minimum']['Value'],
                                                                           day['Temperature']['Maximum']['Value']))
    
location_key = ''
def call_for_weather(conditions_or_temp):
    city_code = ""
    if conditions_or_temp == 'conditions':
        city_code = input("Enter a city's postal code to get it's current conditions: ")
        
    if conditions_or_temp == 'temp':
        city_code = input("Enter a city's postal code to get a forecast for "\
                            "the temperature highs and lows for the next 5 days\n"
                          "or enter Q to quit: ")
    
    if (city_code == "Q") | (city_code == "q"):
        print("Quit code entered, quitting!")
        return
    print("Retrieving location key...")
    if len(city_code) != 5:
        raise NotAZipCode("Invalid length.")
    
    try:
        location_key = get_location(city_code)
        get_conditions(location_key, conditions_or_temp)
    except NoSuchLocation:
        print("Unable to get the location")


call_for_weather('conditions')
call_for_weather('temp')


# JSON debugging sample object
jsonDummy = '{ \
  "Headline": { \
    "EffectiveDate": "2022-09-25T17:00:00-04:00", \
    "EffectiveEpochDate": 1664139600, \
    "Severity": 5, \
    "Text": "Expect showery weather late Sunday afternoon through Sunday evening", \
    "Category": "rain", \
    "EndDate": "2022-09-26T02:00:00-04:00", \
    "EndEpochDate": 1664172000, \
    "MobileLink": "http://www.accuweather.com/en/us/attleboro-ma/02703/daily-weather-forecast/963_pc?lang=en-us", \
    "Link": "http://www.accuweather.com/en/us/attleboro-ma/02703/daily-weather-forecast/963_pc?lang=en-us" \
  }, \
  "DailyForecasts": [ \
    { \
      "Date": "2022-09-23T07:00:00-04:00", \
      "EpochDate": 1663930800, \
      "Temperature": { \
        "Minimum": { \
          "Value": 43,\
          "Unit": "F",\
          "UnitType": 18\
        },\
        "Maximum": {\
          "Value": 58,\
          "Unit": "F",\
          "UnitType": 18\
        }\
      },\
      "Day": {\
        "Icon": 2,\
        "IconPhrase": "Mostly sunny",\
        "HasPrecipitation": false\
      },\
      "Night": {\
        "Icon": 33,\
        "IconPhrase": "Clear",\
        "HasPrecipitation": false\
      },\
      "Sources": [\
        "AccuWeather"\
      ],\
      "MobileLink": "http://www.accuweather.com/en/us/attleboro-ma/02703/daily-weather-forecast/963_pc?lang=en-us",\
      "Link": "http://www.accuweather.com/en/us/attleboro-ma/02703/daily-weather-forecast/963_pc?lang=en-us"\
    },\
    {\
      "Date": "2022-09-24T07:00:00-04:00",\
      "EpochDate": 1664017200,\
      "Temperature": {\
        "Minimum": {\
          "Value": 46,\
          "Unit": "F",\
          "UnitType": 18\
        },\
        "Maximum": {\
          "Value": 67,\
          "Unit": "F",\
          "UnitType": 18\
        }\
      },\
      "Day": {\
        "Icon": 2,\
        "IconPhrase": "Mostly sunny",\
        "HasPrecipitation": false\
      },\
      "Night": {\
        "Icon": 34,\
        "IconPhrase": "Mostly clear",\
        "HasPrecipitation": false\
      },\
      "Sources": [\
        "AccuWeather"\
      ],\
      "MobileLink": "http://www.accuweather.com/en/us/attleboro-ma/02703/daily-weather-forecast/963_pc?day=1&lang=en-us",\
      "Link": "http://www.accuweather.com/en/us/attleboro-ma/02703/daily-weather-forecast/963_pc?day=1&lang=en-us"\
    },\
    {\
      "Date": "2022-09-25T07:00:00-04:00",\
      "EpochDate": 1664103600,\
      "Temperature": {\
        "Minimum": {\
          "Value": 59,\
          "Unit": "F",\
          "UnitType": 18\
        },\
        "Maximum": {\
          "Value": 69,\
          "Unit": "F",\
          "UnitType": 18\
        }\
      },\
      "Day": {\
        "Icon": 14,\
        "IconPhrase": "Partly sunny w/ showers",\
        "HasPrecipitation": true,\
        "PrecipitationType": "Rain",\
        "PrecipitationIntensity": "Light"\
      },\
      "Night": {\
        "Icon": 12,\
        "IconPhrase": "Showers",\
        "HasPrecipitation": true,\
        "PrecipitationType": "Rain",\
        "PrecipitationIntensity": "Moderate"\
      },\
      "Sources": [\
        "AccuWeather"\
      ],\
      "MobileLink": "http://www.accuweather.com/en/us/attleboro-ma/02703/daily-weather-forecast/963_pc?day=2&lang=en-us",\
      "Link": "http://www.accuweather.com/en/us/attleboro-ma/02703/daily-weather-forecast/963_pc?day=2&lang=en-us"\
    },\
    {\
      "Date": "2022-09-26T07:00:00-04:00",\
      "EpochDate": 1664190000,\
      "Temperature": {\
        "Minimum": {\
          "Value": 55,\
          "Unit": "F",\
          "UnitType": 18\
        },\
        "Maximum": {\
          "Value": 70,\
          "Unit": "F",\
          "UnitType": 18\
        }\
      },\
      "Day": {\
        "Icon": 4,\
        "IconPhrase": "Intermittent clouds",\
        "HasPrecipitation": true,\
        "PrecipitationType": "Rain",\
        "PrecipitationIntensity": "Light"\
      },\
      "Night": {\
        "Icon": 35,\
        "IconPhrase": "Partly cloudy",\
        "HasPrecipitation": false\
      },\
      "Sources": [\
        "AccuWeather"\
      ],\
      "MobileLink": "http://www.accuweather.com/en/us/attleboro-ma/02703/daily-weather-forecast/963_pc?day=3&lang=en-us",\
      "Link": "http://www.accuweather.com/en/us/attleboro-ma/02703/daily-weather-forecast/963_pc?day=3&lang=en-us"\
    },\
    {\
      "Date": "2022-09-27T07:00:00-04:00",\
      "EpochDate": 1664276400,\
      "Temperature": {\
        "Minimum": {\
          "Value": 51,\
          "Unit": "F",\
          "UnitType": 18\
        },\
        "Maximum": {\
          "Value": 70,\
          "Unit": "F",\
          "UnitType": 18\
        }\
      },\
      "Day": {\
        "Icon": 4,\
        "IconPhrase": "Intermittent clouds",\
        "HasPrecipitation": false\
      },\
      "Night": {\
        "Icon": 34,\
        "IconPhrase": "Mostly clear",\
        "HasPrecipitation": false\
      },\
      "Sources": [\
        "AccuWeather"\
      ],\
      "MobileLink": "http://www.accuweather.com/en/us/attleboro-ma/02703/daily-weather-forecast/963_pc?day=4&lang=en-us",\
      "Link": "http://www.accuweather.com/en/us/attleboro-ma/02703/daily-weather-forecast/963_pc?day=4&lang=en-us"\
    }\
  ]\
}'

def json_access_test():
    jsonDailyForecast = json.loads(jsonDummy)['DailyForecasts']
    dayCount = 0
    for day in jsonDailyForecast:
        dayCount += 1
        print("Day {0} ({1}) | Temps: Low - {2}F ; High - {3}F".format(dayCount, day['Date'][:10], day['Temperature']['Minimum']['Value'], day['Temperature']['Maximum']['Value']))
    # print(json_version['DailyForecasts'][0]['Temperature']['Minimum']['Value'])

# for testing json access w/o using up AccuWeather calls
# json_access_test()

pass
