#!/usr/bin/python3.4

from GUI import newLoginWindow, newScrappWindow
from Scrapper import startScrapping
from threading import Thread, Event, current_thread
from queue import Queue

if __name__ == "__main__":
    webDriver = None
    e = Event()
    q = Queue()

    print(current_thread().getName() + " E = " + str(hex(id(e))))

    thrLogin = Thread(name='thrLogin', target=newLoginWindow, args=(e,))
    thrInfos = Thread(name='thrInfos', target=newScrappWindow, args=(e,))
    thrScrapper = Thread(name='thrScrapper', target=startScrapping, args=(e, q))

    thrLogin.start()
    thrInfos.start()
    thrScrapper.start()
