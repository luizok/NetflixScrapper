# STANDARD PACKAGES IN PYTHON 3.X 
import os
import shutil
import sqlite3
from time import sleep
import http.client as httplib

# 3TH PACKAGES
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

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


def internet_is_on():
    conn = httplib.HTTPConnection("www.google.com.br", timeout=5)
    
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True

    except:
        conn.close()
        return False


def login_validator(user, pswd):

    is_logged = False
    url = config.MAIN_URL + '/login'
    opt = Options()
    opt.add_argument('--start-maximized')
    opt.add_argument('user-data-dir=' + config.CACHE_FOLDER)
    # opt.add_argument('-headless')

    driver = webdriver.Chrome(chrome_options=opt)
    driver.get(url)

    XPATH_PROFILE = '//*[@id="appMountPoint"]/div/div/div/div[2]/div/div/ul/li[2]/div/a/div/div'

    if not already_logged():
        driver.find_element_by_id("email").send_keys(user)
        driver.find_element_by_id("password").send_keys(pswd)
        driver.find_element_by_xpath(
            '//*[@id="appMountPoint"]/div/div[2]/div/div/form[1]/button'
        ).click()

    if driver.current_url == config.MAIN_URL + '/browse':
        is_logged = True
        print('OK' if not already_logged() else 'already logged')

        #TODO implementar uma janela para escolher o perfil deseja      
        try:
            print('STATUS: Choosing profile...', end='', flush=True)
            driver.find_element_by_xpath(XPATH_PROFILE).click()
            print('OK')

        except Exception as e:
            print('already chosen')

        sleep(1.5) # depende da velocidade da internet
        driver.get('https://www.netflix.com/browse/genre/34399?so=az')

    else:
        driver.close()
        driver = None

    return is_logged, driver



