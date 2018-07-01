# STANDARD PACKAGES IN PYTHON 3.x
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
import utils
import config

#TODO Quando o looping estiver otimizado,criar uma innerQueue que a medida que 
# os movieSources forem sendo adicionados na innerQueue (ou vetor moviesSource),
# uma thread interna vai adicionando as informações do filme ja tratadas na queue
# principalmente

PROGRESS = 0

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


def scroll_page_until_ends(driver, await_time):
    previous_html = ""
    current_html = driver.page_source

    while current_html != previous_html:
        previous_html = current_html
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        sleep(await_time) # Pode variar de acordo com a velocidade da internet
        current_html = driver.page_source
        break


def start_scrapp(netflixInstance, loginEvent=None, loadedEvent=None, queue=None):
    # loginEvent.wait() 
    #TODO criar o Scrapper 
    #Faça um scroll na página até alcançar todos os filmes
    #TODO otimizar esse looping
    movies_sources = []

    for i, so in enumerate(['az', 'za']):
        netflixInstance.driver.get(config.MAIN_URL + '/browse/genre/34399?so=' + so)
        
        print('STATUS: Finding all movies on netflix...['+str(i+1)+'/2] ', end='', flush=True)
        scroll_page_until_ends(netflixInstance.driver, .9)

        print('OK')           

        print('STATUS: Saving innerHTML of all movies...['+str(i+1)+'/2] ', end='', flush=True)
        movies_sources += list(
            map(lambda p : bs(p.get_attribute('innerHTML'), 'html.parser'),
                netflixInstance.driver.find_elements_by_class_name('slider-item'))
        )        
        print('OK')

    all_sources = utils.remove_duplicates(movies_sources, lambda s: s.find('a')['aria-label'])
    all_sources = sorted(all_sources, key=lambda s: s.find('a')['aria-label'])

    print("TOTAL OF MOVIES = " + str(len(all_sources)))
    print('STATUS: Starting to get information... ')

    if not os.path.exists(config.FOLDER_NAME):
        os.mkdir(config.FOLDER_NAME)

    total_len = len(all_sources)
    for i, s_movie in enumerate(movies_sources):
        t = Thread(
            target=scrapp_image,
            args=(s_movie, total_len), 
            name='MOVIE_' + safe_movie_name(s_movie.find('a')['aria-label'], None))
        t.start()

        while active_count() > config.MAX_THREADS:
            sleep(1)

    # loadedEvent.set()


def build_filename(name, img_lnik):
    return name + \
            '.' + img_link.split('/')[-1] \
            .split('.')[1]


def safe_movie_name(name, img_link):
    return name.replace(' ', '_') \
            .replace('/', "'")   


def scrapp_image(s_movie, total_len):

    global PROGRESS
    driver = utils.generate_webdriver(show=False)

    tag_a = s_movie.find('a')
    name = tag_a['aria-label']
    link = tag_a['href'].split('?')[0].replace('watch', 'title')
    print("GETTING -> " + name)
    driver.get(config.MAIN_URL + link)

    print(tag_a.find('div', {'class': 'video-artwork'}))
    input()
    img_link = get_image_link(tag_a.find('div', {'class': 'video-artwork'}))
    filename = build_filename(safe_movie_name(name), img_link)
    
    with open(config.FOLDER_NAME + '/' + filename, 'wb') as img_file:
        img_file.write(requests.get(img_link).content)
        img_file.close()
    
    driver.close()
    PROGRESS += 1
    print( u'\u2713 ' + ("[{:0"+str(len(str(total_len)))+"}/{:d}]-> ").format(PROGRESS, total_len) + name)
    sys.exit()
