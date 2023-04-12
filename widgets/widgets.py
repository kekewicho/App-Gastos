from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard, MDCardSwipe
from kivymd.uix.pickers import MDDatePicker
from kivy.properties import StringProperty
from kivymd.app import MDApp
from datetime import date


class BtmSheet(MDBoxLayout):
    def get_data(self):
        data = {
            'quien': self.ids.quien.text,
            'cantidad': float(self.ids.cantidad.text)
        }
        return data
    
class ContentNvoPrestamo(MDBoxLayout):
    pass

class Buttons(MDBoxLayout):
    pass


class Cards(MDCard):
    pass


#Widgets Gastos
class ContentGastos(MDBoxLayout):
    screen=StringProperty()

    def __init__(self,*args):
        super().__init__(*args)
        self.screen=MDApp.get_running_app().root.ids.manager.current
        print(self.screen)
        if not self.screen=='ScreenGastos':self.setToday()
    
    def setToday(self):
        self.ids.descripcion.text=str(date.today())

    def show_calendar(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        self.ids.descripcion.text = value.strftime('%Y-%m-%d')

    def on_cancel(self, instance, value):
        pass

    def get_data(self):
        return self.ids.monto.text,self.ids.descripcion.text

    def clean_fields(self):
        self.ids.monto.text = ''
        if self.screen=='ScreenGastos':
            self.ids.descripcion.text = ''
        else:
            self.setToday()

class OPItem(MDCardSwipe):
    monto = StringProperty()
    descripcion = StringProperty()
    op = StringProperty()
    key = StringProperty()

Builder.load_file('widgets\widgets.kv')
