#!/usr/bin/env python

"""
GCScraper.py
Python2 script to parse a GPX file and GC.com admin pages transcribe final (FN) coordinates into the GPX.
Basic GUI with command-line option lifted from https://acaird.github.io/2016/02/07/simple-python-gui
source.
"""

import tkFileDialog
import codecs
import string
import mechanize
import urllib2
import cookielib
import re
import os
from Tkinter import *
from bs4 import BeautifulSoup


def replace_all(text, dict):
  for old, new in dict.iteritems():
    text = text.replace(old, new)
  return text


def get_final_coord(url):
  https = string.replace(url, 'http:', 'https:')
  review = string.replace(https, 'seek/cache_details', 'admin/review')

  # u'http://www.geocaching.com/seek/cache_details.aspx?guid=a71f6d54-45d6-4f53-8320-ad7f49ce5cb1'
  # url = 'https://www.geocaching.com/admin/review.aspx?guid=6fa9769c-4206-4ea8-8f9f-053dca533ce9'

  cj = cookielib.CookieJar()
  br = mechanize.Browser()
  br.set_cookiejar(cj)
  br.open("https://www.geocaching.com/account/login?returnURL=" + review)
  br.select_form(nr=1)
  br.form['Username'] = 'Iowa.Landmark'
  br.form['Password'] = '4Score&Seven'
  br.submit()

  html = br.response().read()
  soup = BeautifulSoup(html, 'html.parser')
  td_list = soup.find_all("td")

  for td in td_list:
    if re.search('Final Location', td.text):
      FN = td.find_next_sibling("td").text
      return FN

  return False


def button_harvest_wpts_callback():
  """ what to do when the "Harvest WPTs" button is pressed """
    
  xmlfile = entry.get()
    
  if xmlfile.rsplit(".")[-1] != "gpx":
    statusText.set("Filename must have a .gpx extension!")
    message.configure(fg="red")
    return
    
  else:
    """ identify all the <wpt> tags. grab the lat, lon, name, description and url"""
    with open(xmlfile, 'r') as gpxfile:
      data = gpxfile.read()

    soup = BeautifulSoup(data, 'lxml')
    wpt_list = soup.find_all("wpt")
    nFound = 0
    nMod = 0

    status = ""
      
    for tag in wpt_list:
      lat = tag.get('lat')
      lon = tag.get('lon')
      code = tag.find('name').text
      desc = tag.find('desc').text.encode("ascii", "ignore")
      url = tag.find('url').text
      nFound += 1
        
      status += "----- Found WPT {0} -----\n".format(code)
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
        status += "Final: {0}, {1}".format(lt, ln)

      #   <wpt lat="40.67915" lon="-96.95545">

      # status += "Lat, Lon = {0}, {1} \n".format(lat, lon)
      # status += "URL = {0} \n".format(url)

        wpts[tag] = '<wpt lat="{0}" lon="{1}">'.format(lt, ln)
        nMod += 1

    # statusText.set(status)
    # message.configure(fg="dark green")

    statusText.set("Done.  Found {0} WPT tags and {1} FN values to modify.".format(nFound, nMod))
    message.configure(fg="blue")


def button_save_wpts_callback():
  """ what to do when the "Save Modified WPTs" button is pressed """

  xmlfile = entry.get()

  if xmlfile.rsplit(".")[-1] != "gpx":
    statusText.set("Filename must have a .gpx extension!")
    message.configure(fg="red")
    return

  else:
    head, tail = os.path.split(xmlfile)
    output = "{0}CORRECTED_{1}".format(head, tail)

    with open(xmlfile, 'r') as in_file:
      text = in_file.read()

    with open(output, 'w') as out_file:
      out_file.write(replace_all(text, wpts))

    statusText.set("Done.  Your modified WPTs are now in '{0}'.".format(output))
    message.configure(fg="blue")


def button_browse_callback():
  """ What to do when the Browse button is pressed """
  filename = tkFileDialog.askopenfilename()
  entry.delete(0, END)
  entry.insert(0, filename)
  
# ------------------------------------------------

wpts = dict()

root = Tk()
root.title("GCScraper v1.0")
root.geometry("1000x300")
frame = Frame(root)
frame.pack()
  
statusText = StringVar(root)
statusText.set("Press Browse button or enter GPX file path then press the Harvest... or Save...")
  
label = Label(root, text="GPX file:")
label.pack(padx=10)
entry = Entry(root, width=80, justify='center')
entry.pack(padx=10)
separator = Frame(root, height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=10, pady=5)
  
button_browse = Button(root, text="Browse", command=button_browse_callback)
button_harvest = Button(root, text="Harvest WPTs", command=button_harvest_wpts_callback)
button_save = Button(root, text="Save Harvested WPTs", command=button_save_wpts_callback())
button_exit = Button(root, text="Exit", command=sys.exit)
button_browse.pack()
button_harvest.pack()
button_save.pack()
button_exit.pack()
  
separator = Frame(root, height=2, bd=1, relief=SUNKEN)
separator.pack(fill=X, padx=10, pady=5)
  
message = Label(root, textvariable=statusText)
message.pack(padx=10, pady=5)
  
mainloop()

