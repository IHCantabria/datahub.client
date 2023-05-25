# Datahub.client

datahub.client is a python library to make it easy to query datahub and obtain data stored in thredds.  

```diff
- Important! This repository is out maintenance
```

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

## Future features
* Use from API.Process
* Normalize data for each hour

## Examples
Examples can be found in the [doc folder](doc)

## Installation

Instructions are in the [INSTALL.md](INSTALL.md) file.
