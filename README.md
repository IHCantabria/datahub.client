# Datahub.client

datahub.client is a python library to make it easy to query datahub and obtain data stored in thredds.


## Implemented features

### Datahub
* Consult product list
* Get a product by id / name / alias
* Get variables of a product

### Thredds
* Access a catalog based on a product
* Access to protected catalogs with authentication.
* Obtain characteristics of the dataset that make up the catalog (dates, areas)
* Obtain data for a point in a date period
* Download the data for a point in CSV and netcdf format
* Download in netcdf format the data for an area
* Download a dataset complete

## Known bugs
* Datasets require a begin and end date.

## Future features
* Use from API.Process
* Normalize data for each hour

## Examples
Examples can be found in the [doc folder](doc)

## Installation

### To use in your application, you can simply install it with:

```sh
python -m pip install git+ssh://git@github.com/IHCantabria/datahub.client@v0.2.1#egg=datahubclient
``` 

You will have the configuration file in the path:

```
{enviroment_path}/lib/python3.7/site-packages/datahub/config.json
```



### To download and work with the source code
These instructions are for linux system. Windows and Mac OS X will have similar instruccions.

#### Requirements
* python v3.6 or higher
* python3-venv
* git

#### Download and environment

Clone repository

```sh
git clone git@github.com:IHCantabria/datahub.client.git
```

Enter the repository

```sh
cd datahub.client
```

Create a virtualenv

```sh
python -m pip venv env --clear
```

Load the new virtualenv

```sh
source env/bin/activate
```

Install dependencies

```sh
python -m pip install -r requirements.txt
```

