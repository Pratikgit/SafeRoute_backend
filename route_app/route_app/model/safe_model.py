import pymongo
from pymongo import MongoClient

CRIME_FACTOR_WEIGHTAGE = 0.5
ACCIDENT_FACTOR_WEIGHTAGE = 0.3
ROAD_FACILITY_WEIGHTAGE = 0.2

class safe_model():
    def __init__(self):
        pass

    def findPathDetailsByID(self,host,db,collection,search_id):
        hconn = self.getConnection(host)
        hdb = self.getDBDetails(hconn, db)
        hcoll = self.getCollectionDetails(hdb, collection)

        try:
	    query = {"path_id" : search_id}
            cursor = hcoll.find(query, {"crime_count":1, "accident_count":1, "hospital_police_services":1, "_id":0})
        except Exception as e:
            print "Unexpected error:", type(e), e
        return cursor
  
    def getConnection(self,host):
        try:
            retConnection = MongoClient(host)
        except Exception  as e:
            print 'Exception occurred while creating connection with mongoDB, value: \n '
            print e
        return retConnection

    def getDBDetails(self,connection,db):
        # create a database connection
        try :
            retDb = connection[db] # NOTE : dictionary style access
        except Exception as e:
            print 'Exception occurred while connecting to database %s, value: \n ' % db
            print e
        return retDb

    def getCollectionDetails(self,db,collection):
        #create a handle for collection
        try :
            retCollection = db[collection] # NOTE : dictionary style access
        except Exception as e:
            print 'Exception occurred while getting details for  collection:  %s, value: \n ' % collection
            print e
        return retCollection

