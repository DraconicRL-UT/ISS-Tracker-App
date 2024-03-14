#! /usr/bin/env python3
#import relevant python libraries
from flask import Flask, request
from astropy import coordinates
from astropy import units
from astropy.time import Time
from geopy.geocoders import Nominatim
import xmltodict
import requests
import math
import time
import logging
import socket

#initating the app for flask/rest API navigation
app = Flask(__name__)

def time_range(a_dict) -> str:
    """
    A function that states the time range of a simulation period. Outputs a     string with the first epoch of input and final epoch, then expalins how
    to interprete the epochs.

    Args:
        a_dict (dictionary): A dictionary list of meteorite landing data.

    Returns:
        result (string): Statement about time range in UTC epoch and also
                         explains the method of interpretation to convert 
                         the epoch to common date and time.
    """
    #storing inital and final values
    try: 
        firstDay = a_dict[0]['EPOCH']
        finalDay = a_dict[-1]['EPOCH']
        logging.debug(f'The first epoch was: {firstDay}, and the final epoch was: {finalDay}\n')
        #constructing the output string
        result = f'This call of the ISS data spanned 15 days starting from an intial EPOCH of {firstDay} to a final EPOCH of {finalDay}. Note that the EPOCH is expressed in the format of (4 digit year, yyyy)-(3 digit day of the year out of 365, ddd)T:(hour, hh):(minutes, mm):(seconds, ss).(time zone offest, zzz)Z. For example, if the current UTC time was 2024 Feb 19th, 2:45:00pm, then the epoch would be 2024-050T14:45:00.000Z as there is no offset and feb 19th is the 50th day of the year (31 days in January + 19th day of Febuary = 50th day of year).\n'
    except KeyError:
        raise KeyError('nonexistant key\n')
        result = "Could not compute due to error\n"
        logging.error(f'wrong or non-existant key, "EPOCH" was the expected key, instead only have: {a_dict[0].keys()} and {a_dict[-1].keys()}\n')
    return result

def currEpoch(a_dict) ->str: 
    """
    A function that outputs the current epoch and state vector elements for     the current time right "now" (as of the time of executing the code).

    Args:
        a_dict (dictionary): A singular dictionary object with keys of: 
                             EPOCH, X, Y, Z, X_DOT, Y_DOT, and Z_DOT.

    Returns:
        result (string): formated string that includes current time (epoch),                         current position, and current velocity.
    """
    currEPOCH = a_dict['EPOCH']
    #pulling the position and velocity vectors from the statevector for the current dictioary object (a_dict)
    currPos = [a_dict['X']['#text'], a_dict['Y']['#text'], a_dict['Z']['#text']]
    currVel = [a_dict['X_DOT']['#text'], a_dict['Y_DOT']['#text'], a_dict['Z_DOT']['#text']]
    result = f'The time right now is: {currEPOCH}; the current position of the ISS is: {currPos} km; and the current velocity of the ISS is: {currVel} km/s\n'
    return result

def speed(a_dict) -> float:
    """
    A function that calculates speed of an object.

    Args:
        a_dict (dictionary): A singular dictionary object with keys: 
                             EPOCH, X, Y, Z, X_DOT, Y_DOT, and Z_DOT.
    Returns:
        speed (float): The speed of the object in the same units as the 
                       corresponding units of the statevector provided with                        the input object (a_dict).
    """
    #making the inital velocity vector
    Vel = [float(a_dict['X_DOT']['#text']), float(a_dict['Y_DOT']['#text']), float(a_dict['Z_DOT']['#text'])]
    try:
        #calculates the speed using Cartesian velocity vectors
        speed = math.sqrt(Vel[0]**2 + Vel[1]**2 + Vel[2]**2)
    except ValueError:
        raise ValueError('Null value\n')
        logging.warning(f'encountered a null value for velcity when trying to calculate the speed in speed()\n')
    return speed

def avg_speed(a_dict) -> float:
    """
    A function that calculates the average speed of objects in dictionary.

    Args:
        a_dict (dictionary): A dictionary list of ISS epoch and state
                             vectors in 4 minute intervals for 15 day 
                             period of time.

    Returns:
        avg_speed (float): The average speed of the ISS during this period.
    """
    #calculating the average by summing up the speed of the ISS at each timestep then dividing by the number of timesteps
    total = 0.
    if len(a_dict)<=1:
        raise ValueError('List must have length >= 1\n')
        logging.error(f'encountered a list of length 1 or less\n')
    for item in a_dict:
        try:
            total += speed(item)
        except TypeError:
            raise TypeError('non-float value\n')
            logging.warning(f'encountered non-float value in {a_dict} in avg_speed()\n')
        except ValueError:
            raise ValueError('null value\n')
            logging.warning(f'encountered null value in {a_dict} in avg_speed()\n')
    avg_speed = float(total/len(a_dict))
    return avg_speed


def find_location(a_dict):
    """
    A function that calculates speed of an object.

    Args:
        a_dict (dictionary): A singular dictionary object (representing a
                             statevector) with keys: EPOCH, X, Y, Z, X_DOT,
                             Y_DOT, and Z_DOT.
    
    Returns: 
        lat (str): The latitude of the ISS at the input epoch.
        lon (str): The longitude of the ISS at the input epoch.
        alt (str): The altitude of the ISS at the input epoch.
    """
    x = float(a_dict['X']['#text'])
    y = float(a_dict['Y']['#text'])
    z = float(a_dict['Z']['#text'])

    #reformats epoch variables (assuming epoch is in the correct format as consistent with other instances, 'YYYY-DDDThh:mm:ss.tttZ', where YYYY is the 4-digit year, DDD is the day of the year (out of 365), hh is the hour, mm is the minute, ss is the second, ttt is the time zone offset from UTC (if 000, then the epoch is in UTC time zone)). 
    curr_time = time.strftime('%Y-%m-%d %H:%m:%S', time.strptime(a_dict['EPOCH'][:-5], '%Y-%jT%H:%M:%S'))

    #convert from cartesion to itrs reference frame (the reference frame used by gps for latitute and longitude)
    cartesian_coord = coordinates.CartesianRepresentation([x, y, z], unit = units.km)
    gcrs = coordinates.GCRS(cartesian_coord, obstime=curr_time)
    itrs = gcrs.transform_to(coordinates.ITRS(obstime=curr_time))
    curr_loc = coordinates.EarthLocation(*itrs.cartesian.xyz)
    
    return str(curr_loc.lat.value), str(curr_loc.lon.value), str(curr_loc.height.value)
      

#setting the "home" page to be the one that outputs the relevant general summary statistics
@app.route('/', methods = ['GET'])
def main():
    #uses requests to pull the most recent data from ISS website and stores it
    response = requests.get(url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.content)
    ml_data = data['ndm']['oem']['body']['segment']['data']['stateVector']
    
    #calculates some general summary statistics and outputs it
    result1 = time_range(ml_data)
    result2 = currEpoch(ml_data[-1])
    result3 = f'The average speed of the ISS for this simulation of the past 15 days was: {avg_speed(ml_data)} km/s. The current speed of the ISS is: {speed(ml_data[-1])} km/s.'
    return f'{result1}\n{result2}\n{result3}\n'

#setting an app decorator that lists all the ISS time steps, and also has query parameters: limit & offset. Limit will limit the size of the list of the ISS epochs. Offset will offset the starting point by the i-th value in the data set
@app.route('/epochs', methods = ['GET'])
def list_epochs():
    #uses requests to pull the most recent data from ISS website and stores it
    response = requests.get(url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.content)
    iss_data = data['ndm']['oem']['body']['segment']['data']['stateVector']

    #stores the query parameters from the input and checks if they are valid, if not then raise errors.
    limit = request.args.get('limit', len(iss_data))
    offset = request.args.get('offset', 0)
    try:
        offset=int(offset)
    except ValueError:
        return 'Invalid start parameter; start must be a non-negative integer\n'
    try:
        limit = int(limit)
    except ValueError:
        return 'Invalid limit parameter; limit must be a non-negative integer\n'
    
    #initialize a ret_data list to store the queried list, and a counter parameter to track the current size of the returned list, ret_data
    ret_data = []
    counter = 0
    for i in range(len(iss_data)):
        #check if the current index is past the offset or not
        if i >= offset:
            ret_data.append(iss_data[i])
            counter += 1
            #checks if the limit has been reached yet
            if counter >= limit:
                return ret_data
    return ret_data

#setting an app decorator that outputs the epoch and statevector for a speciific epoch
@app.route('/epochs/<epoch>', methods = ['GET'])
def specific_epoch(epoch):
     #uses request to pull the most recent data from ISS website and stores it
    response = requests.get(url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.content)
    iss_data = data['ndm']['oem']['body']['segment']['data']['stateVector']
    #parses through the dataset to check if there is an item with the matching epoch
    for item in iss_data:
        if item['EPOCH'] == epoch:
            return item
    return f'Failed to find a state vector, check if epoch was valid (in time range of this 15 day period run and in the correct format: "YYYY"-"ddd"T"hh":"mm":"ss":"ttt"Z, where YYYY is the 4-digit year, ddd is the day of the year (out of 365), hh is in hours, mm is in minutes, ss is in seconds, ttt is the time zone offset from UTC(000 if UTC)). \n'

#setting an app decorator that outputs the speed of the ISS at a particular epoch
@app.route('/epochs/<epoch>/speed', methods = ['GET'])
def specific_epoch_speed(epoch):
    #initilize a speed variable
    sat_speed = -1
    #uses request to pull the most recent data from ISS website and stores it
    response = requests.get(url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.content)
    iss_data = data['ndm']['oem']['body']['segment']['data']['stateVector']
    #parses through the dataset to check if there is an item with the matching epoch, then calls the speed function to return the speed of the ISS at the input epoch time
    for item in iss_data:
        if item['EPOCH'] == epoch:
            try:
                sat_speed = speed(item)
                return f'Speed of about ~ {int(sat_speed)} km/s\n'
            except ValueError:
                return 'null value\n'
            except TypeError:
                return 'non-float value\n'
    return f'Failed to find a valid state vector, check if epoch was valid (in time range of this 15 day period run\n'

@app.route('/comment', methods = ['GET'])
def comment():
    #uses request to pull the most recent data from ISS website and stores it
    response = requests.get(url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.content)
    iss_data_comments = data['ndm']['oem']['body']['segment']['data']['COMMENT']
    return iss_data_comments

@app.route('/header', methods = ['GET'])
def header():
    #uses request to pull the most recent data from ISS website and stores it
    response = requests.get(url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.content)
    iss_data_header = data['ndm']['oem']['header']
    return iss_data_header

@app.route('/metadata', methods = ['GET'])
def metadata():
    #uses request to pull the most recent data from ISS website and stores it
    response = requests.get(url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.content)
    iss_meta_data = data['ndm']['oem']['body']['segment']['metadata']
    return iss_meta_data    

@app.route('/epochs/<epoch>/location', methods = ['GET'])
def specific_epoch_location(epoch):
    #uses request to pull the most recent data from ISS website and stores it
    response = requests.get(url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.content)
    iss_data = data['ndm']['oem']['body']['segment']['data']['stateVector']
    for item in iss_data:
        if item['EPOCH'] == epoch:
            try:
                location_info = find_location(item)
            except ValueError:
                raise ValueError('null value in location route\n')
                logging.warning(f'encountered null value for epoch of {item["EPOCH"]} in location route.\n')
    geolocator = Nominatim(user_agent="ISS Tracker Flask App")
    location = geolocator.reverse((f"{str(location_info[0])}, {str(location_info[1])}"), zoom = 10, language ='en')
    if (location == None):
        return f'The ISS is currently above a body of water, and it\'s coordinates are: {str(location_info[0])}, {str(location_info[1])}. It is also at an altitude of: {str(location_info[2])} km above the Earth\'s surface.\n'
    return f'The ISS is currently above {str(location.address)}, and it\'s coordinates are: {str(location.latitude)}, {str(location.longitude)}. It is also at an altitude of {str(location_info[2])} km above the Earth\'s surface.\n'

@app.route('/now', methods = ['GET'])
def now():
    #uses request to pull the most recent data from ISS website and stores it
    response = requests.get(url = 'https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml')
    data = xmltodict.parse(response.content)
    iss_data = data['ndm']['oem']['body']['segment']['data']['stateVector']
    curr_StateVect = iss_data[-1]
    try: 
        lat, lon, alt = find_location(curr_StateVect)
        geolocator = Nominatim(user_agent="ISS Tracker Flask App")
        location = geolocator.reverse((lat, lon), zoom = 10, language='en')
        sat_speed = speed(curr_StateVect)
        if (location == None):
            return f'The ISS is currently above a body of water, and it\'s coordinates are: {lat}, {lon}. It is also at an altitude of: {alt} km above the Earth\'s surface. It is travling at a speed of about ~ {int(sat_speed)} km/s as of right now.\n'
        return f'The ISS is currently above {str(location.address)}, and it\'s coordinates are: {str(location.latitude)}, {str(location.longitude)}. It is also at an altitude of {str(alt)} km above the Earth\'s surface. It is travling at a speed of about ~ {int(sat_speed)} km/s as of right now.\n'
    except ValueError:
        raise ValueError('null value in location route\n')
        logging.warning(f'encountered null value for epoch of {curr_StateVect["EPOCH"]} in location route.\n')
    except TypeError:
        raise TypeError('non-float value in location route\n')
        logging.warning(f'encountered non-float value for epoch of {curr_StateVect["EPOCH"]} in location route.\n')

#The next statement should usually appear at the bottom of a flask app
if __name__ == '__main__':
    app.run(debug=True, host = '0.0.0.0')







