import instaloader
import os
import pandas as pd
from datetime import datetime as dt
import pickle
import time
from utils.user import update_user
import logging

logger = logging.getLogger('instaloader')

def state_information_opening(state_path: str = './Hashtag.csv') -> pd.DataFrame:
    # Opening state information for hashtag
    logger.info("opening hashtag state")
    hashtag_state = pd.read_csv(state_path)
    hashtag_state['hashtag'].astype(str)
    hashtag_state['last_time_used'].astype(int)
    hashtag_state['last_time_downloaded'].astype(int)
    hashtag_state['old_time_downloaded'].astype(int)
    hashtag_state['total_number_of_images'].astype(int)
    hashtag_state['number_of_images_last_execution'].astype(int)
    return hashtag_state

def get_hashtag(state_path: str = './Hashtag.csv') -> tuple([dict, int]):
    logger.info("Get hashtag to be used")
    hashtag_state = state_information_opening(state_path)
    index_to_download = hashtag_state['last_time_used'].idxmin()
    return tuple([hashtag_state.iloc[index_to_download].to_dict(), index_to_download])

def update_hashtag(hashtag_info: dict, index: int, state_path: str = './Hashtag.csv'):
    logger.info("Update hashtag information")
    hashtag_state = state_information_opening(state_path)
    hashtag_state.at[index, 'last_time_used'] = int(dt.now().strftime("%Y%m%d%H%M%S"))
    hashtag_state.at[index, 'last_time_downloaded'] = hashtag_info['last_time_downloaded']
    hashtag_state.at[index, 'old_time_downloaded'] = hashtag_info['old_time_downloaded']
    hashtag_state.at[index, 'total_number_of_images'] = hashtag_info['total_number_of_images'] + hashtag_info['number_of_images_last_execution']
    hashtag_state.at[index, 'number_of_images_last_execution'] = hashtag_info['number_of_images_last_execution']
    logger.info("Save hashtag state path")
    hashtag_state.to_csv(state_path, index=False) 

def hashtag_download(user_info: dict, hashtag_info:dict, user_index:int, hashtag_index:int, user_state_path:str, hashtag_state_path:str, data_path:str, config_folder:str, number_of_post:int, time_limit:int, waiting: int = 350) -> dict:
    
    logger.info("Preparing post download")
    message = ""
    
    session_folder = config_folder + 'session/'
    hashtag_folder = data_path + 'hashtag/' + hashtag_info['hashtag'].lower() + '/'
    pickle_folder = data_path + 'pickle/'

    #%% Subfolder creation
    os.makedirs(session_folder, exist_ok=True)
    os.makedirs(hashtag_folder, exist_ok=True)
    os.makedirs(pickle_folder, exist_ok=True)
    
    logger.info("Configuring Instaloader")
    IL = instaloader.Instaloader(download_videos=False, max_connection_attempts=10, download_geotags=True,
                                download_comments=True, compress_json=False, dirname_pattern=hashtag_folder)
    # check if the session for this user exist
    session_path = session_folder + user_info['username']
    try:
        if os.path.exists(session_path):
            logger.info("Load session from session file")
            IL.load_session_from_file(username=user_info['username'], filename=session_path)
            update_user(user_index=user_index, state_path=user_state_path)
        else:
            logger.info("Instagram Log-in")
            IL.login(user_info['username'], user_info['password'])
            logger.info("Save log-in session")
            IL.save_session_to_file(filename=session_path)
            update_user(user_index=user_index, state_path=user_state_path)
    except Exception as e:
        logger.error("Error during log-in")
        logger.error(e)
        message = "Error during log-in: " + str(e)
        update_user(user_index=user_index, state_path=user_state_path, use=1)
        return None, message
    
    message += f"Used the username: {user_info['username']}\n"
    message += f"Used the hashtag: {hashtag_info['hashtag']}\n"
    
    logger.info("Get date information from state info")
    
    counter = 0
    
    start_date = dt.strptime(str(hashtag_info['last_time_downloaded']), "%Y%m%d%H%M%S")#dt.fromtimestamp(hashtag_info['last_time_downloaded'] / 1000)
    end_date = dt.strptime(str(hashtag_info['old_time_downloaded']), "%Y%m%d%H%M%S")#dt.fromtimestamp(hashtag_info['old_time_downloaded'] / 1000)
    logger.info(f"start_date: {start_date}")
    logger.info(f"end_date: {end_date}")

    oldest_post = dt.now() if hashtag_info['last_time_downloaded'] == 0 else start_date
    newest_post = dt.fromtimestamp(0) if hashtag_info['old_time_downloaded'] == 0 else end_date

    start_time = time.time()
    
    logger.info(f"Starting post search and download at: {start_time}")
    
    try:
        hashtag = instaloader.Hashtag.from_name(IL.context, hashtag_info['hashtag'].lower())

        posts = hashtag.get_posts()

        logger.info("GraphQL query worked.")
        
        update_hashtag(hashtag_info=hashtag_info, index=hashtag_index, state_path=hashtag_state_path)
        
        message += f"Founded posts for the used hashtag\n"
        
        for post in posts:
            post_date = post.date
            if counter == number_of_post or time.time() > start_time + time_limit:
                logger.info("Time limit reached or Post limit reached")
                break
            if hashtag_info['old_time_downloaded'] == 0 and hashtag_info['last_time_downloaded'] == 0:
                logger.info("First time hashtag download")
                logger.info(f"Download the post {post.url}")
                IL.download_post(post, os.path.join(data_path, hashtag_info['hashtag'].lower()))
                counter += 1
                oldest_post = post_date
                newest_post = post_date
            else:
                if post_date > end_date and post_date < start_date:
                    continue
                else:
                    logger.info(f"Download the post {post.url}")
                    IL.download_post(post, os.path.join(data_path, hashtag_info['hashtag'].lower())) 
                    counter += 1
                    if oldest_post > post_date:
                        oldest_post = post_date
                    elif newest_post < post_date:
                        newest_post = post_date
            if counter == 1:
                logger.info("Update hashtag and user info")
                update_hashtag(hashtag_info, hashtag_index, hashtag_state_path)
                update_user(user_index, user_state_path)
            logger.info("Waiting for the next download")
            time.sleep(waiting)
        hashtag_info['last_time_downloaded'] = int(newest_post.strftime("%Y%m%d%H%M%S"))
        hashtag_info['old_time_downloaded'] = int(oldest_post.strftime("%Y%m%d%H%M%S"))
        hashtag_info['number_of_images_last_execution'] = counter
        message += f"Downloaded {counter} posts.\n"
    except KeyError:
        logger.info("GraphQL query not worked. Using Iterator")
        message += "GraphQL Not worked. Uses Alternative solution. \n"
        # Manage the error of the GraphQL
        post_iterator = instaloader.NodeIterator(
            IL.context, "9b498c08113f1e09617a1703c22b2f32",
            lambda d: d['data']['hashtag']['edge_hashtag_to_media'],
            lambda n: instaloader.Post(IL.context, n),
            {'tag_name': hashtag_info['hashtag'].lower()},
            f"https://www.instagram.com/explore/tags/{hashtag_info['hashtag'].lower()}/"
        )
        logger.info("Iterator created")
        message += f"Founded posts for the used hashtag\n"
        
        counter = 0
        
        try:
            for post in post_iterator:
                post_date = post.date
                if counter == number_of_post or time.time() > start_time + time_limit:
                    logger.info("Time limit reached or Post limit reached")
                    break
                if hashtag_info['old_time_downloaded'] == 0 and hashtag_info['last_time_downloaded'] == 0:
                    logger.info("First time hashtag download")
                    logger.info(f"Download the post {post.url}")
                    # this means that it is the first time that the code is executed
                    IL.download_post(post, target=hashtag_info['hashtag'].lower()) 
                    counter += 1
                    oldest_post = post_date
                    newest_post = post_date
                else:
                    if post_date > end_date and post_date < start_date:
                        continue
                    else:
                        logger.info(f"Download the post {post.url}")
                        IL.download_post(post, target=hashtag_info['hashtag'].lower()) 
                        counter += 1
                        if oldest_post > post_date:
                            oldest_post = post_date
                        elif newest_post < post_date:
                            newest_post = post_date
                if counter == 1:
                    logger.info("Update hashtag and user info")
                    update_hashtag(hashtag_info, hashtag_index, hashtag_state_path)
                    update_user(user_index, user_state_path)
                logger.info("Waiting for the next download")
                time.sleep(waiting)
            hashtag_info['last_time_downloaded'] = int(newest_post.strftime("%Y%m%d%H%M%S"))
            hashtag_info['old_time_downloaded'] = int(oldest_post.strftime("%Y%m%d%H%M%S"))
            hashtag_info['number_of_images_last_execution'] = counter
            message += f"Downloaded {counter} posts.\n"
        except instaloader.exceptions.TooManyRequestsException:
            logger.info(f"Too Many Request exception with the account {user_info['username']}")
            user_info['many_request'] = 1
            message += "Receive Too many request exception. The account for the next future can't be used. \nPlease reset the password and update the account information. \n"
            return hashtag_info, message
        except instaloader.exceptions.LoginRequiredException:
            logger.info(f"Login required for the account {user_info['username']}")
            user_info['redirect_to_login'] = 1
            message += "Receive Redirect to login message. The account for the next future can't be used. \nPlease reset the password and update the account information. \n"
            return hashtag_info, message
        except Exception as e:
            logger.info("Download problems")
            iteratorfreeze = post_iterator.freeze()
            hashtag_info['number_of_images_last_execution'] = counter
            with open(os.path.join(pickle_folder, hashtag_info['hashtag'].lower() + '.pkl') , 'wb') as resumefile:
                pickle.dump(iteratorfreeze, resumefile)
            
            message += "Receive exception no post downloaded. In the next line the exception was reported:\n"
            message += str(e)

    return hashtag_info, message