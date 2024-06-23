## AI Module

The code for training and testing the models is closed inside this directory that include code, configuration files, and data to training and testing the models.

### Dataset

First of all, you have to download in the "dataset" folder all data you need for each experiment from this [link](https://univpm-my.sharepoint.com/:f:/g/personal/s1084334_pm_univpm_it/EsCPooRruZ9OsXGJjddHf4YBPisDGy-Rmys1HWb8OyYYVA?e=chqwFt)

### Training and Test

In the “model” path, there is a folder for each experiment done or to be done. In each folder there is the "training.json" configuration file. The trained model "best.pt", the training reports "trainingRes.txt" and test "trainingTest.txt" will be saved in the same folder. 

First of all, you have to replace the string [expFolder] in the following commands with the right folder name of experiment (e.g. artefact_v3, or frescoes_location, or …)

To run training and test code you need to execute the commands in sequence:

`python trainingmodels/main.py -cf model/[expFolder]/training.json > model/[expFolder]/trainingRes.txt`

`python trainingmodels/mainTest.py -cf model/[expFolder]/training.json > model/[expFolder]/testRes.txt`
