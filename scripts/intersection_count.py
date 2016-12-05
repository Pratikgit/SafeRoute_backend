from pyspark import SparkContext
import sys
from geopy.distance import great_circle
import polyline
from pymongo import MongoClient


sc = SparkContext("local", "Safe App")
a = sc.accumulator(0)
cl = MongoClient("ec2-35-161-196-226.us-west-2.compute.amazonaws.com", 27017)
path_cache = cl.SAFE_ROUTE_DB.Path_Cache
path_info = cl.SAFE_ROUTE_DB.Paths_Info

def f(poly_string):
    def _f(x):
        global a
        points = polyline.decode(poly_string)
        for point in points:
            if great_circle(point, x).miles <= 0.1:
                a +=1
                break
        return
    return _f
    
if __name__ == "__main__":
    c = sc.textFile("hdfs://localhost:9000/user/mayur/f_new_crime.csv").map(lambda line: line.split(',')).map(lambda field:(field[9],field[10])).map(lambda record: (float(record[0]) if record[0].replace('.','',1).isdigit() else 0, float(record[1]) if record[1].replace('.','',1).replace('-','',1).isdigit() else 0))
    for path in path_cache.find():
        c.foreach(f(path['polyline']))
        print "Path is:%s and Crime Count:%s" %(path['path_id'],a.value)
        new_path = {'polyline': path['polyline'],
                'path_id': path['path_id'],
                'crime_count': a.value,
                'accident_count': 0,
                'hospital_police_services': 5}
        record_id = path_info.insert_one(new_path)
        print "Record Created in Mongo:%s" %(record_id)
        #path_cache.delete_many({"path_id": path['path_id']})
        a = sc.accumulator(0)

