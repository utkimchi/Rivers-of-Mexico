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
#POST Stuff
import requests as r
import time
import json

#INIT QGIS & PROCESSING W/ NATIVE TOOLS
QgsApplication.setPrefixPath("/usr/bin/qgis",True)
qgs = QgsApplication([],False)
qgs.initQgis()
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

#SHAPEFILE AS VECTOR
pathSalado = "/home/utkimchi/Documents/RoM/Mexican_Basins_Project/Shapefiles/el_salado_smooth.shp"
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
	#Checks the # of points that make up the polygon and sets them
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

downloadLinks = {}

for x in range(len(polygonGeo)):
	print ("Looking at Polygon ", x)
	print(polygonGeo[x])

	#Proper WKT format
	rwPG = utils.wkt_rewind(polygonGeo[x],digits=1)

	url = 'http://api.gbif.org/v1/occurrence/download/request'

	#JSON parameters
	jsonPayload = {"creator":YOURNAME_STR, \
	"notificationAddresses":[YOUREMAIL_STR], \
	"format":"SIMPLE_CSV", \
	'predicate':{'type':'within', 'geometry':rwPG}}

	#POST Headers
	headers = {'Content-Type': 'application/json'}

	#Final POST request
	req = r.post(url,headers=headers,json=jsonPayload,auth=(USERNAME_STR,PASSWORD_STR))
	
	#Generates download links for each polygon
	print("Waiting 60 Seconds for download to complete")
	time.sleep(60)
	downloadreq = r.get('http://api.gbif.org/v1/occurrence/download/' + req.text)
	ddic = json.loads(downloadreq.text)
	downloadLinks[x] = ddic["downloadLink"]

with open('dFile.txt','w') as f:
	print(downloadLinks,file=f)

qgs.exitQgis()