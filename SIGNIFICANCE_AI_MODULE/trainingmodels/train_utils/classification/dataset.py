from torchvision import transforms as T
from torchvision.datasets import ImageFolder

def create_dataset(img_path, train: bool = True):
    
    if train:
        transform = T.Compose([T.RandomRotation(30),
                                T.Resize([224, 224]), #h x w
                                T.RandomHorizontalFlip(),
                                T.RandomVerticalFlip(),
                                T.ToTensor(),
                                T.Normalize([0.485, 0.456, 0.406], # PyTorch recommends these but in this
                                                    [0.229, 0.224, 0.225]) # case I didn't get good results
                                
                                        ])
    else:
        transform = T.Compose([T.Resize([224,224]),
                                         T.ToTensor(),
                                         T.Normalize([0.485, 0.456, 0.406],
                                                              [0.229, 0.224, 0.225])
                                      ])
    
    dataset = ImageFolder(img_path, transform=transform)
    
    return dataset

def load_train_test(datadir_t, datadir_v, batchsize, valid_size = .2):
    train_transforms = T.Compose([T.RandomRotation(30),
                                       T.Resize([224, 224]), #h x w
                                       T.RandomHorizontalFlip(),
                                       T.RandomVerticalFlip(),
                                       T.ToTensor(),
                                       T.Normalize([0.485, 0.456, 0.406], # PyTorch recommends these but in this
                                                            [0.229, 0.224, 0.225]) # case I didn't get good results
                                       
                                       ])

    val_transforms = T.Compose([T.Resize([224,224]),
                                         T.ToTensor(),
                                         T.Normalize([0.485, 0.456, 0.406],
                                                              [0.229, 0.224, 0.225])
                                      ])

    train_data = ImageFolder(datadir_t, transform=train_transforms)
    val_data = ImageFolder(datadir_v, transform=val_transforms)
    
    return train_data, val_data