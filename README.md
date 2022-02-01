Credits to [@Tom-stack3](https://github.com/Tom-stack3) for the initial script [Tom-stack3/ticketsFinder](https://github.com/Tom-stack3/ticketsFinder)
This prokect was simply my personal touch to give a cosmetic improvement to the text output from the program.

# Tickets Finder
*ticketsFinder* is a Python script that looks for available tickets for Mount Hermon
and sends an alert in Real-Time to all the emails interested.\
It looks for available tickets in all the dates available for sale.

[EDIT 01/02/22 by @github/benjamin-elusers]
## How it works: 
STEP 0
Upon execution, the script takes as arguments:
 - (option m) how many minutes the program should be running
 - (option e) the email addresses to send alerts to
 - (option t) how much time the program will wait between two unsuccessful searches

If no arguments is provided, the script will ask user input for each.

STEP 1
After giving the needed parameters, the script starts searching for tickets.
First, it loads the ticket reservation page in Firefox using selenium.webdriver (*requires geckodriver installed*).
Second, it waits for loading the calendar with the current date.

STEP 2
With beautifulSoup, it parses the HTML content to find the dates available for sale.
Then we check whether the date is open and if there is available tickets (contains the string "**יש**").

STEP 3.1
Every 20 seconds, we reload the HTML tickets reservation page to check again for dates with tickets for sale.

STEP 3.2
If there are available tickets, the dates are stored.
An email will be sent giving which dates were open for sale and which had available tickets.
Then, it waits 10 minutes before checking again for available tickets.

## Setup before run:

### Installations: ###
**Libraries used**:  
1. time
2. smtplib
3. getopt
4. logging
5. selenium - ```python -m pip install selenium```
6. Beautiful Soup - ```python -m pip install beautifulsoup4```

**Selenium setup:**
Firefox needs the be installed and relatively up-to-date.
* Install or update Firefox with a recent version (less than 2 years old)
* Install selenium.webdriver [geckodriver](https://github.com/mozilla/geckodriver/releases/tag/v0.29.0) \
  After installing/extracting the geckodriver executable/binaries, add its path to the the system paths \
  *e.g.* On linux you can execute in the terminal: `export=$PATH:"/path/to/geckodriver"` \
  This is only valid for the instance of the terminal it was run.\
  Add it to the custom configuration file for your session (~/.bashrc) for having it loaded by default.

  On Windows, environment variables are accessed from “Advanced system settings” on the left of the “System” control panel.
  *from: https://www.mathworks.com/matlabcentral/answers/94933-how-do-i-edit-my-system-path-in-windows*
  
  How you access and edit the environment variables depends on the version of Windows you are using.\
  **Windows 10 (Also Windows 8.1):**
    1. Right-click on the Start Button
    2. Select “System” from the context menu.
    3. Click “Advanced system settings”
    4. Go to the “Advanced” tab
    5. Click “Environment Variables…”
    6. Click variable called “Path” and click “Edit…”
    
  Now choose one of the PATHs shown, (the python one is prefered) and just copy geckodriver.exe there.
  
 ### Code setup: ###
 The program sends alerts through smtp using gmail server.\
 You might need 2 Factor Authentification (2FA) password for the program to be able to send emails. \
 Setting up 2FA password for the program:
  * Go to your Google Account. 
  * Click on your profile.
  * Go to *Manage your Google account* -> *Security* -> *Signing in to Google: App Passwords*
  * You might be asked your personal google password. Authenticate yourself.
  * Click on "Select app" dropdown menu
  * Generate a password for *ticketsFinder* and save it somewhere
       
 In ```Line 255``` and ```Line 257``` fill a valid gmail address from where the alerts are sent.\
 Change those lines:
 ```python
    # change this to an email you want the alerts of the bot to be sent from
    email_address = 'example@gmail.com'
    # change this to the password for the 2FA password generated
    email_pass = 'google_2FA_password_example'
 ```
 **Without a valid email and an authorized App password from Google, the script will fail to run!**
 
 ## Running the script: ##
 After the setup, just run the python script.\
 In the terminal:
 ```python tickets.py -m 1500 -e person1@email.com,person2@email.com,person3@email.com```
 
 If you want to input the parameters manually just run the script:
 ```python tickets.py```
 Enter the time in minutes you want the script to keep checking for tickets.
 Then enter the email addresses you want to be alerted seperated by a comma.
 
 ---
 
 Again all the credits to [@Tom-stack3](https://github.com/Tom-stack3) for the original idea
 I only tried to have a slightly improved text output.
 
 That's it!
 Have fun in skiing in the Hermon :)

## Run example:

![run example]()  
