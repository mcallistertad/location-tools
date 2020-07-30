#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Created by Tad McAllister (tad@theconvexlens.co) 23-08-2019
usage:
$ export GEO_API_KEY=value
$ echo "data_to_parse" | python3 cell_translate.py
'''
# +CEREG:
# <n> net reg result code
# <stat> EPS registration status
# <tac> tracking area code in hex format
# <ci> E-UTRAN cell ID in hex format
# <AcT>  access technology of the serving cell
# <cause_type> type of <reject_cause>
# <reject_cause> cause of the failed reg defined by <cause_type>
# <Active-Time> active time val allocated to UE in E-UTRAN
# <Periodic-TAU> extended periodic TAU value allocated to UE in E-UTRAN */

import os
import sys
import re
import requests
from requests_toolbelt.utils import dump
import webbrowser
import json
import binascii

geo_api_key = os.environ['GEO_API_KEY']
encoding = 'utf-8'

url = 'https://www.googleapis.com/geolocation/v1/geolocate?key=' + geo_api_key
maps_url = 'https://maps.google.com/?q='
# https://maps.google.com/?q=%a[GPS][coordinates.latitude],%a[GPS][coordinates.longitude]
# https://maps.google.com/?q=53.3834,-10.458961

radio_type = 'lte'
mcc = 272
mnc = 1
plmnid = 27201

reg_str = "CEREG"
rssi_str = "CSQ"

test_hex_data = '40010000B16210FFCC50E382E36800030000000000010000000000000000000000003930313238383030323230353334332B4347534E3A3836333730333033333935323136342B434750414444523A312C31302E32312E3131392E32333776312E302E302D626574612D31332D67643465322D64697274795175656374656C424339352D4232305265766973696F6E3A4243393542323048425230314130355731362B43455245473A322C352C323333322C30323446414331462C374E554553544154533A43454C4C2C363335342C3239302C312C2D3835372C2D3131372C2D3737302C36342B4353513A31392C39392B43434C4B3A31392F30382F32322C32313A34333A31332B303025AE9A59'


def check_hex(s):
    try:
        int(s, 16)
        return True
    except ValueError:
        return False


def get_hex_data():
    try:
        hex_data = sys.stdin.read()
        if hex_data:
            print('>> fetched input')
            return hex_data.strip().rstrip('\r\n')
        else:
            print('>> failed to fetch input')
            return None

    except Exception as e:
        print(e)


def getGeoLocation(cid, tac, rssi):
    payload = {'considerIp': 'false', 'radioType': radio_type, 'cellTowers': [
        {'cellId': cid, 'locationAreaCode': tac, 'mobileCountryCode': mcc, 'mobileNetworkCode': mnc,
         'signalStrength': rssi}]}
    json_payload = json.dumps(payload, indent=1)
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json_payload, headers=headers)

    raw_req = dump.dump_all(r)
    print(raw_req.decode('utf-8'))

    try:
        r.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(e)
        exit(4)
    response = json.loads(r.text)
    lat = response['location']['lat']
    long = response['location']['lng']
    accuracy = response['accuracy']
    return lat, long, accuracy, r


def main():
    if not geo_api_key:
        print('<< Err: user not authenticated')

    hex_data = get_hex_data()

    if check_hex(hex_data):
        print('<< got valid hex')
    else:
        print('<< invalid hex... using dummy data')
        hex_data = test_hex_data

    attempts = 2
    for i in range(attempts):
        try:
            ascii_data = binascii.unhexlify(hex_data)

        except Exception as e:
            print('<< Err: encountered error while asciifying:', e)
            if i < attempts - 1:
                print('>> padding hex_string')
                hex_data = hex_data + '0'
                continue
            else:
                print('<< Err: padding not successful')
                exit(1)
        break

    ascii_data = ascii_data.decode('unicode_escape').encode(encoding)
    print('<< ASCII STR: ', ascii_data)

    ascii_data = ascii_data.decode()
    if reg_str in ascii_data:

        search_str = ascii_data.split(reg_str, 1)[1]
        tac = int(search_str.split(',')[2])
        cid = (int(search_str.split(',')[3], 16) - 20)
        print('[ TAC:', tac, 'CELL_ID:', cid, ']')

        if rssi_str in search_str:
            search_str = ascii_data.split(rssi_str, 1)[1]
            try:
                rssi = re.search(':(.+?),', search_str).group(1)
                rssi = int('-' + rssi)
                print('[RSSI:', rssi, 'dBm]')
            except Exception as e:
                print('<< Err: regex search failed:', e)

        try:
            print(">> Sending Geolocation Request")
            lat, long, accuracy, r = getGeoLocation(cid, tac, rssi)

            if r.status_code == 200:
                print('<< Geolocation request Sent\r\n', '[',
                      'Latitude: %s | Longitude: %s | Accuracy: %sm' % (lat, long, accuracy), ']')
            else:
                print(r.status_code)
                exit(3)

        except Exception as e:
            print('<< Err: an error occurred sending Geolocation request...\n', e)

        try:
            webbrowser.open_new((maps_url + str(lat) + ',' + str(long)))
        except Exception as e:
            print('<< Err: an error occurred opening maps location...\n', e)

    else:
        print('<< Err: reg_str not found')
        exit(2)

    exit(0)


if __name__ == '__main__':
    sys.exit(main())
