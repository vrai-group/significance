from pymongo import MongoClient
import logging


logger = logging.getLogger('API-offline')


def db_connection(host: str, port: int, username, password, db_name):
    logger.info("Connect to the Database with username and password specification")
    client = MongoClient(host, port, username=username, password=password, authSource=db_name, authMechanism='SCRAM-SHA-256')
    return client


def get_collection(configuration: dict):
    client = db_connection(host=configuration['host'], port=int(configuration['port']), username=configuration['username'], password=configuration['password'], db_name=configuration['name'])
    logger.info("Get the db and collection for the working")
    return client[configuration['name']][configuration['collection']]
