#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import http.client, urllib.request, urllib.parse, urllib.error, base64, user_info

base64string = base64.encodestring(('%s:%s' % (user_info.plex_username, user_info.plex_password)).encode()).decode().replace('\n', '')
txdata = ""

headers={'Authorization': "Basic %s" % base64string,
                'X-Plex-Client-Identifier': "MMA script",
                'X-Plex-Product': "MMA script 356546545",
                'X-Plex-Version': "0.001"}

conn = http.client.HTTPSConnection("plex.tv")
conn.request("POST","/users/sign_in.json",txdata,headers)
response = conn.getresponse()
data = response.read()
data_str = str(data)
token_str_plus = data_str.split('_token":"')[1]
token_str =  token_str_plus.split('"')[0]
token = token_str
conn.close()

section_info_xml = urllib.request.urlopen('http://'+user_info.plex_ip+':32400/library/sections/?X-Plex-Token='+token_str).read().decode('utf-8')
section_info_plus2 = section_info_xml.split(user_info.mma_lib)[0]
section_info_plus = section_info_plus2.rsplit('key="',1)[1]
section_str = section_info_plus.split('"')[0]
section = section_str
