from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from widgets.widgets import OPItem
from kivymd.utils import asynckivy as ak
import crud
import os

Builder.load_file(os.path.join("screens","screenFrecuentes","screenFrecuentes.kv"))

class ScreenFrecuentes(MDScreen):

    itemsCount=0

    def on_enter(self):
        self.loadFrecuentes()

    def loadFrecuentes(self):
        async def loadFrecuentes():
            self.ids.ingresos.clear_widgets()
            self.ids.egresos.clear_widgets()

            data=crud.get("frecuentes/luis")

            if not data is None:
                for key,value in dict(data).items():
                    for subK,subV in value.items():
                        item = OPItem(
                            monto='$'+subV['monto'],
                            descripcion=subV['descripcion'],
                            key=subK,
                            op=key
                        )
                        self.ids[key].add_widget(item)
                        self.itemsCount+=1               
        ak.start(loadFrecuentes())

