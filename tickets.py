### Original script by @Tom-stack3 (github repo Tom-stack3/ticketsFinder)
### Forked by me @benjamin-elusers (github repo benjamin-elusers/ticketsFinder)
### Edited on 01/02/2022
import datetime
from selenium import webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sys
import getopt
import logging as log

tickets_url = 'https://hermon.pres.global/vouchers'

#https://stackoverflow.com/questions/2183233/how-to-add-a-custom-loglevel-to-pythons-logging-facility/35804945#35804945
def addLoggingLevel(levelName, levelNum, methodName=None):
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present 

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')

    """
    if not methodName:
        methodName = levelName.lower()

    if hasattr(log, levelName):
       raise AttributeError('{} already defined in logging module'.format(levelName))
    if hasattr(log, methodName):
       raise AttributeError('{} already defined in logging module'.format(methodName))
    if hasattr(log.getLoggerClass(), methodName):
       raise AttributeError('{} already defined in logger class'.format(methodName))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)
    def logToRoot(message, *args, **kwargs):
        log.log(levelNum, message, *args, **kwargs)

    log.addLevelName(levelNum, levelName)
    setattr(log, levelName, levelNum)
    setattr(log.getLoggerClass(), methodName, logForLevel)
    setattr(log, methodName, logToRoot)

addLoggingLevel('CHECK', log.WARNING + 5)
addLoggingLevel('SUCCESS', log.CRITICAL + 5)

def usage():
    print('<program.py> -m integer -e example@gmail.com -w 20 -v')
    print('-m minutes to run the program')
    print('-e email to send alerts to')
    print('-w waiting time in seconds between unsuccessful searches')
    print('-v verbose output (INFO)')
    print('-d debug output (DEBUG + INFO)')
    print('-h usage of the program')

def ask_tmax():
    tmax = input("Time to keep checking (in minutes):")
    while not tmax.isnumeric() or int(tmax) > 48 * 60:
        tmax = input("Time to keep checking (in minutes):")
    return tmax

def ask_emails():
    emails= input("Email addresses to send alerts to (separated by commas):\n")
    recipients = [email.strip() for email in emails.split(',')]
    return recipients

def get_input_params(argv = sys.argv[1:]):
    maxtime = None
    recipients = None
    waiting = 20
    try:
        opts, args = getopt.getopt(argv, "m:e:w:vhd",["minutes=","emails=","search_waiting=20",'debug','verbose','help'])
    except:
      print("Error")
    # here we get the params to run with.
    for opt, arg in opts:
        if opt in ['-m', '--minutes']:
            maxtime = arg
        elif opt in ['-e', '--emails']:
            recipients = [email.strip() for email in arg.split(',')]
        elif opt in ['-w', '--search_waiting']:
            waiting = arg
        elif opt in ['-d', '--debug']:
            log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
            log.info("Extremely verbose output.")
        elif opt in ['-v', '--verbose']:
            log.basicConfig(format="%(levelname)s: %(message)s", level=log.INFO)
            log.info("Verbose output.")
        elif opt in ['-h', '--help']:
            usage(); exit();

    log.basicConfig(format="%(levelname)s: %(message)s", level=log.WARNING)

    if( maxtime == None): 
        maxtime=ask_tmax()
    if( recipients == None): 
        recipients=ask_emails()

    print("="*15+"  INPUTS  "+"="*15)
    print (f"running until {maxtime} minutes")
    print (f"sending to {recipients}")
    print (f"Waiting {waiting} sec. between searches ")
    print("="*40)
    print(" "*40)
    return maxtime,recipients,waiting;

# we get the html of the page using selenium.
# we use selenium inorder to load the page after the javascript had already ran and the calendar shows up.
# then we use BeautifulSoup to work easily with the html loaded.
def get_soup_page(url,hide=True,maxload=10,verbose=False):
    opts = Options()
    opts.headless = hide
    if(hide==True):
        assert opts.headless  # Operating in headless mode
    
    browser = Firefox(options=opts)
    wait = WebDriverWait(browser, maxload)
    
    log.info(" * Loading reservation page")
    browser.get(url)
    # Make sure the calendar has loaded succesfully with the current day
    try:
        class_week="v-calendar-weekly__day"
        calendar_week = wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_week)))
        log.info(" ** Calendar [READY]")

        class_today="v-present"
        calendar_today = wait.until(EC.presence_of_element_located((By.CLASS_NAME, class_today)))
        log.info(" ** Today [READY]")

    except TimeoutException:
        log.error("Loading ticket reservation page took too much time!")
    soup = BeautifulSoup(browser.page_source, "html.parser")
    browser.close()
    return soup


def find_available():
    today = datetime.date.today()
    soup = get_soup_page(tickets_url)
    dates_available = []   
    dates_open = []
    
    for day_index in range(1, 5 * 7):
        date = today + datetime.timedelta(days=day_index)  
        # format: 2021-02-06
        date_in_format = date.strftime("%Y-%m-%d")
        day_month= date.strftime("%d-%b")
        search_result = soup.find("div", {"data-date": date_in_format})
        # if the day doesn't exist - means we got to the end of the calendar.
        if search_result is None:
            continue
        if 'אזל' in str(search_result):
            dates_open.append(day_month)
            continue
        elif 'יש' in str(search_result):
            dates_open.append(day_month)
            log.success('===>>> FOUND TICKETS !!! ('+what_time(True)+') <<<===')
            dates_available.append(date_in_format)
        else:
            log.warning(date_in_format+' failed')
            log.warning("Search result:\n"+search_result)
    notickets="|".join(map(str,dates_open))
    log.info(f" * Open dates without available tickets: {notickets}\n")
    return dates_available,dates_open

def search_counter(n,nfound,increment=5):
    increment = abs(int(increment))
    if( n == 1 ):
        on=what_time(noday=False)
        log.check(f"searched for the first time... {on}")
    elif( n % increment == 0 ):
        at=what_time()
        log.check(f"searched {n} times already... ({nfound} successful searches) {at}")

# we generate the content of the email.
# we send a list of the dates available, the link to buy the tickets,
# and the current time and date
def email_content(dates_available,dates_open):
    today = datetime.datetime.now()
    text = 'Checked at ' + today.strftime("%X %d/%m/%Y") + "\n"
    text += 'Opened dates:\n'
    text += "\n".join(map(str,dates_open)) + "\n"
    text += 'Available dates:\n'
    text += "\n".join(map(str,dates_available)) + "\n"
    text += '\n\nlink to buy: ' + tickets_url + "\n"
    return text


# send the email with the available tickets to the recipients
def send_mail(recipients, dates_available, dates_open):
    body = email_content(dates_available,dates_open)
    msg = MIMEMultipart()

    # change this to an email you want the alerts of the bot to be sent from
    email_address = 'example@gmail.com'
    # change this to the google 2FA password for this program email you chose (should be 16 characters )
    email_pass = 'password_2fa_google'
    

    msg['Subject'] = 'Found available tickets to Hermon!'
    msg['From'] = email_address
    msg['Bcc'] = ', '.join(recipients)

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(email_address, email_pass)
    server.send_message(msg)
    server.quit()

### GENERAL FUNCTIONS
def what_time(noday=True):
    if(noday == True):
        return time.strftime('%H:%M:%S (%Z)')
    return time.strftime('%H:%M:%S (%Z) on %d.%m.%Y (%A)')

def elapsed(t0,t1):
    return int((t1 - t0))

def tominutes(t):
    mn=int((t/60))
    return f"{mn} min."

def tohours(t):
    hr=int((t/60/60))
    mn=int(((t/60)%60))
    return f"{hr}h.{mn}min."

def checkpoint_time(t0,tlast):
    tnow=time.time()
    elapsed_time=elapsed(t0,tnow)
    dt_check=elapsed(tlast,tnow)
    if(dt_check > 600 or tlast==-1):
        spent=f"{elapsed_time}s"
        if( elapsed_time >= 300 and elapsed_time < 3600):
            spent = tominutes(elapsed_time)
        elif( elapsed_time >= 3600 ):
            spent = tohours(elapsed_time)
        log.check(f"___running for {spent}___")
        tlast=tnow
    return(tlast)

def main():
    
    (minutes_to_run,recipients,waiting_search)=get_input_params(sys.argv[1:])
    # the time to wait before searching for tickets again after finding.
    # in seconds
    wait_time_after_finding = 600

    # the time to wait after searching for tickets (and didn't find) before searching again.
    # in seconds
    wait_time_after_search = waiting_search
    n_search=0
    n_success=0
    print("--- started search ---")
    
    start_time = time.time()
    elapsed_time = 0
    end_time = start_time + 60 * int(minutes_to_run)
    t_check=-1

    while time.time() < end_time:
        (dates_available,dates_open) = find_available()
        n_search+=1
        search_counter(n_search,n_success,5)
        t_check=checkpoint_time(start_time,t_check)
        # if list not empty, means we found some tickets
        if dates_available:
            n_success+=1
            log.success("dates_available ["+" ".join(map(str,dates_available))+"]")
            send_mail(recipients, dates_available, dates_open)
            # if there is no time left, we can save the wait
            if time.time() + wait_time_after_finding > end_time:
                break
            time.sleep(wait_time_after_finding)
        else:
            # if there is no time left, we can save the wait
            if time.time() + wait_time_after_search > end_time:
                break
            time.sleep(wait_time_after_search)
    print("\n--- search ended ---\n")
    print("run ended after ", tohours(elapsed(start_time,time.time())))

if __name__ == '__main__':
    main()
