from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard, MDCardSwipe
from kivymd.uix.pickers import MDDatePicker
from kivy.properties import StringProperty, NumericProperty
from kivymd.app import MDApp
from datetime import date
from kivy.utils import platform
from kivymd.uix.behaviors import TouchBehavior
from kivy.clock import Clock
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.label import MDLabel
import os


class GastoConcubinoItem(MDCard, TouchBehavior):
    quien = StringProperty()
    cantidad = NumericProperty()
    fecha = StringProperty()
    key = StringProperty()
    descripcion = StringProperty()

    touch_down_time = 0
    touch_up_time = 0
    umbral = 0.5

    def __init__(self, quien: str, cantidad: float, fecha: str, key: str, descripcion: str, *args):
        super().__init__(*args)
        self.quien = quien
        self.cantidad = cantidad
        self.fecha = fecha
        self.key = key
        self.descripcion = descripcion

    def update_info(self, data):
        self.quien=str(data['quien']).capitalize()
        self.cantidad=float(data['cantidad'])
        self.fecha=str(data['fecha'])
        self.descripcion=str(data['descripcion'])

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.touch_down_time = touch.time_start
            self.event=Clock.schedule_once(self.long_touch,1)
            return super(GastoConcubinoItem,self).on_touch_down(touch)
        
    def long_touch(self,*args):
        MDApp.get_running_app().root.ids.manager.get_screen('ScreenConcubinos').deleteItem(self)
    
    def short_touch(self,*args):
        MDApp.get_running_app().root.ids.manager.get_screen('ScreenConcubinos').updateItem(self)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.touch_up_time = touch.time_end
            duration = self.touch_up_time - self.touch_down_time
            if duration < self.umbral:
                self.event.cancel()
                self.short_touch()
            return super(GastoConcubinoItem,self).on_touch_up(touch)    

class ConcubinosContent(MDBoxLayout):
    who = 'luis' if platform != 'macosx' else 'joss'
    quien = StringProperty()

    def __init__(self, quien='', cantidad=0, fecha='', descripcion='', *args):
        super().__init__(*args)
        if not quien == '':
            self.quien = quien
            self.ids.cantidad.text = str(cantidad)
            self.ids.fecha.text = fecha
            self.ids.descripcion.text = descripcion
        else:
            self.ids.fecha.text = str(date.today())
            self.quien = self.who
        if str(self.quien).upper() == 'LUIS':
            self.ids.luis.active = True
        if str(self.quien).upper() == 'JOSS':
            self.ids.joss.active = True

    def get_data(self):
        data = {
            'quien': (self.quien).capitalize(),
            'cantidad': float(self.ids.cantidad.text),
            'fecha': self.ids.fecha.text,
            'descripcion': self.ids.descripcion.text
        }
        return data

    def clean_fields(self):
        self.ids.fecha.text = str(date.today())
        self.ids.cantidad.text = ''

    def show_calendar(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        self.ids.fecha.text = value.strftime('%Y-%m-%d')

    def on_cancel(self, instance, value):
        pass


class ContentNvoPrestamo(MDBoxLayout):
    pass


class Buttons(MDBoxLayout):
    pass


class Cards(MDCard):
    pass


# Widgets Gastos
class ContentGastos(MDBoxLayout):
    screen = StringProperty()

    def __init__(self, *args):
        super().__init__(*args)
        self.screen = MDApp.get_running_app().root.ids.manager.current
        print(self.screen)
        if not self.screen == 'ScreenGastos':
            self.setToday()

    def setToday(self):
        self.ids.descripcion.text = str(date.today())

    def show_calendar(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save, on_cancel=self.on_cancel)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        self.ids.descripcion.text = value.strftime('%Y-%m-%d')

    def on_cancel(self, instance, value):
        pass

    def get_data(self):
        return self.ids.monto.text, self.ids.descripcion.text

    def clean_fields(self):
        self.ids.monto.text = ''
        if self.screen == 'ScreenGastos':
            self.ids.descripcion.text = ''
        else:
            self.setToday()


class OPItem(MDCardSwipe):
    monto = StringProperty()
    descripcion = StringProperty()
    op = StringProperty()
    key = StringProperty()


Builder.load_file(os.path.join("widgets", "widgets.kv"))
