#from email import message
import json
import os
from utils import hashtag
from utils import user
#from utils import mail
import argparse
import time
import logging
#from cryptography.fernet import Fernet
import urllib.request

logging.basicConfig(format='%(asctime)s-%(levelname)s-%(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('--configuration_file', '-cf', required=False, default="instaloder/config-sample.json", help="Represent the path for configuration file.")
parser.add_argument('--time_shift', '-ts', type=int, required=False, default=0, help="It permits to define the time shift for the execution of the crawling")
args = parser.parse_args()

with open(args.configuration_file, 'r') as config_file:
    config_parameter = json.load(config_file)

time_scale: dict = {
    's': 1,
    'm': 60,
    'h': 60*60,
    'd': 60*60*24
}

#external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')

save_post_folder = config_parameter['data_folder']
config_folder = config_parameter['config_folder']
n_post = config_parameter['single_hashtag_n_post']
execution_duration = config_parameter['execution_time'] * time_scale[config_parameter['time_scale']] 
hashtag_file = config_parameter['hashtag_data_path']
user_file = config_parameter['user_data_path']
instagram_data_path = config_parameter['instagram_data_path']
time_shift_multiplier = int(config_parameter['time_shift_multiplier'])
logging_file_path = config_parameter['logging_file_path']
waiting_time = config_parameter['waiting_time']

#%% mail configuration
username = config_parameter['account']
encripted_password = config_parameter['encripted_pw']
smtp_server = config_parameter['smtp_server']
receivers = config_parameter['receiver']
smtp_port = config_parameter['smtp_port']
activate_notification = config_parameter['activate_notification']

if activate_notification:
    encription_file_path = 'pathTo/fernet.key'
    with open(encription_file_path, 'rb') as kf:
        key = kf.readline()
    f = Fernet(key)
    clear_password = f.decrypt(encripted_password.encode())
    clear_password = clear_password.decode("utf-8")

#mail.send_mail(username=username, password=clear_password, message="Ciao sono una notifica", smtp_server=smtp_server)
#%% logging configuration
logger = logging.getLogger('instaloader')
logging_file = logging_file_path + "scraper-" + str(os.getpid()) + ".log" #"scraper.log"#

logging_file_conf = logging.FileHandler(logging_file)
logging_file_conf.setFormatter(logging.Formatter('%(asctime)s-%(levelname)s-%(message)s', '%d-%b-%y %H:%M:%S'))
logging_file_conf.setLevel(logging.INFO)
logger.addHandler(logging_file_conf)
#%% waiting befor starting
logger.info("Waiting for start")
time.sleep(time_shift_multiplier * args.time_shift)

#%% external ip
#logger.info("External ip: " + external_ip)

#%% Get user information
logger.info("Get user information")
user_info, user_index = user.get_user(user_file)
logger.info(f"user info: {user_info}")

#%% Get hashtag information
logger.info("Get Hashtag information")
hashtag_info, hashtag_index = hashtag.get_hashtag(state_path=hashtag_file)
logger.info(f"haashtag_info: {hashtag_info}")
#%% Download hashtag
logger.info("Start downloading hashtag media")
hashtag_info, message = hashtag.hashtag_download(user_info, hashtag_info, user_index, hashtag_index, user_state_path=user_file, hashtag_state_path=hashtag_file, data_path=save_post_folder, config_folder=config_folder, number_of_post=n_post, time_limit=execution_duration, waiting=waiting_time)

#%% Update hashtag
logger.info("Update hashtag information")
if hashtag_info is not None:
    hashtag.update_hashtag(hashtag_info=hashtag_info, index=hashtag_index, state_path=hashtag_file)

    #%% update user
    logger.info("Update user information")
    user.update_user(user_index, state_path=user_file)

if activate_notification:
    mail.send_mail(username=username, password=clear_password, message=message, smtp_server=smtp_server, port=smtp_port, receiver=receivers)