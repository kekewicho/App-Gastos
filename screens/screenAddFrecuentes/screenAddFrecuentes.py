from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.utils import asynckivy as ak
from kivymd.uix.menu import MDDropdownMenu
import crud
import os

Builder.load_file(os.path.join("screens","screenAddFrecuentes","screenAddFrecuentes.kv"))

class ScreenAddFrecuentes(MDScreen):
    def showOpType(self):
        caller=self.ids.typeOp.ids.text_field
        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Ingresos",
            },
            {
                "viewclass": "OneLineListItem",
                "text": "Egresos",
            }
        ]
        MDDropdownMenu(
            caller=caller, items=menu_items,width_mult=6, position="bottom"
        ).open()

    def setType(self,value):
        self.ids.typeOp.text_field.text=value

    def showFrecuencia(self):
        caller=self.ids.frecuencia.ids.text_field
        menu_items = [
            {
                "text": "Mediados de mes",
                "on_release": lambda x:self.setFrecuencia('Mediados de mes'),
            },
            {
                "text": "Inicios/final de mes",
                "on_release": lambda x:self.setFrecuencia('Inicios/final de mes'),
            },
        ]
        MDDropdownMenu(
            caller=caller, items=menu_items,width_mult=4
        ).open()

    def setFrecuencia(self,value):
        self.ids.frecuencia.text_field.text=value