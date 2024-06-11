import pandas as pd
from datetime import datetime as dt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--start_file', required=True, help="The basic file from which we generate the state file need to be a CSV data type")
parser.add_argument('--end_file', required=True, help="The save file name and path for the state generated need to be a CSV data tipe")
args = parser.parse_args()
start_file = args.start_file
end_file = args.end_file

start = int(dt.now().strftime("%Y%m%d%H%M%S"))

with open(start_file, 'r') as hashtag_list:
    hashtags = [hashtag.strip() for hashtag in hashtag_list.readlines()]

table = pd.DataFrame(columns=['hashtag', 'last_time_used', 'last_time_downloaded', 'old_time_downloaded', 'total_number_of_images', 'number_of_images_last_execution'])

for hashtag in hashtags:
    content = {
        'hashtag': hashtag,
        'last_time_used': int(dt.now().strftime("%Y%m%d%H%M%S")),
        'last_time_downloaded': 0, #int(dt.now().strftime("%Y%m%d%H%M%S")),
        'old_time_downloaded': 0, #int(dt.now().strftime("%Y%m%d%H%M%S")),
        'total_number_of_images': 0,
        'number_of_images_last_execution': 0
    }

    table = table.append(content, ignore_index=True)

end = int(dt.now().strftime("%Y%m%d%H%M%S"))

table.to_csv(end_file, index=False)
