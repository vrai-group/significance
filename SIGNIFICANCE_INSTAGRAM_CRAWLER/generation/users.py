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

with open(start_file, 'r') as account_list:
    users = [hashtag.strip() for hashtag in account_list.readlines()]

table = pd.DataFrame(columns=['username', 'password', 'last_time_used'])

for user in users:
    content = {
        'username': user.split(',')[0],
        'password': user.split(',')[1].strip(),
        'last_time_used': int(dt.now().strftime("%Y%m%d%H%M%S")),
    }

    table = table.append(content, ignore_index=True)

end = int(dt.now().strftime("%Y%m%d%H%M%S"))

table.to_csv(end_file, index=False)