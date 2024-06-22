# SIGNIFICANCE

⚠️ ***Work in Progress...*** ⚠️

This repository describes the framework for automatically process and classify works of art images with the aim of obtaining useful information about the depicted artwork. The framework consists of two stages. Firstly the artwork depicted in the image is classified among 5 classes: icons, frescoes, coins, manuscripts, and others. 

After the image has been classified at the first stage, it goes to the stage classification models (specific to the type of artwork) to extract specific features (e.g., location, period, etc.).

In order to classify images, we use the neural network [VGG16](
https://doi.org/10.48550/arXiv.1409.1556). VGG16 is a convolutional neural network for image classification task.

![arch](/docs/arch.png)

## Dataset

![dataSample](/docs/dataSample.png)

The following image datasets were collected and labelled as previously defined. For each artwork, the images were labelled according to a feature/field of each works of art (e.g., location, periods, material, etc.). Different classes belong to each field.

![featureFields](/docs/featureFields.png)

The following tables reports the data cardinality (number of images), for each class, used for the training and test of the models. The results are for both the phases defined. 	

![dataset](/docs/dataset.png)

## Experiment

The classification task is performed to classify the goods and the fields of each artworks. In each experiment:
- The dataset was split between training and test set: 80% and 20%, respectively. The data were taken to maintain class balance in both datasets.
- A model was trained from the pre-trained model on imagenet (fine tuning). The adopted architecture is vgg16, adaptive optimizer (Adam), learning rate 10e-5, mini-batch size 32, 50 training epochs.

Experiments were performed using 2 GPUs in parallel in the training phase. Only one GPU was used in the testing phase.

Hardware and Software specifications:
-	2 Nvidia GeForce RTX 2080 Ti
-	CUDA Version: 11.2
-	libcudnn.so.7
-	Pytorch 1.8.1

## Results

The following Tables reports the results of all models. 

![results](/docs/results.png)
