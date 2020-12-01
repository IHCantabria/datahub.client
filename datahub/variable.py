class Variable(object):
    id = None
    nameShort = None
    nameLong = None
    alias = None
    aliasSp = None
    units = None
    idVariableTypes = None
    definition = None
    aliasShortEn = None
    aliasLongEn = None
    idCfConventions = (None,)
    scaleFactor = None
    offset = None
    idCfConventionsNavigation = None
    idVariableTypesNavigation = None
    productVariable = None

    def __init__(self, variable):
        self.id = variable["id"]
        self.nameShort = variable["nameShort"]
        self.nameLong = variable["nameLong"]
        self.alias = variable["alias"]
        self.aliasSp = variable["aliasSp"]
        self.units = variable["units"]
        self.idVariableTypes = variable["idVariableTypes"]
        self.definition = variable["definition"]
        self.aliasShortEn = variable["aliasShortEn"]
        self.aliasLongEn = variable["aliasLongEn"]
        self.idCfConventions = (variable["idCfConventions"],)
        self.scaleFactor = variable["scaleFactor"]
        self.offset = variable["offset"]
        self.idCfConventionsNavigation = variable["idCfConventionsNavigation"]
        self.idVariableTypesNavigation = variable["idVariableTypesNavigation"]
        self.productVariable = variable["productVariable"]

    def __str__(self):
        return self.nameShort

    def __repr__(self):
        return self.nameShort
