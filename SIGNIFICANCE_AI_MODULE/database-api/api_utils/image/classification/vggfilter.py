from api_models.classification.vgg import VGG
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
        if collection.update_one({"$and": [{"_id": data['_id']}, {"analysis.use": {"$exists": True}}]}, {"$set": {"analysis.use": update['use'], "analyzed.classification": True}}) == 0:
            logger.info("Dominance color not updated in the document")
            logger.info("Try to update the analysis key at all")
            collection.update_one({"_id": data['_id']}, {"$set": {"analysis": update, "analyzed.classification": True}}, upsert=True)
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

def classify(base_image_path: str, image_name: str, image_size: list, model: torch.nn.Module, device):
    transformation = transforms.Compose([
        transforms.ToTensor(),
        transforms.ConvertImageDtype(torch.float)
    ])
    # create the model
    # open the image
    # get classification
    logger.info("Verify if it is a fashion image")
    img_path = img_path_generator(base_path=base_image_path, img_name=image_name)
    # opening the image for the classification model
    logger.info("Image path: ", img_path)
    logger.info("Opening the image")
    image = imread(img_path)
    img_size = (image_size[0], image_size[1], 3)
    image = resize(image, img_size, anti_aliasing=True)
    #image = image.transpose((2, 0, 1))
    image = transformation(image)
    image = image.to(device)
    logger.info("Image converted to pytorch tensor")
    logger.info("Classify of the image")
    # Classify
    classication_result = torch.max(model(image.unsqueeze_(0)), 1)
    logger.info("Classification result: ", classication_result.indices[0])
    return classication_result.indices[0].cpu()

def update_usability(collection, config_parameter):
    logger.info("Defining the device for the computation")
    
    model_configuration = config_parameter['model']['classification']
    imgs_base_path = config_parameter['data']['images']['base']
    
    if model_configuration['gpu']:
        logger.info("Requested the GPU")
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    else:
        logger.info("Request the CPU")
        device = torch.device("cpu")
    logger.info("Obtained the device: ", device)

    logger.info("Creating the model")
    model = VGG(pretrained=model_configuration['configuration']['pretrained'], init_weights=model_configuration['configuration']['init_weight'])
    
    if os.path.exists(model_configuration['weight']):
        logger.info("Loading the wheights")
        model.load_state_dict(torch.load(model_configuration['weight']))
    
    model.to(device)
    model.eval()
    
    logger.info("Start analyze the read collection")
    for data in collection['read'].find({}, no_cursor_timeout=True):
        imgs_count = len(data['imgs'])
        is_usable = []
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
        if analyzed['classification'] or analyzed['dominance'] or analyzed['detection']:
            logger.info("The document was already analyzed: try to loading old analysis")
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
            classification_result = classify(base_image_path=imgs_base_path, image_name=img_name, image_size=model_configuration['resize']['size'], model=model, device=device)
            if classification_result == 1:
                logger.info(f"The image {img_name} was classified as usable")
                is_usable.insert(index, True)
            else:
                logger.info(f"The image {img_name} was classified as unusable")
                is_usable.insert(index, False)
        
        logger.info("Update the document keys")
        output['use'] = is_usable
        analyzed['classification'] = True
        data['analysis'] = output
        data['analyzed'] = analyzed
        logger.info("Update the document in the write collection")
        apply_update(collection=collection['write'], data=data, update=output)
    return None