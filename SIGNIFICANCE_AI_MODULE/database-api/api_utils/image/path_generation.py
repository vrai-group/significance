import os
import logging


logger = logging.getLogger('API-offline')


def img_path_generator(base_path: str, img_name: str):
    logger.info("Generate the bath of the image")
    level1 = img_name[0]
    level2 = img_name[0:2]
    
    return os.path.join(base_path, level1, level2, img_name)
