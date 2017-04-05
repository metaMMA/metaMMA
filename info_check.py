#!/usr/bin/env python
import user_info, re, os
from pathlib import PurePath
dic = {'inv':'Invicta','bel':'Bellator','ufc':'UFC','wsof':'WSOF','ttn':'Titan','lfa':'Legacy','one':'ONE','glr':'Glory'}
info_updated = 0
promolist = []
for k, v in dic.items():
    if eval('user_info.'+v) == 1: # create list of promotions that need metadata scrape
        promolist.append(k)
if user_info.mma_destination == '/media/QQQ/MMA/':
    print('Please update the MMA destination directory.')
    exit()
elif user_info.MMA != 1:
    for x in range(0,len(promolist)): # if all promotions will have different destination directories, make sure they are specified
        if eval('user_info.'+promolist[x]+'_destination') == os.path.join('/media/QQQ/'+dic[promolist[x]],''):
            print('Please update the '+dic[promolist[x]]+' destination directory.')
            exit()
        elif PurePath(user_info.mma_destination) not in PurePath(eval('user_info.'+promolist[x]+'_destination')).parents:
            print(user_info.mma_destination+' must be the parent dicrectory of '+eval('user_info.'+promolist[x]+'_destination'))
            exit()
elif user_info.refresh_plex > 1:
    print('Please choose \'1\' or \'0\' for \'refresh_plex\'')
    exit()
elif user_info.refresh_kodi > 1:
    print('Please choose \'1\' or \'0\' for \'refresh_kodi\'')
    exit()
elif (user_info.tmp_dir == '/media/QQQ/tmp/'):
    print('Please update the temporary directory.')
    exit()
elif (user_info.done_dir == '/media/QQQ/done/'):
    print('Please update the the video source directory.')
    exit()
if user_info.refresh_kodi == 1:
    if not os.path.isfile(os.path.join(os.path.expanduser("~"),"")+'texturecache.py'):
        print('Please install \'texturecache.py\' in order to refresh KODI.')
        exit()
if user_info.refresh_plex  == 1:
    if (user_info.mma_lib == 'QQQ'):
        print('Please update the name of the pleX library that scans for MMA videos.')
        exit()
    elif (user_info.plex_username == 'QQQ'):
        print('Please update your plex username.')
        exit()
    elif (user_info.plex_password == 'QQQ'):
        print('Please update your plex password.')
        exit()
    elif (user_info.plex_ip == '192.168.QQQ.QQQ'):
        print('Please update the ip address of the machine running the pleX media server software.')
        exit()
home = os.path.join(os.path.expanduser("~"),"")
mma_direct = os.path.join(os.path.join(home,".MMA"),"")
meta = os.path.join(os.path.join(home,".metaMMA"),"")
info_updated = 1
