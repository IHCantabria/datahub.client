# Installation
### To use in your application, you can simply install it with:

```sh
python -m pip install git+ssh://git@github.com/IHCantabria/datahub.client@v0.2.1#egg=datahubclient
``` 

You will have the configuration file in the path:

```
{enviroment_path}/lib/python{your-python-version}/site-packages/datahub/config.json
```

There are several ways to install it depending on the operating system and python frameworks.

## 1. Unix (linux) and pip

#### Requirements
* python v3.6 or higher
* python3-venv
* git

#### Download and environment

Create a virtualenv

```sh
python -m pip venv env --clear
```

Load the new virtualenv

```sh
source env/bin/activate
```

Install datahub.client

```sh
python -m pip install git+git://github.com/IHCantabria/datahub.client.git
```

## 2. Windows and Anaconda

#### Requirements
* [Anaconda](https://www.anaconda.com/products/individual#Downloads)

#### Enviroment and packages
Create a enviroment and load it

```
conda create --name {MyEnvironmentName}
conda activate {MyEnvironmentName}
```

Install git

```
conda install git
````

Install pip

```
conda install pip
````

#### Install datahub.client using pip

```
pip install git+git://github.com/IHCantabria/datahub.client.git
```