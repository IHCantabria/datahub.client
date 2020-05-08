import json
import requests
from xml.etree import ElementTree
import csv
from io import StringIO
from datahub import Conf

class ProductThredds():
    def __init__(self, datahub_product):
        self.datahub_product = datahub_product
    def get_data(self):
       # Obtener  latestNcssUrl __getLatestNcssUrl
       latestNcssUrl = self._getLatestNcssUrl()
       return latestNcssUrl

    def _getLatestNcssUrl(self):
        productLatest = requests.get(
            "{0}{1}".format(self.datahub_product["urlBase"], self.datahub_product["urlXmlLatest"])
        )
        tree = ElementTree.fromstring(productLatest.content)
        service = tree.find(
            "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0}service"
        )
        for child in service:
            if child.attrib["name"] == "ncss":
                ncssPath = child.attrib["base"]
        dataset = tree.find(
            "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0}dataset"
        )
        latestNcssUrl = "{0}{1}{2}".format(
            self.datahub_product["urlBase"], ncssPath, dataset.attrib["urlPath"]
        )
        return latestNcssUrl

class DatahubAccess:
    def __init__(
        self, idProduct, idVariable, longitude, latitude, startDate=None, endDate=None
    ):
        self.idProduct = idProduct
        self.idVariable = idVariable
        self.startDate = startDate
        self.endDate = endDate
        self.longitude = longitude
        self.latitude = latitude

    def __getDates(self, latestNcssUrl):
        if self.startDate == None or self.endDate == None:
            datasetDetailsGet = requests.get("{0}/dataset.xml".format(latestNcssUrl))
            datasetDetails = ElementTree.fromstring(datasetDetailsGet.content)
            begin = datasetDetails.find("TimeSpan").find("begin").text
            end = datasetDetails.find("TimeSpan").find("end").text
        else:
            begin = self.startDate
            end = self.endDate
        return begin, end

    def __getLatestNcssUrl(self):
        productGet = requests.get(
            "{0}Products/{1}".format(Conf.datahubUrl, self.idProduct)
        )
        product = json.loads(productGet.content.decode("utf-8"))
        productLatest = requests.get(
            "{0}{1}".format(product[0]["urlBase"], product[0]["urlXmlLatest"])
        )
        tree = ElementTree.fromstring(productLatest.content)
        service = tree.find(
            "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0}service"
        )
        for child in service:
            if child.attrib["name"] == "ncss":
                ncssPath = child.attrib["base"]
        dataset = tree.find(
            "{http://www.unidata.ucar.edu/namespaces/thredds/InvCatalog/v1.0}dataset"
        )
        latestNcssUrl = "{0}{1}{2}".format(
            product[0]["urlBase"], ncssPath, dataset.attrib["urlPath"]
        )
        return latestNcssUrl

    def __getVariable(self, idVariable):
        variableGet = requests.get(
            "{0}Variables/{1}".format(Conf.datahubUrl, self.idVariable)
        )
        variable = json.loads(variableGet.content.decode("utf-8"))
        return variable

    def get_data(self):
        latestNcssUrl = self.__getLatestNcssUrl()
        begin, end = self.__getDates(latestNcssUrl)
        variable = self.__getVariable(self.idVariable)
        latestNcssUrlVariables = "{0}?var={1}".format(
            latestNcssUrl, variable[0]["nameShort"]
        )
        ncssUrl = "{0}&longitude={1}&latitude={2}&time_start={3}&time_end={4}&accept={5}&vertCoord=0.49402499198913574".format(
            latestNcssUrlVariables,
            self.longitude,
            self.latitude,
            begin,
            end,
            Conf.responseFormat,
        )
        response = requests.get(ncssUrl)
        csvFile = StringIO(response.text)
        if not "Lat/Lon" in response.text:
            csv_reader = csv.reader(csvFile, delimiter=",")
            next(csv_reader)
            with open("output.csv", mode="w", newline="") as output:
                spamwriter = csv.writer(
                    output, delimiter=";", quoting=csv.QUOTE_MINIMAL
                )
                for row in csv_reader:
                    spamwriter.writerow(
                        [
                            row[0],
                            row[1],
                            row[2],
                            float(row[3]) * variable[0]["scaleFactor"]
                            + variable[0]["offset"],
                        ]
                    )
        else:
            print(response.text)