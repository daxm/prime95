# Welcome to the Prime95 Stats project!

The goal of this project is to allow user's of the Great Internet Mersenne Prime Search (GIMPS) to gather statistics of
their efforts on this project.

To install the necessary packages issue the following command:
```bazaar
pip3 install -r requirements.txt
```

NOTE:  I purposely didn't add the userdata.py file as that is where your username and password should be stored in that
file.  Create a userdata.py file and add the following two lines:
```bazaar
USERNAME = 'your_gimps_username'
PASSWORD = 'your_gimps_password'
```
OR, you can just add the **USERNAME** and **PASSWORD** variables to the top of your ghz-days.py script and comment out 
the following in my_gimps_stats.py:
```bazaar
from userdata import *
```

##Runable files:

**my_gimps_stats.py**
* Reports your average Ghz-days/day, your 365 and Overall rankings, as well as your estimated date of surpassing the
 next "Top 500" rank above you.

**build_and_populate_top500_db.py**
* If the file doesn't exist it will build a sqlite3 db file.  It will also add today's Top500 stats into said db.
This file should be run **daily** to give you accurate reporting on the "last 365" deltas.

**report_ave_ghzdays_top500.py**
* This file will pull the current moment rankings and their current Ghz Days values.  It will then compare those
rank/value pairs against the daily record (in the Top500.db file created by the build_and_populate_top500_db.py program)
that is nearest to 365 days ago.
