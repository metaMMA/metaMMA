#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import fnmatch
import re
from shutil import copyfile
from shutil import move
from datetime import datetime
import time
import glob
import user_info
import plex_token
import info_check
import urllib
import urllib.request
ts = "["+time.strftime("%Y-%m-%d %H:%M:%S")+"] " # timestamp string used at beginning of log file
addts = "\n"+ts # timestamp string used after beginning of log file
buf = "\n                      " # buffer space for mult-line log entries

#############################################################################################################################################
# Check to make sure the user has updated their information in user_info.py
if (info_check.info_updated == 0) or (info_check.b_updated != 1):
    exit()
#############################################################################################################################################

# Block 0 checks to see if this is the first time running the script and exits until Bellator.py creates the correct directories
# 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
if not os.path.exists(info_check.ufc_direct):
    exit()
if not os.path.exists(info_check.b_direct):
    exit()
# 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
def logger(loginfo):
    with open(info_check.b_direct+"log.txt", "a") as log:
        log.write(addts+loginfo)
        log.close()
def endit():
    os.remove(info_check.mma_direct+'mover-running.holder')
    exit()
time.sleep(15) # this prevents UFCmover.py and BellatorMover.py from running at the same time at :00 and :30
# Block 1 checks to see if this script is attempting to execute while it has not finished running
# 1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
BellatorMover_running_holder_list = glob.glob(info_check.mma_direct+'mover-running.holder') # check to see if this the "mover-running.holder" file exists (if it does, that means this UFCmover.py or BellatorMover.py script is currently running)
if len(BellatorMover_running_holder_list) == 1:
    log = open(info_check.b_direct+'stop-log.txt','a')
    log.write(addts+"An attempt to run BellatorMover.py was made. However, UFCmover.py or BellatorMover.py is currently running because mover-running.holder is present.")
    log.close()
    exit() # end the script if the "mover-running.holder" is present
else:
    BellatorMover_running_holder = open(info_check.mma_direct+'mover-running.holder','w') # if "mover-running.holder" doesn't exist (the script is NOT currently running), then create "mover-running.holder"
    BellatorMover_running_holder.write(ts+"BellatorMover.py started running.")
    BellatorMover_running_holder.close()
    logger("BellatorMover.py started running.")
# 1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

# Block 2 checks to see how old the log.txt file is, if it is older than 3 weeks, create a new log.tx file and move the log.txt file to previous-log.txt
# 2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222
Bellator_running_holder_list = glob.glob(info_check.b_direct+'BellatorRunning.holder') # check to see if the "BellatorRunning.holder" file exists (if it does, that means this Bellator.py script is currently running)
if len(Bellator_running_holder_list) < 1:
    with open(info_check.b_direct+'log.txt','r') as myfile:
        earliest_date=myfile.read()[1:20]
        myfile.close()
    earliest_date_object = datetime.strptime(earliest_date,'%Y-%m-%d %H:%M:%S')
    current_date_object = datetime.now()
    time_dif = current_date_object - earliest_date_object
    second_dif = time_dif.total_seconds()
    if (second_dif > 1814400) and (len(Bellator_running_holder_list) < 1): # if the current log.txt file is has over 3 weeks of logs and the other script is not running then proceed
        previous_log_holder_list = glob.glob(info_check.b_direct+'previous-log.txt') # check to see if the "previous-log.txt" file exists
        if len(previous_log_holder_list) == 1:
            os.remove(info_check.b_direct+'previous-log.txt')
        move(info_check.b_direct+'log.txt', info_check.b_direct+'previous-log.txt')
        filename = info_check.b_direct+"log.txt"
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(filename, "w") as log:
            log.write(ts+"New log.txt file created. For the previous 3 weeks of logs, open previous-log.txt.")
            log.close()
# 2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222

video_holder_filename = [] # this list will contain all the "holder" filenames that are waiting for a video file to replace them
video_holder_path = [] # this list will contain the path to the "holder" files
video_holder_path_and_file = [] # this list contains the whole path and filname of the "holder" file (will be used to delete the holder file after the video file that is replacing it is moved)

for root, dirnames, filenames in os.walk(user_info.b_destination): # this directory is where all new events directories will be created
    for filename in fnmatch.filter(filenames, '*.holder.avi'): # look for all 'holder' files that were created with each new event directory
        video_holder_filename.append(filename[:-11])
        video_holder_path.append(root)
        video_holder_path_and_file.append(os.path.join(root,filename))
'''
for root, dirnames, filenames in os.walk(user_info.b_destination): # this directory is where all new events directories will be created
    for filename in fnmatch.filter(filenames, '*Soon - Early Prelims.holder'): # look for all 'holder' files that were created with each new event directory
        video_holder_path_and_file.append(os.path.join(root,filename))
        video_holder_path.append(root)
        ep_filename = open(os.path.join(root,filename),'r').read()
        video_holder_filename.append(ep_filename)

for root, dirnames, filenames in os.walk(user_info.b_destination): # this directory is where all new events directories will be created
    for filename in fnmatch.filter(filenames, '*Soon - Prelims.holder'): # look for all 'holder' files that were created with each new event directory
        video_holder_path_and_file.append(os.path.join(root,filename))
        video_holder_path.append(root)
        p_filename = open(os.path.join(root,filename),'r').read()
        video_holder_filename.append(p_filename)
'''
if len(video_holder_path) < 1:
    logger("There were no holder files in the destination directory, therefore no files to look for. The script will stop running now.")
    endit()

for x in range(0,len(video_holder_filename)):
    holder_search_terms1 = video_holder_filename[x].lower()
    holder_search_terms = holder_search_terms1.split()
    completed_video_path_and_filename = []
    completed_video_filename = []
    for root, dirnames, filenames in os.walk(user_info.done_dir): # this is the directory that the completed video files are moved to. MUST BE ON SAME DRIVE AS DOWNLOAD DIRECTORY
        for filename in fnmatch.filter(filenames, '*[m|M][k|K|p|P][v|V|4]'): # search for video files ending in "mp4" or "mkv"
            completed_video_path_and_filename.append(os.path.join(root, filename))
            completed_video_filename.append(filename)
    for y in range(0,len(completed_video_path_and_filename)):
        completed_video_name_lower = completed_video_filename[y].lower()
        completed_video_name_no_spaces = completed_video_name_lower.replace(" ",".")
        completed_video_name_fixed = re.sub(r'[P|p][R|r][E|e][L|l][I|i][a-zA-Z]+',r'prelim',completed_video_name_no_spaces) # replaces any version of "PRELIMINARY/prelims" with "prelim" to standardize the search term
        video_name_search_terms = completed_video_name_fixed.rsplit(".")
        if set(video_name_search_terms).issuperset(holder_search_terms):
            if ('early' in video_name_search_terms) and ('early' in holder_search_terms):
                if 'mkv' in video_name_search_terms:
                    copyfile(completed_video_path_and_filename[y], video_holder_path[x]+'/Early Prelims.mkv')
                    os.remove(video_holder_path_and_file[x])
                    logger("Video found at"+buf+completed_video_path_and_filename[y]+buf+"was copied to"+buf+video_holder_path[x]+"/Early Prelims.mkv"+buf+"and"+buf+video_holder_path_and_file[x]+buf+"was deleted.")
                    whole_dir_plus = video_holder_path[x]
                    whole_dir = whole_dir_plus[:-10]
                    move(whole_dir,user_info.tmp_dir)
                    urllib.request.urlopen('http://localhost:32400/library/sections/'+plex_token.section+'/refresh?X-Plex-Token='+plex_token.token)
                    logger("Directory"+buf+whole_dir+buf+"was moved to "+buf+user_info.tmp_dir+buf+"to remove from pleX.")
                    time.sleep(30)
                    for node in os.listdir(user_info.tmp_dir):
                        if not os.path.isdir(node):
                            move(os.path.join(user_info.tmp_dir, node) , os.path.join(user_info.b_destination, node))
                            urllib.request.urlopen('http://localhost:32400/library/sections/'+plex_token.section+'/refresh?X-Plex-Token='+plex_token.token)
                    logger("Directories and files moved back to"+buf+user_info.b_destination+buf+"in order to force pleX to refresh. The script will stop running now.")
                    endit()
                else:
                    copyfile(completed_video_path_and_filename[y], video_holder_path[x]+'/Early Prelims.mp4')
                    os.remove(video_holder_path_and_file[x])
                    logger("Video found at"+buf+completed_video_path_and_filename[y]+buf+"was copied to"+buf+video_holder_path[x]+"/Early Prelims.mp4"+buf+"and"+buf+video_holder_path_and_file[x]+buf+"was deleted.")
                    whole_dir_plus = video_holder_path[x]
                    whole_dir = whole_dir_plus[:-10]
                    move(whole_dir,user_info.tmp_dir)
                    urllib.request.urlopen('http://localhost:32400/library/sections/'+plex_token.section+'/refresh?X-Plex-Token='+plex_token.token)
                    logger("Directory"+buf+whole_dir+buf+"was moved to "+buf+user_info.tmp_dir+buf+"to remove from pleX.")
                    time.sleep(30)
                    for node in os.listdir(user_info.tmp_dir):
                        if not os.path.isdir(node):
                            move(os.path.join(user_info.tmp_dir, node) , os.path.join(user_info.b_destination, node))
                            urllib.request.urlopen('http://localhost:32400/library/sections/'+plex_token.section+'/refresh?X-Plex-Token='+plex_token.token)
                    logger("Directories and files moved back to"+buf+user_info.b_destination+buf+"in order to force pleX to refresh. The script will stop running now.")
                    endit()
            elif ('prelim' in video_name_search_terms) and ('prelim' in holder_search_terms) and ('early' not in video_name_search_terms) and ('early' not in holder_search_terms):
                if 'mkv' in video_name_search_terms:
                    copyfile(completed_video_path_and_filename[y], video_holder_path[x]+'/Prelims.mkv')
                    os.remove(video_holder_path_and_file[x])
                    logger("Video found at"+buf+completed_video_path_and_filename[y]+buf+"was copied to"+buf+video_holder_path[x]+"/Prelims.mkv"+buf+"and"+buf+video_holder_path_and_file[x]+buf+"was deleted.")
                    whole_dir_plus = video_holder_path[x]
                    whole_dir = whole_dir_plus[:-10]
                    move(whole_dir,user_info.tmp_dir)
                    urllib.request.urlopen('http://localhost:32400/library/sections/'+plex_token.section+'/refresh?X-Plex-Token='+plex_token.token)
                    logger("Directory"+buf+whole_dir+buf+"was moved to "+buf+user_info.tmp_dir+buf+"to remove from pleX.")
                    time.sleep(30)
                    for node in os.listdir(user_info.tmp_dir):
                        if not os.path.isdir(node):
                            move(os.path.join(user_info.tmp_dir, node) , os.path.join(user_info.b_destination, node))
                            urllib.request.urlopen('http://localhost:32400/library/sections/'+plex_token.section+'/refresh?X-Plex-Token='+plex_token.token)
                    logger("Directories and files moved back to"+buf+user_info.b_destination+buf+"in order to force pleX to refresh. The script will stop running now.")
                    endit()
                else:
                    copyfile(completed_video_path_and_filename[y], video_holder_path[x]+'/Prelims.mp4')
                    os.remove(video_holder_path_and_file[x])
                    logger("Video found at"+buf+completed_video_path_and_filename[y]+buf+"was copied to"+buf+video_holder_path[x]+"/Prelims.mp4"+buf+"and"+buf+video_holder_path_and_file[x]+buf+"was deleted.")
                    whole_dir_plus = video_holder_path[x]
                    whole_dir = whole_dir_plus[:-10]
                    move(whole_dir,user_info.tmp_dir)
                    urllib.request.urlopen('http://localhost:32400/library/sections/'+plex_token.section+'/refresh?X-Plex-Token='+plex_token.token)
                    logger("Directory"+buf+whole_dir+buf+"was moved to "+buf+user_info.tmp_dir+buf+"to remove from pleX.")
                    time.sleep(30)
                    for node in os.listdir(user_info.tmp_dir):
                        if not os.path.isdir(node):
                            move(os.path.join(user_info.tmp_dir, node) , os.path.join(user_info.b_destination, node))
                            urllib.request.urlopen('http://localhost:32400/library/sections/'+plex_token.section+'/refresh?X-Plex-Token='+plex_token.token)
                    logger("Directories and files moved back to"+buf+user_info.b_destination+buf+"in order to force pleX to refresh. The script will stop running now.")
                    endit()
            elif ('early' not in video_name_search_terms) and ('prelim' not in video_name_search_terms) and ('early' not in holder_search_terms) and ('prelim' not in holder_search_terms):
                title = video_holder_path[x].rsplit('/',1)[1]
                if 'mkv' in video_name_search_terms:
                    copyfile(completed_video_path_and_filename[y], video_holder_path[x]+'/'+title+'.mkv')
                    logger("Video found at"+buf+completed_video_path_and_filename[y]+buf+"was copied to"+buf+video_holder_path[x]+"/"+title+".mkv.")
                    for basename in os.listdir(video_holder_path[x]+'/'):
                        if basename.endswith('.jpg'):
                            pathname = os.path.join(video_holder_path[x]+'/', basename)
                            if os.path.isfile(pathname):
                                move(pathname, video_holder_path[x]+'/'+title+".jpg")
                    logger("Poster renamed to match recently moved Main Card")
                    old_nfo = open(video_holder_path[x]+'/'+title+'.nfo','r')
                    new_nfo = open(video_holder_path[x]+'/'+title+'2.nfo', 'w')
                    for line in old_nfo:
                        new_nfo.write(line.replace('Soon - ', ''))
                    old_nfo.close()
                    new_nfo.close()
                    os.remove(video_holder_path[x]+'/'+title+'.nfo')
                    move(video_holder_path[x]+'/'+title+'2.nfo',video_holder_path[x]+'/'+title+'.nfo')
                    logger("NFO file updated, removed \"Soon - \" from before the title")
                    os.remove(video_holder_path_and_file[x])
                    logger(video_holder_path_and_file[x]+" was deleted.")
                    move(video_holder_path[x]+"/",user_info.tmp_dir)
                    urllib.request.urlopen('http://localhost:32400/library/sections/'+plex_token.section+'/refresh?X-Plex-Token='+plex_token.token)
                    logger("Directory"+buf+video_holder_path[x]+"/"+buf+"was moved to "+buf+user_info.tmp_dir+buf+"to remove from pleX.")
                    time.sleep(30)
                    for node in os.listdir(user_info.tmp_dir):
                        if not os.path.isdir(node):
                            move(os.path.join(user_info.tmp_dir, node) , os.path.join(user_info.b_destination, node))
                            urllib.request.urlopen('http://localhost:32400/library/sections/'+plex_token.section+'/refresh?X-Plex-Token='+plex_token.token)
                    logger("Directories and files moved back to"+buf+user_info.b_destination+buf+"in order to force pleX to refresh. The script will stop running now.")
                    endit()
                else:
                    copyfile(completed_video_path_and_filename[y], video_holder_path[x]+'/'+title+'.mp4')
                    logger("Video found at"+buf+completed_video_path_and_filename[y]+buf+"was copied to"+buf+video_holder_path[x]+"/"+title+".mp4.")
                    for basename in os.listdir(video_holder_path[x]+'/'):
                        if basename.endswith('.jpg'):
                            pathname = os.path.join(video_holder_path[x]+'/', basename)
                            if os.path.isfile(pathname):
                                move(pathname, video_holder_path[x]+'/'+title+".jpg")
                    logger("Poster renamed to match recently moved Main Card")
                    old_nfo = open(video_holder_path[x]+'/'+title+'.nfo','r')
                    new_nfo = open(video_holder_path[x]+'/'+title+'2.nfo', 'w')
                    for line in old_nfo:
                        new_nfo.write(line.replace('Soon - ', ''))
                    old_nfo.close()
                    new_nfo.close()
                    os.remove(video_holder_path[x]+'/'+title+'.nfo')
                    move(video_holder_path[x]+'/'+title+'2.nfo',video_holder_path[x]+'/'+title+'.nfo')
                    logger("NFO file updated, removed \"Soon - \" from before the title")
                    os.remove(video_holder_path_and_file[x])
                    logger(video_holder_path_and_file[x]+" was deleted.")
                    move(video_holder_path[x]+"/",user_info.tmp_dir)
                    urllib.request.urlopen('http://localhost:32400/library/sections/'+plex_token.section+'/refresh?X-Plex-Token='+plex_token.token)
                    logger("Directory"+buf+video_holder_path[x]+"/"+buf+"was moved to "+buf+user_info.tmp_dir+buf+"to remove from pleX.")
                    time.sleep(30)
                    for node in os.listdir(user_info.tmp_dir):
                        if not os.path.isdir(node):
                            move(os.path.join(user_info.tmp_dir, node) , os.path.join(user_info.b_destination, node))
                            urllib.request.urlopen('http://localhost:32400/library/sections/'+plex_token.section+'/refresh?X-Plex-Token='+plex_token.token)
                    logger("Directories and files moved back to"+buf+user_info.b_destination+buf+"in order to force pleX to refresh. The script will stop running now.")
                    endit()
logger("There were holder files in the destination directory, but there were no matching video files in your source directory. The script will stop running now.")
endit()
