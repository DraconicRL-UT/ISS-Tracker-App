#! /usr/bin/env python3
#import relevant python libraries
import xmltodict
import requests
import math
import logging
import socket
import pytest

from astropy import coordinates, units
from astropy.time import Time
from geopy.geocoders import Nominatim
from flask import Flask, request
from iss_tracker import time_range,currEpoch, speed, avg_speed, find_location

data = {
    "EPOCH": "2024-062T12:00:00.000Z",
    "X": {
      "#text": "0.0",
      "@units": "km"
    },
    "X_DOT": {
      "#text": "0.0",
      "@units": "km/s"
    },
    "Y": {
      "#text": "0.0",
      "@units": "km"
    },
    "Y_DOT": {
      "#text": "0.0",
      "@units": "km/s"
    },
    "Z": {
      "#text": "0.0",
      "@units": "km"
    },
    "Z_DOT": {
      "#text": "0.0",
      "@units": "km/s"
    }}
data_bad = {
    "EPOCH": "2024-062T12:00:00.000Z",
    "X": {
      "#text": "0.0",
      "@units": "km"
    },
    "X_DOT": {
      "#text": "",
      "@units": "km/s"
    },
    "Y": {
      "#text": "0.0",
      "@units": "km"
    },
    "Y_DOT": {
      "#text": "",
      "@units": "km/s"
    },
    "Z": {
      "#text": "0.0",
      "@units": "km"
    },
    "Z_DOT": {
      "#text": "",
      "@units": "km/s"
    }}
data1 = [{'EPOCH': "2024-000T00:00:00.000Z"}, {'EPOCH':"2024-000T00:00:00.000Z"}]
data1_bad = [{'epoch': "2024-000T00:00:00.000Z"}, {'pech':"2024-000T00:00:00.000Z"}]
data2 = [data, data]
data2_bad = [data_bad, data_bad]
data3_single = {
    "EPOCH": "2024-062T12:00:00.000Z",
    "X": {
      "#text": "0.0",
      "@units": "km"
    },
    "X_DOT": {
      "#text": "dlkfhaskj",
      "@units": "km/s"
    },
    "Y": {
      "#text": "0.0",
      "@units": "km"
    },
    "Y_DOT": {
      "#text": "lj;askdhfka",
      "@units": "km/s"
    },
    "Z": {
      "#text": "0.0",
      "@units": "km"
    },
    "Z_DOT": {
      "#text": "fkhdasjklf",
      "@units": "km/s"
    }}
data3 = [ data3_single, data3_single]

#testing built-in functions:
def test_time_range():
    assert(isinstance(time_range(data1), str) == True)
    with pytest.raises(KeyError):
        time_range(data1_bad)

def test_currEpoch():
    assert(isinstance(currEpoch(data), str) == True)
    currPos = [data['X']['#text'], data['Y']['#text'], data['Z']['#text']]
    currVel = [data['X_DOT']['#text'], data['Y_DOT']['#text'], data['Z_DOT']['#text']]

def test_speed():
    assert(isinstance(speed(data), float) == True)
    assert(speed(data) == 0.0) 
    with pytest.raises(ValueError):
        speed(data_bad)

def test_avg_speed():
    assert(isinstance(avg_speed(data2), float) == True)
    assert(avg_speed(data2) == 0.0)
    with pytest.raises(ValueError):
        avg_speed(data3) 
    with pytest.raises(ValueError):
        avg_speed(data2_bad)

def test_find_location():
    results = find_location(data)
    print(results)
    assert(isinstance(results[0], str) == True)
    assert(isinstance(results[1], str) == True)
    assert(isinstance(results[2], str) == True)
    assert(float(results[0]) >=-90 and float(results[0]) <=90) #check for valid latitude
    assert(float(results[1]) >=-180 and float(results[1]) <=180) #check for valid longitude
    assert(abs(float(results[2])) >= 0) #check for valid altitude

#testing routes:
response1 = requests.get('http://127.0.0.1:5000/epochs')
a_rep_epoch = str(response1.json()[0]['EPOCH'])
response2 = requests.get('http://127.0.0.1:5000/epochs/'+a_rep_epoch)
resp3 = requests.get('http://127.0.0.1:5000/comment')
resp4 = requests.get('http://127.0.0.1:5000/header')
resp5 = requests.get('http://127.0.0.1:5000/metadata')
epoch_q1 = requests.get('http://127.0.0.1:5000/epochs?limit=1')
epoch_q2 = requests.get('http://127.0.0.1:5000/epochs?offset=1')
a_rep_epoch2 = str(response1.json()[1]['EPOCH'])
epoch_q3 = requests.get('http://127.0.0.1:5000/epochs?limit=1&offset=1')
resp6 = requests.get('http://127.0.0.1:5000/epochs/'+a_rep_epoch+'/speed')
resp7 = requests.get('http://127.0.0.1:5000/epochs/'+a_rep_epoch+'/location')
resp8 = requests.get('http://127.0.0.1:5000/now')

def test_epochs_route():
    assert response1.status_code == 200
    assert isinstance(response1.json(), list) == True

def test_specific_epochs_route():
    assert response2.status_code == 200
    assert isinstance(response2.json(), dict) == True

def test_comment_route():
    assert resp3.status_code == 200
    assert isinstance(resp3.json(), list) == True

def test_header_route():
    assert resp4.status_code == 200
    assert isinstance(resp4.json(), dict) == True

def test_metadata_route():
    assert resp5.status_code == 200
    assert isinstance(resp5.json(), dict) == True

def test_epoch_query_route():
    assert epoch_q1.status_code == 200
    assert epoch_q2.status_code == 200
    assert epoch_q3.status_code == 200
    assert isinstance(epoch_q1.json(), list) == True
    assert (str(epoch_q1.json()[0]['EPOCH']) == a_rep_epoch)
    assert isinstance(epoch_q2.json(), list) == True
    assert isinstance(epoch_q3.json(), list) == True
    assert (str(epoch_q3.json()[0]['EPOCH']) == a_rep_epoch2)

def test_epoch_speed_route():
    assert resp6.status_code == 200
    assert isinstance(resp6.text, str) == True

def test_epoch_location_route():
    assert resp7.status_code == 200
    assert isinstance(resp7.text, str) == True

def test_now_route():
    assert resp8.status_code == 200
    assert isinstance(resp8.text, str) == True

def main():
    test_time_range()
    test_currEpoch()
    test_speed()
    test_avg_speed()
    test_find_location()
    test_epochs_route()
    test_specific_epochs_route()
    test_comment_route()
    test_header_route()
    test_metadata_route()
    test_epoch_query_route()
    test_epoch_speed_route()
    test_epoch_location_route()
    test_now_route()

if __name__ == '__main__':
    main()
