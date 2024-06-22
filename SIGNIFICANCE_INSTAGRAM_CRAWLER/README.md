## Instagram crawler

The code for crawling from Instagram is closed inside this directory that include code, and configuration files.

The file "instaloader/config-sample.json" contains the configurable parameters, including the paths to the files containing hashtags and users info, to the directories in which to save downloaded data, log files, and checkpoints.

The most important parameters are:
- "execution_time": time expressed in (seconds, minutes, hours, or days based on the value of the "time_scale" parameter. For how long you want to execute the search
- "time_scale": optional values between 's', 'm', 'h', 'd' (respectively for seconds, minutes, hours, day)
- "single_hashtag_n_post": number of posts to download for that hashtag. 

The file "instagram/Hashtag.csv" contains the list of hashtags to be searched. In case you want to add one more, or rerun the search from zero, you need to set all fields to 0 except 'hashtag' field which contains the name of the hashtag itself.

The file 'instagram/User.csv' contains the list of users (accounts) from which to search. You need to set the 'username', 'password', 'phone', 'mail' fields with those of your own account, set the 'use' field to 1, set all other fields to 0.

To run the crawler (after setting the configuration parameters, hashtag file and user file), you need to run the command

`python main.py`

The main python package needed to run the code is instaloader.

The downloaded data will be saved in the "scrapedDatahashtag" folder, grouped into subfolders with the name of the hashtag.

It has noted some instabilities in the cowling code from instagram. Some of these is mainly due to the fact that instagram servers block access when they note too many requests.
In this case, it would be useful to try rerun it and the problem is overcome.
