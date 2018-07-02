# STANDARD PACKAGES IN PYTHON 3.x
import os
import re
import shutil
import sqlite3
from time import sleep
import http.client as httplib

# 3RD PACKAGES
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

# LOCAL PACKAGES
import config


#TODO Verificar se realmente a verificação funciona pra
# todos os casos.
""" ('memclid',) <- EXISTS EVEN IF USER HAS NOT LOGGED ONCE
    ('nfvdid',) <- EXISTS EVEN IF USER HAS NOT LOGGED ONCE
    ('SecureNetflixId',) <- EXISTS EVEN IF USER HAS NOT LOGGED ONCE
    ('NetflixId',) <- EXISTS EVEN IF USER HAS NOT LOGGED ONCE
    ('netflix-sans-normal-2-loaded',)
    ('netflix-sans-bold-2-loaded',)
    ('profilesNewSession',)
    ('lhpuuidh-browse-AERBMHGTKBFRTN7KCFCH2VAGBI',)
    ('lhpuuidh-browse-AERBMHGTKBFRTN7KCFCH2VAGBI-T',)
    ('cL',)  <-netflix's cookies that saves the session """


def generate_webdriver(show=True):
    opt = Options()
    opt.add_experimental_option("prefs", {
        'profile.managed_default_content_settings.images': 2,
        'profile.managed_default_content_settings.javascript': 0
    })

    opt.add_argument('user-data-dir=' + config.CACHE_FOLDER)
    opt.add_argument('start-maximized' if show else 'headless')

    return webdriver.Chrome(chrome_options=opt)


def internet_is_on():
    conn = httplib.HTTPConnection("www.google.com.br", timeout=5)
    
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True

    except:
        conn.close()
        return False


def already_logged():
    shutil.copy2(config.CACHE_FOLDER+'/Default/Cookies', config.DB_NAME)

    conn = sqlite3.connect(config.DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT count(cookies.name) " \
        "FROM cookies " \
        "WHERE " \
        "cookies.host_key LIKE '%netflix%' " \
        "AND cookies.name NOT IN " \
        "('SecureNetflixId', 'NetflixId', 'memclid', 'nfvdid');"
    )

    is_logged = False
    if cursor.fetchone()[0] > 0:
        is_logged = True

    os.remove(config.DB_NAME)
    
    return is_logged


def remove_duplicates(array: list, comparator):
    aux_set = set()
    vector = []

    for element in array:
        if comparator(element) not in aux_set:
            aux_set.add(comparator(element))
            vector.append(element)

    return vector


def already_in_profile(netflixInstance):

    try:
        drop = netflixInstance.driver.find_element_by_class_name('account-dropdown-button')
        name = drop.find_element_by_tag_name('a').get_property('aria-label')

        return True

    except NoSuchElementException:
        print("FALSAO")
        return False


def build_filename(img_name, img_link):

    img_ext = img_link.split('/')[-1].split('.')[1]
    return img_name + '.' + img_ext


def safe_movie_name(name):
    return name.replace(' ', '_') \
            .replace('/', "'")  


def save_movie_miniature(movie_name, img_link):

    filename = build_filename(safe_movie_name(movie_name), img_link)
    
    with open(config.FOLDER_NAME + '/' + filename, 'wb') as img_file:
        img_file.write(requests.get(img_link).content)
        img_file.close()
    

def parse_date(date):

    hours = re.findall(r'\d+h', date)
    try: hours = int(hours[0][:-1])
    except: hours = 0

    mins = re.findall(r'\d+min', date)
    try: mins = int(mins[0][:-3])
    except: mins = 0

    return 60 * hours + mins
