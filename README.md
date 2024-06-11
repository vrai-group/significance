# SIGNIFICANCE



Table 1 and Table 2 reports the data cardinality (number of images), for each class, used for the training and test of the models. The results are for both the phases defined. 

## Dataset

Table 1. Artworks Classes Classification Results
class	# samples for class	# all sample
 	total	train	test	total	train	test
coins	718	574	144	3590	2870	720
frescoes	718	574	144			
icons	718	574	144			
manuscripts	718	574	144			
others	718	574	144			

Table 2. Artworks Features
artefact	# samples	field	class	# samples for class	# all sample
				total	train	test	total	train	test
Icons	1678	location	cyprus	839	671	168	1678	1342	336
			other	839	671	168			
Frescoes	718	location	cyprus	248	198	50	718	574	144
			italy	248	198	50			
			other	222	178	44			
		periods	byzantine	326	261	65	718	575	143
			other	392	314	78			
									

## Experiment

The classification task is performed to classify the goods and the fields of each artworks. In each experiment:
- The dataset was split between training and test set: 80% and 20%, respectively. The data were taken to maintain class balance in both datasets.
- A model was trained from the pre-trained model on imagenet (fine tuning). The adopted architecture is vgg16, adaptive optimizer (Adam), learning rate 10e-5, mini-batch size 32, 50 training epochs.

Experiments were performed using 2 GPUs in parallel in the training phase. Only one GPU was used in the testing phase.


## Results



The following Tables reports the results of all models. 

Icons_location

						
Confusion Matrix						
 	cyprus	other					
cyprus	166	2					
other	3	165					
							
Confusion Matrix Normalized					
 	cyprus	other					
cyprus	0.494048	0.005952					
other	0.008929	0.491071					
							
Classification Metrics					
 	precision 	recall	f1-score	accuracy	support		
cyprus	0.98	0.99	0.99	 	168		
other	0.99	0.98	0.99	 	168		
OVERALL	0.99	0.99	0.99	0.99	336		
							
Time Metrics		OUR PC			HPC	
training time for 50 epochs: 	7870.6950762271881 seconds		
test time for 336 samples: 	69.01968908309937 seconds		
							
frescoes_location 						
							
Confusion Matrix						
 	cyprus	italy	other				
cyprus	49	0	1				
italy	0	49	1				
other	2	6	36				
							
Confusion Matrix Normalized					
 	cyprus	italy	other				
cyprus	0.340278	0	0.006944				
italy	0	0.340278	0.006944				
other	0.013889	0.041667	0.25				
							
Classification Metrics					
	precision 	recall	f1-score	accuracy	support		
cyprus	0.96	0.98	0.97	 	50		
italy	0.89	0.98	0.93	 	50		
other	0.95	0.82	0.88	 	44		
OVERALL	0.93	0.93	0.93	0.93	144		
							
Time Metrics		OUR PC			HPC	
training time for 50 epochs: 	4983.8516481564682 seconds		
test time for 144 samples: 	8.449592590332031 seconds		
							
frescoes_period						
							
Confusion Matrix						
 	cyprus	other					
cyprus	60	5					
other	4	74					
							
Confusion Matrix Normalized					
 	cyprus	other					
cyprus	0.41958	0.034965					
other	0.027972	0.517483					
							
Classification Metrics					
 	precision 	recall	f1-score	accuracy	support		
byzantine	0.94	0.92	0.93	 	65		
other	0.94	0.95	0.94	 	78		
OVERALL	0.94	0.94	0.94	0.94	143		
							
Time Metrics		OUR PC			HPC	
training time for 50 epochs: 	4951.2189649846356 seconds		
test time for 143 samples: 	7.021983623504639 seconds		
							
							
artefact_v3						
							
Confusion Matrix						
 	coins	frescoes	icons	manuscripts	others		
coins	144	0	0	0	0		
frescoes	3	137	4	0	3		
icons	0	7	132	4	1		
manuscripts	0	1	2	141	0		
others	1	1	0	0	142		
							
Confusion Matrix Normalized					
 	coins	frescoes	icons	manuscripts	others		
coins	0.19917	0	0	0	0		
frescoes	0.004149	0.189488	0.005533	0	0.004149		
icons	0	0.009682	0.182573	0.005533	0.001383		
manuscripts	0	0.001383	0.002766	0.195021	0		
others	0.001383	0.001383	0	0	0.196404		
							
Classification Metrics					
 	precision 	recall	f1-score	accuracy	support		
coins	0.99	1	1	 	144		
frescoes	0.94	0.95	0.94	 	144		
icons	0.96	0.92	0.94	 	144		
manuscripts	0.97	0.98	0.98	 	144		
others	0.97	0.99	0.98	 	144		
OVERALL	0.97	0.97	0.97	0.97	720		
							
Time Metrics		OUR PC			HPC	
training time for 10 epochs: 	3204.6192967891693 seconds		
test time for 720 samples: 	53.86625933647156 seconds		
