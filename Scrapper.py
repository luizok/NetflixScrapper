from threading import current_thread
from time import sleep
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.keys import Keys
from queue import Queue

#TODO Quando o looping estiver otimizado,criar uma innerQueue que a medida que 
# os movieSources forem sendo adicionados na innerQueue (ou vetor moviesSource),
# uma thread interna vai adicionando as informações do filme ja tratadas na queue
# principalmente

def fixupFirstMovie(firstMovie):
    return None


def startScrapping(loginEvent=None, loadedEvent=None, queue=None):
    loginEvent.wait() 
    #TODO criar o Scrapper
    from GUI import WEB_DRIVER   

    print(current_thread().getName() + " loginEvent = " + str(hex(id(loginEvent))))
    print(current_thread().getName() + " URL = " + WEB_DRIVER.current_url)
    print(100*"#")

    MAIN_URL = 'https://www.netflix.com'
    previous_html = ""
    current_html = WEB_DRIVER.page_source

    #Faça um scroll na página até o alcançar todos os filmes
    #TODO otimizar esse looping
    moviesSources = []

    for i, so in enumerate(['az', 'za']):
        WEB_DRIVER.get(MAIN_URL + '/browse/genre/34399?so=' + so)
        
        previous_html = ""
        current_html = WEB_DRIVER.page_source
        
        print('STATUS: Finding all movies on netflix...['+str(i+1)+'/2] ', end='', flush=True)
        while current_html != previous_html:
            previous_html = current_html
            WEB_DRIVER.execute_script("window.scrollTo(0,document.body.scrollHeight);")
            sleep(1.2) # Pode variar de acordo com a velocidade da internet
            current_html = WEB_DRIVER.page_source

        print('OK')           

        print('STATUS: Saving innerHTML of all movies...['+str(i+1)+'/2] ', end='', flush=True)
        moviesSources += list(
            map(lambda p : bs(p.get_attribute('innerHTML'), 'html.parser'),
                WEB_DRIVER.find_elements_by_class_name('slider-item'))
        )        
        print('OK')

    moviesSources = sorted(moviesSources, key=lambda s: s.find('a')['aria-label'])
    print("TAMANHAO TOTAL = " + str(len(moviesSources)))
    print('STATUS: Start to get information... ', end='', flush=True)
    input()
    for sMovie in moviesSources:
        tag_a = sMovie.find('a')
        name = tag_a['aria-label']
        link = tag_a['href'].split('?')[0].replace('watch', 'title')
        print(name + " : " + MAIN_URL + link)

    

    loadedEvent.set()
    
    
