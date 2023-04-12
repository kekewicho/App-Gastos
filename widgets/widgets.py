from kivy.lang import Builder
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard, MDCardSwipe
from kivymd.uix.pickers import MDDatePicker
from kivy.properties import StringProperty
from kivymd.app import MDApp
from datetime import date

class GastoConcubinoItem(MDCard):
    quien=StringProperty()
    cantidad=NumericProperty()
    fecha=StringProperty()

    def __init__(self,quien:str,cantidad:float,fecha:str,*args):
        super().__init__(*args)
        self.quien=quien
        self.cantidad=cantidad
        self.fecha=fecha

class ConcubinosContent(MDBoxLayout):
    def __init__(self,*args):
        super().__init__(*args)
        self.ids.fecha.text=str(date.today())

    def get_data(self):
        data = {
            'quien': self.ids.quien.text,
            'cantidad': float(self.ids.cantidad.text),
            'fecha':self.ids.fecha.text
        }
        return data
    
    def clean_fields(self):
        self.ids.fecha.text=str(date.today())
        self.ids.quien.text=''
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

Builder.load_file('widgets\widgets.kv')
