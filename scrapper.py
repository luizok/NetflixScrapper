# STANDARD PACKAGES IN PYTHON 3.X
import os
import sys
import shutil
import sqlite3
from time import sleep
from threading import Thread, active_count

# 3RD PACKAGES
import requests
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

# LOCAL PACKAGES
import config
import utils

#TODO Quando o looping estiver otimizado,criar uma innerQueue que a medida que 
# os movieSources forem sendo adicionados na innerQueue (ou vetor moviesSource),
# uma thread interna vai adicionando as informações do filme ja tratadas na queue
# principalmente


def fixup_first_movie(firstMovie):
    return None


def normalize_image_url(div):
    link = div['style'].split('https://')[1]
    idx = link.index(')')

    if link[idx-1] != '"': # link[idx-1] != "
        link = link[:idx] + '"' + link[idx:]
    
    return 'https://' + link.split('"')[0]


def get_image_link(div):
    return normalize_image_url(div)


def start_scrapp(driver: WebDriver, loginEvent=None, loadedEvent=None, queue=None):
    # loginEvent.wait() 
    #TODO criar o Scrapper 

    print(100*"#")

    #Faça um scroll na página até alcançar todos os filmes
    #TODO otimizar esse looping
    movies_sources = []

    for i, so in enumerate(['az', 'za']):
        driver.get(config.MAIN_URL + '/browse/genre/34399?so=' + so)
        
        previous_html = ""
        current_html = driver.page_source
        
        print('STATUS: Finding all movies on netflix...['+str(i+1)+'/2] ', end='', flush=True)
        while current_html != previous_html:
            previous_html = current_html
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            sleep(1.2) # Pode variar de acordo com a velocidade da internet
            current_html = driver.page_source
            break

        print('OK')           

        print('STATUS: Saving innerHTML of all movies...['+str(i+1)+'/2] ', end='', flush=True)
        movies_sources += list(
            map(lambda p : bs(p.get_attribute('innerHTML'), 'html.parser'),
                driver.find_elements_by_class_name('slider-item'))
        )        
        print('OK')
        break

    all_sources = sorted(movies_sources, key=lambda s: s.find('a')['aria-label'])
    aux_set = set()
    movies_sources = []

    for s in all_sources:
        if s not in aux_set:
            aux_set.add(s)
            movies_sources.append(s)
    
    del aux_set

    print('STATUS: Starting to get information... ')

    if not os.path.exists(config.FOLDER_NAME):
        os.mkdir(config.FOLDER_NAME)

    driver.close()
    for i, s_movie in enumerate(movies_sources):
        t = Thread(target=scrapp_image, args=(s_movie,), name='movie_' + str(i))
        t.start()

        # MAX_THREADS + gui thread + main thread (prompt)
        while active_count() > config.MAX_THREADS:
            sleep(.5)

    # loadedEvent.set()


def scrapp_image(s_movie):

    driver = utils.generate_webdriver(show=False)

    tag_a = s_movie.find('a')
    name = tag_a['aria-label']
    link = tag_a['href'].split('?')[0].replace('watch', 'title')
    print("GETTING -> " + name)
    driver.get(config.MAIN_URL + link)

    assert driver.current_url == config.MAIN_URL+link

    img_link = get_image_link(tag_a.find('div', {'class': 'video-artwork'}))

    filename = name.replace(' ', '_').replace('/', "'")+'.'+img_link.split('/')[-1].split('.')[1]
    with open(config.FOLDER_NAME + '/' + filename, 'wb') as img_file:
        img_file.write(requests.get(img_link).content)
        img_file.close()
    
    driver.close()
    print( u'\u2713' + "\t-> " + name)
    sys.exit()
