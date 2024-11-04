import cv2
import pytesseract
import numpy as np
from urllib.request import urlopen
from random import choice, randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException as NSEE
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from datetime import datetime
from os.path import abspath
import sqlite3
from warnings import filterwarnings


class Database():
    def __init__(self):
        self.db = sqlite3.connect(abspath('database.db'))
        self.cursor = self.db.cursor()

    def insert(self, username, password, image, captcha, time):
        self.cursor.execute("INSERT INTO accounts(id,username,image,captcha,password,time) VALUES (NULL,?,?,?,?,?)",
                            (username, image, captcha, password, time))
        self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()


def get_img(src):
    return urlopen(src).read()


def clean_img(img):
    img = np.frombuffer(img, np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_GRAYSCALE)
    img = cv2.threshold(img, 157, 255, cv2.THRESH_BINARY)[-1]
    img = cv2.medianBlur(img, 3)
    cv2.imshow('img', img)
    cv2.waitKey(0)
    return img


def read_text(img):
    pytesseract.pytesseract.tesseract_cmd = r'D:\Programming\Python\Projects\login\tesseract\tesseract.exe'
    text = pytesseract.image_to_string(img, config='--psm 8 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz').replace('\n','')
    return text


def random_password():
    elements = [chr(i) for i in range(ord('a'),ord('z')+1)]+[chr(i).upper() for i in range(ord('a'),ord('z')+1)]+[str(num) for num in range(10)]+['_','.']*3
    password = ''.join([choice(elements) for i in range(randint(10,18))])
    return password


def random_username():
    with open('username/adjectives.txt') as file:
        adjs = file.readlines()
    with open('username/nouns.txt') as file:
        nouns = file.readlines()
    adj = choice(adjs)
    noun = choice(nouns)
    username = f'{adj[0].upper()+adj[1:-1]}{noun[0].upper()+noun[1:-1]}{randint(0,10**randint(0,3)-1)}'
    return username

def register(browser, username, password, url):
    browser.get(url)

    username_input = browser.find_element(By.XPATH, '//input[@id="wpName2"]')
    password_input_1 = browser.find_element(By.XPATH, '//input[@id="wpPassword2"]')
    password_input_2 = browser.find_element(By.XPATH, '//input[@id="wpRetype"]')
    captcha_input = browser.find_element(By.XPATH, '//input[@id="mw-input-captchaWord"]')

    src = browser.find_element(By.XPATH, '//img[@class="fancycaptcha-image"]').get_attribute('src')
    img_bytes = get_img(src)
    img = clean_img(img_bytes)
    captcha_text = read_text(img)
    print(captcha_text)


    username_input.send_keys(username)
    password_input_1.send_keys(password)
    password_input_2.send_keys(password)
    captcha_input.send_keys(captcha_text)

    try:
        create_button = browser.find_element(By.XPATH, '//button[@id="wpCreateaccount"]')
        create_button.click()
    except NSEE:
        print('Dont need button')

    try:
        browser.find_element(By.XPATH, '//div[@class="mw-message-box-error mw-message-box"]')
        try:
            browser.find_element(By.XPATH,
                                 '//div[@class="mw-message-box-error mw-message-box"][contains(text(), "Visitors to Wikipedia using your")]')
            browser.get(url)
            print('Ip error')
            return True
        except NSEE:
            print('NonIp error')
            return
    except NSEE:
        db = Database()
        db.insert(username, password, img_bytes, captcha_text, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        db.close()
        print('New account')
        return False


def main():
    filterwarnings('ignore')
    ua = UserAgent().random
    url = 'https://en.wikipedia.org/w/index.php?title=Special:CreateAccount'
    try:
        opt = Options()
        opt.add_argument(f"user-agent={ua}")
        s = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(service=s, chrome_options=opt)
        while True:
            username, password = random_username(), random_password()
            br = register(browser, username, password, url)
            if br: break

    except Exception as ex:
        print(type(ex), '\n\n')
        print(ex)

    finally:
        browser.close()
        browser.quit()

if __name__ == '__main__':
    main()
