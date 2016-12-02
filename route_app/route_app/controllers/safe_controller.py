import logging
import hashlib
import polyline
import googlemaps
import json

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from safe_route.model.safe_model import safe_model
from hashlib import md5
from pprint import pprint

from safe_route.lib.base import BaseController, render

log = logging.getLogger(__name__)

class SafeControllerController(BaseController):

    global a
    
    a = safe_model()

    def index(self):
	global path_count
	path_count = 1
        maps = self.init_google_maps('AIzaSyAF8n02MUVzzlMriqUMYb7rlSkaeBW1qDs')
        if not maps:
            log.info("Please Check Your API Key...")
        log.info("Maps Intialized...") 

        source = request.params.get("source")
        destination = request.params.get("destination")
        all_routes = self.find_all_routes(maps, source, destination)

	for route in all_routes.get('routes'):
	   pathScore = self.fetchPathsInfoFromDB(route)	
           print "Safe Score of Path  " , path_count, " : "
	   pprint(pathScore)
	   path_count = path_count + 1

        return json.dumps(all_routes)

    def init_google_maps(self, api_key):
        maps = googlemaps.Client(key = api_key)
        return maps if maps else None

    def find_all_routes(self, g_maps, source, destination, mode = 'driving', need_all_routes = True):
        polyline_string_list = []
        all_routes = g_maps.directions(source, destination, mode = mode, 
                                alternatives = need_all_routes)
        for route in all_routes:
            polyline_string_list.append(route.get('overview_polyline').get('points'))
    
        return {'routes': polyline_string_list}

    def fetchPathsInfoFromDB(self, route):
        global resultValue
        crimeCount = None
	accidentCount = None
	policeCount = None
	resultValue = None
        m = hashlib.md5()
        m.update(route.encode('utf-8'))
        search_id =  m.hexdigest()
        print "Path ID to be searched (md5)", search_id

        c = a.findPathDetailsByID("mongodb://localhost","SAFE_ROUTE_DB","Paths_Info", str(search_id))
        for j in c:
            print j
	    crimeCount = j['crime_count']
	    accidentCount = j['accident_count']
	    policeCount = j['hospital_police_services']
	    resultValue = self.weightedAverage(crimeCount, accidentCount, policeCount)

        return resultValue
     
    def weightedAverage(self, crimeCount, accidentCount, policeCount):
	global crimeFactorWeightage, accidentFactorWeightage, policeFactorWeightage, resultValue
        
	test = a.findFactorWeightage("mongodb://localhost","SAFE_ROUTE_DB","Factors_Weightage", "Crime")
        for i in test:
            crimeFactorWeightage =  i['weightage']

	test = a.findFactorWeightage("mongodb://localhost","SAFE_ROUTE_DB","Factors_Weightage", "Accident")
        for i in test:
            accidentFactorWeightage =  i['weightage']

	test = a.findFactorWeightage("mongodb://localhost","SAFE_ROUTE_DB","Factors_Weightage", "Police and Health Services")
        for i in test:
            policeFactorWeightage =  i['weightage']
	
	resultValue = ((crimeCount*crimeFactorWeightage) + (accidentCount*accidentFactorWeightage) + (policeCount*policeFactorWeightage))/3
	#print "Crime: ", crimeFactorWeightage, "Accident: ", accidentFactorWeightage, "Police and Health: ", policeFactorWeightage

	return resultValue
