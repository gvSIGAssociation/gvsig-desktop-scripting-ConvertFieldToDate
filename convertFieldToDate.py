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


class ConvertFieldToDate(ToolboxProcess):
  def defineCharacteristics(self):
    i18nManager = ToolsLocator.getI18nManager()
    
    self.setName(i18nManager.getTranslation("_Convert_field_to_date"))
    self.setGroup(i18nManager.getTranslation("_Transform"))
    params = self.getParameters()
    self.setUserCanDefineAnalysisExtent(False)
    params.addInputVectorLayer("inputVectorLayer",i18nManager.getTranslation("_Input_Layer"), AdditionalInfoVectorLayer.SHAPE_TYPE_ANY,True)
    params.addTableField("dateField", i18nManager.getTranslation("_Date_Field"), "inputVectorLayer", True)
    params.addFilepath("outputFilePath",i18nManager.getTranslation("_Output_Layer"),False,False,True,[".shp"])

  def processAlgorithm(self):
    params = self.getParameters()
    inputVectorLayer = params.getParameterValueAsVectorLayer("inputVectorLayer").getFeatureStore()
    dateField = params.getParameterValueAsInt("dateField")
    outputFilePath = params.getParameterValueAsString("outputFilePath")
    
    if outputFilePath == "":
        outputFilePath = gvsig.getTempFile("result_geometries",".shp")
    elif not outputFilePath.endswith('.shp'):
        outputFilePath = outputFilePath+".shp"
    process(inputVectorLayer,dateField,outputFilePath,self)
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

def process(fstore, field,outputFilePath=None,selfStatus=None):
    print "process.."
    fset = fstore.getFeatureSet()#lection()
    ft = gvsig.createFeatureType(fstore.getDefaultFeatureType())
    nameField = ft.get(field).getName()
    allFields = [attr.getName() for attr in ft.getAttributeDescriptors()]
    n=0
    while True:
        n += 1
        newFieldName = nameField+str(n)
        if newFieldName not in allFields:
            break
        
    ft.add(newFieldName,DataTypes.DATE)

    if outputFilePath is None:
        outputFilePath = gvsig.getTempFile("result",".shp")
    ns = gvsig.createShape(ft,filename=outputFilePath)
    ns.edit()
    dataManager = ApplicationLocator.getManager().getDataTypesManager() 

    for f in fset:
        nf = ns.getFeatureStore().createNewFeature(f)
        nf.set(newFieldName, intToDate(f.get(field)))
        ns.getFeatureStore().insert(nf)
    ns.commit()
    gvsig.currentView().addLayer(ns)
            
            
