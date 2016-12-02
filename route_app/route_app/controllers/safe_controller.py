import logging
import hashlib
import polyline
import googlemaps
import json

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect
from route_app.model.safe_model import *
from hashlib import md5

from route_app.lib.base import BaseController, render

log = logging.getLogger(__name__)

class SafeControllerController(BaseController):

    global a
    
    a = safe_model()

    def index(self):
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
           log.info("Safe Score of Path %s:%s" %(path_count, pathScore))
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
	resultValue = None
        m = hashlib.md5()
        m.update(route.encode('utf-8'))
        search_id =  m.hexdigest()
        log.info("Path ID to be searched (md5):%s" %search_id)

        c = a.findPathDetailsByID("mongodb://localhost","SAFE_ROUTE_DB","Paths_Info", str(search_id))
        for j in c:
	    crimeCount = j['crime_count']
	    accidentCount = j['accident_count']
	    policeCount = j['hospital_police_services']
	    resultValue = self.weightedAverage(crimeCount, accidentCount, policeCount)

        return resultValue
     
    def weightedAverage(self, crimeCount, accidentCount, policeCount):	
	return ((crimeCount * CRIME_FACTOR_WEIGHTAGE) + (accidentCount * ACCIDENT_FACTOR_WEIGHTAGE) 
                    - (policeCount * ROAD_FACILITY_WEIGHTAGE)) / 3

