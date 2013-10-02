"""
Implement repository pattern to CRUD stores in database
"""
import pymongo
from bson.objectid import ObjectId

from restapp.models import ExternalStore

class StoreRepository(object):
    """
    Implement repository pattern to CRUD stores in database
    """

    def __init__(self, db_settings):
        try:
            if (db_settings['REPLSET'] == ""):
                self.connection = pymongo.MongoClient(db_settings['HOST'], db_settings['PORT'])
            else:
                self.connection = pymongo.MongoClient(db_settings['HOST'], db_settings['PORT'],
                                                      replicaset=db_settings['REPLSET'])
        except pymongo.errors.AutoReconnect as ex:
            #raise api.CouldNotConnectToDatabase(ex.message)
            raise
        except pymongo.errors.ConnectionFailure as ex:
            #raise api.CouldNotConnectToDatabase(ex.message)
            raise
        try:
            self._system_db = self.connection[db_settings['SYS_DB_NAME']]
            self._stores_collection = self._system_db["stores"]
        except Exception as ex:
            #raise api.CouldNotConnectToDatabase(ex.message)
            raise
        #self.collection.create_index([("location", pymongo.GEO2D), ("category", pymongo.ASCENDING)],
        #safe=True)

    def add_store(self, external_store):
        """Add a new store into repository and return new store id as str"""

        try:
            new_store = dict()
            new_store['name'] = external_store.name
            new_store['address'] = external_store.address
            store_id = self._stores_collection.insert(new_store, safe=True)

            return str(store_id)
        except (pymongo.errors.OperationFailure, pymongo.errors.AutoReconnect) as ex:
            #raise api.DatabaseOperationError('add store: ' + ex.message)
            raise

    def delete_store(self, store_id):
        """Delete the store with the given id"""

        criteria = {'id': store_id}
        try:
            #object_id = ObjectId(store_id)
            return self._stores_collection.remove(criteria)
        except (pymongo.errors.OperationFailure, pymongo.errors.AutoReconnect) as ex:
            raise
            #raise api.DatabaseOperationError('delete store: ' + ex.message)

    def find_store_by_id(self, store_id):
        """Return store with given id or None if not found"""

        criteria = {'_id': ObjectId(store_id)}
        try:
            internal_store = self._stores_collection.find_one(criteria)
        except (pymongo.errors.OperationFailure, pymongo.errors.AutoReconnect) as ex:
            #raise api.DatabaseOperationError('find store: ' + ex.message)
            raise

        if internal_store is None:
            return None
        else:
            return _convert_to_external_store(internal_store)

    def find_stores_by_criteria(self, criteria):
        """Return store matching given criteria"""

        # add pagination!
        try:
            internal_stores = self._stores_collection.find(criteria)
        except (pymongo.errors.OperationFailure, pymongo.errors.AutoReconnect) as ex:
            #raise api.DatabaseOperationError('find stores: ' + ex.message)
            raise

                        #{
                        #    "location": {
                        #        "$maxDistance": distance,
                        #        "$near": [resource["latitude"], resource["longitude"]]
                        #        },
                        #    "category": resource["category"]
                        #}).limit(1)     # Limit is equal to the amount of providers by category

        external_stores = list()
        for store in internal_stores:
            external_stores.append(_convert_to_external_store(store))

        return external_stores


def _convert_to_external_store(internal_store):
    """Convert a store from internal representation to the external one"""

    #class ExternalStore(object):
    #    def __init__(self, store):
    #        self.raw_obj = store
    #        self.pk = str(store['_id'])
    #        self.name = store['name']
    #        self.address = store['address']

    return ExternalStore(internal_store)
    #return external_store
