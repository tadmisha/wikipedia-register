import cv2
import pytesseract
from urllib.request import urlretrieve
from random import choice, randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException as NSEE
from fake_useragent import UserAgent
from datetime import datetime
from os.path import abspath, split as ossplit
import sys
import sqlite3
from warnings import filterwarnings


class Database():
    def connect(self):
        self.db = sqlite3.connect(abspath('database.db'))
        self.cursor = self.db.cursor()

    def insert(self, username, password, time):
        self.cursor.execute("INSERT INTO accounts(id,username,password,time) VALUES (NULL,?,?,?)", (username, password, time))
        self.db.commit()

    def close(self):
        self.cursor.close()
        self.db.close()

def get_img(src):
    urlretrieve(src, 'imgs/captcha.jpg')

def clean_img(img):
    img = cv2.threshold(img, 157, 255, cv2.THRESH_BINARY)[-1]
    img = cv2.medianBlur(img, 3)
    return img

def read_text(img):
    pytesseract.pytesseract.tesseract_cmd = r'D:\Programming\Python\Projects\login\tesseract\tesseract.exe'
    text = pytesseract.image_to_string(img, config='--psm 8 --oem 3 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz')
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

def register(url, ua, username, password):
    try:
        opt = Options()
        opt.add_argument(f"user-agent={ua}")
        s = Service(executable_path='D:\Programming\Python\Projects\login\chromedriver.exe')
        browser = webdriver.Chrome(service=s, chrome_options=opt)
        browser.get(url)

        username_input = browser.find_element(By.XPATH, '//input[@id="wpName2"]')
        username_input.send_keys(username)
        while True:
            password_input_1 = browser.find_element(By.XPATH, '//input[@id="wpPassword2"]')
            password_input_2 = browser.find_element(By.XPATH, '//input[@id="wpRetype"]')
            captcha_input = browser.find_element(By.XPATH, '//input[@id="mw-input-captchaWord"]')

            src = browser.find_element(By.XPATH, '//img[@class="fancycaptcha-image"]').get_attribute('src')
            get_img(src)
            captcha_text = read_text('imgs/captcha.jpg')

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
                print(1)
            except NSEE:
                db = Database()
                db.connect()
                db.insert(username, password, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                db.close()
                break

    except Exception as ex:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = ossplit(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, print(type(ex)))

    finally:
        browser.close()
        browser.quit()

def main():
    filterwarnings('ignore')
    register('https://en.wikipedia.org/w/index.php?title=Special:CreateAccount', UserAgent().google, random_username(), random_password())

if __name__ == '__main__':
    main()
