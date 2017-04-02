#!/usr/bin/env python

import info_check
import urllib.request
from urllib.request import urlopen
from shutil import copyfile
from shutil import move
import shutil
import re
import os
from distutils.version import StrictVersion
import time
import random
import subprocess
import logging

if info_check.info_updated == 0 or not os.path.exists(info_check.mma_direct):
    exit()
if os.path.isfile(info_check.mma_direct+"log.txt"):
    logging.basicConfig(filename=info_check.mma_direct+"log.txt",level=logging.DEBUG,format='[%(asctime)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger(__name__)
buf = "\n                      " # buffer space for mult-line log entries

def endit():
    os.remove(info_check.mma_direct+'mover.running')
    exit()

def exit_stats():
    f = open(info_check.mma_direct+'stats.txt','r')
    filedata = f.read()
    f.close()
    newdata = re.sub(r'\[.*last time updater\.py successfully exited.*[0-9]', '['+time.strftime("%Y-%m-%d %H:%M:%S")+'] - last time updater.py successfully exited. --Latest: v'+version, filedata)
    f = open(info_check.mma_direct+'stats.txt','w')
    f.write(newdata)
    f.close()
    endit()

vdata = open(info_check.meta+'version.txt','r')
v = vdata.read()
version = re.sub('\n','',v[1:])
vdata.close()

f = open(info_check.mma_direct+'stats.txt','r')
filedata = f.read()
f.close()
newdata = re.sub(r'\[.*last time updater\.py was started.*[0-9]','['+time.strftime("%Y-%m-%d %H:%M:%S")+'] - last time updater.py was started. ---------Current: v'+version,filedata)
f = open(info_check.mma_direct+'stats.txt','w')
f.write(newdata)
f.close()

time.sleep(random.randint(5,600))

for try_count in range(0,2):
    try_count += 1
    if os.path.isfile(info_check.mma_direct+'mover.running'):
        running = open(info_check.mma_direct+'mover.running','r')
        running_script = running.read()
        running.close()
        running_script_name = running_script[22:]
        log = open(info_check.mma_direct+'execution-log.txt','a')
        if running_script_name == 'mover.py':
            if try_count == 1:
                log.write("\n["+time.strftime("%Y-%m-%d %H:%M:%S")+"] An attempt to run updater.py was made. However, mover.py is currently running. Waiting 4 minutes and trying again.")
                log.close()
                time.sleep(240)
            if try_count == 2:
                log.write("\n["+time.strftime("%Y-%m-%d %H:%M:%S")+"] A second attempt to run updater.py was made. However, mover.py is still currently running. Trying again tomorrow.")
                log.close()
                exit()
        elif running_script_name == 'updater.py':
            log.write("\n["+time.strftime("%Y-%m-%d %H:%M:%S")+"] An attempt to run updater.py was made. However, updater.py is currently running. The script will stop running now.")
            log.close()
            exit()

with open(info_check.mma_direct+'mover.running', "w") as running:
    running.write('['+time.strftime("%Y-%m-%d %H:%M:%S")+'] updater.py')
    running.close()

readme = urllib.request.urlopen('https://github.com/metaMMA/metaMMA/blob/master/README.md').read().decode('utf-8')

latest_version_line = re.findall(r'<p>v.*? - latest stable version</p>',readme)[0]
latest_version_num = re.findall(r'(?<=v)[0-9].*?(?=\s-)',latest_version_line)[0]

if StrictVersion(latest_version_num) > StrictVersion(version):
    logger.info("v"+latest_version_num+" is an update you your current version (v"+version+"). Attempting to dowload from github.com.")
    PIPE = subprocess.PIPE
    branch = "https://github.com/metaMMA/metaMMA"
    process = subprocess.Popen(['git', 'clone', branch], stdout=PIPE, stderr=PIPE, cwd=info_check.home)
    stdoutput, stderroutput = process.communicate()

    if os.path.isdir(os.path.join(os.path.join(info_check.home,".metaMMAold"),"")): #if the previous metaMMA version is stored, delete it
        logger.info("Attempting to delete previous .metaMMA directory found at .metaMMAold.")
        shutil.rmtree(os.path.join(os.path.join(info_check.home,".metaMMAold"),""))

    logger.info("Attempting to rename current .metaMMA directory to .metaMMAold.")
    move(info_check.meta, os.path.join(os.path.join(info_check.home,".metaMMAold"),"")) # rename the current metaMMA release to 'metalMMAold'
    logger.info("Attempting to rename newly downloaded metaMMA directory to .metaMMA.")
    move(info_check.home+'metaMMA', info_check.meta)

    if os.path.isfile(info_check.meta+'user_info.py'):
        old_user_info = open(os.path.join(info_check.home+'.metaMMAold','')+'user_info.py','r')
        old_user_info_block = old_user_info.read()
        old_user_info.close()
        new_generic_user_info = open(info_check.meta+'user_info.py').readlines()
        updated_user_info = open(info_check.meta+'user_info2.py','a')
        for line in new_generic_user_info:
        	place = line.find('=')
        	if place > 0:
        		if len(re.findall(line[:place],old_user_info_block))>0:
        			word=line[0:place]
        			updated_user_info.write(re.search(word+r'.*'+'\n',old_user_info_block).group())
        		else:
        			updated_user_info.write(line.rstrip()+'\n')
        	else: updated_user_info.write(line.rstrip()+'\n')
        updated_user_info.close()
        logger.info("Attempting to delete generic user_info file from new download.")
        os.remove(info_check.meta+'user_info.py') #remove the new stock user_info.py file
        logger.info("Attempting to rename updated user_info.py.")
        move(info_check.meta+'user_info2.py',info_check.meta+'user_info.py')

vdata = open(info_check.meta+'version.txt','r')
v = vdata.read()
version = re.sub('\n','',v[1:])
vdata.close()
exit_stats()
