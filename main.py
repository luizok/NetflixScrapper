from GUI import newLoginWindow, newScrappWindow
from threading import Thread, Event, current_thread

if __name__ == "__main__":
    webDriver = None
    e = Event()

    print(current_thread().getName() + " E = " + str(hex(id(e))))

    thrLogin = Thread(name='thrLogin', target=newLoginWindow, args=(webDriver, e))
    thrInfos = Thread(name='thrInfos', target=newScrappWindow, args=(webDriver, e))

    thrLogin.start()
    thrInfos.start()
