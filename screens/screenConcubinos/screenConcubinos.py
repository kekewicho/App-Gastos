from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton as bt
from kivy.properties import StringProperty
import crud
from kivymd.uix.snackbar import Snackbar
from widgets.widgets import ConcubinosContent,GastoConcubinoItem
from kivymd.uix.screen import MDScreen
from kivymd.utils import asynckivy as ak
from kivymd.uix.label import MDLabel
from kivy.lang import Builder
import os

Builder.load_file(os.path.join("screens","screenConcubinos","screenConcubinos.kv"))


class ScreenConcubinos(MDScreen):
    gastos=[]

    def on_enter(self):
        async def get_data():
            data=crud.db.child('concubinos/gastos').get()
            if data.each() is None:
                self.ids.gastos_concubinos.add_widget(
                MDLabel(
                    text='Aún no hay nada por aquí',
                    halign='center',
                    font_size='15sp',
                    adaptive_height=True,
                    theme_text_color= "Custom",
                    text_color= '#727372')),
                return None
            else:
                for i in data.each():
                    await ak.sleep(0)
                    item=dict(i.val())
                    item['key']=i.key()
                    self.addConcubinoItem(item)
            self.update_balance()
        ak.start(get_data())

    def addConcubinoItem(self, data):
        async def addConcubinoItem():
            item=GastoConcubinoItem(
                    data['quien'],
                    data['cantidad'],
                    data['fecha'],
                    data['key'])
            self.ids.gastos_concubinos.add_widget(item)
            self.gastos.append(item)
        ak.start(addConcubinoItem())
    
    def addGastoConcubino(self):
        def addGastoConcubino(object):
            data = self.dialog.content_cls.get_data()
            try:
                key = crud.db.child('concubinos/gastos').push(data)
            except:
                Snackbar(text="¡Ocurrió un error!").open()
                return None
            data['key']=str(key['name'])
            self.addConcubinoItem(data)
            self.dialog.content_cls.clean_fields()
            self.update_balance()
            self.dialog.dismiss()
            Snackbar(text='Gasto registrado con éxito').open()

        def cancelar(object):
            self.dialog.content_cls.clean_fields()
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title='Registrar gasto',
            type='custom',
            content_cls=ConcubinosContent(),
            buttons=[
                bt(text='Cancelar', on_release=cancelar),
                bt(text='Registrar', on_release=addGastoConcubino)]
        )
        self.dialog.open()

    def update_balance(self):
        async def update_balance():
            balance_luis, balance_joss = 0, 0
            for i in self.gastos:
                if i.quien == 'Joss':
                    balance_joss += i.cantidad
                if i.quien == 'Luis':
                    balance_luis += i.cantidad
            diferencia = abs(balance_luis-balance_joss)
            if balance_luis > balance_joss:
                self.ids.balanceConcubino.text = f'La yos le debe al yoryis {"${:,.2f}".format(diferencia)}'
            if balance_joss > balance_luis:
                self.ids.balanceConcubino.text = f'El yoryis le debe a la yos {"${:,.2f}".format(diferencia)}'
            if balance_joss == balance_luis:
                self.ids.balanceConcubino.text = 'Ahorita estan a mano, no pelien'
        ak.start(update_balance())

    def delete_gasto_concubino(self, wdg):
        pass

    def edit_gasto_concubino(self, key):
        pass
