from api_utils.image.classification.vggfilter import update_usability
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

# dump configuration
logger.info("Opening the MongoDB dump...")
f = open(config_parameter['data']['dump_path']['read'], 'r')
dump_file = json.load(f)


if config_parameter['model']['classification']['activate']:
    result = update_usability(collection=dump_file, config_parameter=config_parameter)
    with open(config_parameter['data']['dump_path']['write'], "w") as final:
        json.dump(result, final)