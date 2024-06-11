from pymongo import MongoClient
from retry import retry


def db_connection(host: str, port: int, username, password, db_name):
    client = MongoClient(host, port, username=username, password=password, authSource=db_name, authMechanism='SCRAM-SHA-256')
    return client


def get_collection(configuration: dict):
    client = db_connection(host=configuration['host'], port=int(configuration['port']), username=configuration['username'], password=configuration['password'], db_name=configuration['name'])
    return client[configuration['name']][configuration['collection']]


@retry(ValueError, tries=10, delay=1, max_delay=5)
def apply_update(collection, data, update):
    if collection.count_documents({'_id': data['_id']}) != 0:
        if collection.update_one({"$and": [{"_id": data['_id']}, {"analysis.dominance_color": {"$exists": True}}]}, {"$set": {"analysis.dominance_color": update['dominance_color']}}) == 0:
            collection.update_one({"_id": data['_id']}, {"$set": {"analysis": update}}, upsert=True)
        else:
            raise ValueError("Update not applied")
    else:
        data['analysis'] = update
        if collection.insert_one(data) == 0:
            raise ValueError("Update not applied")
    return True


database_dict = {
            "read": {
                "host": "cresco-mgdb04.portici.enea.it",
                "port": "27017",
                "username": "coco",
                "password": "DepecheMode",
                "name": "miafashion",
                "collection": "instaloader"
            },
            "write": {
                "host": "cresco-mgdb04.portici.enea.it",
                "port": "27017",
                "username": "dior",
                "password": "AltaModa",
                "name": "miafashion",
                "collection": "test"
            }
        }

collection: dict = {}
collection['read'] = get_collection(configuration=database_dict['read'])
collection['write'] = get_collection(configuration=database_dict['write'])

for data in collection['read'].find({}, no_cursor_timeout=True):
    imgs_count = len(data['imgs'])
    for index, img_name in enumerate(data['imgs']):
        # TODO verificare che i vari pezzi siano completati
        # TODO per la dominanza bisogna verificare che vi sia già l'array con elementi dentro e vedere se corrisponde al numero di immagini
        count = 0
        if 'analysis' in data.keys():
            output = data['analysis']
            print("Analysis found: ", data['_id'], output)
            output.append([[2, 4, 5], [3, 5, 6], [5, 6, 6]])
        else:
            output = [[2, 4, 5], [3, 5, 6], [5, 6, 6]]
    apply_update(collection=collection['write'], data=data, update=output)
