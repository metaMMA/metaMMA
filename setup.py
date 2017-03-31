#!/usr/bin/env python
import info_check
import user_info
import event_info
import os
import time
import re
import platform

ts = "["+time.strftime("%Y-%m-%d %H:%M:%S")+"] " # timestamp string used at beginning of log file
dic = {'Invicta FC':'inv','Bellator':'bel','UFC':'ufc','WSOF':'wsof','Titan FC':'ttn','Legacy Fighting Alliance':'lfa','ONE Championship':'one','Glory':'glr'}
i_dic = {v: k for k, v in dic.items()}
if platform.system() == 'Windows' or platform.system() == 'windows':
    os.system("py -3 info_check.py")
    os.system("py -3 plex_token.py")
else:
    os.system("python3 info_check.py")
    os.system("python3 plex_token.py")
meta_dir = info_check.meta
vdata = open(info_check.meta+'version.txt','r')
v = vdata.read()
v = v.strip('\n')
vdata.close()
version = v[1:]

if not os.path.exists(info_check.mma_direct):
    os.makedirs(info_check.mma_direct)
if not os.path.isfile(info_check.mma_direct+'execution-log.txt'):
    elog = open(info_check.mma_direct+'execution-log.txt','w')
    elog.write(ts+"This file logs whenever meta.py or mover.py was attempting to execute while it had not finished running.")
    elog.close()
if not os.path.exists(user_info.tmp_dir):
    os.makedirs(user_info.tmp_dir)
if not os.path.isfile(info_check.mma_direct+"log.txt"):
    log = open(info_check.mma_direct+"log.txt", "w")
    log.write(ts+"Set-up started. Created .MMA directory, temporary directory, execution-log.txt, and log.txt.")
    log.close()
if not os.path.isfile(info_check.mma_direct+'stats.txt'):
    stats = open(info_check.mma_direct+"stats.txt", "w")
    stats.write("---------------------------Stats since "+ts+"---------------------------\n[2000-00-00 00:00:00] - last time meta.py was started.\n[2000-00-00 00:00:00] - last time meta.py successfully exited.\n\n[2000-00-00 00:00:00] - last time mover.py was started.\n[2000-00-00 00:00:00] - last time mover.py successfully exited.\n\n[2000-00-00 00:00:00] - last time updater.py was started. ---------Current: v"+version+"\n[2000-00-00 00:00:00] - last time updater.py successfully exited. --Latest: v"+version+"\n----------------------------------------------------------------------------------------\n\n0: total number of MMA events scraped\n0: total number of MMA video files moved")
    stats.close()
if not os.path.isfile(info_check.mma_direct+'event_dates.txt'):
    dates = open(info_check.mma_direct+'event_dates.txt','w')
    dates.write('----------Dates of upcoming MMA events----------')
    dates.close()
if not os.path.exists(user_info.done_dir):
    os.makedirs(user_info.done_dir)
if not os.path.exists(user_info.mma_destination):
    os.makedirs(user_info.mma_destination)

for x in range(0,len(info_check.promolist)):
    if user_info.MMA == 0:
        if not os.path.exists(eval('user_info.'+info_check.promolist[x]+'_destination')):
            os.makedirs(eval('user_info.'+info_check.promolist[x]+'_destination'))
    s = open(info_check.mma_direct+'stats.txt','r')
    stats = s.read()
    stats_exist = re.findall(i_dic[info_check.promolist[x]],stats)
    s.close()
    if len(stats_exist) < 1:
        edit = open(info_check.mma_direct+'stats.txt','a')
        edit.write('\n0: '+i_dic[info_check.promolist[x]]+' events scraped\n0: '+i_dic[info_check.promolist[x]]+' video files moved')
        edit.close()
    d = open(info_check.mma_direct+'event_dates.txt','r')
    dates = d.read()
    promo_date_exists = re.findall(i_dic[info_check.promolist[x]],dates)
    d.close()
    if len(promo_date_exists) < 1:
        event = event_info.Event(info_check.promolist[x])
        event.future('setup')
        time.sleep(5)
