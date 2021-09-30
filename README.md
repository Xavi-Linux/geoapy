# GEOAPY
----

This repository provides a Python-based handler for [ipgeolocation](https://ipgeolocation.io/)'s API service.

## Requirements:
----

1. You must sign up for a free-plan account at [ipgeolocation.io](https://ipgeolocation.io/signup.html).
2. This project relies on the third-party library **requests**. Please, make sure it is available to your Python interpreter or execute on your command line interface:

```Shell
pip3 install requests
```

## Before start using the API...
----

1. Consider if you want to register the package to access globally. A simple strategy is to create a symbolic link in the dist-packages folder.
2. Copy the API key you have been given by ipgeolocation.
3. Register the API key by running:

```Python
import geoapy as g

g.registerkey('a2ddede8d8eab2123') #using an invented key as example!

```

## Limitations:
----

1. The API handler just covers the free-plan account features.
2. It only accepts ips in ipv4 format (xxx.xxx.xxx.xxx).

## Examples:
----

##### Get to know what information the API is able to send:

```Python
import geoapy as g

print(g.listfields())

```

##### Search for an IP:

```Python
import geoapy as g

r = g.get('123.123.123.123') # get a response object 

print(r) #check all the retrieved information in a dictionary-like fashion.

print(r.zipcode) #access and manipulate information in an object-oriented way.

```

##### Receive filtered responses:

```Python
import geoapy as g

r = g.get('123.123.123.123', ['country_name', 'zipcode'])  

```

##### Avoid querying the API for the same ip multiple times by caching results:


```Python
import geoapy as g

r = g.get('123.123.123.123', ['country_name', 'zipcode'])  

r.cache()

```

