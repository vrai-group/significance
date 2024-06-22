The code for training and testing the models is closed inside a directory that include code, configuration files, and data to training and testing the models.

In the “code/model” path, there is a folder for each experiment done or to be done. In each folder there is the "training.json" configuration file. The trained model "best.pt", the training reports "trainingRes.txt" and test "trainingTest.txt" will be saved in the same folder. 

First of all, you have to replace the string [expFolder] in the following commands with the right folder name of experiment (e.g. artefact_v3, or frescoes_location, or …)

To run training and test code you need to execute the commands in sequence:

`python code/trainingmodels/main.py -cf code/model/[expFolder]/training.json > code/model/[expFolder]/trainingRes.txt`

To run training and test code you need to execute the commands in sequence:

`python code/trainingmodels/mainTest.py -cf code/model/[expFolder]/training.json > code/model/[expFolder]/testRes.txt`
