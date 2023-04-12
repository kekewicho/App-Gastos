from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.clock import Clock

#from screens.screenConcubinos.screenConcubinos import screenConcubinos
from screens.screenGastos.screenGastos import ScreenGastos
#from screens.screenFondo.screenFondo import screenFondo

'''
Nota importante: saber que para el caso de las cuentas quincenales, los ingresos y egresos si significan su valor literal
pero para el caso de las cuentas del ahorro, el calculo si se hace en referencia al monto del prestamo, es decir: un egreso
sería un abono a la cuenta y viceversa.
'''

KV='''
#:include screens\screenGastos\screenGastos.kv
#:include screens\screenFondo\screenFondo.kv
#:include screens\screenConcubinos\screenConcubinos.kv

MDNavigationLayout:
	ScreenManager:
		id:manager
		ScreenGastos:
		#screenFondo:
		#screenConcubinos
	MDNavigationDrawer:
		id:nav_drawer
		MDBoxLayout:
			orientation:'vertical'
			MDFloatLayout:
				size_hint_y:.05
			MDRectangleFlatIconButton:
				font_size:sp(20)
				halign:'left'
				size_hint_x:1
				icon: "sack"
				text: "Ahorros"
				theme_text_color: "Custom"
				text_color: "black"
				line_color: "white"
				theme_icon_color: "Custom"
				icon_color: "black"
				on_release:
					nav_drawer.set_state('close')
					scr_manager.current='fondo'
			MDRectangleFlatIconButton:
				font_size:sp(20)
				halign:'left'
				size_hint_x:1
				icon: "cash-multiple"
				text: "Cuentas quincenales"
				theme_text_color: "Custom"
				text_color: "black"
				line_color: "white"
				theme_icon_color: "Custom"
				icon_color: "black"
				on_release:
					nav_drawer.set_state('close')
					scr_manager.current='ingre_egre'
			MDRectangleFlatIconButton:
				font_size:sp(20)
				halign:'left'
				size_hint_x:1
				icon: "home-heart"
				text: "Casa Concubina"
				theme_text_color: "Custom"
				text_color: "black"
				line_color: "white"
				theme_icon_color: "Custom"
				icon_color: "black"
				on_release:
					nav_drawer.set_state('close')
					scr_manager.current='concubinos'
			MDFloatLayout:
'''

class Appson(MDApp):
	def build(self):
		return Builder.load_string(KV)
	
	def on_start(self):
		Clock.schedule_once(lambda x:self.root.ids.manager.get_screen("ScreenGastos").ingre_egre_init_consulta(),2)
		
	
if __name__=="__main__":
	Appson().run()
