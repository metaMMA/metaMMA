#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import urllib.request
import re
import os
import errno
import random
import time
import fnmatch
import glob
from datetime import datetime
import user_info
import info_check
ts = "["+time.strftime("%Y-%m-%d %H:%M:%S")+"] " # timestamp string used at beginning of log file
addts = "\n"+ts # timestamp string used after beginning of log file
buf = "\n                      " # buffer space for mult-line log entries

#############################################################################################################################################
# Check to make sure the user has updated their information in user_info.py
if info_check.info_updated == 0:
    exit()
#############################################################################################################################################

# Block 0 checks to see if this is the first time running the script and creates the necessary files and directories if it is the first time
# 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
if not os.path.exists(info_check.ufc_direct):
    os.makedirs(info_check.ufc_direct) # create the directory for script-related files
    if not os.path.exists(os.path.dirname(info_check.ufc_direct+"stop-log.txt")):
        try:
            os.makedirs(os.path.dirname(info_check.ufc_direct+"stop-log.txt")) # create the stop-log file
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(info_check.ufc_direct+"stop-log.txt", "w") as log:
        log.write(ts+"This file logs whenever UFC.py or UFCmover.py was attempting to run while it was not finished running.")
        log.close()
    time.sleep(random.randint(5,125)) # prevent the UFC Events list webpage from being accessed at the same time, if multiple people install on the same day
    entire_UFC_wiki_page_html = urllib.request.urlopen('https://en.wikipedia.org/wiki/List_of_UFC_events').read().decode('utf-8') # open the entire wikipedia page for UFC events and store the html in a string
    scheduled_events_plus_bottom_of_page = entire_UFC_wiki_page_html.split("<th scope=\"col\">Location</th>\n</tr>")[1] # take the string that is the whole wikipedia page html and store the html text that is after the position of "location" in the "scheduled events" table
    scheduled_events_html = scheduled_events_plus_bottom_of_page.split('</table>')[0] # take the previous string and cutoff everthing below the "scheduled events" table
    next_events = re.split(r'>00000000',scheduled_events_html) # split the html text in the "scheduled events" at each date
    next_event_html = next_events[len(next_events)-1] # html text starting at the closest date to today in the "scheduled events" table
    next_event_date = next_event_html[0:10] # the very last event (date) in the "scheduled events" table on Wikipedia. This should be the next upcoming event
    if not os.path.exists(os.path.dirname(info_check.ufc_direct+next_event_date+".next")):
        try:
            os.makedirs(os.path.dirname(info_check.ufc_direct+next_event_date+".next")) #create a ".next" file that hold the date of the next scheduled UFC event
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(info_check.ufc_direct+next_event_date+".next", "w") as next1:
        next1.write(ts+"The next time the script will look for events is on "+next_event_date+".")
        next1.close()
    if not os.path.exists(user_info.tmp_dir):
        try:
            os.makedirs(user_info.tmp_dir) # create temporary directory to move video and video-realted files to. This should be a directory that pleX DOES NOT index
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    if not os.path.exists(os.path.dirname(info_check.ufc_direct+"log.txt")):
        try:
            os.makedirs(os.path.dirname(info_check.ufc_direct+"log.txt")) # create a log file to log all creations, changed and moves
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(info_check.ufc_direct+"log.txt", "w") as log2:
        log2.write(ts+"First time running this script. Created .UFC directory, temporary directory, date_of_next-event.next, stop-log.txt and log.txt.")
        log2.write(addts+"Because this is the first time, Wikipedia will not be checked until the next run. The script will stop running now.")
        log2.close()
    exit()
# 0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
def endit():
    os.remove(info_check.ufc_direct+'UFCrunning.holder')
    exit()
def logger(loginfo):
    with open(info_check.ufc_direct+"log.txt", "a") as log:
        log.write(addts+loginfo)
        log.close()
# Block 1 checks to see if this script is attempting to execute while it has not finished running
# 1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111
UFCrunning_holder_list = glob.glob(info_check.ufc_direct+'UFCrunning.holder') # check to see if this the "UFCrunning.holder" file exists (if it does, that means this UFCmover.py script is currently running)
if len(UFCrunning_holder_list) == 1:
    log = open(info_check.ufc_direct+'stop-log.txt','a')
    log.write(addts+"An attempt to run UFC.py was made. However, UFC.py is currently running because UFCrunning.holder is present. The script will stop running now.")
    log.close()
    exit()
else:
    if not os.path.exists(os.path.dirname(info_check.ufc_direct+'UFCrunning.holder')):
        try:
            os.makedirs(os.path.dirname(info_check.ufc_direct+'UFCrunning.holder'))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    with open(info_check.ufc_direct+'UFCrunning.holder', "w") as running: # if "UFCrunning.holder" doesn't exist (the script is NOT currently running), then create "UFCrunning.holder"
        running.write(ts+"UFC.py started running.")
        running.close()
    logger("UFC.py started running.")
# 1111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111111

# Block 2 checks to make sure that a file has been saved with the date of the next upcoming UFC event
# 2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222
next_event_holder_list = glob.glob(info_check.ufc_direct+'[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9].next') # check to see if this the "date".next file exists
if len(next_event_holder_list) < 1:
    logger("ERROR The next event \"holder file\" is missing/deleted."+buf+"You can manually create it by opening a text file (you can leave it blank) and saving it as the date of the next upcoming UFC event."+buf+"For example, if today is 2016-11-22, a text file should be saved that is named \"2016-11-29.next\" because it would be the date of the next UFC event."+buf+"The file should be saved/moved to"+info_check.ufc_direct+" ."+buf+"The script will stop running now.")
    endit()
else:
    next_wanted_event_holder_filename = next_event_holder_list[0]
    next_wanted_event_date = next_wanted_event_holder_filename[-15:-5] # this is the date that was saved as the next UFC event date when the files were created for the previous event
# 2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222

# Block 3 checks to see if today is the day of a UFC event, and exits the program if it is not
# 3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333
next_wanted_event_date_object = datetime.strptime(next_wanted_event_date,'%Y-%m-%d')
today_date_object = datetime.now()
dif = (next_wanted_event_date_object - today_date_object).days # number of days until the UFC event that is saved in the .UFC directory as the next upcoming event date
if dif > -1:
    logger("The next scheduled event is still "+str(dif+1)+" days away. The script will stop running now.")
    endit()
# 3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333

time.sleep(random.randint(5,245)) # prevent the UFC Events list webpage from being accessed at the same time by multiple users on the day of the UFC event
entire_UFC_wiki_page_html = urllib.request.urlopen('https://en.wikipedia.org/wiki/List_of_UFC_events').read().decode('utf-8') # this statement stores the entire wikipedia page for UFC events and stores the html in a string
scheduled_events_plus_bottom_of_page = entire_UFC_wiki_page_html.split("<th scope=\"col\">Location</th>\n</tr>")[1] # this statement takes the string that is the whole wikipedia page html and splits it after the position of "location" in the "scheduled events" table
scheduled_events_html = scheduled_events_plus_bottom_of_page.split('</table>')[0]
next_events = re.split(r'>00000000',scheduled_events_html)
next_event_html = next_events[len(next_events)-1]
next_event_date = next_event_html[0:10] # the very last event in the "scheduled events" table on Wikipedia. This should be the next upcoming event
next_event_date_object = datetime.strptime(next_event_date,'%Y-%m-%d')
days_to_event = (next_event_date_object - today_date_object).days

# Block 4 runs only if the date file saved in the .UFC directory as the next upcoming event matched today's date.  It checks to make sure that that date we expected a UFC event to take place is still the most upcoming event on the Wikipedia page. If it is not, then the event most likely was cancelled. If it is, it finds the next event date after today's
# 4444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444
if (days_to_event > -1):
    logger("ERROR The event that was supposed to take place today is no longer on Wikipedia's \"scheduled events\" table. The next event holder has been updated. The script will stop running now.")
    os.remove(info_check.ufc_direct+next_wanted_event_date+".next")
    next_event_holder = open(info_check.ufc_direct+next_event_date+".next",'w')
    next_event_holder.write(addts+"The next day the script will look for events is "+next_event_date+".")
    next_event_holder.close()
    endit()
elif days_to_event < -1:
    logger("ERROR Yesterday's event hasn't been moved to the \"Past Events\" table, yet. Once the event is moved, then the information from today's event will be downloaded. The script will stop running now.")
    endit()
else: # find the next event date after today's events
    days_to_next_event = 60
    pattern = "\d\d\d\d-\d\d-\d\d"
    date_search = re.compile(pattern)
    for match in date_search.finditer(scheduled_events_html):
        found_date = match.group()
        scheduled_date_object = datetime.strptime(found_date,'%Y-%m-%d')
        days_to_event2 = (scheduled_date_object - today_date_object).days
        if -1 < days_to_event2 < days_to_next_event:
            days_to_next_event = days_to_event2
            date_of_next_event = found_date
# 4444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444

# Block 5 creates the directories, nfo files, and posters for today's events
# 5555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555
today_events_plus = re.split(date_of_next_event,scheduled_events_html)[1]
number_of_events_today = len(re.findall("</tr>\n<tr>",today_events_plus))
for g in range(1,number_of_events_today+1):
    today_events_html = re.split('</tr>\n<tr>',today_events_plus)
    event = today_events_html[g]
    event_html_row = re.split('</td>', event, 3) # splits event the 4 columns (title, date, venue, location)
    title_html = event_html_row[0]
    title_html2 = re.split('\">', title_html)[1]
    title = re.split('</a>', title_html2)[0]
    date_html = event_html_row[1]
    date_html2 = re.split('>00000000', date_html)[1]
    date = re.split('-0000<',date_html2)[0]
    venue_html = event_html_row[2]
    venue_html2 = re.split('\">', venue_html)[1]
    venue = re.split('</a>', venue_html2)[0]
    location_html = event_html_row[3]
    if len(re.findall('title',location_html)) == 2: # these two blocks differentiate between a location that is a city + state/province + country and a location that is just a city + country
        location_html2 = re.split('title',location_html)
        state_country = re.split('<(?!/a)', location_html2[2])[0]
        state_plus = re.split('</a>', state_country)[0]
        state = re.split('>', state_plus)[1]
        country_plus = re.split('</a>', state_country)[1]
        country = country_plus[2:]
        city_plus = re.split('</a>',location_html2[1])[0]
        city = re.split('>', city_plus)[1]
        location = city + ', ' + state + ', ' + country
    else:
        location_html2 = re.split('title',location_html)
        city_country = re.split('<(?!/a)', location_html2[1])[0]
        country_plus = re.split('</a>,',city_country)[1]
        country = country_plus[1:]
        city_plus = re.split('</a>,',city_country)[0]
        city = re.split('>',city_plus)[1]
        location = city + ", " + country
    if os.path.exists(user_info.ufc_destination+title+'/'): # if this script has already created the directories and files, then exit the script
        logger("ERROR - Attempted to create a directory that already exists. The script will stop running now.")
        endit()
    try: # creates a directory for the .nfo file to be saved to
        os.makedirs(user_info.ufc_destination+title+'/')
    except OSError:
        if not os.path.isdir(user_info.ufc_destination+title+'/'):
            raise
    nfo = open(user_info.ufc_destination+title+'/'+title+".nfo",'w')
    nfo.write("<movie>\n<title>Soon - "+title+"</title>\n<genre>Sports</genre>\n<releasedate>"+date+"</releasedate>\n<tagline>"+venue+" - "+location+"</tagline>\n<plot>")
    nfo.close()
    logger("NFO file "+user_info.ufc_destination+title+'/'+title+".nfo was created. Checking Wikipedia for info to write to nfo file.")
    wiki_url_part = re.split('\"', title_html)[1]
    individual_wiki_page_url = "https://en.wikipedia.org" + wiki_url_part # entire url for individual event wikipedia page
    individual_wiki_page = urllib.request.urlopen(individual_wiki_page_url).read().decode('utf-8') # create new string of individual wikpedia page
    page_split_at_correct_event = re.compile("b>"+title).split(individual_wiki_page)[1] # user event_title with b> before it
    is_alt_title = re.findall('known as',page_split_at_correct_event) # determine if there is an alternative title
    if len(is_alt_title) > 0:
        alternative_title3 = re.compile('.*?known\sas.*?<i><b>').split(page_split_at_correct_event)[1]
        alternative_title2 = re.compile('<').split(alternative_title3)[0]
        alternative_title = alternative_title2.lower()
        approved_words = ['ufc', 'fight', 'night','fox', 'versus', 'fuel', 'fx', 'ultimate', 'fighter', 'finale']
        alternative_title_list = alternative_title.split()
        fight_number_list = re.findall('[0-9][0-9]+', alternative_title)
        if len(fight_number_list) == 1:
            fight_number = fight_number_list[0]
        searchable_title_words_list  = [word for word in alternative_title_list if word.lower() in approved_words]
        searchable_title_words = ' '.join(searchable_title_words_list)
        searchable_title = searchable_title_words+" "+''.join(fight_number)
    if len(is_alt_title) < 1:
        searchable_title = title[0:7]
    table_of_all_fights_plus = re.compile("id=\"Official_").split(page_split_at_correct_event,1)[1]
    table_of_all_fights = re.compile("<\/table>").split(table_of_all_fights_plus,1)[0]
    number_of_cards = len(re.findall("<tr>\n<th.*?\n<\/tr>",table_of_all_fights))
    table_of_fights_in_card_plus = re.compile("<tr>\n<th.*?\n<\/tr>").split(table_of_all_fights)
    card_titles_html = re.compile("<th colspan=\"8\"").split(table_of_all_fights,number_of_cards)
    for x in range(1,number_of_cards+1):
        if len(re.findall("Notes",table_of_fights_in_card_plus[x])) > 0: # if the table has headers above each card (instead of just at the top) strip them out
            table_of_fights_in_card = re.compile("(?<=Notes<\/th>\n)<\/tr>\n").split(table_of_fights_in_card_plus[x])[1]
        else:
            table_of_fights_in_card = table_of_fights_in_card_plus[x]
        number_of_fights_on_card = len(re.findall("<\/tr>",table_of_fights_in_card))
        each_fight_on_card = re.compile("<\/tr>").split(table_of_fights_in_card,number_of_fights_on_card)
        card_title_chunk = re.compile("<\/th>").split(card_titles_html[x])[0]
        if len(re.findall("<a",card_title_chunk)) > 0:
            card_title_chunk1 = re.compile("<b>").split(card_title_chunk)[1]
            if len(re.findall("\(",card_title_chunk1)) > 0:
                card_title_chunk_parts = re.compile("\(").split(card_title_chunk1)[0]
                card_title_part1 = card_title_chunk_parts[:-1]
                card_title_part2_chunk = re.compile("\(").split(card_title_chunk1)[1]
                card_title_part2_chunk2 = re.compile(">").split(card_title_part2_chunk)[1]
                card_title_part2 = card_title_part2_chunk2[:-3]
                card_title = card_title_part1 + " " + card_title_part2
            else:
                card_title_chunk2 = re.compile("title").split(card_title_chunk1)[1]
                card_title_chunk3 = re.compile(">").split(card_title_chunk2)[1]
                card_title =card_title_chunk3[:-3]
        else:
            card_title_chunk1 = re.compile("<b>").split(card_title_chunk)[1]
            card_title = card_title_chunk1[:-4]
        nfo = open(user_info.ufc_destination+title+'/'+title+".nfo",'a')
        nfo.write(card_title+"\n")
        for y in range(0,number_of_fights_on_card):
            number_of_col = len(re.findall("<\/td>",each_fight_on_card[y]))
            info_chunk = re.compile("<\/td>").split(each_fight_on_card[y],number_of_col)
            weight_class_html = info_chunk[0]
            rand = random.randint(0,2)
            if rand > 1:
                mystery = 1
            else:
                mystery = -1
            fighter1_html = info_chunk[2+mystery]
            fighter2_html = info_chunk[2-mystery]
            if len(re.findall("<\/a>",weight_class_html)) > 0:
                weight_class_chunk = re.compile("title=").split(weight_class_html)[1]
                weight_class_chunk2 = re.compile(">").split(weight_class_chunk)[1]
                weight_class = weight_class_chunk2[:-3]
                nfo = open(user_info.ufc_destination+title+'/'+title+".nfo",'a')
                nfo.write(weight_class+" ")
            else:
                weight_class_chunk = re.compile("<td").split(weight_class_html)[1]
                weight_class = re.compile(">").split(weight_class_chunk)[1]
                nfo = open(user_info.ufc_destination+title+'/'+title+".nfo",'a')
                nfo.write(weight_class+" ")
            if len(re.findall("<\/a>",fighter1_html)) > 0:
                fighter1_chunk = re.compile("title=").split(fighter1_html)[1]
                fighter1_chunk2 = re.compile(">").split(fighter1_chunk)[1]
                fighter1 = fighter1_chunk2[:-3]
                nfo = open(user_info.ufc_destination+title+'/'+title+".nfo",'a')
                nfo.write(fighter1+" vs. ")
            else:
                fighter1 = re.compile(">").split(fighter1_html)[1]
                nfo = open(user_info.ufc_destination+title+'/'+title+".nfo",'a')
                nfo.write(fighter1+" vs. ")
            if len(re.findall("<\/a>",fighter2_html)) > 0:
                fighter2_chunk = re.compile("title=").split(fighter2_html)[1]
                fighter2_chunk2 = re.compile(">").split(fighter2_chunk)[1]
                fighter2 = fighter2_chunk2[:-3]
                nfo = open(user_info.ufc_destination+title+'/'+title+".nfo",'a')
                nfo.write(fighter2+"\n")
            else:
                fighter2 = re.compile(">").split(fighter2_html)[1]
                nfo = open(user_info.ufc_destination+title+'/'+title+".nfo",'a')
                nfo.write(fighter2+"\n")
            time.sleep(0.3)
    nfo = open(user_info.ufc_destination+title+'/'+title+".nfo",'a')
    nfo.write("</plot>\n</movie>")
    nfo.close()
    logger("NFO file"+buf+user_info.ufc_destination+title+"/"+title+".nfo"+buf+"has finished being written.")
    poster_url_part_plus = re.split('/wiki/File:', individual_wiki_page)[1]
    poster_url_end = re.split('\"', poster_url_part_plus)[0]
    poster_page = urllib.request.urlopen('https://en.wikipedia.org/wiki/File:'+poster_url_end).read().decode('utf-8') # this statement stores the entire wikipedia page for UFC events and stores the html in a string
    poster_image_url_plus = re.split('//upload.wikimedia.org/wikipedia/',poster_page)[1]
    poster_image_url = re.split('\"',poster_image_url_plus)[0]
    with urllib.request.urlopen('https://upload.wikimedia.org/wikipedia/'+poster_image_url) as response, open(user_info.ufc_destination+title+'/'+searchable_title+'.holder.jpg', 'wb') as out_file:
        data = response.read() # a `bytes` object
        out_file.write(data)
    logger("POSTER FILE"+buf+user_info.ufc_destination+title+"/"+searchable_title+".holder.jpg"+buf+"was created.")
    os.makedirs(user_info.ufc_destination+title+'/Featurette')
    logger("FEATURETTE DIRECTORY"+buf+user_info.ufc_destination+title+"/Featurette/"+buf+"was created.")
    main_holder = open(user_info.ufc_destination+title+'/'+searchable_title+".holder.avi",'w')
    main_holder.write(title)
    main_holder.close()
    logger("MAIN CARD VIDEO PLACEHOLDER file"+buf+user_info.ufc_destination+title+"/"+searchable_title+".holder.avi"+buf+"was created.")
    if number_of_cards > 1:
        prelim_holder = open(user_info.ufc_destination+title+'/Featurette/Soon - Prelims.avi','w')
        prelim_holder.write(searchable_title+" prelim")
        prelim_holder.close()
        logger("PRELIMINARY CARD VIDEO PLACEHOLDER file"+buf+user_info.ufc_destination+title+"/Featurette/Soon - Prelims.avi"+buf+"was created.")
    if number_of_cards > 2:
        early_holder = open(user_info.ufc_destination+title+'/Featurette/Soon - Early Prelims.avi','w')
        early_holder.write(searchable_title+" early prelim")
        early_holder.close()
        logger("EARLY PRELIMINARY CARD VIDEO PLACEHOLDER file"+buf+user_info.ufc_destination+title+"/Featurette/Soon - Early Prelims.avi"+buf+"was created.")
    time.sleep(5)

# 5555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555555

# Block 6 updates the "upcoming event".next filename
# 6666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666
os.remove(info_check.ufc_direct+next_wanted_event_date+".next")
new_next_wanted_event = open(info_check.ufc_direct+date_of_next_event+".next",'w')
new_next_wanted_event.write(addts+"The next time the script will look for fight cards is on the date in this filename - "+date_of_next_event)
new_next_wanted_event.close()
logger("The next time the script will look for fight cards on Wikipedia is on "+date_of_next_event+"."+addts+"The script will stop running now.")
endit()
# 6666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666
