from statistics import mode
from api_models.detection.yolo import YOLO
from api_utils.image.path_generation import img_path_generator
from api_utils.output.output_format import analysis_output
from skimage.io import imread
from skimage.transform import resize
from torchvision import transforms
from retry import retry
import torch
import os
import logging


logger = logging.getLogger('API-offline')

@retry(ValueError, tries=10, delay=1, max_delay=5)
def apply_update(collection, data, update):
    logger.info("Update the database...")
    if collection.count_documents({'_id': data['_id']}) != 0:
        logger.info(f"Found a document with the _id: {data['_id']}")
        if collection.update_one({"$and": [{"_id": data['_id']}, {"analysis.detected_object": {"$exists": True}}]}, {"$set": {"analysis.detected_object": update['detected_object'], "analyzed.classification": True}}) == 0:
            logger.info("Dominance color not updated in the document")
            logger.info("Try to update the analysis key at all")
            collection.update_one({"_id": data['_id']}, {"$set": {"analysis": update, "analyzed.detection": True}}, upsert=True)
            logger.info("Updated the analysis key at all")
        else:
            logger.info("Document not updated... retry later")
            return ValueError("Update not applied")
    else:
        data['analysis'] = update
        logger.info("The document does not exist.")
        logger.info("Insert the document in the collection")
        if collection.insert_one(data) == 0:
            return ValueError("Update not applied")
    logger.info("Document updated")
    return True

def detect(base_image_path: str, image_name: str, image_size: dict, model: torch.nn.Module, device):
    transformation = transforms.Compose([
        transforms.ToTensor(),
        transforms.ConvertImageDtype(torch.float)
    ])
    
    logger.info("Detect fashion object")
    img_path = img_path_generator(base_path=base_image_path, img_name=image_name)
    
    logger.info("Image path: ", img_path)
    logger.info("Opening the image")
    
    image = imread(img_path)
    img_size = (image_size['size'][0], image_size['size'][1], 3)
    
    #image = transformation(image)
    #image = image.to(device)
    
    if image_size['activated']:
        detection_result = model(image, img_size[0])
    else:
        detection_result = model(image.unsqueeze_(0))
    
    logger.info("Detection result: ", detection_result.pandas().xyxy[0])
    
    return detection_result

def update_detection(collection, config_parameter):
    logger.info("Defining the device for the computation")
    
    model_configuration = config_parameter['model']['detection']
    imgs_base_path = config_parameter['data']['images']['base']
    
    if model_configuration['gpu']:
        logger.info("Requested the GPU")
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    else:
        logger.info("Creating the model")
        device = torch.device("cpu")
    
    logger.info("Obtained the device: ", device)
    
    logger.info("Creating the model")
    model = YOLO(name=model_configuration['yolo_model_name'], class_number=model_configuration['n_classes'], pretrained=model_configuration['yolo_pretrained'])
    
    model.to(device)
    model.eval()
    
    logger.info("YOLO Model Created")
    
    for data in collection['read'].find({}, no_cursor_timeout=True):
        imgs_count = len(data['imgs'])
        is_detected = []
        logger.info(f"Founded {imgs_count} images in the document with _id {data['_id']}")
        
        if 'analyzed' in data.keys():
            logger.info("Get the analyzed presence from the document")
            analyzed = data['analyzed']
        else:
            logger.info("Created the new analyzed structure for the document")
            analyzed = {
                "classification": False,
                "dominance": False,
                "detection": False
            }
        
        if analyzed['detection'] or analyzed['dominance'] or analyzed['classification']:
            logger.info("The document was already analyzed: try to load old analysis")
            if 'analysis' in data.keys():
                output = data['analysis']
                logger.info("Loaded the old analysis result")
            else:
                logger.info("Created the analysis structure because it is not present")
                output = analysis_output
        else:
            logger.info("Created the analysis structure because it is the first time that this document will be analyzed")
            output = analysis_output
        
        for index, img_name in enumerate(data['imgs']):
            logger.info("Get the classification result")
            detection_result = detect(base_image_path=imgs_base_path, image_name=img_name, image_size=model_configuration['resize'], model=model, device=device)
                        
            result_list =[]
            
            if len(detection_result.pandas().xyxy[0]) == 0:
                logger.info(f"No objects found in the image {img_name}")
                continue
            
            for result in detection_result.pandas().xyxy[0]:
                result_dict = {}
                result_dict['xmin'] = result['xmin']
                result_dict['ymin'] = result['ymin']
                result_dict['xmax'] = result['xmax']
                result_dict['ymax'] = result['ymax']
                result_dict['confidence'] = result['confidence']
                result_dict['class'] = result['class']
                #TODO opening the classes file
                result_list.append(result_dict)
            
            is_detected.insert(index, result_list)
            
        logger.info("Update the document keys")
        output['detected_object'] = is_detected
        analyzed['detection'] = True
        data['analysis'] = output
        data['analyzed'] = analyzed
        logger.info("Update the document in the write collection")
        #TODO apply update
    return None
                