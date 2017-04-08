#!/usr/bin/env python
import info_check
import user_info
import urllib.request
import fileinput
import sys
import os
import time
import re
import random
from datetime import datetime
from shutil import copyfile
import logging

if os.path.isfile(info_check.mma_direct+"log.txt"):
    logging.basicConfig(filename=info_check.mma_direct+"log.txt",level=logging.DEBUG,format='[%(asctime)s] %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
    logger = logging.getLogger(__name__)
buf = "\n                      " # buffer space for mult-line log entries
dic = {'Invicta FC':'inv','Bellator':'bel','UFC':'ufc','WSOF':'wsof','Titan FC':'ttn','Legacy Fighting Alliance':'lfa','ONE Championship':'one','Glory':'glr'}
i_dic = {v: k for k, v in dic.items()}
today_date_object = datetime.now()
today_str = today_date_object.strftime('%Y-%m-%d')
class Event:
    def __init__(self,promo):
        self.promo = promo

    def future(self,birth):
        time.sleep(random.randint(10,20))
        logger.info("Opening and reading wikipedia page containing "+i_dic[self.promo]+" events.")
        if self.promo == 'ufc':wiki = urllib.request.urlopen('https://en.wikipedia.org/wiki/List_of_UFC_events').read().decode('utf-8')
        elif self.promo == 'inv':wiki = urllib.request.urlopen('https://en.wikipedia.org/wiki/Invicta_Fighting_Championships').read().decode('utf-8')
        elif self.promo == 'bel':wiki = urllib.request.urlopen('https://en.wikipedia.org/wiki/List_of_Bellator_events').read().decode('utf-8')
        elif self.promo == 'wsof':wiki = urllib.request.urlopen('https://en.wikipedia.org/wiki/List_of_WSOF_events').read().decode('utf-8')
        elif self.promo == 'ttn':wiki = urllib.request.urlopen('https://en.wikipedia.org/wiki/Titan_FC_events').read().decode('utf-8')
        elif self.promo == 'lfa':wiki = urllib.request.urlopen('https://en.wikipedia.org/wiki/Legacy_Fighting_Alliance').read().decode('utf-8')
        elif self.promo == 'one':wiki = urllib.request.urlopen('https://en.wikipedia.org/wiki/List_of_ONE_Championship_events').read().decode('utf-8')
        elif self.promo == 'glr':wiki = urllib.request.urlopen('https://en.wikipedia.org/wiki/Glory_(kickboxing)').read().decode('utf-8')

        scheduled_events_plus_bottom_of_page = wiki.split("<th scope=\"col\">Location</th>")[1] # this statement takes the string that is the whole wikipedia page html and splits it after the position of "location" in the "scheduled events" table
        scheduled_events_table_html = scheduled_events_plus_bottom_of_page.split('</table>')[0]
        pattern = "\d\d\d\d-\d\d-\d\d"
        date_search = re.compile(pattern)
        num_events_today = len(re.findall(today_str,scheduled_events_table_html))
        days_to_next_event = 60
        num_dates_in_table = len(re.findall(pattern,scheduled_events_table_html))
        date_of_future_event = '2050-01-01'
        for match in date_search.finditer(scheduled_events_table_html): # this loop searches for dates in the scheduled events table from the top down
            found_date = match.group()
            scheduled_date_object = datetime.strptime(found_date,'%Y-%m-%d')
            days_to_future_event = (scheduled_date_object - today_date_object).days
            if -1 < days_to_future_event < days_to_next_event:
                days_to_next_event = days_to_future_event
                date_of_future_event = found_date # this is the date for the next scheduled event taking place after today
        if date_of_future_event != '2050-01-01': # If there are future events in the table after today's
            logger.info("Attempmting to update event_dates.txt with future "+i_dic[self.promo]+" event"+buf+"Event expected to take place on "+date_of_future_event+".")
            self.date_updater(date_of_future_event,birth)
            if num_events_today > 0:
                logger.info("Attempting the scrape metadata for "+i_dic[self.promo]+"event taking place today.")
                self.basic_info(date_of_future_event, scheduled_events_table_html)
            elif birth == 'verified':
                logger.info("The "+i_dic[self.promo]+" event that was scheduled to take place today is no longer found in the \"scheduled events\" section on Wikipedia."+buf+"It may have been cancelled or already moved to \'past events\'.")
        else:
            logger.info("There were no future "+i_dic[self.promo]+" events listed under \"scheduled events\" on Wikpedia."+buf+"Attempting to update event_dates.txt to "+date_of_future_event+buf+"This is done so the program can periodically check for updates to the page.")
            self.date_updater(date_of_future_event,birth)
            if num_dates_in_table > 0:
                logger.info("Attempting the scrape metadata for "+i_dic[self.promo]+"event taking place today.")
                self.basic_info(date_of_future_event, scheduled_events_table_html)
            elif birth == 'verified':
                logger.info("The "+i_dic[self.promo]+" event that was scheduled to take place today is no longer found in the \"scheduled events\" section on Wikipedia."+buf+"It may have been cancelled or already moved to \'past events\'.")

    def date_updater(self,date_of_future_event,birth):
        if birth == 'setup':
            edit = open(info_check.mma_direct+'event_dates.txt','a')
            edit.write('\n'+date_of_future_event+'.'+i_dic[self.promo])
            edit.close()
        else:
            f = open(info_check.mma_direct+'event_dates.txt','r')
            filedata = f.read()
            f.close()
            newdata = re.sub(r'.*%s' % i_dic[self.promo],date_of_future_event+'.%s' % i_dic[self.promo],filedata)
            f = open(info_check.mma_direct+'event_dates.txt','w')
            f.write(newdata)
            f.close()

    def basic_info(self, date_of_future_event, scheduled_events_table_html):
        if user_info.MMA == 1: destination = user_info.mma_destination
        else: destination = eval("user_info."+self.promo+"_destination")
        if self.promo == 'glr' :
            cols = 6
            row_num = 4
        elif self.promo == "bel" :
            cols = 5
            row_num = 4
        else:
            cols = 4
            row_num = 3
        if date_of_future_event != '2050-01-01': today_events_plus = re.split(date_of_future_event,scheduled_events_table_html)[1]
        else: today_events_plus = scheduled_events_table_html
        if self.promo =="ufc": number_of_events_today = len(re.findall("</tr>\n<tr>",today_events_plus))
        else: number_of_events_today = 1
        logger.info("According to the wikipedia page, there is "+str(number_of_events_today)+" "+i_dic[self.promo]+" event taking place today."+buf+"Extracting information about event title, date, venue and location.")
        for g in range(1,number_of_events_today+1):
            if date_of_future_event != '2050-01-01':
                today_events_html = re.split('</tr>\n<tr>',today_events_plus)
                event_html = today_events_html[g]
            else:
                event_html = today_events_plus
            event_html_row = re.split('</td>', event_html, cols-1) # splits event into 4 - 6 columns ((event number), title, date, venue, location,(attendance))
            title_html = event_html_row[row_num-3]
            ind_wiki = 1
            try:
                title_html2 = re.split('\">', title_html)[1]
                title = re.split('</a>', title_html2)[0]
            except IndexError as e:
                logger.info("There is no individual wiki page for this event. Fight card information cannot be found.")
                title = title_html[5:]
                ind_wiki = 0
            date_html = event_html_row[row_num-2]
            date_html2 = re.split('>00000000', date_html)[1]
            date = re.split('-0000<',date_html2)[0]
            venue_html = event_html_row[row_num-1]
            if len(re.findall('href',venue_html)) > 0: # this prevents the script from crashing if the venue is not hyperlinked to a wiki page
                venue_html2 = re.split('\">', venue_html)[1]
                venue = re.split('</a>', venue_html2)[0]
            else:
                venue_html2 = re.split('<td>', venue_html)[1]
                venue = re.split('</td>', venue_html2)[0]
            location_html = event_html_row[row_num]
            location_html2 = re.split('title',location_html)
            city_country = re.split('<(?!/a)', location_html2[1])[0]
            country_plus = re.split('</a>,',city_country)[1]
            country = country_plus[1:]
            city_plus = re.split('</a>,',city_country)[0]
            city = re.split('>',city_plus)[1]
            location = city + ", " + country

            logger.info("Information about event title, date, venue and location successfully extracted."+buf+"Attempting to create the directory named"+buf+os.path.join(destination+title,''))

            try: # creates a directory for the .nfo file to be saved to
                os.makedirs(os.path.join(destination+title,''))
            except OSError:
                if not os.path.isdir(os.path.join(destination+title,'')):
                    raise
            logger.info("Created the directory named"+buf+os.path.join(destination+title,'')+buf+"Attempting to create .nfo file.")

            nfo = open(os.path.join(destination+title,'')+title+".nfo",'w')
            nfo.write("<movie>\n<title>Soon - "+title+"</title>\n<genre>Sports</genre>\n<releasedate>"+date+"</releasedate>\n<tagline>"+venue+" - "+location+"</tagline>\n<plot>")
            nfo.close()
            page_title = title
            if self.promo == 'inv': searchable_title=title[0:13].lower(); page_title = title
            elif self.promo == 'bel': searchable_title=title.lower(); page_title = title
            elif self.promo == 'one': searchable_title=title[0:19].lower(); page_title=re.sub(' \d\d','',title)
            elif self.promo == 'glr': searchable_title=title[0:8].lower(); page_title = title
            elif self.promo == 'ttn': searchable_title=title[0:11].lower(); page_title = title[0:11]
            elif self.promo == 'lfa': num = re.search(r'\d+', title).group(); searchable_title= 'lfa '+str(num); page_title = title
            elif self.promo == 'wsof':
                page_title = re.sub('WSOF','World Series of Fighting',title)
                if len(re.findall('Global Championship',title))>0:
                    searchable_title=title[:24].lower()
                else:
                    searchable_title=title[:7].lower()
            if ind_wiki == 1:
                logger.info("Info file "+buf+os.path.join(destination+title,'')+title+".nfo"+buf+"was created."+buf+"Attempting to open Wikipedia page containing thefor fight card information for this event.")
                try:
                    mma_event_page_end_of_url = re.split('\"', title_html)[1]
                    mma_event_page_url = "https://en.wikipedia.org" + mma_event_page_end_of_url # entire url for individual event page or page containing individual event on wikipedia page
                    page_with_mma_event = urllib.request.urlopen(mma_event_page_url).read().decode('utf-8')
                    page_split_at_correct_event = re.compile("b>"+page_title).split(page_with_mma_event)[1]
                    if self.promo == "ufc":
                        is_alt_title = re.findall('known as',page_split_at_correct_event) # determine if there is an alternative title
                        if len(is_alt_title) > 0:
                            logger.info("There is an \"also known as\" title on the Wikipedia page. The alternative title will be used for file matching.")
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
                            searchable_title = title[0:7].lower()
                    kbox = 0
                    logger.info("Looking under \"Fight card\" header for fight cards.")
                    table_of_all_cards_plus = re.compile(">[F|f]ight [C|c]ard<").split(page_split_at_correct_event,1)[1]
                    table_of_all_cards = re.compile("<\/table>").split(table_of_all_cards_plus,1)[0]
                    number_of_cards = len(re.findall("<tr>\n<th.*?\n<\/tr>",table_of_all_cards))
                    table_of_fights_in_card_plus = re.compile("<tr>\n<th.*?\n<\/tr>").split(table_of_all_cards)
                    card_titles_html = re.compile("<th colspan=\"8\"").split(table_of_all_cards,number_of_cards)
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
                            if self.promo == 'bel' and len(re.findall('ickboxing',card_title)) > 0: kbox = 1

                        nfo = open(os.path.join(destination+title,'')+title+".nfo",'a')
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
                                nfo = open(os.path.join(destination+title,'')+title+".nfo",'a')
                                nfo.write(weight_class+" ")
                            else:
                                weight_class_chunk = re.compile("<td").split(weight_class_html)[1]
                                weight_class = re.compile(">").split(weight_class_chunk)[1]
                                nfo = open(os.path.join(destination+title,'')+title+".nfo",'a')
                                nfo.write(weight_class+" ")
                            if len(re.findall("<\/a>",fighter1_html)) > 0:
                                fighter1_chunk = re.compile("title=").split(fighter1_html)[1]
                                fighter1_chunk2 = re.compile(">").split(fighter1_chunk)[1]
                                fighter1 = fighter1_chunk2[:-3]
                                nfo = open(os.path.join(destination+title,'')+title+".nfo",'a')
                                nfo.write(fighter1+" vs. ")
                            else:
                                fighter1 = re.compile(">").split(fighter1_html)[1]
                                nfo = open(os.path.join(destination+title,'')+title+".nfo",'a')
                                nfo.write(fighter1+" vs. ")
                            if len(re.findall("<\/a>",fighter2_html)) > 0:
                                fighter2_chunk = re.compile("title=").split(fighter2_html)[1]
                                fighter2_chunk2 = re.compile(">").split(fighter2_chunk)[1]
                                fighter2 = fighter2_chunk2[:-3]
                                nfo = open(os.path.join(destination+title,'')+title+".nfo",'a')
                                nfo.write(fighter2+"\n")
                            else:
                                fighter2 = re.compile(">").split(fighter2_html)[1]
                                nfo = open(os.path.join(destination+title,'')+title+".nfo",'a')
                                nfo.write(fighter2+"\n")
                            time.sleep(0.3)
                    nfo = open(os.path.join(destination+title,'')+title+".nfo",'a')
                    nfo.write("</plot>\n</movie>")
                    nfo.close()
                    logger.info("Meta-data file"+buf+os.path.join(destination+title,'')+title+".nfo"+buf+"has finished being written.")
                    if number_of_cards > 1:
                        feat_dir = os.path.join(os.path.join(os.path.join(destination+title,''),'Featurette'),'')
                        os.makedirs(feat_dir)
                        logger.info("Featurette directory"+buf+feat_dir+buf+"was created.")
                        if self.promo == 'glr':
                            prelim_holder = open(feat_dir+'Soon - Superfight Series.avi','w')
                            prelim_holder.write(searchable_title+" superfight")
                            prelim_holder.close()
                            logger.info("Preliminary card video placeholder file"+buf+feat_dir+"Soon - Superfight Series.avi"+buf+"was created.")
                        elif self.promo == 'bel' and kbox == 1:
                            prelim_holder = open(feat_dir+'Soon - Bellator Kickboxing.avi','w')
                            prelim_holder.write(searchable_title+" kickboxing")
                            prelim_holder.close()
                            logger.info("Preliminary card video placeholder file"+buf+feat_dir+"Soon - Bellator Kickboxing.avi"+buf+"was created.")
                        else:
                            prelim_holder = open(feat_dir+'Soon - Prelims.avi','w')
                            prelim_holder.write(searchable_title+" prelim")
                            prelim_holder.close()
                            logger.info("Preliminary card video placeholder file"+buf+feat_dir+"Soon - Prelims.avi"+buf+"was created.")
                    if number_of_cards > 2:
                        early_holder = open(feat_dir+'Soon - Early Prelims.avi','w')
                        early_holder.write(searchable_title+" early prelim")
                        early_holder.close()
                        logger.info("Early preliminary card video placeholder file"+buf+feat_dir+"Soon - Early Prelims.avi"+buf+"was created.")
                    self.poster_fetch(destination, title, searchable_title,page_with_mma_event)
                except (IndexError, ValueError, urllib.error.HTTPError) as e:
                    logger.info("ERROR: Someting unexpected happened while scraping metdata from wikipedia page for "+title+"."+buf+"Info file can not be completed.")
                    logger.exception(e)
            if ind_wiki == 0:
                logger.info("Info file "+buf+os.path.join(destination+title,'')+title+".nfo"+buf+"was created."+buf+"There is no available fight card data.")
                nfo = open(os.path.join(destination+title,'')+title+".nfo",'a')
                nfo.write("MMA Event</plot>\n</movie>")
                nfo.close()
                if self.promo != 'lfa': self.poster_fetch(destination, title,searchable_title,'error')
                else: self.poster_fetch(destination,title,searchable_title,'lfa')

            main_holder = open(os.path.join(destination+title,'')+searchable_title+".avi",'w')
            main_holder.write(searchable_title)
            main_holder.close()
            logger.info("Main card video placeholder file"+buf+os.path.join(os.path.join(destination+title,''),searchable_title)+".avi"+buf+"was created.")
            time.sleep(5)
        f = open(info_check.mma_direct+'event_dates.txt','r')
        filedata = f.read()
        f.close()
        newdata = re.sub(r'.*%s' % i_dic[self.promo],date_of_future_event+'.%s' % i_dic[self.promo],filedata)
        f = open(info_check.mma_direct+'event_dates.txt','w')
        f.write(newdata)
        f.close()
        for line in fileinput.input(info_check.mma_direct+'stats.txt'):
            temp = sys.stdout
            sys.stdout = open(info_check.mma_direct+'stats2.txt', 'a')
            if (i_dic[self.promo] in line and 'scraped' in line) or ('total'in line and 'scraped' in line):
                tmp = re.findall('[0-9]+',line)
                num = str(int(str(tmp[0]))+1)
                new = re.sub(r'[0-9]+',num, line)
                print(new,end='')
            else:
                print(line,end='')
            sys.stdout.close()
            sys.stdout = temp
        os.remove(info_check.mma_direct+'stats.txt')
        os.rename(info_check.mma_direct+'stats2.txt',info_check.mma_direct+'stats.txt')

    def poster_fetch(self,destination, title, searchable_title,page_with_mma_event):
        if page_with_mma_event != 'error':
            if self.promo == "ufc":
                try:
                    poster_url_part_plus = re.split('/wiki/File:', page_with_mma_event)[1]
                    poster_url_end = re.split('\"', poster_url_part_plus)[0]
                    poster_page = urllib.request.urlopen('https://en.wikipedia.org/wiki/File:'+poster_url_end).read().decode('utf-8')
                    poster_image_url_plus = re.split('//upload.wikimedia.org/wikipedia/',poster_page)[1]
                    poster_image_url = re.split('\"',poster_image_url_plus)[0]
                    with urllib.request.urlopen('https://upload.wikimedia.org/wikipedia/'+poster_image_url) as response, open(os.path.join(os.path.join(destination+title,''),searchable_title+'.jpg'), 'wb') as out_file:
                        data = response.read() # a `bytes` object
                        out_file.write(data)
                    logger.info("Poster file "+buf+os.path.join(os.path.join(destination+title,''),searchable_title+'.jpg')+buf+"was created.")
                except (IndexError, ValueError, urllib.error.HTTPError):
                    logger.info("ERROR: URL for webpage containing "+title+" event poster is not where expected."+buf+"Attempting to use locally stored generic poster.")
                    self.local_poster(destination, title, searchable_title)
            elif self.promo == 'inv':
                event_num = searchable_title[-2:]
                url_of_page_with_poster = os.path.join('http://www.invictafc.com/portfolio-item/invicta-fc-'+event_num,'')
                try:
                    poster_page = urllib.request.urlopen(url_of_page_with_poster).read().decode('utf-8')
                    poster_image_url_plus2 = re.split('class="flex_column av_one_third',poster_page)[1]
                    poster_image_url_plus = re.split('(?<=.jpg)\'',poster_image_url_plus2,1)[0]
                    poster_image_url = re.split('href=\'',poster_image_url_plus)[1]
                    with urllib.request.urlopen(poster_image_url) as response, open(os.path.join(os.path.join(destination+title,''),searchable_title+'.jpg'), 'wb') as out_file:
                        data = response.read() # a `bytes` object
                        out_file.write(data)
                    logger.info("Poster file "+buf+os.path.join(os.path.join(destination+title,''),searchable_title+'.jpg')+buf+"was created.")
                except (IndexError,ValueError, urllib.error.HTTPError):
                    logger.info("ERROR: URL for webpage containing "+title+" event poster is not where expected."+buf+"Attempting to use locally stored generic poster.")
                    self.local_poster(destination, title, searchable_title)
            elif self.promo == 'lfa':
                l_title = title.lower()
                event_number = re.findall('[0-9]+',searchable_title)[0]
                url_part1 = re.sub(' ','-',re.sub('\.','',re.sub(':','',l_title)))
                url_part2 = re.sub('legacy-fighting-alliance','lfa',url_part1)
                try:
                    poster_page = urllib.request.urlopen('http://lfafighting.com/event/'+url_part1).read().decode('utf-8')
                except urllib.error.HTTPError:
                    lfa_fail = 1
                    logger.info("http://lfafighting.com/event/"+url_part1+" doesn't exist. Trying second url")
                else:
                    lfa_fail = 0
                if lfa_fail == 1:
                    try:
                        poster_page = urllib.request.urlopen('http://lfafighting.com/event/'+url_part2).read().decode('utf-8')
                    except urllib.error.HTTPError:
                        lfa_fail = 2
                        logger.info("http://lfafighting.com/event/"+url_part2+" doesn't exist.")
                        logger.info("Attempting to use locally stored generic poster.")
                        self.local_poster(destination, title, searchable_title)
                if lfa_fail < 2:
                    try:
                        images = re.findall('http.*?fighting.*?LFA-'+event_number+'.*?jpg',poster_page)
                        poster_image_url = images[len(images)-1]
                        with urllib.request.urlopen(poster_image_url) as response, open(os.path.join(os.path.join(destination+title,''),searchable_title+'.jpg'), 'wb') as out_file:
                            data = response.read() # a `bytes` object
                            out_file.write(data)
                        logger.info("Poster file was created.")
                    except (IndexError,ValueError, urllib.error.HTTPError):
                        logger.info("ERROR: Poster image could not be found on the webpage for "+title+". Attempting to use locally stored generic poster.")
                        self.local_poster(destination, title, searchable_title)

            else: self.local_poster(destination, title, searchable_title)
        else: self.local_poster(destination, title, searchable_title)

    def local_poster(self,destination, title, searchable_title):
        poster_dir = os.path.join(os.path.join(info_check.meta,"poster"),'')
        copyfile(poster_dir+self.promo+'.jpg', os.path.join(os.path.join(destination+title,''),searchable_title+'.jpg'))
        logger.info("A generic poster file"+buf+os.path.join(os.path.join(destination+title,''),searchable_title+'.jpg')+buf+"was created.")
