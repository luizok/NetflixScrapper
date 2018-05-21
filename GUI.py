import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk
from gi.repository.GdkPixbuf import Pixbuf, InterpType
from time import sleep
from threading import Thread, Event, current_thread
import sys

import utils


EVENT = Event()
WEB_DRIVER = None

STATUS_ERROR = Gdk.Color(0xb7b7, 0x4343, 0x1616)
STATUS_WARN = Gdk.Color(0xf2f2, 0xeaea, 0x4f4f)
STATUS_SUCCESS = Gdk.Color(0, 0x8080, 0)


def newLoginWindow(loginEvent=None):
    global EVENT
    EVENT = loginEvent
    win = LoginWindow()
    win.init()


def newScrappWindow(loginEvent=None, loadedEvent=None, queue=None):
    global EVENT
    loginEvent.wait()

    EVENT = loadedEvent
    win = ScrappWindow()
    win.init()


class ScrappWindow(Gtk.Window):
    #TODO Criar a janela do Scrapp
    def __init__(self, queue=None):
        super().__init__(title="Netflix Scrapper")
        
        self.set_size_request(460, 230)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.connect('delete-event', self.exitFunc)

        self.modify_fg(Gtk.StateType.NORMAL, Gdk.Color(0xffff,0,0))
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0x0fff,0x0fff,0x0fff))
        
        fixed = Gtk.Fixed()

        # Cria logotipo e redimensiona
        pixBuf = Pixbuf.new_from_file('netflix_logo.jpg')
        pixBuf = pixBuf.scale_simple(130, 135, InterpType.BILINEAR)
        img = Gtk.Image()
        img.set_from_pixbuf(pixBuf)
        fixed.put(img, 5, 5)

        self.add(fixed)
    
    
    def init(self):
        global EVENT
        EVENT.wait()

        self.show_all()
        Gtk.main()


    def exitFunc(self, some, thing):
        Gtk.main_quit()
        sys.exit()


class LoginWindow(Gtk.Window):
    def __init__(self, webDriver=None, event=None):
        super().__init__(title="Netflix Login")

        self.webDriver = None
        
        self.set_size_request(460, 230)
        self.set_resizable(False)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.connect('delete-event', self.exitFunc)

        self.modify_fg(Gtk.StateType.NORMAL, Gdk.Color(0xffff,0,0))
        self.modify_bg(Gtk.StateType.NORMAL, Gdk.Color(0x0fff,0x0fff,0x0fff))
        
        fixed = Gtk.Fixed()

        # Cria logotipo e redimensiona
        pixBuf = Pixbuf.new_from_file('netflix_logo.jpg')
        pixBuf = pixBuf.scale_simple(130, 135, InterpType.BILINEAR)
        img = Gtk.Image()
        img.set_from_pixbuf(pixBuf)
        fixed.put(img, 5, 5)

        # Cria label de status
        self.lblStatus = Gtk.Label('')
        self.lblStatus.set_size_request(80, 35)
        fixed.put(self.lblStatus, 230, 145)

        # Adiciona Label Email
        lblUser = Gtk.Label('Email:')
        fixed.put(lblUser, 150, 15)

        # Adiciona input para email
        self.inpNetflixUser = Gtk.Entry()
        self.inpNetflixUser.set_placeholder_text('email')
        self.inpNetflixUser.set_alignment(.5)
        self.inpNetflixUser.set_size_request(250, 35)
        self.inpNetflixUser.modify_fg(Gtk.StateType.NORMAL, Gdk.Color(0,0,0))
        fixed.put(self.inpNetflixUser, 150, 35)
        
        # Adiciona label Senha
        lblPass = Gtk.Label('Senha:')
        fixed.put(lblPass, 150, 85)

        # Adiciona input de senha
        self.inpNetflixPass = Gtk.Entry()
        self.inpNetflixPass.set_placeholder_text('senha')
        self.inpNetflixPass.set_alignment(.5)
        self.inpNetflixPass.set_visibility(False)
        self.inpNetflixPass.set_size_request(250, 35)
        self.inpNetflixPass.modify_fg(Gtk.StateType.NORMAL, Gdk.Color(0,0,0))
        fixed.put(self.inpNetflixPass, 150, 105)

        #Adiciona Label Banco de Dados
        lblDB = Gtk.Label('Banco De Dados:')
        fixed.put(lblDB, 5, 155)

        # Adiciona ComboBox para selecionar db
        databases = Gtk.ListStore(str)
        databases.append(['None'])
        databases.append(['MongoDB'])
        databases.append(['MySQL'])

        self.cmbDatabase = Gtk.ComboBox.new_with_model(databases)
        renderText = Gtk.CellRendererText()
        self.cmbDatabase.pack_start(renderText, True)
        self.cmbDatabase.add_attribute(renderText, 'text', 0)
        self.cmbDatabase.set_active(0)
        self.cmbDatabase.set_size_request(135, 35)
        self.cmbDatabase.modify_fg(Gtk.StateType.NORMAL, Gdk.Color(0,0,0))
        self.cmbDatabase.connect('changed', self.comboChanged)
        fixed.put(self.cmbDatabase, 5, 175)

        #Adiciona botões <Filmes> e <Séries>
        self.btnMovie = Gtk.Button()
        self.btnMovie.set_label('Filmes')
        self.btnMovie.set_name('movie')
        self.btnMovie.set_size_request(120, 35)
        self.btnMovie.modify_fg(Gtk.StateType.NORMAL, Gdk.Color(0,0,0))
        self.btnMovie.connect('clicked', self.btnClicked)
        fixed.put(self.btnMovie, 150, 175)

        self.btnSerie = Gtk.Button()
        self.btnSerie.set_label('Séries')
        self.btnSerie.set_name('serie')
        self.btnSerie.set_size_request(120, 35)
        self.btnSerie.set_sensitive(False)
        self.btnSerie.modify_fg(Gtk.StateType.NORMAL, Gdk.Color(0,0,0))
        self.btnSerie.connect('clicked', self.btnClicked)
        fixed.put(self.btnSerie, 280, 175)

        # Cria botão com ícone para reconectar
        self.btnReconnect = Gtk.Button()
        self.btnReconnect.set_label('.')
        self.btnReconnect.set_name('btnReconnect')
        self.btnReconnect.set_size_request(35, 35)
        self.btnReconnect.connect('clicked', self.checkConnection)
        fixed.put(self.btnReconnect, 410, 175)

        self.checkConnection(None)

        self.add(fixed)


    def init(self):
        self.show_all()
        self.set_keep_above(True)
        print('STATUS: Waiting for login...', end='', flush=True)
        Gtk.main()
        


    def exitFunc(self, some, thing):
        Gtk.main_quit()


    def btnClicked(self, widget):
        global EVENT
        global WEB_DRIVER
        global STATUS_WARN

        if widget.get_name() == "movie": # Ainda não fiz os das séries
            print('OK')           
            user = self.inpNetflixUser.get_text()
            pswd = self.inpNetflixPass.get_text()
            
            print('STATUS: Checking login...' , end='', flush=True)
            isLogged, WEB_DRIVER = utils.login_validator(user, pswd)

            if isLogged:
                EVENT.set()
                sleep(.5)
                self.close()
            else:
                print('\nERROR: User not found')
                print('STATUS: Waiting for login...', end='', flush=True)
                self.lblStatus.set_label("Usuário não encontrado")
                self.lblStatus.modify_fg(Gtk.StateType.NORMAL, STATUS_WARN)

    # TEMP
    def comboChanged(self, widget):
        active = widget.get_active_iter()
        name = widget.get_model()[active][0]
        print("db selected = " + name)


    def checkConnection(self, widget):
        global STATUS_ERROR
        global STATUS_SUCCESS

        label = "Sem Conexão"
        color = STATUS_ERROR
        status = False
        
        if utils.internet_is_on():
            label = "Pronto"
            color = STATUS_SUCCESS
            status = True
   
        self.lblStatus.modify_fg(Gtk.StateType.NORMAL, color)
        self.cmbDatabase.set_sensitive(status)
        self.btnMovie.set_sensitive(status)
        self.btnSerie.set_sensitive(status)
        self.lblStatus.set_label(label)

