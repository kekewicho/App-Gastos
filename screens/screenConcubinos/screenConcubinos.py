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
from widgets.widgets import ConcubinosContent,GastoConcubinoItem
from kivymd.uix.screen import MDScreen
from kivymd.utils import asynckivy as ak

class ScreenConcubinos(MDScreen):
    gastos=[]

    def on_enter(self):
        async def get_data():
            data=crud.db.child('concubinos/gastos').get()
            if data.each() is None:
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
