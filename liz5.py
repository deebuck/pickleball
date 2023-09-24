#!/usr/bin/python3 

# Packages that needed to be installed: 
# I haven't kept this list up to date. I've added a few more to the list, but not sure I have everything. 
# On arch (on oregano) the packages are installed at the system level. 
# On debian 12 (on tarragon) I have created a virtual environment (/home/dee/pickle-environment/venv) and 
# some of the packages are installed there. 
#
# These are the packages I had to install.  
# python-selenium
# python-trio python-trio-websocket
# python-tz python-tzdata
#
# In addition I have installed at the system level: 
# argparse
# email, mime, smtp libraries for sending mail, including mail with mime attachments
# some timezone stuff tz, tzdata, zoneinfo
# random
# pretty print
#
import time

import datetime

import os

import sys

import math

import argparse

import smtplib
import mimetypes
import email
import email.mime.application
import email.mime.multipart
import email.mime.text

from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo

from random import randrange

from pprint import pprint

from selenium import webdriver

from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from selenium.webdriver.common.action_chains import ActionChains # open link in new tab

from email.message import EmailMessage

# variables
args=None # arguments to the program

# these are set by arguments to the program 
dryrun = 1        # do not actually make reservations, stop before clicking the final button
verbose = None    # be chatty on the console
debug = True      # generate debugging messages, only send email/texts to dee
width = 1200      # width of screen, unless headless
height = 1200     # height of screen, unless headless
headless = None   # "headless": do not show a browser screen on console
immediate = False # do the look/reserve right away, don't wait for midnight
court_name = None # "location": location at which to reserve 
session = None    # the coded value stipulating court time and duration
preference = None # a string with court preferences
offset = 0        # additional delay after midnight, to give a different pickle picker an advantage
hostname = os.uname() [1] # where am I running
logfile = None    # Log file
secs = 0.4        # time to sleep between screens so that we can see the pages changing

# midnight delay stuff
# basically, we usually sleep until just after midnight, and then wake up and try to reserve a court.
# two factors affect how soon after midnigh we will wake up. 
# one, called midnight_delay, is a random number generated here between 20 and 240 seconds. 
# the second, called offset, is a parameter which can be specified to the program at run time, 
# and if non-zero is added to the delay. The purpose of this is to enable having a pickle run
# on tarragon and another on oregano which runs as a "backup" (just in case). 
# This is probably belt and braces. If something goes wrong one place, it may also go wrong in the other. 

midnight_delay = randrange(20,240)

web_site = "https://web1.myvscloud.com/wbwsc/vafallschurchwt.wsc/splash.html"

# the log
picklejuice = "/tmp/picklejuice.log"

# screenshots are saved into a local directory in some debugging situations
my_debug_dir = '/Users/abrao/Downloads/pickleball_'
my_debug_dir = '/tmp/pickleball_'

# many specified reservations require us to make 2 separate reservations
nReservations = 1 # whether to make 1 or 2 reservations 

court_type = 'Pickleball' # as opposed to Tennis court

# if we make 2 reservations they have to be made by different users
# we have (currently) 3 users to chose from. Which are used is pseudo-random.
usernames = ['Liz', 'Sue', 'Brenda']
userids = ['8158', '24270', '20388']
passwords = ['C0rn1ch0n3!', '24270', 'Extracheese25!']

# the dates are now computed, and these values initialized there 
month = None
day = None

# this is the class field which exists on the html element if the time is available 
# we really only need to look for the "success" class
reservable_time_class = 'button multi-select full-block success cart-button cart-button--state-block'

# the possible times when courts may be reserved
desired_time_values = [
    # 1 hour sessions
    ['8:00 am - 9:00 am'],['8:30 am - 9:30 am'],
    ['9:00 am - 10:00 am'],['9:30 am - 10:30 am'],
    ['10:00 am - 11:00 am'],['10:30 am - 11:30 am'],
    ['11:00 am - 12:00 pm'],['11:30 am - 12:30 pm'],
    ['12:00 pm - 1:00 pm'],['12:30 pm - 13:30 pm'],
    ['1:00 pm - 2:00 pm'],['1:30 pm - 2:30 pm'],
    ['2:00 pm - 3:00 pm'],['2:30 pm - 3:30 pm'],
    ['3:00 pm - 4:00 pm'],['3:30 pm - 4:30 pm'],
    ['4:00 pm - 5:00 pm'],['4:30 pm - 5:30 pm'],
    ['5:00 pm - 6:00 pm'],['5:30 pm - 6:30 pm'],
    ['6:00 pm - 7:00 pm'],['6:30 pm - 7:30 pm'],
    ['7:00 pm - 8:00 pm'],['7:30 pm - 8:30 pm'],
    ['8:00 pm - 9:00 pm'],['8:30 pm - 9:30 pm'],
    ['9:00 pm - 10:00 pm'],
    # 1.5 hour sessions
    ['8:00 am - 9:30 am'],
    ['9:30 am - 11:00 am'],
    ['11:00 am - 12:30 pm'],
    ['12:30 pm - 2:00 pm'],
    ['2:00 pm - 3:30 pm'],
    ['3:30 pm - 5:00 pm'],
    ['5:00 pm - 6:30 pm'],
    ['6:30 pm - 8:00 pm'],
    ['8:00 pm - 9:30 pm'],
    # 2 hour sessions, 2 reservations 1 hour each
    ['8:00 am - 9:00 am', '9:00 am - 10:00 am'],['8:30 am - 9:30 am', '9:30 am - 10:30 am'],
    ['9:00 am - 10:00 am', '10:00 am - 11:00 am'],['9:30 am - 10:30 am', '10:30 am - 11:30 am'],
    ['10:00 am - 11:00 am', '11:00 am - 12:00 pm'],['10:30 am - 11:30 am', '11:30 am - 12:30 pm'],
    ['11:00 am - 12:00 pm', '12:00 pm - 1:00 pm'],['11:30 am - 12:30 pm', '12:30 pm - 1:30 pm'],
    ['12:00 pm - 1:00 pm', '1:00 pm - 2:00 pm'],['12:30 pm - 1:30 pm', '1:30 pm - 2:30 pm'],
    ['1:00 pm - 2:00 pm', '2:00 pm - 3:00 pm'],['1:30 pm - 1:30 pm', '1:30 pm - 2:30 pm'], 
    ['2:00 pm - 3:00 pm', '3:00 pm - 4:00 pm'],['2:30 pm - 3:30 pm', '3:30 pm - 4:30 pm'],
    ['3:00 pm - 4:00 pm', '4:00 pm - 5:00 pm'],['3:30 pm - 4:30 pm', '4:30 pm - 5:30 pm'],
    ['4:00 pm - 5:00 pm', '5:00 pm - 6:00 pm'],['4:30 pm - 5:30 pm', '5:30 pm - 6:30 pm'],
    ['5:00 pm - 6:00 pm', '6:00 pm - 7:00 pm'],['5:30 pm - 6:30 pm', '6:30 pm - 7:30 pm'],
    ['6:00 pm - 7:00 pm', '7:00 pm - 8:00 pm'],['6:30 pm - 7:30 pm', '7:30 pm - 8:30 pm'],
    ['7:00 pm - 8:00 pm', '8:00 pm - 9:00 pm'],['7:30 pm - 8:30 pm', '8:30 pm - 9:30 pm'],
    ['8:00 pm - 9:00 pm', '9:00 pm - 10:00 pm'],['8:30 pm - 9:30 pm', '9:30 pm - 10:30 pm'],
    # 2.5 hour sessions, 2 reservations, 1.5 hour followed by 1 hour, or 1 hour followed by 1.5 hour
    ['8:30 am - 9:30 am', '9:30 am - 11:00 am'],['9:30 am - 11:00 am', '11:00 am - 12:00 pm'],
    ['10:00 am - 11:00 am', '11:00 am - 12:30 am'],['11:00 am - 12:30 pm', '12:30pm - 1:30 pm'],
    ['11:30 am - 12:30 pm', '12:30 pm - 2:00 pm'],['12:30 pm - 2:00 pm', '2:00 pm - 3:00 pm'], 
    ['1:00 pm - 2:00 pm', '2:00 pm - 3:30 pm'], ['2:00 pm - 3:30 pm', '3:30 pm - 4:30 pm'],
    ['2:30 pm - 3:30 pm', '3:30 pm - 5:00 pm'], ['3:30 pm - 5:00 pm', '5:00 pm - 6:00 pm'],
    ['4:00 pm - 5:00 pm', '5:00 pm - 6:30 pm'], ['5:00 pm - 6:30 pm', '6:30 pm - 8:00 pm'],
    ['5:30 pm - 6:30 pm', '6:30 pm - 8:00 pm'], ['6:30 pm - 8:00 pm', '8:00 pm - 9:00 pm'],
    ['7:00 pm - 8:00 pm', '8:00 pm - 9:30 pm'],
    # 3 hour sessions, 2 reservations, 1.5 hour each 
    ['8:00 am - 9:30 am', '9:30 am - 11:00 am'], 
    ['9:30 am - 11:00 am', '11:00 am - 12:30 am'], 
    ['11:00 am - 12:30 pm', '12:30 pm - 2:00 pm'], 
    ['12:30 pm - 2:00 pm', '2:00 pm - 3:30 pm'], 
    ['2:00 pm - 3:30 pm', '3:30 pm - 5:00 pm'], 
    ['3:30 pm - 5:00 pm', '5:00 pm - 6:30 pm'], 
    ['5:00 pm - 6:30 pm', '6:30 pm - 8:00 pm'], 
    ['6:30 pm - 8:00 pm', '8:00 pm - 9:30 pm'] 
]

# the "session" argument to the program which selects the corresponding time value above
# The first integer is the duration, 1, 1.5, 2, 2.5, or 3 hours. But expressed *10 so it is an integer. 
# The second integer after the period is a four digit value representing a time, in 24 hour time
# 6:30pm is 1830, 11am is 1100. 

desired_time_keys = [
    '10.0800','10.0830',
    '10.0900','10.0930',
    '10.1000','10.1030',
    '10.1100','10.1130',
    '10.1200','10.1230',
    '10.1300','10.1330',
    '10.1400','10.1430',
    '10.1500','10.1530',
    '10.1600','10.1630',
    '10.1700','10.1730',
    '10.1800','10.1830',
    '10.1900','10.1930',
    '10.2000','10.2030',
    '10.2100',
    '15.0800',
    '15.0930',
    '15.1100',
    '15.1230',
    '15.1400',
    '15.1530',
    '15.1700',
    '15.1830',
    '15.2000',
    '20.0800','20.0830',
    '20.0900','20.0930',
    '20.1000','20.1030',
    '20.1100','20.1130',
    '20.1200','20.1230',
    '20.1300','20.1330',
    '20.1400','20.1430',
    '20.1500','20.1530',
    '20.1600','20.1630',
    '20.1700','20.1730',
    '20.1800','20.1830',
    '20.1900','20.1930',
    '20.2000','20.2030',
    '25.0830','25.0930',
    '25.1000','25.1100',
    '25.1130','25.1230',
    '25.1300','25.1400',
    '25.1430','25.1530',
    '25.1600','25.1700',
    '25.1730','25.1830',
    '25.1900',
    '30.0800',
    '30.0930',
    '30.1100',
    '30.1230',
    '30.1400',
    '30.1530',
    '30.1700',
    '30.1830'
]

# This is a mapping of the preference specification coming in on the command line to the values which will be found 
# in the reservation tables. The reservation tables have values for data-elements that are called "location", "facility", and "type" which 
# have the values shown below. 
preferences = {
    'ChT1': { "location" : "North Cherry Street Tennis Courts", "facility": "Cherry Street Court #1",       "type": "Tennis Court" },
    'ChT2': { "location" : "North Cherry Street Tennis Courts", "facility": "Cherry Street Court #2",       "type": "Tennis Court" },
    'ChP1': { "location" : "North Cherry Street Tennis Courts", "facility": "Cherry Street Pickleball #1",  "type": "Pickleball Courts" },
    'ChP2': { "location" : "North Cherry Street Tennis Courts", "facility": "Cherry Street Pickleball #2",  "type": "Pickleball Courts" },
    'ChP3': { "location" : "North Cherry Street Tennis Courts", "facility": "Cherry Street Pickleball #3",  "type": "Pickleball Courts" },
    'ChP4': { "location" : "North Cherry Street Tennis Courts", "facility": "Cherry Street Pickleball #4",  "type": "Pickleball Courts" },
    'CvT1': { "location" : "Cavalier Trail Park",               "facility": "Cavalier Trail Court #1",      "type": "Tennis Court" },
    'CvT2': { "location" : "Cavalier Trail Park",               "facility": "Cavalier Trail Court #2",      "type": "Tennis Court" },
    'CvP1': { "location" : "Cavalier Trail Park",               "facility": "Cavalier Trail Pickleball #1", "type": "Pickleball Courts" },
    'CvP2': { "location" : "Cavalier Trail Park",               "facility": "Cavalier Trail Pickleball #2", "type": "Pickleball Courts" },
    'CvP3': { "location" : "Cavalier Trail Park",               "facility": "Cavalier Trail Pickleball #3", "type": "Pickleball Courts" },
    'CvP4': { "location" : "Cavalier Trail Park",               "facility": "Cavalier Trail Pickleball #4", "type": "Pickleball Courts" }
}

# utility functions, to make the code easier to read

def waitelement(path):
    try:
        elem = WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.XPATH,path)))
    except TimeoutError:
        error("Timeout waiting for path: " + path,True)
    except NoSuchElementException:
        error("No such element exception via path: " + path,True)
    return elem

def waitelementCSS(css):
    try:
        elem = WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.CSS_SELECTOR,css)))
    except TimeoutError:
        error("Timeout exception waiting for CSS: " + css,True)
    except NoSuchElementException:
        error("No such element exception via CSS: " + css,True)
    return elem

def waitclick(path):
    waitelement(path).click()
    
def waitclickw(path):
    waitclick(path)    
    time.sleep(secs)

def findelement(path):
    return driver.find_element(By.XPATH,path)

def findelementbyCSS(selector):
    return driver.find_element(By.CSS_SELECTOR,selector)

def clickelement(path):
    findelement(path).click()

def clickelementbyCSS(selector):
    findelementbyCSS(selector).click()

# recording, debuging, communications

def record(msg):
    if verbose:
        print(msg)
    picklelogger.write(msg+"\n")

def sendemail(recipients,subject,body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['To'] = recipients
    msg['From'] = "picklemachine"
    msg.set_content(body)
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

# used to send a screenshot attachment. To use this for anything else, you probably 
# need to parameterize the filetype, because this assumes and hardcodes "jpg"
def sendemailwithattachment(recipients,subject,body,filename):
    msg = email.mime.multipart.MIMEMultipart()
    msg['Subject'] = subject
    msg['To'] = recipients
    msg['From'] = "picklemachine"
    body = email.mime.text.MIMEText(body)
    msg.attach(body)
    f=open(filename,'rb')
    attachment=email.mime.application.MIMEApplication(f.read(),_subtype="jpg")
    f.close
    attachment.add_header('Content-Disposition','attachment',filename=filename)
    msg.attach(attachment)
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

def sendsms(body):
    sendemail(text_recipients,'Pickletext:',body)
        
def getpicklejuice():
    picklelogger.flush();
    juice = ""
    with open(picklejuice) as fp:
        str = fp.read()
        juice += str + "\n"
    return juice

def sendresult(subject,send_screenshot):
     if send_screenshot:
         screenshot=do_screenshot()
     juice=getpicklejuice()
     if send_screenshot:
        sendemailwithattachment(email_recipients,subject,juice,screenshot)
     else:
        sendemail(email_recipients,subject,juice)
     sendsms(subject)

def error(errormsg,with_screenshot):
    record(errormsg)
    sendresult("Reservation Error",with_screenshot)
    driver.quit()    
    sys.exit(errormsg)
#
# Save a screenshot for debugging
#    
def do_screenshot():
    my_date_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    my_file = my_debug_dir + my_date_time + '.png'
    driver.save_full_page_screenshot(my_file)
    record("Screen shot saved as: "+my_file)
    return my_file

# This was an attempt to perform a logout of the user if the program experiences an exception 
# after logging someone in. The problem is that we don't know where we are. The idea was to 
# get back to the main screen again, but this hasn't worked and isn't currently being used. 
def logout():
    driver.get(web_site)
    WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))
    # this time delay was so I could explore the page before the program causes it to disappear from my screen
    time.sleep(200)
    # show the my account menu in the page header, to expose the logout button
    waitclickw('/html/body/div/div/header/div/div[4]/ul/li/a')
    # click logout button
    waitclickw('/html/body/div/div/header/div/div[4]/ul/li/div/ul/li[5]/ul/li[4]/a')

# This was for debugging, it dumps out what times are available and/or unavailable in a table set 
def dump_tableset(tableset):
    for t in range(len(tableset)):
        print("Table Set "+str(t)) 
        table = tableset[t]
        rows = table.find_elements(By.TAG_NAME, "tr")
        data = rows[1].find_elements(By.TAG_NAME, "td")
        facility = data[1].text
        location = data[2].text
        courttype = data[3].text
        print(" Location: "+location+" Facility: "+facility+" Type: "+courttype); 
        avail = rows[2].find_elements(By.CSS_SELECTOR, "a.success")
        unavail = rows[2].find_elements(By.CSS_SELECTOR,"a.error")
        for tm in range(len(avail)):
            print("Available times: "+avail[tm].text)
        for tm in range(len(unavail)):
            print("Unavailable times: "+unavail[tm].text)

# A piece of debugging code it took me a little time to get right, so I'm keeping it, for now. 
# This isn't being used now. 
# The problem that this helped me sort out, is that after the body is loaded, javascript triggers which MAY determine that the user is already logged in elsewhere, 
# or that the user is trying to make a second reservation. In such a case javascript triggers a redirect. This creates a race condition, selenium is trying to analyze
# the page it has just loaded, while meantime javascript is changing the page out from under us. 
# I was trying to identify certain error conditions by looking at an attribute of the body tag, and it was changing on the redirect. 
#
def dump_body_attributes(bodyelem):
    record("Body attributes:")
    attscript='var items = {}; for (index = 0; index < arguments[0].attributes.length; ++index) { items[arguments[0].attributes[index].name] = arguments[0].attributes[index].value }; return items;'
    attrs = driver.execute_script(attscript, bodyelem)
    pprint(attrs)
    #propscript='var items = {}; for (index = 0; index < arguments[0].properties.length; ++index) { items[arguments[0].properties[index].name] = arguments[0].properties[index].value }; return items;'
    #props = driver.execute_script(propscript, bodyelem)
    #pprint(props)
    #html body div#app.webaddtocard div#app-container div#content div.inner form#processingprompts

# These are the "substantive" routines

# Fetch_tableset is a function to navigate a web page reservation window, specifying the date (myday, mymonth) and try to obtain the html elements for the table of available 
# court locations and times. It returns that tableset for subsequent analysis. 
# The program now selects the courts both at Cavalier Trail and North Cherry Street, for date mymonth/myday. It fetches at time myreservation_time. 
def fetch_tableset(myday, mymonth, myreservation_time):
    
    monthNum = mymonth
    dayNum = myday
    
    # click in first page Tennis pic 
    waitclickw('/html/body/div/div/div/div/div[2]/section/div/a[5]')

    # activate the date drop-down
    waitclickw('//*[@id="date_vm_4_button"]')

    # click month button
    waitclick('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[1]/div[1]/div/div/div[1]/div[1]/div/button/span')
    waitclick('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[1]/div[1]/div/div/div[1]/div[1]/div/div/ul/li[' +str(monthNum)+ ']/span')

    # click day button
    waitclick('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[1]/div[1]/div/div/div[1]/div[2]/div/button/span') 
    waitclick('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[1]/div[1]/div/div/div[1]/div[2]/div/div/ul/li[' +str(dayNum)+ ']/span')

    # click on Done button
    waitclickw('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[1]/div[1]/div/div/button')

    # select time
    beginTimeElement = waitelement('/html/body/div[1]/div[1]/div/div/form/div[1]/div[1]/div[1]/div[2]/div[1]/div/input')
    
    # the time select is pre-filled with 8:00AM, erase that
    for i in range(len('8:00AM')):
        beginTimeElement.send_keys((Keys.BACKSPACE))
        
    # and put in our own value    
    beginTimeElement.send_keys(myreservation_time)

    # now select the location - click on the location dropdown list icon, then select the location(s)
    clickelement('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[3]/label/span[1]')

    # Click the select boxes for both Cavalier and Cherry. 
    locationdropdown = findelement('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[3]/div/div/div/ul')
    clickelementbyCSS("li[data-value='NCHER']")
    clickelementbyCSS("li[data-value='CAVAL']")
    
    # click on Max Available Blocks to Display to show the drop down, then activate the drop-down
    clickelement('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[4]/label/span')
    clickelement('//*[@id="blockstodisplay_vm_2_button"]')
 
    # select 6 blocks: the maximum we can display
    clickelement('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[4]/div[1]/div/div/ul/li[6]/span')

    # click on Search button: this will refresh the page with the tableset of court times, types, locations
    clickelement('//*[@id="frwebsearch_buttonsearch"]')

    # here we wait to ensure the search tables are visible, don't need result
    waitelement('//*[@id="frwebsearch_output_table"]')

    # obtain the court reservation tableset
    tableset = driver.find_elements(By.CLASS_NAME, "result-content")
    # dump_tableset(tables)

    return tableset

def choose_user(): 
    if debug: 
        record("Userids: " + " ".join(str(x) for x in userids))
        record("Usernames: " + " ".join(str(x) for x in usernames))

    # select a user under whose account we will make a reservation, then remove it from the list
    # Counter-intuitively, have to specify the range as 0 - #of users, rather than 0 - #users-1. 
    #
    userindex = randrange(0,len(userids))
    user = {"userid":userids[userindex],"username":usernames[userindex],"password":passwords[userindex]}
    userids.remove(user["userid"])
    usernames.remove(user["username"])
    passwords.remove(user["password"])
    if debug:
        record ( "Chose user " + user["username"] + "(" + str(userindex) + ")" )
    return user

#
# Search an available times tableset (returned by fetch_tableset) looking for a specific desired time
# tableset is the tableset returned from fetch_tableset
# soughttime is a string time specification 
#
def search_tableset(tableset,court,soughttime): 
    foundtime = False  
    location = court["location"]
    type = court["type"]
    facility = court["facility"]
    if debug: 
        record ("Checking "+facility)   
    try: 
        for table_index in range(len(tableset)):
            table = tableset[table_index]
            rows = table.find_elements(By.TAG_NAME, "tr")
            data=rows[1].find_elements(By.TAG_NAME, "td")
            if facility in data[1].text and location in data[2].text and type in data[3].text: 
                available_time = [None, None]
                all_available_times = rows[2].find_elements(By.CSS_SELECTOR, "a.success")
                for all_available_times_index in range(len(all_available_times)):
                    curr_available_time = all_available_times[all_available_times_index]                            
                    if soughttime in curr_available_time.text:
                        foundtime = curr_available_time
                        record(facility+" available at " + foundtime.text)
                        break  # for availableTime_index in availableTimes:
                if debug and not foundtime: 
                    record(facility+" not available at "+soughttime); 
            if foundtime: 
                return foundtime 
    except Exception as e:
        error("Exception in searching tableset: "+str(e),True)
    return False

# 
# having found a suitable available time/court, log in as one of the users, and make a reservation, then log out
# my_element: activeTime1 or activeTime2
# my_handle: driver handle for this window

def make_reservation(my_element,user):

    # click on the passed in element, to activate the reservation process
    my_element.click()
    
    # obtain the user info
    my_userid=user["userid"]
    my_username=user["username"]
    my_password=user["password"]

    # enter data on the add-to-cart pop up that appears after clicking on a reservation time slot
    waitclick('/html/body/div[1]/div[2]/div/div/div/button[2]/span')
    
    # after adding a reservation to the cart, we are obliged to log in
    usernameXPATH = '//*[@id="weblogin_username"]'
    passwordXPATH = '//*[@id="weblogin_password"]'
    loginButtonXPATH = '//*[@id="weblogin_buttonlogin"]'
    for item in [[usernameXPATH, my_userid], [passwordXPATH, my_password], [loginButtonXPATH, Keys.ENTER]]:
        waitelement(item[0]).send_keys(item[1])
    
    time.sleep(secs)

    if debug:
        record("Logged in successfully as "+my_userid)

    # Here I am trying to detect two error conditions that occur when trying to log in to make a reservation. 
    # One is that there is an active session open for the user we choose. This happens frequently in debugging, because something goes wrong, and we bomb out
    # with the user still logged in. 
    # The second condition is that this user already has a reservation. 
    #
    # It has been hard to catch this stuff and check for it, because I think there is code on the loaded page to detect this situation. The javascript is invoked on 
    # page load, and if it needs to, it does a redirect. The markers I am looking for are on the redirected/reloaded page. If I check too soon, I am missing the markers
    # because I'm still looking at the initial page, before the redirect. Therefore, I need to wait, after the page loads for the javascript on the page to 
    # run, to detect the condition, and then to perform a redirect. 
    # So this sleep is to give javascript time to redirect, and for the new page to be acquired.  
    time.sleep(5)

    # the body tag has an attribute we can trigger off of. 
    bodyelem=waitelement("/html/body")
    
    try:
        if findelementbyCSS('body[data-view="websessionalert"]'):
            error(my_username + ' has an active session open',True)
    except NoSuchElementException:
        if debug: 
            record(my_username + ' has no active session')
    except Exception as e: 
        error('Threw error looking for websession alert page: '+str(e),True)

    try: 
        if findelementbyCSS('div#content div.inner form#processingprompts div#tab-24127 div.rule-group div#processingprompts_rulegroup'):
            record("matched"); 
            time.sleep(600)
            error(my_username + ' already has a reservation',True)
    except NoSuchElementException:
        if debug: 
            record(my_username + ' has no existing reservation')
    except Exception as e:
        error('Threw exception looking for processing prompt form: '+str(e),True)

    # after logging in a new set of prompts must be satisfied, to complete the "purchase"

    # Event Type: Tennis Court Reservations
    # Activate Event Type drop-down
    waitclick('/html/body/div/div/div/div/form/div[1]/div[1]/div[1]/div[1]/div[1]/div/button/span')
    
    # Click on tennis court reservation
    waitclick('/html/body/div/div/div/div/form/div[1]/div[1]/div[1]/div[1]/div[1]/div/div/ul/li[2]/span')
 
    # Reservation Purpose
    # Activate Reservation Purpose drop-down
    waitclick('//*[@id="question4791204_vm_2_button"]')
     
    # Select Pickleball
    waitclick('/html/body/div/div/div/div/form/div[1]/div[1]/div[1]/div[2]/div[1]/div/div/ul/li[4]/span')

    # Click Continue button
    waitclickw('//*[@id="processingprompts_buttoncontinue"]')

    # Now we are on the final Shopping Cart page, reviewing our purchases, and ready to proceed to checkout
    # Activate the Proceed to checkout button
    waitclickw('//*[@id="webcart_buttoncheckout"]')

    # On the Checkout page, where we accept the charge of $0.
    # We accept the payment and proceed, unless this is a dry run
    if dryrun: 
        if debug: 
            record("Dry run: Reservation was not actually made")

        # since we aren't really making a reservation, we have to empty the cart and log out.         
        # So first go back to the shopping cart page by activating the back button
        waitclickw('//*[@id="webcheckout_buttonback"]')
        # empty the cart, using the button provided for that
        waitclickw('//*[@id="webcart_buttonemptycart"]')
        # show the my account menu in the page header, to expose the logout button
        waitclickw('/html/body/div/div/header/div/div[4]/ul/li/a')
        # click logout button
        waitclickw('/html/body/div/div/header/div/div[4]/ul/li/div/ul/li[5]/ul/li[4]/a')
    else:
        # Activate the Continue button on the Checkout page, to complete our purchase
        waitclickw('//*[@id="webcheckout_buttoncontinue"]')
        if debug:
            print("Made a reservation as user "+my_username+" ("+my_userid+")") 

        # And now activate the logout button which is presented
        waitclickw('//*[@id="webconfirmation_buttonlogout"]')

    return

def ensure_started():
    to=0
    found=False

    while to < 3 and not found:
        try:
            driver.get(web_site)
            found = WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))
        except Exception as e0:
            to += 1
            record("Exception 0: " + str(e0) + " getting original page")
    if not found: 
        error("Failed to load the website")

def search_for_court():
    tables = [None, None]
    times = [None,None]
    found = False

    if nReservations > 1:
        script = "window.open(" + '"' + web_site + '"' + ")"
        driver.execute_script("window.open(" + '"' + web_site + '"' + ")")
        time.sleep(secs)

    handles = driver.window_handles
    
    driver.switch_to.window(handles[0])

    if nReservations > 1:                                 
        driver.switch_to.window(handles[1])
        tables[1] = fetch_tableset(day, month, reservation_time)
        driver.switch_to.window(handles[0])
            
    tables[0] = fetch_tableset(day, month, reservation_time)
    
    # now trying to find a court with availability at the desired time(s)
    first_time = second_time = None

    # check against each of the preferences we were give for a court and type at the indicated time 
    for p in range(len(court_prefs)):
        court = court_prefs[p]; 
        times[0] = search_tableset(tables[0],court,desired_times[0])
        if times[0]: 
            if nReservations >1:
                driver.switch_to.window(handles[1])
                times[1] = search_tableset(tables[1],court_prefs[p],desired_times[1])
                driver.switch_to.window(handles[0])
        if times[0] and times[1]: 
            break #for loop over possible prefs

    if not(times[0]):
        error("Could not find a time slot to reserve",False)

    if nReservations > 1 and not(times[1]):
        error("Could not find the second required court time",False)

    record("Will make a reservation for "+times[0].text+" at "+court['facility'])
    if nReservations > 1:
        record("Will make a second reservation for "+times[1].text+", also at "+court['facility'])

    return times

#
# mainline code begins here
#

#
# All time calculations are in Falls Church timezone
#
FallsChurchtz = ZoneInfo("America/New_York")
now = datetime.now(FallsChurchtz)

picklelogger = open(picklejuice,"w")
picklelogger.write("----- "+str(now.strftime('%I:%M:%S%p'))+'\n')

# first parse the arguments
try:
    parser = argparse.ArgumentParser("Make reservations for a pickleball court");
    parser.add_argument("-p", "--preferences", dest="Preferences", help="Preference for location [Cv or CH][court type T or P][number], e.g. ChT2 of CvP4", nargs='*')
    parser.add_argument("-s", "--session", dest="Session",required=True, help="Session duration & start time, in 24H clock. E.g. 1830=6:30p.m.",choices=desired_time_keys)
    parser.add_argument("-g", "--debug",help="Turn on debugging",dest="Debug",action="store_true")
    parser.add_argument("-v", "--verbose",help="Be loquacious",dest="Verbose",action="store_true")
    parser.add_argument("-z", "--headless",help="Headless, don't show webpage",dest="Headless",action="store_true")
    parser.add_argument("-i", "--immediate",help="Do not wait till midnight",dest="Immediate",action="store_true")
    parser.add_argument("-d", "--dry-run",help="Dry run, don't make a reservation",dest="Dryrun",action="store_true")
    parser.add_argument("-x", "--width",help="Window width unless headless",dest="Width",action="store")
    parser.add_argument("-y", "--height",help="Window height unless headless",dest="Height",action="store")
    parser.add_argument("-o", "--offset",help="Extra offset delay after midnight",dest="Offset",action="store")
    args = parser.parse_args();
except Exception as e:
    error("Exception parsing arguments",False)

debug = args.Debug
verbose = args.Verbose
headless = args.Headless
immediate = args.Immediate
width = args.Width
height = args.Height
session = args.Session
dryrun = args.Dryrun
offset = args.Offset

# Process the incoming court-time preference 
court_prefs = []
for p in range(len(args.Preferences)):
    pref = preferences[args.Preferences[p]]
    court_prefs.append(pref)

if debug:
    email_recipients = "dee@wmbuck.net"
    text_recipients = "3037751709@tmomail.net" # dee 
    sargs = "Arguments: "
    for a in args.__dict__:
        if args.__dict__[a] is not None:
            sargs = sargs + a + ":" + str(args.__dict__[a]) + ",";
    record('Attempting court reservation on '+str(hostname)+':\n'+sargs)
else:
    email_recipients = "dee@wmbuck.net, lsalak@verizon.net"
    text_recipients = "3037751709@tmomail.net, 7039738520@vtext.com"

# build desired_times dictionary
desired_times_dict = dict(zip(desired_time_keys, desired_time_values))

# check if this is a dry run. Do this before we decide whether to sleep
if dryrun: 
    record("This is a dry run on "+str(hostname))
else: 
    record("This is a live run on "+str(hostname)+" and will try to make a real reservation")

# 
# In immediate mode the reservation will be made for tomorrow
# Otherwise (the normal mode) we wait till midnight tonight, and then attempt to reserve for the "new" tomorrow
#
tomorrow = now+timedelta(days=1); 
midnight = datetime(tomorrow.year,tomorrow.month,tomorrow.day,0,0,0,0,FallsChurchtz)
#
if immediate:
    reservedate=tomorrow
else:
    reservedate = tomorrow+timedelta(days=1)
month = reservedate.month
day = reservedate.day

# 
# About the delay after midnight. 
#
# We experienced an odd failure, which I interpret as some kind of reset occurring on the city 
# website immediately after midnight. This wouldn't surprise me. At the website end they have  
# to somehow accommodate a change in the data availability, and this could be accompanied by
# a reset of the web server, which could reset all the http connections. 
# So, there is an automatic delay to be sure we don't wake up until at least 20 seconds past midnight,
# so that whatever shenanigans are going on can settle. 
# A second factor in picking the delay is a pseudo random number between that 20 seconds and 
# 4 minutes (240 seconds), which is intended to ensure our pickle picking looks like a human being
# rather than a robot.  
# Finally, I have added a parameter "offset" which can be passed into the program at run time 
# with the -o or --offset flag, which, if non-zero, adds "n" 5 minute (300 second) delays. So if 
# offset = 1, we add 300 seconds. If offset = 2 we hadd 600 seconds.  
# The intention is that during the development/debugging stage, when court picking has sometimes been
# sporadically unreliable, we can have a backup pickle-picker on another machine, with a delay, as 
# a backup in case the first one fails. 
#
if offset: 
    offset = int(offset)
    if offset > 12:
        offset = 12
    offset = offset*300
    midnight_delay += offset
    if debug: 
        record("Offset will be "+str(offset)+". Midnight delay="+str(midnight_delay)+".")
    

sleeptime = (midnight-now).total_seconds()+midnight_delay

# figure out what time she wants to play pickleball

desired_times = desired_times_dict[session]
reservation_time = desired_times[0].split("-")[0].rstrip() # begin time on earliest desired timeslot

# need to know if we have to make more than one reservation, parse the session id
SessionParts = session.split('.');

# the duration is kept as an integer 10, 15, 20, 25, 30, for 1.0, 1.5, 2.0, 2.5, 3.0 hours 
Duration = int(SessionParts[0])

# A duration longer than 1.5 hours requires two reservations
if Duration > 15:
    nReservations = 2

# String version of the duration as hours
sDuration = str(Duration/10)

# this is to add "dry run" to the message, if appropriate
drs=""
if dryrun:
    drs=" (dry run)"

reservemessage = 'Pickleprocessor on ' + str(hostname) + ' reserving '+str(nReservations)+' slots: '+str(month)+'/'+str(day)+", "+sDuration+" hrs @ "+str(desired_times)+drs 
record(reservemessage)
sendsms(reservemessage)

if not(immediate):
    record("Time is "+str(now.strftime('%I:%M:%S%p'))+" Falls Church time. Sleeping until midnight plus "+str(midnight_delay)+" seconds.");
    time.sleep(sleeptime)
    now = datetime.now(FallsChurchtz)
    tomorrow = now+timedelta(days=1)
    record("Time is "+str(now.strftime('%I:%M:%S%p'))+" Falls Church time, tomorrow is "+str(tomorrow.strftime('%a, %m/%d/%Y')))
else:
    record("Time is "+str(now.strftime('%I:%M:%S%p'))+" Falls Church time. Immediate is set, so not sleeping.")

# now set up to bring up some web pages to scrape
options = Options()
if args.Headless:
    options.add_argument("--headless")
else:
    options.add_argument('--width='+width)
    options.add_argument('--height='+height)

service = Service(log_output=os.path.devnull)

driver = webdriver.Firefox(options=options, service=service) 

# ensure that the page is stable, and that the desired "tennis court" element is present
ensure_started()

# Look for a court to reserve
# There is some problem with occasionally happens where a fault is experienced
# while looking for the court. It seems to be sporadic. So now we try three times. 
look=0
found=False

while look < 3 and not found:
    try:
        timeelements = search_for_court() 
        if timeelements:
            found = True  
    except Exception as e0:
        look += 1
        record("Exception 0: " + str(e0) + " searching for a court")

if not found: 
    error("Failed to find a court after three tries")

# Make the reservation

try:
    user = choose_user()
    record("Trying to make reservation as user " + user["username"] + "(" + str(user["userid"]) + ")")
    make_reservation(available_time[0],user)
except Exception as e:
    # logout()
    error("Exception making first reservation: " + str(e) + ". Screenshot attached.",True)

if nReservations > 1:
    driver.switch_to.window(handles[1])
    user = choose_user()
    try: 
        record("Trying to make a second reservation as user " + user["username"] + "(" + str(user["userid"]) + ")")
        make_reservation(available_time[1],user)
    except Exception as e:
        # logout()
        error("Exception making second reservation: " + str(e) + ". Screenshot attached.",True)

if dryrun: 
    sendresult("(Dryrun) Reservation run was successful",False)
else:
    sendresult("Reservation was successful",False)

##### cleanup

driver.switch_to.window(handles[0])
driver.close()

if nReservations > 1:
    driver.switch_to.window(handles[1])
    driver.close()

driver.quit()
