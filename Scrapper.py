from threading import Thread, active_count
from time import sleep
import requests
import os
import sys
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.remote.errorhandler import ErrorHandler
from selenium.webdriver.chrome.options import Options
from queue import Queue
import sqlite3
import shutil
import config

#TODO Quando o looping estiver otimizado,criar uma innerQueue que a medida que 
# os movieSources forem sendo adicionados na innerQueue (ou vetor moviesSource),
# uma thread interna vai adicionando as informações do filme ja tratadas na queue
# principalmente


def fixupFirstMovie(firstMovie):
    return None


def normalizeImageURL(div):
    link = div['style'].split('https://')[1]
    idx = link.index(')')

    if link[idx-1] != '"': # link[idx-1] != "
        link = link[:idx] + '"' + link[idx:]
    
    return 'https://' + link.split('"')[0]


def getImageLink(div):
    return normalizeImageURL(div)


def startScrapping(loginEvent=None, loadedEvent=None, queue=None):
    loginEvent.wait() 
    #TODO criar o Scrapper
    from GUI import WEB_DRIVER   

    print(100*"#")

    previous_html = ""
    current_html = WEB_DRIVER.page_source

    #Faça um scroll na página até alcançar todos os filmes
    #TODO otimizar esse looping
    moviesSources = []

    for i, so in enumerate(['az', 'za']):
        WEB_DRIVER.get(config.MAIN_URL + '/browse/genre/34399?so=' + so)
        
        previous_html = ""
        current_html = WEB_DRIVER.page_source
        
        print('STATUS: Finding all movies on netflix...['+str(i+1)+'/2] ', end='', flush=True)
        while current_html != previous_html:
            previous_html = current_html
            WEB_DRIVER.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            sleep(1.2) # Pode variar de acordo com a velocidade da internet
            current_html = WEB_DRIVER.page_source
            break

        print('OK')           

        print('STATUS: Saving innerHTML of all movies...['+str(i+1)+'/2] ', end='', flush=True)
        moviesSources += list(
            map(lambda p : bs(p.get_attribute('innerHTML'), 'html.parser'),
                WEB_DRIVER.find_elements_by_class_name('slider-item'))
        )        
        print('OK')
        break

    allSources = sorted(moviesSources, key=lambda s: s.find('a')['aria-label'])
    auxSet = set()
    moviesSources = []

    for s in allSources:
        if s not in auxSet:
            auxSet.add(s)
            moviesSources.append(s)
    
    del auxSet

    print('STATUS: Starting to get information... ')

    if not os.path.exists(config.FOLDER_NAME):
        os.mkdir(config.FOLDER_NAME)

    WEB_DRIVER.close()
    for i, sMovie in enumerate(moviesSources):
        t = Thread(target=scrappImage, args=(sMovie,), name='movie_' + str(i))
        t.start()

        # MAX_THREADS + gui thread + main thread (prompt)
        while active_count() > config.MAX_THREADS+2:
            sleep(.5)

    loadedEvent.set()


def scrappImage(sMovie):

    opt = Options()
    opt.add_argument('user-data-dir=' + config.CACHE_FOLDER)
    opt.add_argument('-headless')

    driver = webdriver.Chrome(chrome_options=opt)

    tag_a = sMovie.find('a')
    name = tag_a['aria-label']
    link = tag_a['href'].split('?')[0].replace('watch', 'title')
    print("GETTING -> " + name)
    driver.get(config.MAIN_URL + link)

    assert driver.current_url == config.MAIN_URL+link

    imgLink = getImageLink(tag_a.find('div', {'class': 'video-artwork'}))

    fileName = name.replace(' ', '_').replace('/', "'")+'.'+imgLink.split('/')[-1].split('.')[1]
    with open(config.FOLDER_NAME + '/' + fileName, 'wb') as imgFile:
        imgFile.write(requests.get(imgLink).content)
        imgFile.close()
    
    driver.close()
    print("DONE    -> " + name)
    sys.exit()
