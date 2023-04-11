from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton as bt
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard, MDCardSwipe
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelTwoLine
from kivymd.uix.pickers import MDDatePicker
from kivy.properties import StringProperty
from kivy.utils import platform
from kivymd.uix.card import MDSeparator
import crud
from threading import Thread
from kivy.clock import mainthread
from kivymd.uix.bottomsheet import MDCustomBottomSheet
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel


class BtmSheet(MDBoxLayout):
    def get_data(self):
        data = {
            'quien': self.ids.quien.text,
            'cantidad': float(self.ids.cantidad.text)
        }
        return data


class OPItem(MDCardSwipe):
    monto = StringProperty()
    descripcion = StringProperty()
    op = StringProperty()
    key = StringProperty()


class ContentNvoPrestamo(MDBoxLayout):
    pass


class ContentFondo(MDBoxLayout):
    pass


class Buttons(MDBoxLayout):
    pass


class Cards(MDCard):
    pass


class ContentGastos(MDBoxLayout):
    def show_calendar(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        self.children[0].text = value.strftime('%Y-%m-%d')

    def on_cancel(self, instance, value):
        pass

    def get_data(self):
        return self.ids.monto.text,self.ids.descripcion.text

    def clean(self):
        self.ids.monto.text = ''
        self.ids.descripcion.text = ''


class Scr(MDBoxLayout):
    who = 'luis' if platform != 'macosx' else 'joss'

    

    


Builder.load_file('main.kv')
