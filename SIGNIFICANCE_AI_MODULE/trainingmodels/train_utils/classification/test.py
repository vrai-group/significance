import torch
import os
import time
import torch.optim as O
import torch.nn as NN
from tqdm import tqdm
from train_utils.classification.dataset import create_dataset
from train_utils.classification.dataloader import create_dataloader
from models.classification.vgg import VGG
from sklearn.metrics import confusion_matrix, classification_report

def classifier_test(config_parameter):
    
    # Creation of the dataset and dataloader
    test_dataset = create_dataset(config_parameter['data']['test_img_path'], train=False)
    test_dataloader = create_dataloader(test_dataset, batch_size=config_parameter['test_parameter']['batch_size'], shuffle=False)

    # Creation of the model
    classifier = VGG(config_parameter['model_parameter']['n_classes'], config_parameter['model_parameter']['pretrained'])
    
    # # Define the loss function and the optimizer
    # criterion = NN.CrossEntropyLoss()
    # optimizer = O.Adam(classifier.parameters(), lr=config_parameter['training_parameter']['learning_rate'], amsgrad=True)


    #define the device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    num_of_gpus = torch.cuda.device_count()
    print("Let's use", num_of_gpus, "GPUs!")
    #if num_of_gpus > 1:
    classifier = NN.DataParallel(classifier)

    classifier.to(device=device)

    # load trained model
    classifier.load_state_dict(
        torch.load(os.path.join(config_parameter['save']['save_path'], "best.pt"), map_location=device))

    with torch.no_grad():

        classifier.eval()
        test_sample= 0
        test_correct = 0
        GT= []
        PRED= []

        tic = time.time()
        with tqdm(test_dataloader, unit="batch") as tepoch_test:
            for data, target in tepoch_test:
                tepoch_test.set_description(f"Test ")

                data, target = data.to(device), target.to(device)

                output = classifier(data)
                predicted = torch.max(output, 1)

                test_sample += len(data)
                test_correct += torch.sum(target == predicted[1]).item()
                GT += target.tolist()
                PRED += predicted[1].tolist()

                tepoch_test.set_postfix(accuracy=test_correct/test_sample)

            test_accuracy = float(test_correct) / len(test_dataset)
            # print("test score: ", "accuracy=", test_accuracy, "loss=", test_loss)
            print("test acc", test_accuracy)

            print(test_dataset.class_to_idx)
            print(confusion_matrix(GT, PRED))
            print(classification_report(GT, PRED))

        toc = time.time()
        print("test time for {} samples: {} seconds".format(len(test_dataset), toc - tic))
