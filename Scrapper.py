from threading import current_thread

def startScrapping(event=None, queue=None):
    event.wait() 
    #TODO criar o Scrapper
    from GUI import WEB_DRIVER   

    print(current_thread().getName() + " E = " + str(hex(id(event))))
    print(current_thread().getName() + " URL = " + WEB_DRIVER.current_url)
    print(100*"#")
    print(WEB_DRIVER.page_source)
    print(100*"#")

    for i in range(100):
        print(str(i) + " scrapping...")
    
    
