import torch
import torch.nn as nn

class YOLO(nn.Module):
    
    def __init__(self, name:str, class_number: int, weight_path:str=None, pretrained:bool = True, set_train:bool = False):
        super(YOLO, self).__init__()
        if weight_path is not None:
            self.yolo = torch.hub.load('ultralytics/yolov5', name, path=weight_path)
        else:
            self.yolo = torch.hub.load('ultralytics/yolov5', name, classes=class_number, pretrained=pretrained)
        
    def forward(self, x, size:int = 0) -> torch.Tensor:
        if size != 0:
            return self.yolo(x, size=size)
        else:
            return self.yolo(x)