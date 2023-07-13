#!/usr/bin/python3 
# import, constants, etc

# Packages that needed to be install: 
# 
# These are the AUR packages I had to install on Arch: 
# python-selenium
# python-trio-websocket
# python-tzdata
#
import time

import datetime

import os

import sys

import math

import argparse

import smtplib

from datetime import datetime
from datetime import timedelta
from zoneinfo import ZoneInfo

import tzdata


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
verbose = None    # more chatty
debug = True      # generate debugging messages, only send email/texts to dee
width = 1200      # width of screen, unless headless
height = 1200     # height of screen, unless headless
headless = None   # "headless": do not show a browser screen on console
immediate = False # do the look/reserve right away, don't wait for midnight
court_name = None # "location": location at which to reserve 
session = None    # the coded value stipulating court time and duration
preference = None # a string with court preferences

logfile = None  # Log file

secs = 0.5 # time to sleep so that we can see the pages changing
midnight_delay = 30.0  # delay after midnight before we start trying to reserve

web_site = "https://web1.myvscloud.com/wbwsc/vafallschurchwt.wsc/splash.html"


# screenshots are saved into a local directory in some debugging situations
my_debug_dir = '/Users/abrao/Downloads/pickleball_'
my_debug_dir = '/home/dee/Downloads/pickleball_'

# man specified reservations require us to make 2 separate reservations
nReservations = 1 # whether to make 1 or 2 reservations 

court_type = 'Pickleball' # court_name = 'Cherry Street Court #1' 

# if we make 2 reservations they have to be made by different users
usernames = ['8158', '24270']
passwords = ['C0rn1ch0n3!', '24270']

# the dates are now computed, and these values initialized there 
month = None
day = None

# this is the class field which exists on the html element if the time is available 
reservable_time_class = 'button multi-select full-block success cart-button cart-button--state-block'

# the times when courts may be reserved
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
    '20.2000',
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
# in the reservation tables. 
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

# utility functions, to make it easier to read

def waitelement(path):
    try:
        elem = WebDriverWait(driver,20).until(EC.element_to_be_clickable((By.XPATH,path)))
    except TimeoutError:
        raise "ElementTimeout";
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

# recording and debuging

def record(msg):
    if verbose:
        print(msg)
    picklelogger.write(msg+"\n")

# Function to navigate a web page reservation window, specifying the date (myday, mymonth) and obtain the html elements for the table of available 
# court locations and times, returning that table for subsequent analysis. 
# The program now selects the courts both at Cavalier Trail and North Cherry Street. 

def fetch_tables(myday, mymonth, myreservation_time):
    
    monthNum = mymonth
    dayNum = myday
    
    # click in first page Tennis pic 
    waitclickw('/html/body/div/div/div/div/div[2]/section/div/a[5]')

    # now on second page
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
    
    for i in range(len('8:00AM')):
        beginTimeElement.send_keys((Keys.BACKSPACE))
        
    beginTimeElement.send_keys(myreservation_time)

    # now selecting the location - click on the dropdown list icon, then select the location
    clickelement('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[3]/label/span[1]')

    # The original version entered a court name string (which did an autocomplete action) then clicked select all
    #findelement('//*[@id="location_vm_1_filter_input"]').send_keys(mycourt_name)
    #clickelement('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[3]/div[1]/div/div/div[2]/a[1]')

    # The newer version clicks the select boxes for both Cavalier and Cherry. This is kludgy and fragile. 
    # It would be better to check the li's and check for the courts we want
    clickelement('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[3]/div/div/div/ul/li[1]')
    clickelement('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[3]/div/div/div/ul/li[4]')
    
    # click on Max Available Blocks to Display to activate drop down
    clickelement('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[4]/label/span')
    clickelement('//*[@id="blockstodisplay_vm_2_button"]')
 
    # select 6 blocks: the maximum we can display
    clickelement('/html/body/div/div[1]/div/div/form/div[1]/div[1]/div[1]/div[4]/div[1]/div/div/ul/li[6]/span')

    # click on Search button: this will refresh the page with the table of court times, types, locations
    clickelement('//*[@id="frwebsearch_buttonsearch"]')

    # here we wait to ensure the search tables are visible, don't need result
    waitelement('//*[@id="frwebsearch_output_table"]')

    # find all the court reservation tables
    tables = driver.find_elements(By.CLASS_NAME, "result-content")
    # dump_tables(tables)

    return tables

# This was for debugging, it dumps out what times are available and/or unavailable in a set of tables 
def dump_tables(tables):
    for t in range(len(tables)):
        print("Table "+str(t)) 
        table = tables[t]
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

#
# Search the available times table (returned by find_tables) looking for a specific desired time
# atable is the table returned from find_tables
# soughttime is a string time specification 
#
def search_atable(atable,preference,soughttime): 
    foundtime = False  
    location = preference["location"]
    type = preference["type"]
    facility = preference["facility"]
    if debug: 
        record ("Searching for "+facility+" at time "+str(soughttime))   
    try: 
        for table_index in range(len(atable)):
            table = atable[table_index]
            rows = table.find_elements(By.TAG_NAME, "tr")
            data=rows[1].find_elements(By.TAG_NAME, "td")
            if facility in data[1].text and location in data[2].text and type in data[3].text: 
                if debug: 
                    record("Found matching facility, location and type, checking times") 
                available_time = [None, None]
                all_available_times = rows[2].find_elements(By.CSS_SELECTOR, "a.success")
                for all_available_times_index in range(len(all_available_times)):
                    curr_available_time = all_available_times[all_available_times_index]                            
                    if soughttime in curr_available_time.text:
                        foundtime = curr_available_time
                        record("Found a court available at " + facility + " at " + foundtime.text)
                        break  # for availableTime_index in availableTimes:
            if foundtime: 
                return foundtime 
    except Exception as e:
        error("Exception in searching table: "+str(e))
    return False

#
# Save a screenshot for debugging
#    
def do_screenshot():
    if debug:
        my_date_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        my_file = my_debug_dir + my_date_time + '.png'
        driver.save_full_page_screenshot(my_file)
        record("Debug: screen shot saved as: "+my_file)
    
# 
# log in as a user, and make a reservation, then log out
# my_element: activeTime1 or activeTime2
# my_handle: driver handle for this window
#  
def make_reservation(my_element, my_userid, my_password):
    
    my_element.click()
    
    # enter data on the pop up that appears after clicking on a reservation time slot
    
    waitclick('/html/body/div[1]/div[2]/div/div/div/button[2]/span')
    
    usernameXPATH = '//*[@id="weblogin_username"]'
    passwordXPATH = '//*[@id="weblogin_password"]'
    loginButtonXPATH = '//*[@id="weblogin_buttonlogin"]'
    for item in [[usernameXPATH, my_userid], [passwordXPATH, my_password], [loginButtonXPATH, Keys.ENTER]]:
        waitelement(item[0]).send_keys(item[1])
        time.sleep(secs)
        
    # satisfy the remaining prompts

    # question1XPATH = '//*[@id="question3756474_vm_1_button"]'
    waitclick('/html/body/div/div/div/div/form/div[1]/div[1]/div[1]/div[1]/div[1]/div/button/span')
    
    # it is a tennis court reservation
    waitclick('/html/body/div/div/div/div/form/div[1]/div[1]/div[1]/div[1]/div[1]/div/div/ul/li[2]/span')
 
    # click on question 2
    waitclick('//*[@id="question4791204_vm_2_button"]')
     
    # it is Pickleball
    waitclick('/html/body/div/div/div/div/form/div[1]/div[1]/div[1]/div[2]/div[1]/div/div/ul/li[4]/span')

    # Continue button
    waitclickw('//*[@id="processingprompts_buttoncontinue"]')

    # Proceed to checkout
    waitclickw('//*[@id="webcart_buttoncheckout"]')

    # Checkout "payment" unless dry run
    if dryrun: 
        if debug: 
            record("Dry run: Reservation was not actually made")
#            if verbose: 
#                do_screenshot()
        # since we aren't really making a reservation, we have to empty the cart and log out.         
        # go back to cart
        waitclickw('//*[@id="webcheckout_buttonback"]')
        # empty the cart
        waitclickw('//*[@id="webcart_buttonemptycart"]')
        # show the my account menu, to expose the logout button
        waitclickw('/html/body/div/div/header/div/div[4]/ul/li/a')
        # click logout button
        waitclickw('/html/body/div/div/header/div/div[4]/ul/li/div/ul/li[5]/ul/li[4]/a')
    else:
        # continue button
        waitclickw('//*[@id="webcheckout_buttoncontinue"]')
        if debug:
            print("Made a reservation as user "+my_userid) 
 #           if verbose: 
 #               do_screenshot()
        # logout button
        waitclickw('//*[@id="webconfirmation_buttonlogout"]')

    return

def sendemail(recipients,subject,body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['To'] = recipients
    msg['From'] = "picklemaster"
    msg.set_content(body)
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()

def sendresultemail(subject):
    picklelogger.close()
    body = ""
    with open("picklejuice.log") as fp:
        str = fp.read()
        print("L:"+str)
        body += str + "\n"
    sendemail(email_recipients,subject,body)

def sendtext(body):
    sendemail(text_recipients,'Picklemaster says:',body)
        
def error(body):
    record(body)
    sendresultemail("Reservation Error")
    sendtext("Reservation Error")
    driver.quit()    # FIX ME
    sys.exit(body)

#
# mainline code begins here
#

picklelogger = open("picklejuice.log","w")

# first parse the arguments
try:
    parser = argparse.ArgumentParser("Make reservations for a pickleball court");
    parser.add_argument("-p", "--preferences", dest="Preferences", help="Preference for location [Cv or CH][court type T or P][number], e.g. ChT2 of CvP4", nargs='*')
    parser.add_argument("-s", "--session", dest="Session",required=True, help="Session duration & start time, in 24H clock. E.g. 1830=6:30p.m.",
                         choices=desired_time_keys)
    parser.add_argument("-g","--debug",help="Turn on debugging",dest="Debug",action="store_true")
    parser.add_argument("-v","--verbose",help="Be loquacious",dest="Verbose",action="store_true")
    parser.add_argument("-z","--headless",help="Headless, don't show webpage",dest="Headless",action="store_true")
    parser.add_argument("-i","--immediate",help="Do not wait till midnight",dest="Immediate",action="store_true")
    parser.add_argument("-d","--dry-run",help="Dry run, don't make a reservation",dest="Dryrun",action="store_true")
    parser.add_argument("-x","--width",help="Window width unless headless",dest="Width",action="store")
    parser.add_argument("-y","--height",help="Window height unless headless",dest="Height",action="store")
    args = parser.parse_args();
except Exception as e:
    error("Exception parsing arguments")

debug = args.Debug
verbose = args.Verbose
headless = args.Headless
immediate = args.Immediate
width = args.Width
height = args.Height
session = args.Session
dryrun = args.Dryrun

# Process the incoming shorthand preference request, and turn it into the full specification 
# that will show up in the tables. 
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
    record('Attempting court reservation:\n'+sargs)
else:
    email_recipients = "dee@wmbuck.net, lsalak@verizon.net, abrao.grynglas@gmail.com, david@salaks.net"
    text_recipients = "3037751709@tmomail.net, 7039738520@vtext.com" # dee liz

# built desired_times dictionary
desired_times_dict = dict(zip(desired_time_keys, desired_time_values))

# check if this is a dry run. Do this before we decide whether to sleep
if dryrun: 
    record("This is a dry run")
else: 
    record("This is a live run, and will make a reservation")

#
# this code attempts to make all time calculations in terms 
# of time in Falls Church
# 
# In immediate mode the reservation will be made for tomorrow
# Otherwise (the normal mode) we wait till midnight tonight, and will then reserve for the "new" tomorrow
#
FallsChurchtz = ZoneInfo("America/New_York")
now = datetime.now(FallsChurchtz)
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
# We experienced an odd failure, which I interpret as some kind of reset occurring on their 
# website immediately after midnight. This wouldn't surprise me. At the website end they have  
# to somehow accommodate a change in the data availability, and this could be accompanied by
# a reset of the web server, which could reset all the http connections. 
#
# I'm now adding a delay to be sure we don't wake up until well past midnight
#
sleeptime = (midnight-now).total_seconds()+midnight_delay

# figure out what time she wants to play pickleball

desired_times = desired_times_dict[session]
reservation_time = desired_times[0].split("-")[0].rstrip() # first time on earliest desired time

# need to know if we have to make more than one reservation, parse the session id
SessionParts = session.split('.');

Duration = int(SessionParts[0])/10

# A duration longer than 1.5 hours requires two reservations
if Duration > 1.5:
    nReservations = 2

# more useful to have the duration as a string
Duration = str(Duration)

# this is to add "dry run" to the message, if appropriate
drs=""
if dryrun:
    drs=" (dry run)"

reservemessage = 'Reserving '+str(nReservations)+' court slots for: '+str(month)+'/'+str(day)+" for "+Duration+" hours, times: "+str(desired_times)+drs 
record(reservemessage)
sendtext(reservemessage)

if not(immediate):
    record("Time is now "+str(now)+" Falls Church time. Sleeping for "+str(sleeptime)+" seconds, until midnight, Falls Church time.");
    time.sleep(sleeptime)
    now = datetime.now(FallsChurchtz)
    tomorrow = now+timedelta(days=1)
    if verbose: 
        record("Awoke feeling refreshed, let's get to work! Time is now "+str(now)+" Falls Church time, tomorrow is "+str(tomorrow))
else:
    record("Time is now "+str(now)+" Falls Church time. Immediate is set, so not sleeping.")

# now set up to bring up some web pages to scrape
options = Options()
if args.Headless:
    options.add_argument("--headless")
else:
    options.add_argument('--width='+width)
    options.add_argument('--height='+height)

service = Service(log_path=os.path.devnull)

driver = webdriver.Firefox(options=options, service=service)
 
reservation_done = False
available_time = [None, None]
reserved_time = [None,None]
tables = [None, None]

try:
    driver.get(web_site)
    WebDriverWait(driver,10000).until(EC.visibility_of_element_located((By.TAG_NAME,'body')))
    
    # ensure that the page is stable, and that the desired "tennis court" element is present
    to=0
    found=False
    while to < 3 and not found:
        try:
            found = waitelement('/html/body/div/div/div/div/div[2]/section/div/a[5]')
        except TimeoutError:
            to += 1

    if nReservations > 1:
        script = "window.open(" + '"' + web_site + '"' + ")"
        driver.execute_script("window.open(" + '"' + web_site + '"' + ")")
        time.sleep(secs)

    handles = driver.window_handles
    driver.switch_to.window(handles[0])
    
    if len(handles) > 2:
        error("Too many handles")

    if nReservations > 1:                                 
        driver.switch_to.window(handles[1])
        tables[1] = fetch_tables(day, month, reservation_time)
        driver.switch_to.window(handles[0])
            
    tables[0] = fetch_tables(day, month, reservation_time)
    
    # now trying to find a court with availability at the desired time(s)
    first_time = second_time = None

    # check against each of the preferences we were give for a court and type at the indicated time 
    for p in range(len(court_prefs)):
        available_time[0] = search_atable(tables[0],court_prefs[p],desired_times[0])
        if available_time[0]: 
            first_time = available_time[0].text
            if nReservations >1:
                driver.switch_to.window(handles[1])
                available_time[1] = search_atable(tables[1],court_prefs[p],desired_times[1])
                second_time = available_time[1].text
                driver.switch_to.window(handles[0])
        if first_time and second_time: 
            break #for loop over possible prefs

    if not(first_time):
        error("Could not find a time slot to reserve")

    if nReservations > 1 and not(second_time):
        error("Could not find the second required court time")

    record("Will make a reservation for "+first_time)
    if nReservations > 1:
        record("Will make a second reservation for "+second_time)
except Exception as e:
    error("Exception during table search stage:"+str(e))

### code to make the resevations:

record("Trying to make reservation(s)") 
try:
    make_reservation(available_time[0], usernames[0], passwords[0])
except Exception as e:
    error("Looks like Liz already has a reservation pending")

if nReservations > 1:
    record("Trying to make a second reservation") 
    driver.switch_to.window(handles[1])
    try: 
        make_reservation(available_time[1], usernames[1], passwords[1])
    except Exception as e:
        error("Looks like Sue already has a reservation pending")
 
record("Reservation process was successful")

sendresultemail("Reservation was successful")
sendtext("Reservation was successful")
##### cleanup

driver.switch_to.window(handles[0])
driver.close()

if nReservations > 1:
    driver.switch_to.window(handles[1])
    driver.close()

driver.quit()


