#!/usr/bin/python3.4

from temp import netflix_login
from scrapper import start_scrapp
from threading import Thread, Event
from queue import Queue


if __name__ == "__main__":
    web_driver = None
    login_event = Event()
    loaded_event = Event()
    q = Queue()

    thread_login = Thread(
        name='thread_login',
        target=netflix_login,
        args=(login_event,)
    )

    thread_scrapper = Thread(
        name='thread_scrapper',
        target=start_scrapp,
        args=(login_event, loaded_event, q)
    )

    # thread_wrapper = Thread(
    #     name='thread_wrapper',
    #     target=newScrappWindow,
    #     args=(login_event, loaded_event, q)
    # )

    thread_login.start()
    # thread_scrapper.start()
    # thread_wrapper.start()
