from train_utils.classification.train import classifier_train
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--configuration_file', '-cf', required=True, help="Represent the path for configuration file.")
args = parser.parse_args()

with open(args.configuration_file, 'r') as config_file:
    config_parameter = json.load(config_file)
    
classification_parameter = config_parameter['classification']

classifier_train(classification_parameter)