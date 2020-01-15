import os
import sys
sys.path.append('/usr/share/qgis/python/plugins')
#QGIS Packages
from qgis.core import *
from qgis.analysis import QgsNativeAlgorithms
import processing
from processing.core.Processing import Processing

#GBIF
from pygbif import occurrences as occ
from pygbif import utils

#INIT QGIS & PROCESSING W/ NATIVE TOOLS
QgsApplication.setPrefixPath("/usr/bin/qgis",True)
qgs = QgsApplication([],False)
qgs.initQgis()
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

#SHAPEFILE AS VECTOR
pathSalado = "/home/utkimchi/Documents/RoM/Mexican_Basins_Project/Shapefiles/El_Salado.shp"
saladoL = QgsVectorLayer(pathSalado,"Salado","ogr")
if not saladoL.isValid():
	print("Layer Failed to Load")

#CONVERT MULTIPART TO POLYGON
nSalado = processing.run('native:multiparttosingleparts',{ "INPUT" : saladoL, 'OUTPUT': 'memory:Test'})
fSalado = nSalado['OUTPUT']
count = 0
polygonGeo = {}

#ITERATE OVER POLYGON TO WKT COORDINATES
for shape in fSalado.getFeatures():
	print("Aye, Shapefiles number at: " + str(count))
	sGeo = shape.geometry()
	if QgsWkbTypes.isSingleType(sGeo.wkbType()):
		print("Polygon")
		sWKT = sGeo.asPolygon()
	else:
		print("MultipPolygon")
		sWKT = sGeo.asMultiPolygon()
	tList = ""
	fCoord = ""
	#Checks the # of points that make up the polygon an sets them
	#into the GBIF geomtry format
	n = len(sWKT[0])
	for xy in range(n):
		xx = sWKT[0][xy].x()	
		yy = sWKT[0][xy].y()
		nCoord = str(xx)[:6] + " " + str(yy)[:4]+", "
		if tList == "":
			fCoord = nCoord
		if nCoord not in tList:
			tList = tList + nCoord

	polygonGeo[count] = 'POLYGON((' + tList + fCoord[:-2]+'))'
	count += 1

qgs.exitQgis()

print(polygonGeo[0])
rwPG = utils.wkt_rewind(polygonGeo[0],digits=1)

#ADD GBIF QUERY 

ts = occ.search(geometry = rwPG, limit=2)

print (ts)