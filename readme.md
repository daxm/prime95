# Welcome to the Prime95 Stats project!

The goal of this project is to allow user's of the Great Internet Mersenne Prime Search (GIMPS) to gather statistics of
their efforts on this project.

NOTE:  I purposely didn't add the userdata.py file as that is where your username and password should be stored in that
file.  Create a userdata.py file and add the following two lines:
```
USERNAME = 'your_gimps_username'
PASSWORD = 'your_gimps_password'
```
OR, you can just add the **USERNAME** and **PASSWORD** variables to the top of your ghz-days.py script and comment out the
following in ghz-days.py:
```
from userdata import *
```

My first goal is to compute the average GHz-days on a daily basis.  (I know, it is weird to think of GHz-days/day but
that is the units being measured here.)
