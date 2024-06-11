from torchvision.models import vgg16
import torch.nn as nn
import torch

class VGG(nn.Module):
    
    def __init__(self, n_classes:int = 3, pretrained:bool = True, init_weights: bool = False) -> None:
        super(VGG, self).__init__()
        # define the extractor from the VGG
        self.vgg_extractor = vgg16(pretrained=pretrained)
        del(self.vgg_extractor.avgpool)
        del(self.vgg_extractor.classifier)
#        self.vgg_extractor= None
#        self.vgg_extractor.features = vgg16(pretrained=pretrained).features
        # define the classification layers
        self.avgpool = nn.AdaptiveAvgPool2d((7, 7))
        self.classifier = nn.Sequential(
            nn.Linear(512 * 7 * 7, 4096),
            nn.ReLU(True),
            nn.Dropout(),
            nn.Linear(4096, 4096),
            nn.ReLU(True),
            nn.Dropout(),
            nn.Linear(4096, n_classes),
        )
        if init_weights:
            self._initialize_weights()
    
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.vgg_extractor.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        x = self.classifier(x)
        return x
    
    
    def _initialize_weights(self) -> None:
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm2d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
        return None