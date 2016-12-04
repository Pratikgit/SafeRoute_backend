import logging
import hashlib
import polyline
import googlemaps
import json
from pymongo import MongoClient

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
        final_paths = []
        maps = self.init_google_maps('AIzaSyAF8n02MUVzzlMriqUMYb7rlSkaeBW1qDs')
        if not maps:
            log.info("Please Check Your API Key...")

        source = request.params.get("source")
        destination = request.params.get("destination")
        all_routes = self.find_all_routes(maps, source, destination)
        path_score_dict = self.fetchPathsInfoFromDB(all_routes)
 
        route_distance_map = dict(zip(path_score_dict.get('path_array'), all_routes.get('distance_array')))
        route_safe_map = dict(zip(path_score_dict.get('path_array'), path_score_dict.get('score_array')))
        
        for path,safe_score in route_safe_map.iteritems():
            if safe_score == 0:
                client = MongoClient('localhost', 27017)
                db = client.SAFE_ROUTE_DB
                index = path_score_dict.get('path_array').index(path)
                polyline = all_routes.get('routes')[index]
                data = {'path_id': path,
                        'polyline': polyline}
                path_cache = db.Path_Cache
                record_id = path_cache.insert_one(data)
                log.info("Path Cached:%s" %record_id)

        log.info("Route Safe Map:%s" %route_safe_map)
        log.info("Route Distance Map:%s" %route_distance_map)
        
        safe_path_list = self.make_list_of_safe_paths(route_distance_map, route_safe_map)
        log.info("Safe Path List:%s" %safe_path_list)

        for search_id in safe_path_list:
            index = path_score_dict.get('path_array').index(search_id)
            final_paths.append(all_routes.get('routes')[index])

        log.info("Final Paths Polyline:%s" %final_paths)
        return json.dumps({'routes': final_paths})

    def make_list_of_safe_paths(self, route_distance_map, route_safe_map):
        final_route_list = []

        #Delete worst path
        max_path_tuple = max(route_safe_map.items(), key = lambda x: x[1])
        route_distance_map.pop(max_path_tuple[0])
        route_safe_map.pop(max_path_tuple[0])
        final_route_list.append(max_path_tuple[0])

        #Compare and remove paths whoose safe score is double to any other score
        for route,score in route_safe_map.iteritems():
            for temp_score in route_safe_map.values():
                if temp_score and score >= 2* temp_score:
                    final_route_list.append(route)
                    route_safe_map.pop(route)
                    route_distance_map.pop(route)
                    break

        #if more than 1 remains then return paths based on Distance 
        if len(route_safe_map.keys()) == 1:
            final_route_list.append(route)
        else:
            sorted_distance = sorted(route_distance_map.items(), key=lambda x: x[1], reverse = True)
            for path_tuple in sorted_distance:
                final_route_list.append(path_tuple[0])
 
        return final_route_list[::-1] 

    def init_google_maps(self, api_key):
        maps = googlemaps.Client(key = api_key)
        return maps if maps else None

    def find_all_routes(self, g_maps, source, destination, mode = 'driving', need_all_routes = True): 
        polyline_string_list = []
        distance_array = []
        all_routes = g_maps.directions(source, destination, mode = mode, 
                                alternatives = need_all_routes)
        log.info("Length of all routes:%s" %(len(all_routes)))

        for route in all_routes:
            polyline_string_list.append(route.get('overview_polyline').get('points'))
            path_distance = 0
            for leg in route['legs']:
                path_distance = leg['distance']['value']
            distance_array.append(path_distance)
        return {'routes': polyline_string_list, 'distance_array': distance_array}

    def fetchPathsInfoFromDB(self, all_route):
        path_array = []
        score_array = []
        resultValue = 0
        for route in all_route.get('routes'):
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
            path_array.append(search_id)
            score_array.append(resultValue)
        return {'score_array':score_array, 'path_array': path_array}
     
    def weightedAverage(self, crimeCount, accidentCount, policeCount):	
	return ((crimeCount * CRIME_FACTOR_WEIGHTAGE) + (accidentCount * ACCIDENT_FACTOR_WEIGHTAGE) 
                    - (policeCount * ROAD_FACILITY_WEIGHTAGE)) / 3

