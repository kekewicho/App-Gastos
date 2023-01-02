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
import crud

balance=0
actual=''
ahorro=0
prestamo_selected=''
opened_card=[]

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
		
		self.dialog=MDDialog(
				title='Registrar '+operation,
				type='custom',
				content_cls=Content(),
				buttons=[
					bt(text='Cancelar',on_release=cancelar),
					bt(text='Registrar',on_release=registrar)]
			)
		self.dialog.open()

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
		def press_card(self):
			global prestamo_selected,opened_card
			if self.height==130:
				self.clear_widgets()
				anim=Animation(height=100,duration=.2)
				anim.start(self)
				monto=MDLabel(text='En esta cuenta:'+"${:,.2f}".format(tarjeta.val()),bold=True,font_size='15')
				nombre=MDLabel(text='En tarjeta del banco',bold=True,font_size='17')
				self.add_widget(nombre)
				self.add_widget(monto)
			else:
				self.add_widget(Buttons())
				anim=Animation(height=130,duration=.2)
				anim.start(self)
				prestamo_selected=str(self.id).replace('_',' ')
				opened_card.append(self.id)


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
		ahorro=0
		tarjeta=crud.db.child('fondo').child('tarjeta').get()
		prestamos=crud.db.child('fondo').child('prestamos').get()
		lo=MDBoxLayout(padding=15,orientation='vertical',id='tarjeta')
		card=MDCard(elevation=2,
			size_hint_y=None,
			height=100,
			ripple_behavior=True,
			orientation='vertical',
			id='tarjeta',
			padding=15
			)
		monto=MDLabel(text='En esta cuenta:'+"${:,.2f}".format(tarjeta.val()),bold=True,font_size='15')
		nombre=MDLabel(text='En tarjeta del banco',bold=True,font_size='17')
		card.add_widget(nombre)
		card.add_widget(monto)
		self.root.ids.layout_fondo.add_widget(card)
		card.bind(on_release=press_card)
		ahorro+=tarjeta.val()
		
		for i in prestamos.each():
			saldo=0
			for j in ('ingresos','egresos'):
				op=crud.db.child('fondo').child('prestamos').child(i.key()).child(j).get()
				for h in op.each():
					if j=='ingresos':saldo+=eval(h.val()['monto'])
				else: saldo-=eval(h.val()['monto'])
			
			_prestamo=i.key()
			card=MDCard(elevation=2,
				size_hint_y=None,
				height=100,
				ripple_behavior=True,
				orientation='vertical',
				id=_prestamo.replace(' ','_'),
				padding=15
				)
			monto=MDLabel(text='En esta cuenta:'+"${:,.2f}".format(saldo),bold=True,font_size='15')
			nombre=MDLabel(text='Prestamo '+i.key(),bold=True,font_size='17')
			card.add_widget(nombre)
			card.add_widget(monto)
			self.root.ids.layout_fondo.add_widget(card)
			card.bind(on_release=press_card)
			ahorro+=saldo

		self.root.ids.ahorrado.text+="${:,.2f}".format(ahorro)

		
if __name__=="__main__":
	Appson().run()