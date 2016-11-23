import logging

import googlemaps
import polyline
import json

from pylons import request, response, session, tmpl_context as c, url
from pylons.controllers.util import abort, redirect

from route_app.lib.base import BaseController, render


log = logging.getLogger(__name__)

class FetchroutesController(BaseController):

    def index(self):
        maps = self.init_google_maps('AIzaSyAF8n02MUVzzlMriqUMYb7rlSkaeBW1qDs')
        if not maps:
            log.info("Please Check Your API Key...")
        log.info("Maps Intialized...") 

        source = request.params.get("source")
        destination = request.params.get("destination")
        all_routes = self.find_all_routes(maps, source, destination)
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
