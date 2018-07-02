# STANDARD PACKAGES IN PYTHON 3.x
import os
import sys
import shutil
import sqlite3
from time import sleep
from threading import Thread, active_count
from pprint import pprint

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

# def fixup_first_movie(firstMovie):
#     return None


def scroll_page_until_ends(driver, await_time):

    previous_html = ""
    current_html = driver.page_source

    while current_html != previous_html:
        previous_html = current_html
        driver.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        sleep(await_time) # Pode variar de acordo com a velocidade da internet
        current_html = driver.page_source
        break # tests purpose


def start_scrapp(netflixInstance, loginEvent=None, loadedEvent=None, queue=None):
    # loginEvent.wait() 
    #TODO otimizar esse looping

    movies_sources = []

    for i, so in enumerate(['az', 'za']):
        netflixInstance.driver.get(config.MAIN_URL + '/browse/genre/34399?so=' + so)
        
        print('STATUS: Finding all movies on netflix...['+str(i+1)+'/2] ', end='', flush=True)
        scroll_page_until_ends(netflixInstance.driver, .9)

        print('OK')           
        print('STATUS: Saving innerHTML of all movies...['+str(i+1)+'/2] ', end='', flush=True)

        # for each slider-item, save his html code
        movies_sources += list(
            map(lambda p : bs(p.get_attribute('innerHTML'), 'html.parser'),
                netflixInstance.driver.find_elements_by_class_name('slider-item'))
        )        
        print('OK')

    # Removing duplicates and sorting by name
    all_sources = utils.remove_duplicates(movies_sources, lambda s: s.find('a')['aria-label'])
    all_sources = sorted(all_sources, key=lambda s: s.find('a')['aria-label'])

    print("TOTAL OF MOVIES = " + str(len(all_sources)))
    print('STATUS: Starting to get information... ')

    if not os.path.exists(config.FOLDER_NAME):
        os.mkdir(config.FOLDER_NAME)

    # for each slider-item, run a thread to get movie's informations, 
    # if the number of active thread is greater than max_threads
    # wait until one of active threads be released
    total_len = len(all_sources)
    for i, s_movie in enumerate(movies_sources):
        t = Thread(
            target=retrieve_movie,
            args=(s_movie, total_len), 
            name='MOVIE_' + utils.safe_movie_name(s_movie.find('a')['aria-label'])
        )
        t.start()

        while active_count() > config.MAX_THREADS:
            sleep(1)

    # loadedEvent.set()


def retrieve_movie(s_movie, total_len):

    global PROGRESS

    tag_a = s_movie.find('a')
    movie_name = tag_a['aria-label']
    movie_link = tag_a['href'].split('?')[0].replace('watch', 'title')

    print("GETTING -> " + movie_name)
    movie = scrapp_movie_page(movie_link)
    movie.update({'miniature_link': tag_a.find('img', {'class': 'boxart-image'})['src']})


    utils.save_movie_miniature(movie_name, movie['miniature_link'])

    pprint(movie)
    input()

    PROGRESS += 1
    print(u'\u2713 ' + ("[{:0"+str(len(str(total_len)))+"}/{:d}]-> ").format(PROGRESS, total_len) + movie_name)
    sys.exit()


def scrapp_movie_page(movie_link):

    movie = {}
    driver = utils.generate_webdriver(show=False)
    driver.get(config.MAIN_URL + movie_link)

    movie.update({'movie_id': int(driver.current_url.split('/')[-1])})
    movie.update({'title': driver.find_element_by_class_name('text').text})
    movie.update({'year': int(driver.find_element_by_class_name('year').text)})
    movie.update({'duration': utils.parse_date(driver.find_element_by_class_name('duration').text)})
    movie.update({'synopsis': driver.find_element_by_class_name('synopsis').text})
    movie.update({'maturity': 0})

    try:
        movie['maturity'] = int(driver.find_element_by_class_name('maturity-number').text)
    except ValueError:
        pass

    driver.find_element_by_id('tab-ShowDetails').click()
    details = driver.find_element_by_class_name('simpleSlider') \
                    .find_element_by_class_name('sliderContent')

    # cut_indexes saves the initial indexes of director, cast, screenwriter and the last index
    movie_cast = details.find_element_by_tag_name('span').find_elements_by_tag_name('li')
    cut_indexes = [i for i, m in enumerate(movie_cast) if m.get_attribute('class') == 'listLabel'] + [len(movie_cast)]
    cut_map = {0: 'directors', 1: 'cast', 2: 'screenwriters'}

    for i in range(len(cut_indexes)-1):
        movie.update({
            cut_map[i]: [
                {
                    'person_name': movie_cast[j].text, 
                    'person_id': int(movie_cast[j].find_element_by_tag_name('a') \
                                                  .get_attribute('href').split('/')[-1])
                }
                for j in range(cut_indexes[i]+1, cut_indexes[i+1])
            ]
        })

    genres = details.find_element_by_class_name('detailsTags') \
                    .find_elements_by_tag_name('ul')[0] \
                    .find_elements_by_tag_name('li')

    movie.update({
        'genres': [
            {
                'genre': genre.text,
                'genre_id': int(genre.find_element_by_tag_name('a') \
                                     .get_attribute('href').split('/')[-1])
            }
            for genre in genres
        ]
    })

    driver.close()

    return movie