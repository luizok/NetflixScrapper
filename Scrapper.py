from threading import current_thread
from time import sleep
from selenium.webdriver.common.keys import Keys

def startScrapping(loginEvent=None, loadedEvent=None, queue=None):
    loginEvent.wait() 
    #TODO criar o Scrapper
    from GUI import WEB_DRIVER   

    print(current_thread().getName() + " loginEvent = " + str(hex(id(loginEvent))))
    print(current_thread().getName() + " URL = " + WEB_DRIVER.current_url)
    # print(100*"#")
    # print(WEB_DRIVER.page_source)
    print(100*"#")

    previous_html = ""
    current_html = WEB_DRIVER.page_source

    #Faça um scroll na página até o alcançar todos os filmes
    #TODO otimizar esse looping
    while current_html != previous_html:
        previous_html = current_html
        WEB_DRIVER.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        sleep(1.2) # Pode variar de acordo com a velocidade da internet
        current_html = WEB_DRIVER.page_source
        break

    moviesSource = WEB_DRIVER.find_elements_by_class_name('slider-item')

    for sMovie in moviesSource:
        tag_a = sMovie.find_element_by_tag_name('a')
        name = tag_a.get_attribute('aria-label')
        link = tag_a.get_attribute('href').split('?')[0]
        print(name + " : " + link)

    loadedEvent.set()
    
    
