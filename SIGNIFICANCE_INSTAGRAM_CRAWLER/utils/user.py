from itertools import count
import os
import pandas as pd
from datetime import datetime as dt
import logging
logger = logging.getLogger('instaloader')

def user_information_opening(state_path: str = './Users.csv') -> pd.DataFrame:
    logger.info("Opening the user state file")
    user_state = pd.read_csv(state_path)
    logger.info("Setting type of files")
    user_state['username'].astype(str)
    user_state['password'].astype(str)
    user_state['last_time_used'].astype(int)
    user_state['phone'].astype(str)
    user_state['mail'].astype(str)
    user_state['many_request'].astype(int)
    return user_state

def get_user(state_path: str = './Users.csv') -> tuple([dict, int]):
    user_state = user_information_opening(state_path=state_path)
    logger.info("Get usable user")
    user_state['last_time_used'].astype(int)
    # index_to_use = user_state['last_time_used'].idxmin()
    # counter = 0
    # while user_state.loc[index_to_use].to_dict()['many_request'] == 1 and user_state.loc[index_to_use].to_dict()['use'] == 0:
    #     counter += 1
    #     logger.info(f"User {user_state.iloc[index_to_use].to_dict()['username']} has dome too much requests")
    #     user_state.loc[index_to_use, 'use'] = 1
    #     user_state.drop(user_state[user_state['use'] == 1].index, inplace=True)
    #     index_to_use = user_state['last_time_used'].idxmin()
    #
    # logger.info(f"Found {counter} users that need password update")
    # index_to_use = user_state['last_time_used'].idxmin()
    # counter = 0
    # while user_state.loc[index_to_use].to_dict()['redirect_to_login'] == 1 and user_state.loc[index_to_use].to_dict()['use'] == 0:
    #     counter += 1
    #     logger.info(f"User {user_state.iloc[index_to_use].to_dict()['username']} need a password update")
    #     user_state.at[index_to_use, 'use'] = 1
    #     user_state.drop(user_state[user_state['use'] == 1].index, inplace=True)
    #     index_to_use = user_state['last_time_used'].idxmin()
    #
    # logger.info(f"Found {counter} users that need password update")
    index_to_use = user_state['last_time_used'].idxmin()
    return tuple([user_state.loc[index_to_use].to_dict(), index_to_use])

def update_user(user_index: int, state_path: str = './Users.csv', use: int = 0):
    logger.info("Update user information")
    user_state = user_information_opening(state_path)
    user_state.at[user_index, 'last_time_used'] = int(dt.now().strftime("%Y%m%d%H%M%S"))
    user_state.at[user_index, 'use'] = use
    logger.info("Update user state file")
    user_state.to_csv(state_path, index=False)