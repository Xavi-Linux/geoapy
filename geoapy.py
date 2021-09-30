import requests
from pathlib import Path
import re
import shelve

__KEY_FILE = 'key.txt'
__URL = 'https://api.ipgeolocation.io/ipgeo?'
__API_PARAM = 'apiKey'
_FIELDS = [
    'domain',
    'ip',
    'hostname',
    'continent_code',
    'continent_name',
    'country_code2',
    'country_code3',
    'country_name',
    'country_capital',
    'state_prov',
    'district',
    'city',
    'zipcode',
    'latitude',
    'longitude',
    'is_eu',
    'calling_code',
    'country_tld',
    'languages',
    'country_flag',
    'geoname_id',
    'isp',
    'connection_type',
    'organization',
    'asn',
    'currency',
    'time_zone'
]
_CACHE_FILE = 'cache'


class KeyNotFound(BaseException):

    def __init__(self):
        super().__init__('Please register a key before fetching it')


class IncorrectIpFormat(BaseException):

    def __init__(self, iptype):
        """

        :param iptype: ipv4 or ipv6
        """
        super().__init__('Incorrect {0} format'.format(iptype))


class FieldDoesNotExist(BaseException):

    def __init__(self, field):
        """

        :param field: field not found in __FIELDS list.
        """
        super().__init__('Field {0} is not amongst the possible values'.format(field))


class RequestError(BaseException):
    def __init__(self, code, text):
        """

        :param code: HTTP code
        :param text: error detail
        """
        super().__init__('Error {0}: {1}'.format(code, text))


class Response:

    def __init__(self, attributes:dict):
        """
        A class to handle api responses in an object-oriented fashion.
        Attributes are built on the fly.

        :param attributes: a dictionary containing the attributes and values to furnish the class.
        """
        for field in _FIELDS:
            if field in attributes:
                self.__setattr__(field, attributes[field])

            else:
                self.__setattr__(field, '')

        self.currentfolder = Path(__file__).parent

    def cache(self):
        """
        Persist the instance
        :return: nothing
        """
        ip = self.__getattribute__('ip')
        with shelve.open(str(self.currentfolder.joinpath(_CACHE_FILE)), 'w') as db:
            db[ip] = self.__dict__

    def uncache(self):
        """
        Erase the instance from the persistence file
        :return: nothing
        """
        ip = self.__getattribute__('ip')
        with shelve.open(str(self.currentfolder.joinpath(_CACHE_FILE)), 'w') as db:
            value = db.get('ip')
            if value:
                del db[ip]

    @classmethod
    def retreivefromcache(cls, ip: str):
        """
        Check if the ip has been persisted and build the class instance.
        :param ip:
        :return: class instance or None (if the ip's not been previously persisted
        """
        currentfolder = Path(__file__).parent
        with shelve.open(str(currentfolder.joinpath(_CACHE_FILE)), 'c') as db:
            value = db.get(ip)

        if value:
            return cls(ip)

        else:
            return None

    def __str__(self):
        return str(self.__dict__)


def registerkey(keystring:str):
    """
    :param keystring: string containing the API KEY.
    :return: nothing. It's just creates a text file to store the key.
    """
    currentfolder = Path(__file__).parent
    with open(currentfolder.joinpath(__KEY_FILE),'w') as f:
        f.write(keystring)


def getkey():
    """
    Get the API KEY
    :return: the key or raises error
    """
    currentfolder = Path(__file__).parent
    keyfile = currentfolder.joinpath(__KEY_FILE)
    if keyfile.exists():
        with open(keyfile,'r') as f:
            key = f.read()

        return key
    else:
        raise KeyNotFound()


def listfields():
    return _FIELDS


def checkipformat(ip:str):
    """
    Check if the string has ipv4 format.
    :param ip: a string to be checked
    :return: None or raises error
    """
    ipv4 = re.compile('^[0-2]?[0-9]{1,2}\.[0-2]?[0-9]{1,2}\.[0-2]?[0-9]{1,2}\.[0-2]?[0-9]{1,2}$')
    if ipv4.match(ip):
        ipv4_chunks = re.compile('\.').split(ip)
        valid_values = list(filter(lambda v: v < 256,
                                   map(int,
                                       ipv4_chunks)
                                  )
                           )
        if len(valid_values) == 4:
            return None

    raise IncorrectIpFormat('ipv4')


def formatfields(fields:[tuple, list]):
    """
    Format the list of fields to be passed as api request arguments.
    :param fields: a list or tuple.
    :return: a string with comma-separated elements
    """
    for field in fields:
        if field not in _FIELDS:
            raise FieldDoesNotExist(field)

    fields = list(map(lambda v: str(v).lower(), fields))
    return ','.join(fields)


def get(ip:str=None, fields:[tuple, list]=None, excluded_fields:[tuple, list]=None, cache_search=True):
    """
    Executes and API request.
    :param ip: if None, it queries the requestor's ip.
    :param fields: fields to be included in the api response. If None, it returns all available fields.
    :param excluded_fields: fields to be be excluded in the api response.
    :param cache_search: if true, it first check if the searched ip has been previously sought and persisted.
    :return: a Response object or raises error
    """
    key = getkey()
    query_str = __API_PARAM + '=' + key
    if cache_search and ip:
        value = Response.retreivefromcache(ip)
        if value is not None:
            return value

    if ip:
        checkipformat(ip)
        query_str += '&ip=' + ip

    if fields:
        include = formatfields(fields)
        query_str += '&fields=' + include

    if excluded_fields:
        exclude = formatfields(excluded_fields)
        query_str += '&excludes=' + exclude

    r = requests.get(__URL + query_str)
    if r.status_code == 200:
        return Response(r.json())

    elif r.status_code == 401:
        raise RequestError(r.status_code, 'It is returned for one of the following reasons:\n'
                                          '\t(1) If API key (as "apiKey" URL parameter) is missing from the request to'
                                          'IP Geolocation API.\n\t(2) If an invalid (a random value) API key is provided.\n\t'
                                          '(3) If the API request is made from an unverified ipgeolocation.io'
                                          ' account.\n\t'
                                          '(4) If your account has been disabled or locked to use by the admin due to'
                                          ' abuse or illegal activity.\n\t(5) When the request to IP Geolocation API is'
                                          'made using API key for a database subscription.\n\t(6) When the request to IP'
                                          ' Geolocation API is made on the "paused" subscription.\n\t(7) If you’re making'
                                          ' API requests after your subscription trial has been expired.\n\t(8) If your '
                                          'active until date has passed and you need to upgrade your account.\n\t(9) If'
                                          ' bulk IP to geolocation look-ups endpoint is called using free subscription'
                                          ' API key.\n\t(10) If user-agent lookup using custom string or bulk user-agent'
                                          ' look-ups endpoints are called using free subscription API key.\n\t'
                                          '(11) When the wrong input is provided in the request to any endpoint of IP'
                                          ' Geolocation API.')

    elif r.status_code == 403:
        raise RequestError(r.status_code, 'It is returned for one of the following reasons:\n\t(1) If IP to geolocation'
                                          ' look-up for a domain name is done using a free subscription API key.')

    elif r.status_code == 404:
        raise RequestError(r.status_code, 'It is returned for one of the following reasons:\n\t(1) If the queried IP'
                                          ' address or domain name is not found in our database.')

    elif r.status_code == 423:
        raise RequestError(r.status_code, 'If the queried IP address is a [bogon]() (bogus IP address from the bogon'
                                          ' space) IP address.')

    elif r.status_code == 429:
        raise RequestError(r.status_code, 'It is returned for one of the following reasons:\n\t(1) If the API usage '
                                          'limit has reached for the free subscriptions, or paid subscriptions with'
                                          ' the status "past due", "deleted" or "trial expired".\n\t(2) If the surcharge'
                                          ' API usage limit has reached against the subscribed plan.')
    else:
        raise RequestError('Unknown', 'Unknown')

