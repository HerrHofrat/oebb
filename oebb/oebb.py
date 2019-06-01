import requests
import json
from datetime import datetime
from time import time
import os
import logging


_LOGGER = logging.getLogger(__name__)


class OeBB:
    def __init__(self, cookie_keep_time=2300, auto_auth=True):
        self.session_keep_time = min(cookie_keep_time, 2300)
        self.session_expires = 0
        self.headers = {'Channel': 'inet', 'User-Agent' : 'Mozilla/5.0'}
        self.auto_auth = auto_auth

    def stations(self, name=''):
        r = self._make_request('https://tickets.oebb.at/api/hafas/v1/stations',
                               params={'count': 15,
                                       'name': str(name)})
        return json.loads(r.text)

    def connections(self, origin, destination, date=datetime.now(), count=5, opt=None):
           
        if isinstance(origin, dict):
             origin = origin['number']
        if isinstance(destination, dict):
             destination = destination['number']
    
        default = {'reverse': False,
                   'datetimeDeparture': date.strftime("%Y-%m-%dT%H:%M:00.000"),
                   'filter': {'regionaltrains': False,
                              'direct': False,
                              'changeTime': False,
                              'wheelchair': False,
                              'bikes': False,
                              'trains': False,
                              'motorail': False,
                              'droppedConnections': False},
                   'passengers': [
                       {
                           'type': 'ADULT',
                           'id': 1522168483,
                           'me': False,
                           'remembered': False,
                           'challengedFlags': {
                               'hasHandicappedPass': False,
                               'hasAssistanceDog': False,
                               'hasWheelchair': False,
                               'hasAttendant': False
                           },
                           'relations': [],
                           'cards': [],
                           'birthdateChangeable': True,
                           'birthdateDeletable': True,
                           'nameChangeable': True,
                           'passengerDeletable': True,
                       }
                   ],
                   'count': count,
                   'debugFilter': {'noAggregationFilter': False,
                                   'noEqclassFilter': False,
                                   'noNrtpathFilter': False,
                                   'noPaymentFilter': False,
                                   'useTripartFilter': False,
                                   'noVbxFilter': False,
                                   'noCategoriesFilter': False},
                   'from': {'number': origin},
                   'to': {'number': destination},
                   'timeout': {}}
        if type(opt) == dict:
            default.update(opt)
        r = self._make_request('https://tickets.oebb.at/api/hafas/v4/timetable',
                               data=default)
        return json.loads(r.text)['connections']

    def next_connections(self, connection, opt=None):
        default = {'connectionId': connection['id'],
                   'direction': 'after',
                   'count': 5,
                   'filter': {'regionaltrains': False,
                              'direct': False,
                              'changeTime': False,
                              'wheelchair': False,
                              'bikes': False,
                              'trains': False,
                              'motorail': False,
                              'droppedConnections': False}
                   }
        if type(opt) == dict:
            default.update(opt)
        r = self._make_request('https://tickets.oebb.at/api/hafas/v1/timetableScroll',
                               data=default)
        r = json.loads(r.text)
        return r['connections']

    def prices(self, connections):
        params = {'connectionIds[]': []}
        for connection in connections:
            params['connectionIds[]'].append(connection['id'])
        r = self._make_request('https://tickets.oebb.at/api/offer/v1/prices',
                               params=params)
        r = json.loads(r.text)
        return r['offers']

    def _make_request(self, url, data=None, params=None):
        if self.auto_auth and (int(time()) > self.session_expires):
            self.auth()
        if data is None:
            r = requests.get(url, headers=self.headers, params=params)
        else:
            r = requests.post(url, headers=self.headers, json=data)
        return r

    def auth(self):
        r = requests.get('https://tickets.oebb.at/api/domain/v3/init',
                         headers=self.headers,
                         params={'userId': self._generate_uid()})
        r = json.loads(r.text)
        self.headers.update({'AccessToken': r['accessToken'],
                             'SessionId': r['sessionId'],
                             'x-ts-supportid': r['supportId']})
        self.session_expires = int(time()) + self.session_keep_time

    @staticmethod
    def _generate_uid():
        s = os.urandom(7)
        return 'anonym-' + s[:4].hex() + '-' + s[4:6].hex() + '-' + s[6:].hex()

    @staticmethod
    def station_name(station):
        return station['name'] if station['name'] else station['meta']

    @staticmethod
    def get_datetime(text):
        return datetime.strptime(text[:-4], '%Y-%m-%dT%H:%M:%S')
