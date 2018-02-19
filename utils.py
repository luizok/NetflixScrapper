try:
    import httplib
except:
    import http.client as httplib

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def networkIsAvailable():
    conn = httplib.HTTPConnection("www.google.com.br", timeout=5)
    
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True

    except:
        conn.close()
        return False


def netflixLoginValidator(user, pswd, debug=False):
    # TODO criar função para validar o login
    url = "netflix.com"
    opt = Options()
    opt.add_argument('-headless')

    driver = webdriver.Chrome(chrome_options=opt)

    return debug, driver



