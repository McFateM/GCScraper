#!/usr/bin/env python

"""
gc-scraper.py
Python2 script to parse a GPX file and GC.com admin pages transcribe final (FN) coordinates into the GPX.
No GUI, so this thing is Docker-compatible.
"""

import string
import mechanize
import cookielib
import os
import re
import glob
# from time import gmtime, strftime
from random import randint
from time import sleep
from bs4 import BeautifulSoup

import private


def replace_all(text, dict):
  for old, new in dict.iteritems():
    text = text.replace(old, new)
  return text


def get_final_coord(url):
  clean = url.strip()
  https = string.replace(clean, 'http:', 'https:')
  review = string.replace(https, 'seek/cache_details', 'admin/review')

  # u'http://www.geocaching.com/seek/cache_details.aspx?guid=a71f6d54-45d6-4f53-8320-ad7f49ce5cb1'
  # url = 'https://www.geocaching.com/admin/review.aspx?guid=6fa9769c-4206-4ea8-8f9f-053dca533ce9'

  cj = cookielib.CookieJar()
  br = mechanize.Browser()
  br.set_cookiejar(cj)
  dest = "https://www.geocaching.com/account/login?returnURL=" + review
  br.open(dest)
  br.select_form(nr=1)
  br.form['Username'] = private.username
  br.form['Password'] = private.password
  br.submit()

  html = br.response().read()
  soup = BeautifulSoup(html, 'html.parser')
  td_list = soup.find_all("td")

  for td in td_list:
    if re.search('Final Location', td.text):
      FN = td.find_next_sibling("td").text
      return FN

  return False


# ------------------------

print("gc-scraper.py starting...")

for filename in glob.iglob('./*.gpx'):
  if "CORRECTED" not in filename:
    xmlfile = filename
    wpts = dict()
    blocks = []

    if xmlfile.rsplit(".")[-1] != "gpx":
      print("ERROR - Filename must have a .gpx extension!")
      exit(1)
    
    else:
      """ identify all the <wpt> tags. grab the lat, lon, name, description and url"""
      print("Opening {}...".format(xmlfile))

      with open(xmlfile, 'r') as gpxfile:
        data = gpxfile.read()

      print("...{} has been read".format(xmlfile))

      soup = BeautifulSoup(data, 'lxml')
      wpt_list = soup.find_all("wpt")
      nFound = 0
      nMod = 0

      status = ""
      
      for tag in wpt_list:
        lat = tag.get('lat').strip()
        lon = tag.get('lon').strip()
        code = tag.find('name').text.strip()
        desc = tag.find('desc').text.encode("ascii", "ignore").strip()
        url = tag.find('url').text.strip()
        old = '<wpt lat="{0}" lon="{1}">'.format(lat, lon)
        nFound += 1

        print("----- Found WPT {0} -----".format(code))

        final = get_final_coord(url)
        if final:
          fn = final.encode("ascii", "ignore")
          parts = re.split(' |\n', fn)
          nd = parts[2]
          nm = parts[3]
          wd = parts[5]
          wm = parts[6]
          lt = float(nd) + float(nm)/60.
          ln = (float(wd) + float(wm)/60.) * -1.0
          print("  Final: {0}, {1}".format(lt, ln))

          #   <wpt lat="40.67915" lon="-96.95545">
          # status += "Lat, Lon = {0}, {1} \n".format(lat, lon)
          # status += "URL = {0} \n".format(url)

          wpts[old] = '<wpt lat="{0}" lon="{1}">'.format(lt, ln)

          # Make a whole new waypoint...
          # now = strftime("%Y-%m-%dT%H:%M:%S%z", gmtime())
#         blocks.append('<wpt lat="{0}" lon="{1}">\n  <time>{2}</time>\n  <name>{3}</name\n  <urlname>Coordinate Override</urlname>\n  <desc>Coordinate Override</desc>\n  <type>Waypoint</type>\n</wpt>\n'.format(lt, ln, now, code))
#         blocks.append('<wpt lat="{0}" lon="{1}">\n  <name>{2}</name\n  <urlname>Coordinate Override</urlname>\n  <type>Waypoint</type>\n  <gsak:wptExtension xmlns:gsak="http://www.gsak.net/xmlv1/6">\n    <gsak:Parent>{2}</gsak:Parent>\n  </gsak:wptExtension>\n</wpt>\n'.format(lt, ln, code))
          nMod += 1

          s = randint(3, 10)
          print("...sleeping for {} seconds...".format(s))
          sleep(s)     # random sleep...from 3 to 10 seconds

      status += "\nDone scraping.  Found {0} WPT tags and {1} FN values to modify.\n\n".format(nFound, nMod)
      print(status)

      head, tail = os.path.split(xmlfile)
      output = "{0}/CORRECTED_{1}".format(head, tail)

      # output = "/tmp/CORRECTED_Coordinates.gpx"

      with open(xmlfile, 'r') as in_file:
        text = in_file.read()

      with open(output, 'w') as out_file:
        out_file.write(replace_all(text, wpts))

      # with open(output, 'w+') as out_file:
      #   for b in blocks:
      #     out_file.write(b)

      print("Done with substitutions.  Your modified WPTs are now in '{0}'.\n".format(output))

