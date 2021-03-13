import sys
import os
import subprocess

BOT_FILE = os.path.join("src", "bot.py")

def main():
  cleanFiles()

  first = ""
  last = ""
  phone = ""
  botCount = 0
  headless = False
  testing = False

  try:
    for i in range(0, len(sys.argv)):
      print(sys.argv[i])
      if (sys.argv[i] == "--first"):
        first = sys.argv[i+1]
      if (sys.argv[i] == "--last"):
        last = sys.argv[i+1]
      if (sys.argv[i] == "--phone"):
        phone = sys.argv[i+1]
      if (sys.argv[i] == "--count"):
        botCount = int(sys.argv[i+1])
      if (sys.argv[i] == "--headless"):
        headless = True
      if (sys.argv[i] == "--test"):
        testing = True

  except:
    print("Error reading commandline arguments.")

  if (first == ""):
    first = input("Enter first name: ")
  if (last == ""):
    last = input("Enter last name: ")
  if (phone == ""):
    phone = input("Enter phone number: ")
  if (botCount == 0):
    botCount = int(input("Enter bot count: "))

  pythonArgs = createArgs(first, last, phone, headless, testing)

  runBots(pythonArgs, botCount)

'''
cleanFiles()

param : none

return : none

desc :

    Deletes old files from past sessions of the bot. These files need
    to be cleaned for the bot to function properly.

'''
def cleanFiles():
  for f in os.listdir():
    if (f == "complete.txt"):
      os.remove(f)

  open("complete.txt", "w+").close()

'''
createArgs(first, last, phone, headless)

param : first : first name string
        last  : last name string
        phone : phone number string
        headless : whether browser runs headless
        testing : whether bot is running test mode

return : argument string

desc :

    Builds the argument string that will be added on to
    the normal "python3 src/bot.py" or similar call.

'''
def createArgs(first, last, phone, headless, testing):
  argString = ""

  if headless:
    argString += " --headless"
  if testing:
    argString += " --test"

  argString += " --first " + first
  argString += " --last " + last
  argString += " --phone " + phone

  return argString


'''
runBots(arg, count)

param : arg : arguments to add to script
        count : amount of time to run script

return : none

desc :

    Runs the python script with the arguments provided
    count times. These scripts are opened in the background,
    so a process killer may need to be used to stop them.

'''
def runBots(arg, count):
  print(arg)
  for i in range(0, count):
    try:
      argList = ["py", BOT_FILE]
      argList += arg.split(" ")
      subprocess.Popen(argList)
    except:
      argList = ["python3", BOT_FILE]
      argList += arg.split(" ")
      subprocess.Popen(argList)

main()
