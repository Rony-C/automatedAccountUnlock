from __future__ import print_function
from selenium import webdriver
from selenium.webdriver.common.by import By
import time, datetime, yaml, os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

destURL = "https://admin.gigable.app/admin/"

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '126CvfGaIcCZLgzEcFNx7bENRt_brsCddZ-LcozZaxiU'
RANGE_NAME = 'Sheet1!A2:B'

# Store IDs that need to be reactivated
userIds = []

# Open Chrome and login page
driver = webdriver.Chrome()
driver.get(destURL)

def connectGoogleSheet():
    print("Connecting to Google Sheets...")
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                # Created from Google Dev portal
                '/Users/rony/vs_code/python/work_files/reactivateFLAccount/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('sheets', 'v4', credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                    range=RANGE_NAME).execute()
        values = result.get('values', [])

        if not values:
            print('No data found.')
            return
        
        for row in values:
            # Checks if reactivation date has passed
            # TODO: Check if cell is empty
            date = row[1]
            date_format = datetime.datetime.strptime(date,"%d/%m/%Y")
            unix_time = datetime.datetime.timestamp(date_format)
            if(unix_time <= time.time()):
                # Adds ID to list if it has
                userIds.append(row[0])
        print(f"{len(userIds)} account(s) to reactivate found...")
    except HttpError as err:
        print(err)
    print("Connected")

def loginToGigableAdmin():
    with open("/Users/rony/vs_code/python/work_files/reactivateFLAccount/credentials.yml") as f:
        login = f.read()
    
    my_cred = yaml.load(login, Loader=yaml.FullLoader)

    loginEmail, loginPassword = my_cred["user"], my_cred["password"]

    # Find login button and click 
    loginButton = driver.find_element(by=By.CSS_SELECTOR, value="body > div > form > button")
    loginButton.click()

    # Find username and password fields
    userName = driver.find_element(by=By.CSS_SELECTOR, value="#loginId")
    password = driver.find_element(by=By.CSS_SELECTOR, value="#password")

    # Enter username and password
    userName.send_keys(loginEmail)
    password.send_keys(loginPassword)

    # Find login button and click
    loginWithDetails = driver.find_element(by=By.CSS_SELECTOR, value="button")
    loginWithDetails.click()

def toggleActive():
    # Find the activate user button
    toggleActiveButton = driver.find_element(by=By.CSS_SELECTOR, value="#block-user-form > div > button")
    # Click the button
    toggleActiveButton.click()
    # Confirm activate user in alert pop up
    driver.switch_to.alert.accept()

def isBlocked(id):
    driver.get(f"https://admin.gigable.app/admin/users/{id}")

    isBlocked = driver.find_element(by=By.CSS_SELECTOR, value="body > div > div > section.content.container-fluid > section > div.callout.callout-danger")
    # If they're blocked, toggle them active
    if isBlocked:
        toggleActive()
        time.sleep(4)
        print(f"User account {id} reactivated")

def checkIfActive(id):
    driver.get(f"https://admin.gigable.app/admin/users/{id}")
    try:
        # Checks if user is currently blocked
        isBlocked(id)
    # If the user is active print to console
    except Exception:
        print(f"Account {id} already active")

def checkIDs():
    for id in userIds:
        checkIfActive(id)

def end():
    # Close browser window and quit program
    driver.close()
    driver.quit()
    print(f"Please delete the rows for {userIds} from the sheet: https://docs.google.com/spreadsheets/d/126CvfGaIcCZLgzEcFNx7bENRt_brsCddZ-LcozZaxiU/edit#gid=0")

connectGoogleSheet()
#Remove IDs and dates from list
loginToGigableAdmin()
checkIDs()
end()