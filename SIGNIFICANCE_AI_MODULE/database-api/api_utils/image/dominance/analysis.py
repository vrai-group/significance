from api_utils.image.path_generation import img_path_generator
from api_models.dominance.clustering_dominance_color import dominance_color
from api_utils.output.output_format import analysis_output
from pymongo import errors
from retry import retry
import threading
import logging


logger = logging.getLogger('API-offline')


def compute_dominance(base_image_path: str, image_name: str, model_configuration: dict) -> list:
    logger.info("Compute the dominance color")
    img_path = img_path_generator(base_image_path, image_name)
    logger.info("Image path: ", img_path)
    dominance_list = dominance_color(config=model_configuration, img_path=img_path)
    logger.info("Dominance color list obtained: ", dominance_list)
    return dominance_list


@retry(ValueError, tries=10, delay=1, max_delay=5)
def apply_update(collection, data, update):
    logger.info("Update the database...")
    if collection.count_documents({'_id': data['_id']}) != 0:
        logger.info(f"Found a document with the _id: {data['_id']}")
        if collection.update_one({"$and": [{"_id": data['_id']}, {"analysis.dominance_color": {"$exists": True}}]}, {"$set": {"analysis.dominance_color": update['dominance_color'], "analyzed.dominance": True}}) == 0:
            logger.info("Dominance color not updated in the document")
            logger.info("Try to update the analysis key at all")
            collection.update_one({"_id": data['_id']}, {"$set": {"analysis": update, "analyzed.dominance": True}}, upsert=True)
            logger.info("Updated the analysis key at all")
        else:
            logger.info("Document not updated... retry later")
            return ValueError("Update not applied")
    else:
        data['analysis'] = update
        logger.info("The document does not exist.")
        logger.info("Insert the document in the collection")
        if collection.insert_one(data) == 0:
            return ValueError("Update not applied")
    logger.info("Document updated")
    return True


def update_dominance(collection, data_list, config_parameter):
    logger.info("Start the update of the dominance colour")
    for data in data_list:
        imgs_count = len(data['imgs'])
        logger.info(f"Founded {imgs_count} images in the document with _id {data['_id']}")
        for index, img_name in enumerate(data['imgs']):
            # TODO verificare che i vari pezzi siano completati
            # TODO per la dominanza bisogna verificare che vi sia già l'array con elementi dentro e vedere se corrisponde al numero di immagini
            count = 0
            if 'analyzed' in data.keys():
                logger.info("Get the analyzed presence from the document")
                analyzed = data['analyzed']
            else:
                logger.info("Created the new analyzed structure for the document")
                analyzed = {
                    "classification": False,
                    "dominance": False,
                    "detection": False
                }
            if analyzed['classification'] or analyzed['dominance'] or analyzed['detection']:
                logger.info("The document was already analyzed: try to loading old analysis")
                if 'analysis' in data.keys():
                    output = data['analysis']
                    logger.info("Loaded the old analysis result")
                else:
                    logger.info("Created the analysis structure because it is not present")
                    output = analysis_output
            else:
                logger.info("Created the analysis structure because it is the first time that this document will be analyzed")
                output = analysis_output
            if 'analysis' in data.keys():
                logger.info("Founded a previous analysis in the document")
                output = data['analysis']
                if len(output['dominance_color']) == imgs_count:
                    logger.info("The analysis has the same number of images in the dominance_color")
                    continue
                else:
                    logger.info("Update the analysis with new dominance_color")
                    dominance_list = compute_dominance(base_image_path=config_parameter['data']['images']['base'], image_name=img_name, model_configuration=config_parameter['model']['dominance'])
                    output['dominance_color'].insert(index, dominance_list)
            else:
                logger.info("Analysis not found. It was created")
                output = analysis_output
                dominance_list = compute_dominance(base_image_path=config_parameter['data']['images']['base'], image_name=img_name, model_configuration=config_parameter['model']['dominance'])
                output['dominance_color'].insert(index, dominance_list)
                logger.info("Inserted the dominance color list for an image")
        logger.info("The dominance color was updated locally.")
        apply_update(collection=collection, data=data, update=output)


def update_dominance_global(collection, config_parameter):
    logger.info("Updated dominance global function activated")
    if config_parameter['model']['dominance']['n_threads'] > 0:
        logger.info("Thread activated")
        logger.info("Subdivision of the list of data for each thread")
        thread_list = []
        element_list = list(collection['read'].find({}, no_cursor_timeout=True))
        thread_count = config_parameter['model']['dominance']['n_threads']
        data_list = [element_list[i:i+config_parameter['model']['dominance']['element_per_thread']+thread_count] for i in range(0, len(element_list), thread_count)]
        for data in data_list:
            thread_list.append(threading.Thread(target=update_dominance, args=(collection['write'], data, config_parameter)))
        logger.info("Created the thread list")
        for t in thread_list:
            t.start()
        logger.info("Started the threads")
        for t in thread_list:
            t.join()
    else:
        try:
            logger.info("Use sequentially updates for dominance color")
            update_dominance(collection=collection['write'], data_list=collection['read'].find({}, no_cursor_timeout=True), config_parameter=config_parameter)
        except errors.CursorNotFound:
            logger.info("CursorNotFound error. It can be necessary to set this value in the mongoDB execution.")