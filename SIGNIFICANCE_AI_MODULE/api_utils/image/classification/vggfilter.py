from email.mime import base
from api_models.classification.vgg import VGG
from skimage.io import imread
from skimage.transform import resize
from torchvision import transforms
import torch
import os
import logging


logger = logging.getLogger('API-offline')


def classify(base_image_path: str, image_name: str, image_size: list, model: torch.nn.Module, device):
    transformation = transforms.Compose([
        transforms.ToTensor(),
        transforms.ConvertImageDtype(torch.float)
    ])
    # create the model
    # open the image
    # get classification
    logger.info("Verify if it is a fashion image")
    img_path = image_name.replace('.', base_image_path, 1)
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
    logger.info("Classification result: ", str(classication_result.indices[0]))
    return classication_result.indices[0].cpu()

def update_usability(collection, config_parameter):
    logger.info("Defining the device for the computation")
    
    model_configuration = config_parameter['model']['classification']
    imgs_base_path = config_parameter['data']['image_path']
    
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
    analyzed_result: list = []
    for data in collection:
        imgs_count = len(data['images'])
        is_usable = []
        logger.info(f"Founded {imgs_count} images in the document with _id {data['_id']}")
        if 'analyzed' in data.keys():
            logger.info("Get the analyzed presence from the document")
            analyzed = data['analyzed']
        else:
            logger.info("Created the new analyzed structure for the document")
            analyzed = {
                "classification": False,
            }
        if analyzed['classification']:
            logger.info("The document was already analyzed: try to loading old analysis")
            analyzed_result.append(data)
            continue
        for index, img_name in enumerate(data['images']):
            logger.info("Get the classification result")
            classification_result = classify(base_image_path=imgs_base_path, image_name=img_name, image_size=model_configuration['resize']['size'], model=model, device=device)
            if classification_result == 0:
                logger.info(f"The image {img_name} was classified as coin")
                is_usable.insert(index, 'Coin')
            elif classification_result == 1:
                logger.info(f"The image {img_name} was classified as humbug")
                is_usable.insert(index, 'Humbug')
            elif classification_result == 2:
                logger.info(f"The image {img_name} was classified as icon")
                is_usable.insert(index, 'Icon')
        
        logger.info("Update the document keys")
        data['use'] = is_usable
        analyzed['classification'] = True
        data['analyzed'] = analyzed
        logger.info("Update the document in the write collection")
        analyzed_result.append(data)
    return analyzed_result