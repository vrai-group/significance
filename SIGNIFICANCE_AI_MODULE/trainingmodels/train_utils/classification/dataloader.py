from torch.utils.data import DataLoader
from torchvision.datasets import ImageFolder


def create_dataloader(dataset: ImageFolder, batch_size, shuffle=True) -> DataLoader:
    
    return DataLoader(dataset=dataset, batch_size=batch_size, shuffle=shuffle)