#!/usr/bin/python3.4

from GUI import newLoginWindow, newScrappWindow
from Scrapper import startScrapping
from threading import Thread, Event, current_thread
from queue import Queue

if __name__ == "__main__":
    webDriver = None
    loginEvent = Event()
    loadedEvent = Event()
    q = Queue()

    print(current_thread().getName() + " loginEvent = " + str(hex(id(loginEvent))))
    print(current_thread().getName() + " loadedEvent = " + str(hex(id(loadedEvent))))

    thrLogin = Thread(name='thrLogin', target=newLoginWindow, args=(loginEvent,))
    thrScrapper = Thread(name='thrScrapper', target=startScrapping, args=(loginEvent, loadedEvent, q))
    thrInfos = Thread(name='thrInfos', target=newScrappWindow, args=(loginEvent, loadedEvent, q))

    thrLogin.start()
    thrScrapper.start()
    thrInfos.start()
