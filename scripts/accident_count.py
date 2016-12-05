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
    c = sc.textFile("hdfs://localhost:9000/user/mayur/Accident.csv").map(lambda line: line.split(',')).map(lambda field:(field[4],field[5])).map(lambda record: (float(record[0]) if record[0].replace('.','',1).isdigit() else 0, float(record[1]) if record[1].replace('.','',1).replace('-','',1).isdigit() else 0))
    for path in path_cache.find():
        c.foreach(f(path['polyline']))
        print "Path is:%s and Accident Count:%s" %(path['path_id'],a.value)
        path_rec = path_info.find_one({'path_id': path['path_id']})
        if path_rec is not None:
            path_rec['accident_count'] = a.value
            path_info.save(path_rec)
        path_cache.delete_many({"path_id": path['path_id']})
        a = sc.accumulator(0)

