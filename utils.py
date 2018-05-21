try:
    import httplib
except:
    import http.client as httplib

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import os
import sqlite3
import shutil
from time import sleep
import config


DB_NAME = '.temp.db'

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

def alreadyLogged():
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

    isLogged = False
    if cursor.fetchone()[0] > 0:
        isLogged = True

    os.remove(config.DB_NAME)
    
    return isLogged


def networkIsAvailable():
    conn = httplib.HTTPConnection("www.google.com.br", timeout=5)
    
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True

    except:
        conn.close()
        return False


def netflixLoginValidator(user, pswd):

    isLogged = False
    url = "https://www.netflix.com/br/login"
    opt = Options()
    opt.add_argument('--start-maximized')
    opt.add_argument('user-data-dir=' + config.CACHE_FOLDER)
    # opt.add_argument('-headless')

    driver = webdriver.Chrome(chrome_options=opt)
    driver.get(url)

    XPATH_PROFILE = '//*[@id="appMountPoint"]/div/div/div/div[2]/div/div/ul/li[2]/div/a/div/div'

    if not alreadyLogged():
        driver.find_element_by_id("email").send_keys(user)
        driver.find_element_by_id("password").send_keys(pswd)
        driver.find_element_by_xpath(
            '//*[@id="appMountPoint"]/div/div[2]/div/div/form[1]/button'
        ).click()

    if driver.current_url == 'https://www.netflix.com/browse':
        isLogged = True
        print('OK' if not alreadyLogged() else 'already logged')

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

    return isLogged, driver



