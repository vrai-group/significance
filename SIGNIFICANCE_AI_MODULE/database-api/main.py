from api_utils.database.db_manager import get_collection
from api_utils.image.dominance.analysis import update_dominance_global
from api_utils.image.classification.vggfilter import update_usability
from api_utils.image.detection.yolodetection import update_detection
import json
import logging
import argparse

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(filename)s-%(lineno)d-%(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)
logger = logging.getLogger('API-offline')

parser = argparse.ArgumentParser()
parser.add_argument('--configuration_file', '-cf', required=True, help="Represent the path for configuration file.")
args = parser.parse_args()

with open(args.configuration_file, 'r') as config_file:
    config_parameter = json.load(config_file)
    
# logging configuration
logging_file_path = config_parameter['logging']['path']
logging_file = logging_file_path + "offlineapi.log"

logging_file_conf = logging.FileHandler(logging_file)
logging_file_conf.setFormatter(logging.Formatter('%(asctime)s-%(levelname)s-%(filename)s-%(lineno)d-%(message)s', '%d-%b-%y %H:%M:%S'))
logging_file_conf.setLevel(logging.INFO)
logger.addHandler(logging_file_conf)


# db configuration
logger.info("Connection to MongoDB for read and write...")
database_config = config_parameter['data']['database']
collection: dict = {}
collection['read'] = get_collection(configuration=database_config['read'])
collection['write'] = get_collection(configuration=database_config['write'])
logger.info("Connection done")
counter_element = 0


if config_parameter['model']['dominance']['activate'] and config_parameter['model']['classification']['activate'] and config_parameter['model']['detection']['activate']:
    update_usability(collection=collection, config_parameter=config_parameter)
    update_dominance_global(collection=collection, config_parameter=config_parameter)
    update_detection(collection=collection, config_parameter=config_parameter)
elif config_parameter['model']['dominance']['activate'] and config_parameter['model']['classification']['activate']:
    update_dominance_global(collection=collection, config_parameter=config_parameter)
    update_usability(collection=collection, config_parameter=config_parameter)
elif config_parameter['model']['classification']['activate']:
    update_usability(collection=collection, config_parameter=config_parameter)
elif config_parameter['model']['dominance']['activate']:
    update_dominance_global(collection=collection, config_parameter=config_parameter)
elif config_parameter['model']['detection']['activate']:
    update_detection(collection=collection, config_parameter=config_parameter)