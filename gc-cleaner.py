#!/usr/bin/env python

"""
gc-cleaner.py
Python2 script to parse a GPX file and remove any <wpt> tags as indicated in the "remove" list.
No GUI, so this thing is Docker-compatible.
"""

import os
import glob
from bs4 import BeautifulSoup

# ------------------------

remove = [ 'Challenge' ]

print("gc-cleaner.py starting...")

for filename in glob.iglob('./*.gpx'):
  if "CORRECTED" not in filename:
    xmlfile = filename
    wpts = dict()

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
      tags = soup.find_all( )
      nFound = 0
      nRemoved = 0

      for tag in tags:
        if tag.name == 'wpt':
          # lat = tag.get('lat')
          # lon = tag.get('lon')
          code = tag.find('name').text
          desc = tag.find('desc').text.encode("ascii", "ignore")
          # url = tag.find('url').text
          nFound += 1

          print("Found WPT {0}".format(code))

          for s in remove:
            if s in desc:
              tag.extract()
              nRemoved += 1
              print("  Removed!")

      print("\nDone cleaning.  Found {0} tags and removed {1} of them.\n\n".format(nFound, nRemoved))

      head, tail = os.path.split(xmlfile)
      output = "{0}/CLEAN_{1}".format(head, tail)

      with open(output, 'w') as out_file:
        out_file.write(soup.prettify("utf-8"))

      print("Done with removal.  Your cleaned WPTs are now in '{0}'.\n".format(output))

