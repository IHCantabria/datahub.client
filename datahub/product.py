from datahub.variables import Variables


class Product(object):
    id = None
    extent = None
    name = None
    originName = None
    alias = None
    temporalResolutionHours = None
    spatialResolutionLonDegrees = None
    spatialResolutionLatDegrees = None
    spatialResolutionLonKm2 = None
    spatialResolutionLatKm2 = None
    added = None
    addedBy = None
    productFormat = None
    timeHorizon = None
    idSource = None
    active = None
    idProductType = None
    urlProduct = None
    license = None
    graphic = None
    ercurio = None
    startDate = None
    endDate = None
    urlBase = None
    urlXmlLatest = None
    urlCatalog = None

    def __init__(self, json):
        self.id = json["id"]
        self.extent = json["extent"]
        self.name = json["name"]
        self.originName = json["originName"]
        self.alias = json["alias"]
        self.temporalResolutionHours = json["temporalResolutionHours"]
        self.spatialResolutionLonDegrees = json["spatialResolutionLonDegrees"]
        self.spatialResolutionLatDegrees = json["spatialResolutionLatDegrees"]
        self.spatialResolutionLonKm2 = json["spatialResolutionLonKm2"]
        self.spatialResolutionLatKm2 = json["spatialResolutionLatKm2"]
        self.added = json["added"]
        self.addedBy = json["addedBy"]
        self.productFormat = json["productFormat"]
        self.timeHorizon = json["timeHorizon"]
        self.idSource = json["idSource"]
        self.active = json["active"]
        self.idProductType = json["idProductType"]
        self.urlProduct = json["urlProduct"]
        self.license = json["license"]
        self.graphic = json["graphic"]
        self.ercurio = json["mercurio"]
        self.startDate = json["startDate"]
        self.endDate = json["endDate"]
        self.urlBase = json["urlBase"]
        self.urlXmlLatest = json["urlXmlLatest"]
        self.urlCatalog = json["urlCatalog"]

    def __str__(self):
        return self.alias

    def __repr__(self):
        return self.alias

    @property
    def variables(self):
        return Variables().get_all_by_product(self.id)
