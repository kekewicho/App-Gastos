from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard, MDCardSwipe
from kivymd.uix.pickers import MDDatePicker
from kivy.properties import StringProperty,NumericProperty
from kivymd.app import MDApp
from datetime import date
from kivy.animation import Animation
from kivy.utils import platform
import os

class GastoConcubinoItem(MDCard):
    quien=StringProperty()
    cantidad=NumericProperty()
    fecha=StringProperty()
    key=StringProperty()

    def __init__(self,quien:str,cantidad:float,fecha:str,key:str,*args):
        super().__init__(*args)
        self.quien=quien
        self.cantidad=cantidad
        self.fecha=fecha
        self.key=key

class ConcubinosContent(MDBoxLayout):
    who = 'luis' if platform != 'macosx' else 'joss'
    quien=StringProperty(who)
    def __init__(self,*args):
        super().__init__(*args)
        self.ids.fecha.text=str(date.today())
        for chip in self.ids.boxChip.children:
            chip.bind(active=self.set_chip_bg_color)
            chip.bind(active=self.set_chip_text_color)

    def set_chip_bg_color(self, instance_chip, active_value: int):
        '''
        Will be called every time the chip is activated/deactivated.
        Sets the background color of the chip.
        '''
        print(instance_chip, active_value)
        instance_chip.md_bg_color = (
            (0, 0, 0, 0.4)
            if active_value
            else (
                instance_chip.theme_cls.bg_darkest
                if instance_chip.theme_cls.theme_style == "Light"
                else (
                    instance_chip.theme_cls.bg_light
                    if not instance_chip.disabled
                    else instance_chip.theme_cls.disabled_hint_text_color
                )
            )
        )

    def set_chip_text_color(self, instance_chip, active_value: int):
        Animation(
            color=(0, 0, 0, 1) if active_value else (0, 0, 0, 0.5), d=0.2
        ).start(instance_chip.ids.label)

    def get_data(self):
        data = {
            'quien': (self.quien).capitalize(),
            'cantidad': float(self.ids.cantidad.text),
            'fecha':self.ids.fecha.text
        }
        return data
    
    def clean_fields(self):
        self.ids.fecha.text=str(date.today())
        self.ids.cantidad.text=''

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

Builder.load_file(os.path.join("widgets","widgets.kv"))
