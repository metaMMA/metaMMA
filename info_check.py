#!/usr/bin/env python
import user_info

info_updated = 0
b_updated = 0

if (user_info.bellator == 1):
    if (user_info.b_destination == '/media/QQQ/Bellator'):
        print('Please update the Bellator destination directory.')
        exit()
    b_updated = 2

if (user_info.tmp_dir == '/media/QQQ/tmp/'):
    print('Please update the temporary directory.')
    exit()
elif (user_info.done_dir == '/media/QQQ/done/'):
    print('Please update the the video source directory.')
    exit()
elif (user_info.ufc_destination == '/media/QQQ/UFC/'):
    print('Please update the UFC destination directory.')
    exit()
elif (user_info.mma_lib == 'QQQ'):
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
elif user_info.windows + user_info.linux + user_info.mac != 1:
    print('Please choose one and only one operating system.')
    exit()
elif user_info.linux == 1:
    if user_info.linux_username == 'userQQQ':
        print('Please enter your linux username.')
        exit()
    else:
        mma_direct = '/home/'+user_info.linux_username+'/.MMA/'
        ufc_direct = '/home/'+user_info.linux_username+'/.MMA/UFC/'
        info_updated = 1
        if b_updated == 2:
            b_direct = '/home/'+user_info.linux_username+'/.MMA/Bellator/'
            b_poster = '/home/'+user_info.linux_username+'/.MMAmeta/b_posters/'
            b_updated = 1
elif user_info.mac == 1:
    if user_info.mac_username == 'userQQQ':
        print('Please enter your mac username.')
        exit()
    else:
        mma_direct = '/Users/'+user_info.mac_username+'/.MMA/'
        ufc_direct = '/Users/'+user_info.mac_username+'/.MMA/UFC/'
        info_updated = 1
        if b_updated == 2:
            b_direct = '/Users/'+user_info.mac_username+'/.MMA/Bellator/'
            b_poster = '/Users/'+user_info.mac_username+'/.MMAmeta/b_posters/'
            b_updated = 1
elif user_info.windows == 1:
    mma_direct = 'C:\\.MMA\\'
    ufc_direct = 'C:\\.MMA\\UFC\\'
    info_updated = 1
    if b_updated == 2:
        b_direct = 'C:\\.MMA\\Bellator\\'
        b_poster = 'C:\\.MMAmeta\\b_posters\\'
        b_updated = 1
else:
    print('Unknown error in user info. Please take a closer look at your input.')
