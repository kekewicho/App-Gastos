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
from widgets.widgets import ConcubinosContent
from kivymd.uix.screen import MDScreen
from kivymd.utils import asynckivy as ak

class ScreenConcubinos(MDScreen):
    def addGastoConcubino(self, data):
        data = self.custom_sheet.screen.get_data()
        self.custom_sheet.close()
        key = crud.db.child('concubinos/gastos').push(data)
        self.gastos_concubinos.append(data)
        self.add_gasto_widget(data, key)
        Snackbar(text='Gasto guardado con éxito').open()
    
    def addGastoConcubino(self):
        def addGastoConcubino(object):
            data = self.dialog.content_cls.get_data()
            key = crud.db.child('concubinos/gastos').push(data)
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

    def add_gasto_widget(self, data, key):
        def add_gasto_widget():
            item = OPItem(monto="${:,.2f}".format(
                data['cantidad']), descripcion=f'Pagó {data["quien"]}')
            item.ids.btnDelete.on_release = lambda x=key: self.delete_gasto_concubino(x)
            item.ids.btnEdit.on_release = lambda x=key: self.edit_gasto_concubino(x)
        ak.start(add_gasto_widget())

    def delete_gasto_concubino(self, key):
        print(key)

    def edit_gasto_concubino(self, key):
        pass
