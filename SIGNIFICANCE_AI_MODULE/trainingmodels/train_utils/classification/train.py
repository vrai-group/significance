import torch
import os
import time
import torch.optim as O
import torch.nn as NN
from tqdm import tqdm
from train_utils.classification.dataset import create_dataset
from train_utils.classification.dataloader import create_dataloader
from models.classification.vgg import VGG


def classifier_train(config_parameter):
    
    # Creation of the dataset and dataloader
    train_dataset = create_dataset(config_parameter['data']['train_img_path'], train=True)
    train_dataloader = create_dataloader(train_dataset, batch_size=config_parameter['training_parameter']['batch_size'])
    test_dataset = create_dataset(config_parameter['data']['test_img_path'], train=False)
    test_dataloader = create_dataloader(test_dataset, batch_size=config_parameter['test_parameter']['batch_size'], shuffle=False)
    
    # Creation of the model
    classifier = VGG(config_parameter['model_parameter']['n_classes'], config_parameter['model_parameter']['pretrained'])
    
    # Define the loss function and the optimizer
    criterion = NN.CrossEntropyLoss()
    optimizer = O.Adam(classifier.parameters(), lr=config_parameter['training_parameter']['learning_rate'], amsgrad=True)
    
    
    #define the device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    num_of_gpus = torch.cuda.device_count()
    print("Let's use", num_of_gpus, "GPUs!")
    #if num_of_gpus > 1:
    classifier = NN.DataParallel(classifier)

    classifier.to(device=device)

    tic = time.time()
    best_acc = 0.0
    for epoch in range(config_parameter['training_parameter']['epochs']):
        
        running_loss = 0.0
        running_correct = 0
        running_sample = 0

        with tqdm(train_dataloader, unit="batch") as tepoch:
            classifier.train()
            for data, target in tepoch:
                
                tepoch.set_description(f"Train epoch: {epoch}")
                
                data, target = data.to(device), target.to(device)
                
                optimizer.zero_grad()
                
                output = classifier(data)
                
                #assert target.ndim == 1 and target.size() == output.reshape(-1,).size()
                predicted = torch.max(output, 1)
                
                loss = criterion(output, target)
                
                # correct = (target == predicted[1]).sum().item()
                # accuracy = correct / config_parameter['training_parameter']['batch_size']
                        
                loss.backward()
                optimizer.step()

                running_sample += len(data)
                running_loss += loss.item() * len(data)
                running_correct += torch.sum(predicted[1] == target).item()
                
                #tepoch.set_postfix(loss=loss.item(), accuracy=accuracy, lr=optimizer.param_groups[0]['lr'])
                tepoch.set_postfix(loss=running_loss/running_sample, accuracy=running_correct/running_sample, lr=optimizer.param_groups[0]['lr'])
                
            # epoch_loss = running_loss / len(train_dataset)
            epoch_accuracy = float(running_correct) / len(train_dataset)
            print("train acc", epoch_accuracy)
            
            if not config_parameter['test_parameter']['activate'] and config_parameter['save']['best_only'] and epoch_accuracy > best_acc:
                torch.save(classifier.state_dict(), os.path.join(config_parameter['save']['save_path'], "best.pt"))
                best_acc = epoch_accuracy
            elif not config_parameter['test_parameter']['activate'] and not config_parameter['save']['best_only']:
                torch.save(classifier.state_dict(), os.path.join(config_parameter['save']['save_path'], f"epoch_{epoch}-acc_{epoch_accuracy}-loss_{epoch_loss}.pt"))
                if epoch_accuracy > best_acc:
                    torch.save(classifier.state_dict(), os.path.join(config_parameter['save']['save_path'], "best.pt"))
                    best_acc = epoch_accuracy
        
        if config_parameter['test_parameter']['activate'] and (epoch % config_parameter['test_parameter']['epoch_count']) == 0:
        
            with torch.no_grad():
                
                classifier.eval()
                test_sample= 0
                test_loss = 0.0
                test_correct = 0
                
                with tqdm(test_dataloader, unit="batch") as tepoch_test:
                    for data, target in tepoch_test:
                        tepoch_test.set_description(f"Test epoch: {epoch}")
                        
                        data, target = data.to(device), target.to(device)
                        
                        output = classifier(data)
                        
                        # assert target.ndim == 1 and target.size() == output.reshape(-1,).size()
                        predicted = torch.max(output, 1)

                        loss = criterion(output, target)

                        # correct = (target == predicted[1]).sum().item()
                        # accuracy = correct / config_parameter['training_parameter']['batch_size']

                        test_sample += len(data)
                        test_loss += loss.item() * len(data) #config_parameter['test_parameter']['batch_size']
                        test_correct += torch.sum(target == predicted[1]).item()
                        
                        tepoch_test.set_postfix(loss=test_loss/test_sample, accuracy=test_correct/test_sample)
                    
                    # test_loss = test_loss / len(test_dataset)
                    test_accuracy = float(test_correct) / len(test_dataset)
                    # print("test score: ", "accuracy=", test_accuracy, "loss=", test_loss)
                    print("Epoc", epoch,"test acc", test_accuracy)
                    
                    if config_parameter['save']['best_only'] and test_accuracy > best_acc:
                        torch.save(classifier.state_dict(), os.path.join(config_parameter['save']['save_path'], "best.pt"))
                        best_acc = test_accuracy
                    elif not config_parameter['save']['best_only']:
                        torch.save(classifier.state_dict(), os.path.join(config_parameter['save']['save_path'], f"epoch_{epoch}-acc_{epoch_accuracy}-loss_{epoch_loss}.pt"))
                        if test_accuracy > best_acc:
                            torch.save(classifier.state_dict(), os.path.join(config_parameter['save']['save_path'], "best.pt"))
                            best_acc = test_accuracy

    toc = time.time()
    print("training time for {} epochs: {} seconds".format(config_parameter['training_parameter']['epochs'], toc-tic))
