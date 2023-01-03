import weakref
from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton as bt
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.animation import Animation
from kivymd.uix.expansionpanel import MDExpansionPanel,MDExpansionPanelTwoLine
import crud

balance=0
actual=''
ahorro=0
prestamo_selected=''
cards_init=['tarjeta']
buttons_init=[]

class Buttons(MDBoxLayout):
	def registro(self,operation):
		def clean_fields():
			self.dialog.content_cls.ids.monto.text=''
			self.dialog.content_cls.ids.descripcion.text=''
		
		def registrar(object):
			global prestamo_selected
			print(prestamo_selected)
		
		def cancelar(object):
			clean_fields()
			self.dialog.dismiss()
		
		for i in MDApp.root.ids:
			print(i)


class Cards(MDCard):
	pass

class Content(MDBoxLayout):
	pass

class Scr(MDBoxLayout):
	def validacion(self,field,text):
		if field=='monto':
			if '.' in text:
				try:
					float(text)
					return True
				except ValueError:
					return False
			else:
				return text.isnumeric()
		elif field=='descripcion':
			if not text=='':return True
			else: False
	
	def trasladar_quincena(self,direction):
		global actual,balance
		balance=0
		a=crud.quince_actual('valor',direction,actual)
		self.ids.quincena.text=crud.translate_codigo(a)
		actual=a
		for operation in ('ingresos','egresos'):
			self.ids[operation].clear_widgets()
			data=crud.db.child('ingre_egre').child(actual).child(operation).get()
			if data.each() is None:
				pass
			else:
				for value in data.each():
					if operation=='ingresos':
						balance+=eval(value.val()['monto'])
						self.ids.ingresos.add_widget(TwoLineListItem(text='$'+value.val()['monto'],secondary_text=value.val()['descripcion']))
					elif operation=='egresos':
						balance-=eval(value.val()['monto'])
						self.ids.egresos.add_widget(TwoLineListItem(text='$'+value.val()['monto'],secondary_text=value.val()['descripcion']))
		self.ids.balance.text="Balance: ${:,.2f}".format(balance)


	def registro(self,operation):
		def clean_fields():
			self.dialog.content_cls.ids.monto.text=''
			self.dialog.content_cls.ids.descripcion.text=''
		
		def registrar(object):
			global balance, actual
			monto=self.dialog.content_cls.ids.monto.text
			descripcion=self.dialog.content_cls.ids.descripcion.text
			quincena=self.ids.quincena.text
			if self.validacion('monto',monto) and self.validacion('descripcion',descripcion):
				crud.db.child('ingre_egre').child(actual).child(operation).push({'monto':monto,'descripcion':descripcion})
				self.ids[operation].add_widget(TwoLineListItem(text='$'+self.dialog.content_cls.ids.monto.text,secondary_text=self.dialog.content_cls.ids.descripcion.text))
				clean_fields()
				if operation=='ingresos': balance+=eval(monto)
				elif operation=='egresos': balance-=eval(monto)
				self.ids.balance.text='Balance: '+"${:,.2f}".format(balance)
				self.dialog.dismiss()
			else:
				self.dialog.content_cls.ids.monto.error=True
				self.dialog.content_cls.ids.descripcion.error=True
		
		def cancelar(object):
			clean_fields()
			self.dialog.dismiss()
		
		self.dialog=MDDialog(
				title='Registrar '+operation,
				type='custom',
				content_cls=Content(),
				buttons=[
					bt(text='Cancelar',on_release=cancelar),
					bt(text='Registrar',on_release=registrar)]
			)
		self.dialog.open()

Builder.load_file('main.kv')

class Appson(MDApp):
	def build(self):
		return Scr()
	
	def on_start(self):
		#construyendo la pagina de las cuentas quincenales
		global balance
		global actual
		actual=crud.quince_actual('new')
		quincena_actual=crud.translate_codigo(actual)
		self.root.ids.quincena.text=quincena_actual
		for operation in ('ingresos','egresos'):
			data=crud.db.child('ingre_egre').child(actual).child(operation).get()
			if data.each() is None:
				pass
			else:
				for value in data.each():
					if operation=='ingresos':
						balance+=eval(value.val()['monto'])
						self.root.ids.ingresos.add_widget(TwoLineListItem(text='$'+value.val()['monto'],secondary_text=value.val()['descripcion']))
					elif operation=='egresos':
						balance-=eval(value.val()['monto'])
						self.root.ids.egresos.add_widget(TwoLineListItem(text='$'+value.val()['monto'],secondary_text=value.val()['descripcion']))
		self.root.ids.balance.text+="${:,.2f}".format(balance)

		#construyendo la pagina de ahorros
		for i in range(19):
			card=Cards()
			content = Buttons()
			card.add_widget(
				MDExpansionPanel(
					content=content,
					panel_cls=MDExpansionPanelTwoLine(text=f"{i}",secondary_text='descripcion'),
				)
			)
			self.root.ids.layout_fondo.add_widget(card)
	
	def prueba(self):
		for i in self.root.ids.layout_fondo.children:
			try:
				if i.children[-1].height>130:print(f'Sleccionado: {i.children[-1].panel_cls.text}')
			except:
				pass
	
		
if __name__=="__main__":
	Appson().run()