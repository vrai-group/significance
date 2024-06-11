import threading
from utils.image.path_generation import img_path_generator
from models.color.clustering_dominance_color import dominance_color


# TODO check how to use this class
class Dominance(threading.Thread):
    
    def __init__(self, group=None, target=None, name=None, args=None, kwargs=None) -> None:
        super().__init__(group, target, name, args, kwargs)
        self.collection = kwargs['collection']
        self.data_list = kwargs['data_list']
        self.config_parameter = kwargs['config_parameter']
    
    def compute_dominance(base_image_path: str, image_name: str, model_configuration: dict) -> list:
        img_path = img_path_generator(base_image_path, image_name)
        dominance_list = dominance_color(config=model_configuration, img_path=img_path)
        return dominance_list
    
    def run(self) -> None:
        update_dominance(self.collection, self.data_list, self.config_parameter)

