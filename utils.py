try:
    import httplib
except:
    import http.client as httplib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep


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
    # opt.add_argument('-headless')

    driver = webdriver.Chrome(chrome_options=opt)
    driver.get(url)
    
    driver.find_element_by_id("email").send_keys(user)
    driver.find_element_by_id("password").send_keys(pswd)
    driver.find_element_by_xpath(
        '//*[@id="appMountPoint"]/div/div[2]/div/div/form[1]/button'
    ).click()

    if driver.current_url == "https://www.netflix.com/browse":
        isLogged = True
        #TODO implementar uma janela para escolher o perfil deseja
        driver.find_element_by_xpath(
            '//*[@id="appMountPoint"]/div/div/div/div[2]/div/div/ul/li[2]/div/a/div/div'
        ).click()
        sleep(1.5) # depende da velocidade da internet
        driver.get('https://www.netflix.com/browse/genre/34399?so=az')

    else:
        driver.close()
        driver = None

    return isLogged, driver



