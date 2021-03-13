from selenium import webdriver
import selenium.webdriver.chrome.options
import selenium.webdriver.firefox.options
from selenium.webdriver.common.proxy import Proxy, ProxyType
import time
import datetime
import random
import sys
import logging
import math
import os
from signal import signal, SIGINT, SIGTERM, SIGSEGV
from filelock import Timeout, FileLock
from Browser import Browser
from User import User

logging.basicConfig(filename="log.log", format="%(asctime)s %(message)s", level=logging.INFO)

MIN_TIME = 0.1 #Minimum time in seconds bot must take before joining
SITE_URL = "https://v2.waitwhile.com/welcome/microcenterstlo"

  
START_BOT_TIME = 45900   #6:45 am universal time
END_BOT_TIME = 57600     #10:00 am universal time

DRIVER_DIR = "./driver/"
CHROME_AGENTS_FILE = "chrome_agents.txt"
FIREFOX_AGENTS_FILE = "firefox_agents.txt"
RANDOM_REFRESH = 3+(4*random.random())

MEAN_BROWSER_DURATION = 180  #Max seconds before new browser created
START_BROWSER_STEP = 24     #Seconds before another browser (running on different thread) can start

# Not functional on Firefox
PROXY_ON = True

HEADLESS = False

#XPath to buttons
JOIN_XPATH = "//button"
SERVICE_XPATH = "//button"
NEXT_XPATH = "//button"
FIRST_XPATH = "//*[@id=\"name02\"]"
LAST_XPATH = "//*[@id=\"name03\"]"
PHONE_XPATH = "//*[@id=\"phone01\"]"
CONFIRM_XPATH = "//button"

#Assign ID between 100,000 - 999,999
BOT_ID = str(100000 +  math.floor(900000 * random.random()))

#Override some globals if needed
if ("--test" in sys.argv):
  SITE_URL = "https://v2.waitwhile.com/welcome/tg5azh"
  START_BOT_TIME = 0
  END_BOT_TIME = 200000

if ("--headless" in sys.argv):
  HEADLESS = True

def main():  
  #Calculate duration this isntance of browser will last
  browserDuration = (0.5 + random.random()) * MEAN_BROWSER_DURATION

  #Get information from user/cmdline arguments
  firstName = ""
  lastName = ""
  phoneNum = ""

  if (len(sys.argv) != 1):
    try:
      for i in range(0, len(sys.argv)):
        if sys.argv[i] == "--first":
          firstName = sys.argv[i+1]
        elif sys.argv[i] == "--last":
          lastName = sys.argv[i+1]
        elif sys.argv[i] == "--phone":
          phoneNum = sys.argv[i+1]
    except:
      print("Error reading commandline arguments")
      return

  else:
    credsConfirmed = False
    while (not credsConfirmed):
      (firstName, lastName, phoneNum) = getUserCreds()
      credsConfirmed = confirmCreds(firstName, lastName, phoneNum)

  #Create new user with provided credentials
  user = User(fn=firstName, ln=lastName, pn=phoneNum)

  #Bot is active 6:25 AM - 10:00 AM
  waitForStartTime()

  #Create browser objects to use
  activeBrowser = getBrowser()
  #Track time browser created
  t = time.time()
  
  logging.info("[" + BOT_ID + "]" + " Browser created")

  addDriver(activeBrowser)

  returnCode = signupProcess(activeBrowser.getDriver(), user, t, browserDuration)
  while returnCode != 0:
    #Waited too long for element, do signup process again
    if returnCode == -1:
      logging.info("[" + BOT_ID + "]" + " Waitlist not open. Refreshing.")
      activeBrowser.getDriver().refresh()
      returnCode = signupProcess(activeBrowser.getDriver(), user, t, browserDuration)
    #Browser open too long
    elif returnCode == -2:
      logging.info("[" + BOT_ID + "]" + " Browser stale, getting new.")
      
      #Delete old browser and get new one
      activeBrowser.getDriver().quit()
      activeBrowser = getBrowser()
      addDriver(activeBrowser)

      #Get new current time
      t = time.time()

      #Start signup process again
      returnCode = signupProcess(activeBrowser.getDriver(), user, t, browserDuration)

  return

'''
signupProcess(d, u, t)

param : d : selenium driver
        u : user object with credentials
        t : time (should be when browser first opened)
        mt : max time browser can be open

return : 0 to indicate success
         -1 to indicate waiting too long for element
         -2 to indicate browser has been open too long

desc :

    Performs the sign up process for the user
    on the specified web driver.

'''
def signupProcess(d, u, t, mt):
  #Join when open, refresh if not
  joinBox = waitForRelativeXPath(d, JOIN_XPATH, contains="Join waitlist")
  if (isRunningTooLong(t, mt)):
    return -2
  if (joinBox == None):
    return -1
  while (not (joinBox.is_enabled())):
    logging.info("[" + BOT_ID + "]" + " Join not enabled. Refreshing")
    d.refresh()
    joinBox = waitForRelativeXPath(d, JOIN_XPATH, contains="Join waitlist")
    if (isRunningTooLong(t, mt)):
      return -2
    if (joinBox == None):
      return -1
  
  clickElement(d, joinBox)
  logging.info("[" + BOT_ID + "]" + " Join button clicked")
  #Start timer
  formFillTime = time.time() 
  
  #Click build own pc section
  buildOwn = waitForRelativeXPath(d, SERVICE_XPATH, contains="Build Your Own")
  if (isRunningTooLong(t, mt)):
    return -2
  if (buildOwn == None):
    return -1

  clickElement(d, buildOwn)
  logging.info("[" + BOT_ID + "]" + " Service button clicked")

  #Click next button
  nextButton = waitForRelativeXPath(d, NEXT_XPATH, contains="Next")
  if (isRunningTooLong(t, mt)):
    return -2
  if (nextButton == None):
    return -1

  clickElement(d, nextButton)
  logging.info("[" + BOT_ID + "]" + " Next button clicked")
  
  #Enter credentials into boxes
  firstNameBox = waitForRelativeXPath(d, FIRST_XPATH)
  if (isRunningTooLong(t, mt)):
    return -2
  if (firstNameBox == None):
      return -1
  firstNameBox.send_keys(u.getFirst())

  lastNameBox = waitForRelativeXPath(d, LAST_XPATH)
  if (isRunningTooLong(t, mt)):
    return -2
  if (lastNameBox == None):
    return -1
  lastNameBox.send_keys(u.getLast())

  phoneBox = waitForRelativeXPath(d, PHONE_XPATH)
  if (isRunningTooLong(t, mt)):
    return -2
  if (phoneBox == None):
    return -1
  phoneBox.send_keys(u.getPhone())

  logging.info("[" + BOT_ID + "]" + " Form filled out")

  #Confirm place in queue
  confirmButton = waitForRelativeXPath(d, CONFIRM_XPATH, contains="Confirm")
  if (isRunningTooLong(t, mt)):
    return -2
  if (confirmButton == None):
    return -1
# waitForMinTime(formFillTime)

  confirmButton.click()
  logging.info("[" + BOT_ID + "]" + " Confirm button clicked.")
  
  #Forces shutdown of browsers who did not get to completion page first
  checkForCompletion(d)
  
  #Wait 5 minutes before closing browser
  time.sleep(300)
  d.quit()

  return 0

'''
getUserCreds()

param : none

return : first name string
         last name string
         phone number string

desc :

    Gets the first name, last name, and phone number
    as entered by the user.

'''
def getUserCreds():
  firstName = input("Enter first name: ")
  lastName = input("Enter last name: ")
  phoneNum = input("Enter phone number (numbers only): ")
 
  logging.info("[" + BOT_ID + "]" + " User entered:", firstName, lastName, phoneNum)
  
  return (firstName, lastName, phoneNum)

'''
confirmCreds(fname, lname, pn)

param : fname : string of first name
        lname : string of last name
        pn    : string of phone number

return : bool

desc :

    Confirms the entered credentials to the user and returns
    a true if the user confirms these are the correct 
    credentials or false if the user did not confirm it.

'''
def confirmCreds(fname, lname, pn):
  print("=======================================")
  print("Please confirm your credentials:")
  print("First name:", fname)
  print("Last name:", lname)
  print("Phone Number:", pn)
  print("=======================================")
  print("Are these correct? [y/n]")
  response = input().lower()
  return (response == "y")

'''
verifyClick(elem)

param : elem : element to click

return : none

desc:

    Checks to see if the webpage has removed the
    clickable element. If it has not been removed,
    it gets clicked again and rechecked. If it is
    already removed from page, verification has completed
    and normal program continues.

'''
def verifyClick(elem):
  #Assuming button not clicked at start
  buttonClicked = False

  while (not buttonClicked):
    try:
      #Trigger exception if element doesnt exist
      dummy = elem.is_displayed()
      #Click again if exception does not occur
      elem.click()
    #Exception if element no longer exists
    except:
      buttonClicked = True

  return

'''
clickElement(e)

param : d : selenium driver
        e : element

return : none

desc :

      Clicks the element provided.
      
'''
def clickElement(d, e):
  isClicked = False
  while (not isClicked):
    #Dont look at this hideous code
    try:
      e.click()
      isClicked = True
    except:
      try:
        d.execute_script("argument[0].click();", e)
        isClicked = True
      except:
        time.sleep(0.01)
        continue
 
'''
waitForXPath(d, x)

param : d : selenium web driver (open chrome page)
        x : xpath to element

return : Selenium WebElement

desc :

    Searches for a selenium web element by the given
    XPath. If it is not found, the search continues until
    it is found. Once found, the element is returned.

'''
def waitForXPath(d, x):
  #Start timer
  t = time.time()

  found = False
  while (not found):
    try:
      if ((time.time() - t) > 6):
        return None

      elem = d.find_element_by_xpath(x)
      found = True
    except:
      time.sleep(0.01)
      continue

  return elem

'''
waitForRelativeXPath(d, x, contains=None, text=None)

param : d : selenium web driver (open chrome page)
        x : relative xpath to element
        contains : the text of the element but have this within
        text : the text of the element must have text equal to this

return : Selenium WebElement

desc :

    Searches for selenium web elements by the given
    XPath. The multiple returned elements are then filtered
    through checks on their .text property. They must have either
    their text fully equal to the text argument passed in or, if
    not provided, it must have the contains argument text somewhere
    in its text property, it does not have to match fully. If no
    contains or text argument is provided, the first element found
    is returned.

'''
def waitForRelativeXPath(d, x, contains=None, text=None):
  #Start timer
  t = time.time()

  found = False
  foundElement = None
  while (not found):
    try:
      if ((time.time() - t) > RANDOM_REFRESH):
        return None

      elems = d.find_elements_by_xpath(x)
      for e in elems:
        if (text != None):
          if (e.text.lower() == text.lower()):
            foundElement = e
            found = True
        elif (contains != None):
          if (contains.lower() in e.text.lower()):
            foundElement = e
            found = True
        else:
          foundElement = e
          found = True
    except:
      d.implicitly_wait(0.01)
      continue

  return foundElement
  
'''
waitForMinTime(t)

param : t : starting time

return : none

desc :

    Ensures that the delta between the current time
    and the time passed, t, is at least MIN_TIME .

'''
def waitForMinTime(t):
  currTime = time.time()
  while ((currTime - t) < MIN_TIME):
    currTime = time.time()

  return

'''
waitForStartTime()

param : none 

return : none

desc :

    The bot will be stuck in this loop until
    the current time is within range of the bot's
    start and stop times.

'''
def waitForStartTime():
  hr = int(datetime.datetime.utcnow().strftime("%H"))
  mn = int(datetime.datetime.utcnow().strftime("%M"))
  scs = int(datetime.datetime.utcnow().strftime("%S"))
  totalSecs = (hr*3600) + (mn * 60) + scs

  #While current time outside of range, idle bot
  while (not ((totalSecs < END_BOT_TIME) and (totalSecs >= START_BOT_TIME))):
    logging.info("[" + BOT_ID + "]" + " Bot not within time, waiting.")
    time.sleep(2)

    hr = int(datetime.datetime.utcnow().strftime("%H"))
    mn = int(datetime.datetime.utcnow().strftime("%M"))
    scs = int(datetime.datetime.utcnow().strftime("%S"))
    totalSecs = (hr*3600) + (mn * 60) + scs

  return

'''
getUserAgents()

param : s : browser type string

return : array of string

desc :

    Read the user agents file and return all agents
    within.

'''
def getUserAgents(s):
  if (s == "Firefox"):
    fin = open(FIREFOX_AGENTS_FILE, "r")
  elif (s == "Chrome"):
    fin = open(CHROME_AGENTS_FILE, "r")

  lines = fin.readlines()
  agents = []
  for i in range(0, len(lines)):
    lines[i] = lines[i].strip()
    if lines[i] != "":
      agents.append(lines[i])

  return agents

'''
getBrowser()

param : none

return : Browser object

desc :

    Generates a new Browser object.

'''
def getBrowser():
  #Currently only works on Firefox
  browserType = "Firefox"

  if browserType == "Firefox":
    tempOpt = selenium.webdriver.firefox.options.Options()
    if (HEADLESS):
      tempOpt.set_headless()
#   userAgents = getUserAgents("Firefox")
#   tempOpt.add_preference("general.useragent.override", userAgents[round(random.random()*(len(userAgents)-1))])
  else:
    userAgents = getUserAgents("Chrome")
    tempOpt = selenium.webdriver.chrome.options.Options()
    tempOpt.add_experimental_option("excludeSwitches", ["enable-automation"])
    tempOpt.add_experimental_option('useAutomationExtension', False)
    tempOpt.add_argument("user-agent="+userAgents[round(random.random()*(len(userAgents)-1))])
    tempOpt.add_argument("window-size=1920,1080")
    tempOpt.add_argument("--disable-blink-features=AutomationControlled")
 
  if (PROXY_ON):
    tempOpt.add_argument("--proxy-server=" + "socks5://localhost:9050")

  b = Browser(opts=tempOpt, url=SITE_URL, t=browserType)

  return b
 
'''
addDriver(b)

param : Browser

return : none

desc :

    Adds the driver to the Browser object.
    This will cause a browser to open.

'''
def addDriver(b):
  if (b.getType() == "Chrome"):
    d = webdriver.Chrome(options=(b.getOptions()))
  elif (b.getType() == "Firefox"):
    d = webdriver.Firefox(options=(b.getOptions()))
  
  d.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
  d.get(SITE_URL)
  
  b.setDriver(d)

  return

'''
isRunningTooLong(t, mt)

param : t : time to check
        mt : max time allowed

return : bool

desc :

    Determines if the delta between the time, t, 
    and the current time is greater than the 
    max browser duration. Returns True if so,
    False if not

'''
def isRunningTooLong(t, mt):
  currTime = time.time()

  if ((currTime-t) > mt):
    return True
  else:
    return False

'''
enterStarterQueue()

param : none

return : none

desc :

    Browser does not start until it can get the
    starter lock. This process ensures that the 
    IP addresses of each browser are not similar.

'''
def enterStarterQueue():
  lock = FileLock("starter.lock")
  with lock:
    #Stagnate starts to avoid similar ips
    time.sleep(START_BROWSER_STEP)

'''
enterFinisherQueue()

param : b : button to click
        d : selenium web driver

return : 0 if successful signup
         1 if already signed up
        -1 if bot detected

desc :

    Attempts to be the browser to confirm an entry
    into a queue. 

'''
def enterFinisherQueue(b, d):
  logging.info("[" + BOT_ID + "]" + " Attempting to acquire finisher lock.")
  lock = FileLock("finisher.lock")
  with lock:
    logging.info("[" + BOT_ID + "]" + " Finisher lock acquired.")
    f = open("finisher.txt", "r")
    contents = f.read().strip()
    f.close()
    if (contents != "DONE"):
      logging.info("[" + BOT_ID + "]" + " No browser entered yet. Confirming place in queue.")
      b.click()
      t = time.time()  #Track when button was clicked for logging.")
      detected = checkIfDetected(b, d)
      if (not detected):
        logging.info("[" + BOT_ID + "]" + " Browser not detected. Place in queue confirmed.")
        f = open("finisher.txt", "w")
        f.write("DONE")
        f.close()
        return 0
      else:
        logging.info("[" + BOT_ID + "]" + " Browser was detected.")
        return -1
    else:
      return 1


'''
checkIfDetected(b, d)

param : b : confirmation button
        d : web driver

return : bool

desc :

    Returns true or false based on whether
    the bot detection was triggered for the 
    browser instance.

'''
def checkIfDetected(b, d):
  t = time.time()
  try:
    while True:
      #If button is disabled for more than CONFIRM_BUTTON_WAIT seconds, you were detected
      if (not b.is_enabled()):
        time.sleep(CONFIRM_BUTTON_WAIT)
        if (not b.is_enabled()):
          return True
      #If it has taken too long, you were detected
      if (time.time() - t > 2*CONFIRM_BUTTON_WAIT):
        return True
  #Exception means button no longer visible
  except:
    #Check if on completion page
    if ("complete" in d.current_url):
      return False
#      t = time.time()
#      time.sleep(1)
#      #If still on completion page after second, you are good
#      if ("complete" in d.current_url):
#        return False
#      else: 
#        return True
    #Failure if not
    else:
      return True


'''

'''
def checkForCompletion(d):
  while ("complete" not in d.current_url):
    f = open("complete.txt", "r")
    if "DONE" in f.read():
      d.quit()
      f.close()
      return
      
  logging.info("[" + BOT_ID + "]" + " Bot entered into queue.")
  f = open("complete.txt", "w+")
  f.write("DONE")
  f.close()
  return
    
    
  return
  
if __name__ == "__main__":
  main()
