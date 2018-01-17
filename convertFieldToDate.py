# encoding: utf-8

import gvsig
from org.gvsig.fmap.dal import DataTypes
from org.gvsig.fmap.dal import DALLocator
from org.gvsig.app import ApplicationLocator 
from java.util import Date
from java.util import Calendar
# encoding: utf-8

import gvsig
from gvsig.libs import gvpy
import os
from gvsig import geom
from org.gvsig.fmap.geom import Geometry
from org.gvsig.fmap.geom import GeometryLocator
from org.gvsig.fmap.geom.aggregate import MultiPrimitive
from org.gvsig.fmap.geom.primitive import Polygon, Point
# Con geometrias normales se quedaria con el getGeometryType()
from es.unex.sextante.dataObjects import IVectorLayer
from gvsig.libs.toolbox import ToolboxProcess
from es.unex.sextante.gui import core
from es.unex.sextante.gui.core import NameAndIcon
#from es.unex.sextante.parameters import ParameterDataObject
#from es.unex.sextante.exceptions import WrongParameterTypeException
from es.unex.sextante.additionalInfo import AdditionalInfoVectorLayer
#from gvsig import logger
#from gvsig import LOGGER_WARN
#from es.unex.sextante.additionalInfo import AdditionalInfo
from org.gvsig.geoprocess.lib.api import GeoProcessLocator
from org.gvsig.tools import ToolsLocator
from java.lang import Math
from org.gvsig.fmap.geom import Geometry
from org.gvsig.fmap.geom import GeometryLocator
from gvsig.libs.toolbox import *

class ConvertFieldToDate(ToolboxProcess):
  def defineCharacteristics(self):
    i18nManager = ToolsLocator.getI18nManager()
    
    self.setName(i18nManager.getTranslation("_Convert_field_to_date"))
    self.setGroup(i18nManager.getTranslation("_Transform"))
    params = self.getParameters()
    self.setUserCanDefineAnalysisExtent(False)
    params.addInputVectorLayer("inputVectorLayer",i18nManager.getTranslation("_Input_Layer"), AdditionalInfoVectorLayer.SHAPE_TYPE_ANY,True)
    params.addTableField("dateField1", i18nManager.getTranslation("_Date_Field_1"), "inputVectorLayer", True)
    params.addTableField("dateField2", i18nManager.getTranslation("_Date_Field_2"), "inputVectorLayer", True)
    params.addFilepath("outputFilePath",i18nManager.getTranslation("_Output_Layer"),False,False,True,[".shp"])
    params.addBoolean("changeDefaultValue",i18nManager.getTranslation("_Change_default_value"), False)
    params.addNumericalValue("defaultValue", i18nManager.getTranslation("_Default_value"),99999999, NUMERICAL_VALUE_INTEGER)
    params.addNumericalValue("changeForValue", i18nManager.getTranslation("_Change_for_value"),19991231, NUMERICAL_VALUE_INTEGER)


  def processAlgorithm(self):
    params = self.getParameters()
    inputVectorLayer = params.getParameterValueAsVectorLayer("inputVectorLayer").getFeatureStore()
    dateField1 = params.getParameterValueAsInt("dateField1")
    dateField2 = params.getParameterValueAsInt("dateField2")
    outputFilePath = params.getParameterValueAsString("outputFilePath")

    #Change default value
    changeDefaultValue = params.getParameterValueAsBoolean("changeDefaultValue")
    defaultValue = params.getParameterValueAsString("defaultValue")
    changeForValue = params.getParameterValueAsString("changeForValue")

    
    if outputFilePath == "":
        outputFilePath = gvsig.getTempFile("result_geometries",".shp")
    elif not outputFilePath.endswith('.shp'):
        outputFilePath = outputFilePath+".shp"
    process(inputVectorLayer,dateField1,dateField2,changeDefaultValue,defaultValue,changeForValue,outputFilePath,self)
    return True
    
def main(*args):
    process = ConvertFieldToDate()
    process.selfregister("Scripting")
    #gm = GeoProcessLocator.getGeoProcessManager()
    # Actualizamos el interface de usuario de la Toolbox
    process.updateToolbox()
    #layer = gvsig.currentLayer().getFeatureStore()
    #field = "FECHAALTA"
    #process(layer, field)

def intToDate(field):
    d = int(str(field)[6:8])
    m = int(str(field)[4:6])-1
    y = int(str(field)[0:4])
    calendar = Calendar.getInstance()
    calendar.set(y,m,d)
    return calendar.getTime()

# toDate(subString(toString([FECHAALTA]),6,8) +
# "/" + subString(toString([FECHAALTA]),4,6) + 
# "/" + subString(toString([FECHAALTA]),0,4),"dd/MM/yyyy")  

def process(fstore, field1,field2,changeDefaultValue,defaultValue,changeForValue,outputFilePath=None,selfStatus=None):
    print "process.."
    fset = fstore.getFeatureSet()#lection()
    ft = gvsig.createFeatureType(fstore.getDefaultFeatureType())
    nameField1 = ft.get(field1).getName()
    nameField2 = ft.get(field2).getName()
    fields = [field1, field2]
    allFields = [attr.getName() for attr in ft.getAttributeDescriptors()]
    n=0
    while True:
        n += 1
        if len(nameField1)>=10:
            newFieldName1 = nameField1[:-1]+str(n)
        else:
            newFieldName1 = nameField1+str(n)
        if newFieldName1 not in allFields:
            break
    n=0
    while True:
        n += 1
        if len(nameField2)>=10:
            newFieldName2 = nameField2[:-1]+str(n)
        else:
            newFieldName2 = nameField2+str(n)
        
        if newFieldName2 not in allFields and newFieldName1 != newFieldName2:
            break
            
    ft.add(newFieldName1,DataTypes.DATE)
    ft.add(newFieldName2,DataTypes.DATE)
    
    if outputFilePath is None:
        outputFilePath = gvsig.getTempFile("result",".shp")
    ns = gvsig.createShape(ft,filename=outputFilePath)
    ns.edit()
    dataManager = ApplicationLocator.getManager().getDataTypesManager() 

    for f in fset:
        nf = ns.getFeatureStore().createNewFeature(f)
        ## Value 1
        value1 = f.get(field1)
        if changeDefaultValue is True and str(value1)==str(defaultValue):
            value1 = changeForValue
        nf.set(newFieldName1, intToDate(value1))
        ## Value 2
        value2 = f.get(field2)
        if changeDefaultValue is True and str(value2)==str(defaultValue):
            value2 = changeForValue
        nf.set(newFieldName2, intToDate(value2))
        ns.getFeatureStore().insert(nf)
    ns.commit()
    gvsig.currentView().addLayer(ns)
            
            
