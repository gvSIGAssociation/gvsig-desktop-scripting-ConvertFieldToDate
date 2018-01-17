# encoding: utf-8

import gvsig
from addons.ConvertFieldToDate.convertFieldToDate import ConvertFieldToDate
from org.gvsig.tools import ToolsLocator
from java.io import File

def main(*args):
    selfRegister()
    
def selfRegister(*args):
    i18nManager = ToolsLocator.getI18nManager()
    i18nManager.addResourceFamily("text",File(gvsig.getResource(__file__,"i18n")))
    
    process = ConvertFieldToDate()
    process.selfregister("Scripting")
    process.updateToolbox()

    
