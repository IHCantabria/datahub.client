# Changelog

## 0.7.0 (2020.11.26)
- Remove Products.get_by_name_alias method
- Add Products.filter method
- Dates are datetime, not str
- Auth config using id instead of name
- Auth using a tuple as parameter auth=(user,pw)
- Add str and repr method to classes
  
## 0.6.1 (2020.11.24)
- start and end are optional opening a xarray connection
- fix open_xarray_conn in catalog

## 0.6.0 (2020.11.23)
- Filter xarray dataset by date and extent
- Add credential data to opendap url

## 0.5.0 (2020.11.20)
- Add latest dataset as a catalog property

## 0.4.0 (2020.11.20)
- Get xarray connection from a dataset
- Get xarray connection of the datasets from a catalog

## 0.3.6 (2020.11.16)
### Features
- Get variables from a product
- Filter variables using nameShort

## 0.3.5 (2020.10.15)
### Features
- Add metadata info to netcdf (offset, scale factor and date) (0.3.4)
- Fix error in previous version. Improved tests

## 0.3.3 (2020.10.02)
### Features
- Replace values == _fillvalue with None

## 0.3.2 (2020.10.01)
### Bugfix
- Fix test data (v0.3.1)

### Features
- Add new method `get_by_product_filtered_by_name` in Variable. (v0.3.2)


## 0.3.0 (2020.09.09)
### Bugfix
- Calculate correct value using offset and scale factor.

## 0.2.3 (2020.08.27)
- Begin and end dates are optional
- Fix product properties
- Fix test result
- Update linux instructions and add for windows
  
## 0.2.1 (2020.06.29)
### Bugfix
- Remove `pkg-resources==0.0.0` from `requirements.txt`.

## 0.2.1 (2020.06.19)
### Features
- Download dataset file as the original.

## 0.2.0 (2020.06.02)
### Features

#### Datahub
* Consult product list
* Get a product by id / name / alias
* Get variables of a product

#### Thredds
* Access a catalog based on a product
* Access to protected catalogs with authentication.
* Obtain characteristics of the dataset that make up the catalog (dates, areas)
* Obtain data for a point in a date period
* Download the data for a point in CSV and netcdf format
* Download in netcdf format the data for an area

