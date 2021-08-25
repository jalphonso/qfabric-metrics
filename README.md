# Summary
This project has two parts. First part runs on the QFabric director and collects interface stats.
The second parts parses and analyzes the data.

### Usage
Execute collection of data
```
mkdir csv reports
nohup python monitor_interfaces.py >> monitor_interfaces.log &
```

Parse data
`python analyze_data.py`

### Requirements
No external libraries are needed; however, Python 3.7 (64-bit) is required for analyze_data.py
Since monitor_interfaces.py runs on the Qfabric, Python 2.4 is what is used for that.

Memory considerations: consumes approximately 1.11GB per 100K lines of log entries in csv format


###############################################################################
###			Data Collection:
###############################################################################

###############################################################################
###Log into Master DG as user root.
###############################################################################

```
login as: root
root@xxx.xxx.xxx.21's password:
Last login: Fri Apr  5 11:14:07 2019 from 172.24.0.219
Juniper QFabric Director 13.1.8962 2016-02-17 14:28:24 UTC

[root@dg0 ~]#
[root@dg0 ~]#
[root@dg0 ~]# pwd
/root
[root@dg0 ~]# cd /pbdata/packages/scripts/csv
	NOTE: If the csv file isn't auto created, make sure you create the csv
		folder in /scripts folder.

[root@dg0 ~]# cd ..
```
###############################################################################
###SCP script to the /pbdata/packages/scripts folder
###############################################################################

scp the "monitor_interfaces.py" file located in the scripts folder to local
workstation to be burned to cd.
You will also need to scp the file to the Production DG when the time comes.

###############################################################################
###Create the "monitor_interfaces.log" file.
###############################################################################

This is automagically created when you issue the command below.

###############################################################################
###Check to make sure everything looks good.
###############################################################################
```
[root@dg0 scripts]# ls -alh
total 128K
drwxr-xr-x 4 root root 3.8K Apr  5 12:57 .
drwxrwxrwx 6 root root 2.0K Apr  5 11:14 ..
drwxr-xr-x 2 root root 3.8K Apr  4 19:23 csv
-rw-r--r-- 1 root root  65K Apr  5 12:52 monitor_interfaces.log
-rw-r--r-- 1 root root 4.3K Apr  5 12:56 monitor_interfaces.py
drwxr-xr-x 2 root root 3.8K Apr  5 12:57 old
[root@dg0 scripts]#
[root@dg0 scripts]# md5sum monitor_interfaces.py
56a93d7641c3c80ed8cd04a8b3a99d99  monitor_interfaces.py
[root@dg0 scripts]# cat monitor_interfaces.py | wc -l
98
[root@dg0 scripts]#
```
###############################################################################
###Start the "monitor_interfaces.py" script.
###############################################################################
```
[root@dg0 scripts]# pwd
/pbdata/packages/scripts
[root@dg0 scripts]# ls -alh
total 128K
drwxr-xr-x 4 root root 3.8K Apr  5 13:11 .
drwxrwxrwx 6 root root 2.0K Apr  5 11:14 ..
drwxr-xr-x 2 root root 3.8K Apr  4 19:23 csv
-rw-r--r-- 1 root root  65K Apr  5 12:52 monitor_interfaces.log
-rw-r--r-- 1 root root 4.3K Apr  5 12:56 monitor_interfaces.py
drwxr-xr-x 2 root root 3.8K Apr  5 12:57 old
[root@dg0 scripts]# nohup python monitor_interfaces.py >> monitor_interfaces.log &
[1] 2883
[root@dg0 scripts]#
```
###############################################################################
###Tail the "monitor_interfaces.log" to monitor it's progress.
###############################################################################
```
[root@dg0 scripts]# tail -n 20 monitor_interfaces.log
2019-04-05 16:41:08
Retrieving Interface data from Fabric...
The QFabric command 'show interfaces fabric extensive *fte*' took 38 seconds to run
Run completed at 2019-04-05 16:41:48
300 seconds until the next run. Ctrl+c to quit
Countdown until next run:  300 290 280 270 260 250 240 230 220 210 200 190 180 170 160 150 140 130 120 110 100 90 80 70 60 50 40 30 20 10

2019-04-05 16:46:48
Retrieving Interface data from Fabric...
The QFabric command 'show interfaces fabric extensive *fte*' took 42 seconds to run
Run completed at 2019-04-05 16:47:33
300 seconds until the next run. Ctrl+c to quit
Countdown until next run:  300 290 280 270 260 250 240 230 220 210 200 190 180 170 160 150 140 130 120 110 100 90 80 70 60 50 40 30 20
Quitting per user's request...
2019-04-05 17:15:10
Retrieving Interface data from Fabric...
The QFabric command 'show interfaces fabric extensive *fte*' took 40 seconds to run
Run completed at 2019-04-05 17:15:52
300 seconds until the next run. Ctrl+c to quit
Countdown until next run:  300 290 280 270 260 250 240 230 220 [root@dg0 scripts]#
```
###############################################################################
###To kill the PID of the script process use the following command
###############################################################################

Find the PID of the script:
```
[root@dg0 csv]#
[root@dg0 csv]# ps aux | grep python
root      2883  0.5  0.3 209524 119708 ?       S    13:15   0:41 python monitor_interfaces.py
root     18505  0.0  0.0  61212   808 pts/1    S+   15:13   0:00 grep python
[root@dg0 csv]#


kill -SIGINT <PID>
kill -SIGINT 2883
```



###############################################################################
Post Processing
###############################################################################


Copy the analyze_data.py, interface_stats.py files to your Python 2.7 environement.

Make sure you have the following two directories:
	mkdir csv
	mkdir reports
Place all your csv files retrieved from the csv directory on the QFabric Director into the csv folder.

Execute the script:
	python analyze_data.py

