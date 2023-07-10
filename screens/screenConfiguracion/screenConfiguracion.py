from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
import os

Builder.load_file(os.path.join("screens","screenConfiguracion","screenConfiguracion.kv"))

class ScreenConfiguracion(MDScreen):
    pass