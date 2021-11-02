mcbot is a selenium web bot that signs a user up to the microcenter waitwhile list

# Installation

* Python3 is required to run the script.
* Some dependencies are required for the python script to run. Install these via:
  
  ```
  pip install -r requirements.txt
  ```
  
* Firefox is required. The latest version will probably work.



# Setup

To set the bot up, simply edit the run.bat and fill out your first name, last name, and phone number in the first three lines of the file. You may also change the amount of different browsers that are opened by changing the last line:

```
if %count% neq 6 goto loop
```

to:

```
if %count% neq n goto loop
```

where n is the amount of browsers you desire.



# Testing

There is also a provided testrun.bat file that runs on an alternate waitlist that should have the same general structure as the microcenter waitlist. A site has the same general structure if it consists of the same buttons, with the same text on them, that are pressed in a normal signup process (Join -> Service (Build own pc, repair, etc.) -> Party size -> form fillout). The form fillout process requires that only the first name, last name, and phone number are requested from the person signing up.



I have provided a generic test batch file that uses a dummy phone number that likely is not active. 
