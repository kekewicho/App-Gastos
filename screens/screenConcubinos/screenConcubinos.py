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

    async def addConcubinoItem(self, data):
        def addConcubinoItem():
            key = crud.db.child('concubinos/gastos').push(data)
            item=GastoConcubinoItem(
                    data['quien'],
                    data['cantidad'],
                    data['fecha'],
                    key['name'])
            self.ids.gastos_concubinos.add_widget(item)
            self.gastos.append(item)
            Snackbar(text='Gasto registrado con éxito').open()
        ak.start(addConcubinoItem())
    
    def addGastoConcubino(self):
        def addGastoConcubino(object):
            data = self.dialog.content_cls.get_data()
            self.addConcubinoItem(data)
            self.dialog.content_cls.clean_fields()

        def cancelar(object):
            self.dialog.content_cls.clean_fields()
            self.dialog.dismiss()

        self.dialog = MDDialog(
            title='Registrar gasto',
            type='custom',
            content_cls=ConcubinosContent(),
            buttons=[
                bt(text='Cancelar', on_release=cancelar),
                bt(text='Registrar', on_release=registrar)]
        )
        self.dialog.open()

    def update_balance(self):
        balance_luis, balance_joss = 0, 0
        for i in self.gastos_concubinos:
            if i['quien'] == 'joss':
                balance_joss += i['cantidad']
            if i['quien'] == 'luis':
                balance_luis += i['cantidad']
        diferencia = abs(balance_luis-balance_joss)
        if balance_luis > balance_joss:
            self.root.ids.balanceConcubino.text = f'La yos le debe al yoryis {"${:,.2f}".format(diferencia)}'
        if balance_joss > balance_luis:
            self.root.ids.balanceConcubino.text = f'El yoryis le debe a la yos {"${:,.2f}".format(diferencia)}'
        if balance_joss == balance_luis:
            self.root.ids.balanceConcubino.text = 'Ahorita estan a mano, no pelien'

    def delete_gasto_concubino(self, wdg):
        pass

    def edit_gasto_concubino(self, key):
        pass
