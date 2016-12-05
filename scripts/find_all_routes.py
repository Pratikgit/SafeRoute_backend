import googlemaps
import polyline

def init_google_maps(api_key):
    maps = googlemaps.Client(key = api_key)
    return maps if maps else None

def find_all_routes(g_maps, source, destination, mode = 'driving', need_all_routes = True):
    polyline_string_list = []
    all_routes = g_maps.directions(source, destination, mode = mode, 
                            alternatives = need_all_routes)
    for route in all_routes:
        polyline_string_list.append(route.get('overview_polyline').get('points'))
    
    return polyline_string_list 

def decode_polyline_to_coordinates(encoded_polyline):
    new_list = []
    coordinate_list = polyline.decode(encoded_polyline)
    for d in coordinate_list:
        new_list.append(tuple(str(j) for j in d))
    return new_list

if __name__ == '__main__':
    maps = init_google_maps('AIzaSyAF8n02MUVzzlMriqUMYb7rlSkaeBW1qDs')
    if not maps:
        print "Please Check Your API Key..."

    all_routes = find_all_routes(maps, 'Inner Harbor Baltimore', 'Jefferson Street, Baltimore')

    for route in all_routes:
        print decode_polyline_to_coordinates(route)

    

