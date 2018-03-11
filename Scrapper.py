from threading import current_thread
from time import sleep
from selenium.webdriver.common.keys import Keys

def startScrapping(event=None, queue=None):
    event.wait() 
    #TODO criar o Scrapper
    from GUI import WEB_DRIVER   

    print(current_thread().getName() + " E = " + str(hex(id(event))))
    print(current_thread().getName() + " URL = " + WEB_DRIVER.current_url)
    # print(100*"#")
    # print(WEB_DRIVER.page_source)
    print(100*"#")

    previous_html = ""
    current_html = WEB_DRIVER.page_source

    while current_html != previous_html:
        previous_html = current_html
        WEB_DRIVER.execute_script("window.scrollTo(0,document.body.scrollHeight);")
        # WEB_DRIVER.find_element_by_xpath('//body').send_keys(Keys.END)
        sleep(1)
        current_html = WEB_DRIVER.page_source


    for i in range(100):
        print(str(i) + " scrapping...")
    
    
