
import time
import pymstodo
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from pymstodo import ToDoConnection
import datetime


# KIDUM
MAIN_URL = 'http://my.kidum.com/LoginRequired.aspx?Url=/students/'
TASKS_URL = 'http://my.kidum.com/students/Tasks.aspx'

USERNAME = ''
PASSWORD = ''
# TO DO
CLIENT_ID = ''
CLIENT_SECRET = ''


def main():
    error = False
    driver = webdriver.Firefox()
    driver.get(MAIN_URL)

    username = driver.find_element(By.NAME, 'UserName')
    username.send_keys(USERNAME)
    password = driver.find_element(By.NAME, 'Password')
    password.send_keys(PASSWORD)
    password.send_keys(Keys.RETURN)
    time.sleep(4)  # wait 4 sec

    driver.get(TASKS_URL)
    time.sleep(2)  # wait 2 sec

    print("Input number of meeting: ")
    meet_number = int(input())

    selector = driver.find_element(By.ID, 'sessionSelect')
    for option in selector.find_elements(By.TAG_NAME, 'option'):
        if str(meet_number) in option.text:
            option.click()
            break

    tasks_titles = driver.find_elements(By.CLASS_NAME, 'TaskTitle')
    tasks_tags = driver.find_elements(By.CLASS_NAME, 'Tags')

    todo = auth()  # get client authorization
    lists = todo.get_lists()
    tasks_list = lists[0]

    due_date = calc_due_date()

    for i in range(len(tasks_titles)):
        # build task
        curr_task = ""
        if tasks_tags[i].text == 'רשות':  # extra task
            curr_task = tasks_titles[i].text + " - רשות"
        else:
            curr_task = tasks_titles[i].text
        print("Current task: " + curr_task)

        # add task
        try:
            todo.create_task(curr_task, tasks_list.list_id, due_date)
        except Exception as e:
            error = True
            print(e)

    if error:
        print("-- ERROR --")
    else:
        print("-- SUCCESS --")

    driver.close()  # close browser
    driver.quit()  # close driver session


def auth():
    """
    authorization with microsoft account
    :return: microsoft to-do client object
    """
    auth_url = ToDoConnection.get_auth_url(CLIENT_ID)
    redirect_resp = input(f'Go here and authorize:\n{auth_url}\n\nPaste the full redirect URL below:\n')
    token = ToDoConnection.get_token(CLIENT_ID, CLIENT_SECRET, redirect_resp)
    return ToDoConnection(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, token=token)


def calc_due_date():
    """
    calculate closest day of kidum meeting
    :return: closest datetime
    """
    now = datetime.datetime.now().date()
    monday = next_weekday(now, 0)
    thursday = next_weekday(now, 3)

    return nearest([monday, thursday], now)


def nearest(items, pivot):
    """
    Finds the nearest date to pivot date
    :param items: dates
    :param pivot: compare dates to pivot
    :return: closest date to pivot
    """
    return min(items, key=lambda x: abs(x - pivot))


def next_weekday(d, weekday):
    """
    Finds the closest next weekday
    :param d: weekday number
    :param weekday: 0 = Monday, 1=Tuesday, 2=Wednesday...
    :return: closest week day datetime
    """
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


if __name__ == '__main__':
    main()
