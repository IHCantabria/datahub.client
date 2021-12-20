# Changelog

## 0.9.3
- Fix load env values

## 0.9.2
- Fix SECRET_AUTH env key is not required.
## 0.9.1
- Add enconding to compress netCDF4.
## 0.9.0
- Use the `.env` file to find out what environment it is in and where to record the log.
- Change `setup.py` to `pyproject.toml`
### 0.8.6
- Fix join multiples datasets in `catalog.download`.
- Fix error in 0.8.5
### 0.8.4
- Fix close dataset. This error was only on Windows.
### 0.8.3
- Fix `get_by_product_filtered_by_name`.
  
### 0.8.2
- Download multiples files from catalog and merge them into one
- Dates and extent is optional for download datsets
- Default format is netCDF4 now.

### 0.8.1
- Add optional `format` parameter for `datetime_to_string` and `string_to_datetime` functions.
  
## 0.8.0
- Open all datasets in a catalog using xarray
## 0.7.3
- Fix lxml dependency
## 0.7.2
- Fix Variables returning variable objects

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

