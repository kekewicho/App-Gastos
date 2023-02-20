from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton as bt
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.card import MDCard,MDCardSwipe
from kivymd.uix.expansionpanel import MDExpansionPanel,MDExpansionPanelTwoLine
from kivymd.uix.pickers import MDDatePicker
from kivy.properties import StringProperty
from kivy.utils import platform
from kivymd.uix.card import MDSeparator
import crud

balance=0
actual=''
ahorro=0
prestamos_list={}

'''
Nota importante: saber que para el caso de las cuentas quincenales, los ingresos y egresos si significan su valor literal
pero para el caso de las cuentas del ahorro, el calculo si se hace en referencia al monto del prestamo, es decir: un egreso
sería un abono a la cuenta y viceversa.
'''

class OPItem(MDCardSwipe):
	monto=StringProperty()
	descripcion=StringProperty()

class ContentNvoPrestamo(MDBoxLayout):
	pass

class ContentFondo(MDBoxLayout):
	pass

class Buttons(MDBoxLayout):
	def refresh(self):
		global prestamos_list
		ahorrau=0
		for i in self.parent.parent.parent.children:
			if isinstance(i,MDCard):
				prestamo=(i.children[0].panel_cls.text).replace('Prestamo ','') if not 'tarjeta' in i.children[0].panel_cls.text else 'tarjeta'
				i.children[0].panel_cls.secondary_text='En esta cuenta: '+"${:,.2f}".format(prestamos_list[prestamo])
				ahorrau+=abs(prestamos_list[prestamo])
		self.parent.parent.parent.children[-1].children[0].text='Total ahorros: '+"${:,.2f}".format(ahorrau)
		

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
	
	def registro(self,operation,target):
		def clean_fields():
			self.dialog.content_cls.ids.monto.text=''
			self.dialog.content_cls.ids.descripcion.text=''
		
		def registrar(object):
			global prestamos_list,ahorro
			monto=self.dialog.content_cls.ids.monto.text
			descripcion=self.dialog.content_cls.ids.descripcion.text

			if self.validacion('monto',monto) and self.validacion('descripcion',descripcion):
				ahorro+=eval(monto) if self.operation=='ingresos' else eval(monto)*-1
				if 'tarjeta' in self.target:
					saldo=prestamos_list['tarjeta']+eval(monto) if self.operation=='ingresos' else prestamos_list['tarjeta']-eval(monto)
					crud.db.child('fondo').update({'tarjeta':str(saldo)})
					clean_fields()
					prestamos_list['tarjeta']=saldo
				else:
					saldo=prestamos_list[self.target]+eval(monto) if self.operation=='ingresos' else prestamos_list[self.target]-eval(monto)
					tarjeta=prestamos_list['tarjeta']+eval(monto) if self.operation=='ingresos' else prestamos_list['tarjeta']-eval(monto)
					crud.db.child('fondo').child('prestamos').child(self.target).child(self.operation).push({'fecha':descripcion,'monto':monto})
					crud.db.child('fondo').update({'tarjeta':str(tarjeta)})
					clean_fields()
					prestamos_list[self.target]=saldo
					prestamos_list['tarjeta']=tarjeta
				self.refresh()
				self.dialog.dismiss()

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
		self.operation=operation
		self.target=target.replace('Prestamo ','')
		self.dialog.content_cls.ids.descripcion.text=str(crud.datetime.date.today())

class Cards(MDCard):
	pass

class Content(MDBoxLayout):
	def show_calendar(self):
		date_dialog = MDDatePicker()
		date_dialog.bind(on_save=self.on_save,on_cancel=self.on_cancel)
		date_dialog.open()
    
	def on_save(self,instance,value,date_range):
		self.children[0].text=value.strftime('%Y-%m-%d')

	def on_cancel(self,instance,value):
		pass

class Scr(MDBoxLayout):
	def nuevo_prestamo(self):
		def clean_fields():
			self.dialog.content_cls.ids.descripcion.text=''
		
		def registrar(object):
			global prestamos_list
			nombre=self.dialog.content_cls.ids.descripcion.text
			crud.db.child('fondo').child('prestamos').child(nombre).set('')
			card=Cards()
			content = Buttons()
			card.add_widget(
				MDExpansionPanel(
				content=content,
				panel_cls=MDExpansionPanelTwoLine(text='Prestamo '+nombre,secondary_text='En esta cuenta: '+"${:,.2f}".format(0),
			)
			))
			self.ids.layout_fondo.add_widget(card)
			prestamos_list[nombre]=0
			self.dialog.dismiss()
		
		def cancelar(object):
			clean_fields()
			self.dialog.dismiss()
		
		self.dialog=MDDialog(
				title='Nuevo préstamo',
				text='Nota: No uses la palabra "Prestamo"',
				type='custom',
				content_cls=ContentNvoPrestamo(),
				buttons=[
					bt(text='Cancelar',on_release=cancelar),
					bt(text='Registrar',on_release=registrar)]
			)
		self.dialog.open()

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
			data=crud.db.child('ingre_egre').child(actual).child(operation).get() if platform!='macosx' else crud.db.child('joss/ingre_egre').child(actual).child(operation).get()
			if data.each() is None:
				pass
			else:
				for value in data.each():
					self.ids[operation].add_widget(MDSeparator())
					item=OPItem(monto='$'+value.val()['monto'],descripcion=value.val()['descripcion'])
					item.ids.btnDelete.on_release=lambda x=value.key():self.root.delete_op(x,operation,actual)
					item.ids.btnEdit.on_release=lambda x=value.key():self.root.edit_op(x,operation)
					if operation=='ingresos':
						balance+=eval(value.val()['monto'])
						self.ids.ingresos.add_widget(item)
					elif operation=='egresos':
						balance-=eval(value.val()['monto'])
						self.ids.egresos.add_widget(item)
		self.ids.balance.text="Balance: ${:,.2f}".format(balance)


	def registro(self,operation,edit=False):
		def clean_fields():
			self.dialog.content_cls.ids.monto.text=''
			self.dialog.content_cls.ids.descripcion.text=''
		
		def registrar(object):
			global balance, actual
			monto=self.dialog.content_cls.ids.monto.text
			descripcion=self.dialog.content_cls.ids.descripcion.text
			if self.validacion('monto',monto) and self.validacion('descripcion',descripcion):
				crud.db.child('ingre_egre').child(actual).child(operation).push({'monto':monto,'descripcion':descripcion}) if platform!='macosx' else crud.db.child('joss/ingre_egre').child(actual).child(operation).push({'monto':monto,'descripcion':descripcion})
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
		self.root.ids.lblUser.text+='Luisito!' if platform=='win' else 'Joselincita! <3'
		#construyendo la pagina de las cuentas quincenales
		global balance
		global actual
		actual=crud.quince_actual('new')
		quincena_actual=crud.translate_codigo(actual)
		self.root.ids.quincena.text=quincena_actual
		for operation in ('ingresos','egresos'):
			data=crud.db.child('ingre_egre').child(actual).child(operation).get() if platform!='macosx' else crud.db.child('joss/ingre_egre').child(actual).child(operation).get()
			if data.each() is None:
				pass
			else:
				for value in data.each():
					self.root.ids[operation].add_widget(MDSeparator())
					item=OPItem(monto='$'+value.val()['monto'],descripcion=value.val()['descripcion'])
					if operation=='ingresos':
						balance+=eval(value.val()['monto'])
						self.root.ids.ingresos.add_widget(item)
					elif operation=='egresos':
						balance-=eval(value.val()['monto'])
						self.root.ids.egresos.add_widget(item)
					item.ids.btnDelete.on_release=lambda x=value.key():self.delete_op(x,operation,actual,item)
					item.ids.btnEdit.on_release=lambda x=value.key():self.edit_op(x,operation,item)

		self.root.ids.balance.text+="${:,.2f}".format(balance)

		if platform=='macosx':return None

		#construyendo la pagina de ahorros
		global ahorro,prestamos_list
		tarjeta=crud.db.child('fondo').child('tarjeta').get()
		prestamos=crud.db.child('fondo').child('prestamos').get()
		ahorro+=eval(tarjeta.val())
		prestamos_list['tarjeta']=eval(tarjeta.val())
		card=Cards()
		content = Buttons()
		card.add_widget(
			MDExpansionPanel(
				content=content,
				panel_cls=MDExpansionPanelTwoLine(text='En tarjeta del banco',secondary_text='En esta cuenta: '+"${:,.2f}".format(eval(tarjeta.val()))),
			)
		)
		self.root.ids.layout_fondo.add_widget(card)

		for i in prestamos.each():
			saldo=0
			for j in ('ingresos','egresos'):
				op=crud.db.child('fondo').child('prestamos').child(i.key()).child(j).get()
				if op.each() is None:
					pass
				else:
					for h in op.each():
						if j=='ingresos':saldo+=eval(h.val()['monto'])
						else: saldo-=eval(h.val()['monto'])
			card=Cards()
			content = Buttons()
			card.add_widget(
				MDExpansionPanel(
				content=content,
				panel_cls=MDExpansionPanelTwoLine(text='Prestamo '+i.key(),secondary_text='En esta cuenta: '+"${:,.2f}".format(saldo),
			)
			))
			ahorro+=abs(saldo)
			self.root.ids.layout_fondo.add_widget(card)
			prestamos_list[i.key()]=saldo
		self.root.ids.ahorrado.text='Total ahorrado: '+"${:,.2f}".format(ahorro)
	
	def delete_op(self,event,op,quincena,wdg):
		#a='joss/' if platform=='macosx' else ''
		#crud.db.child(f'{a}ingre_egre/{quincena}/{op}/{event}').remove()
		print(self.root.ids.egresos.remove_widget(wdg))
	
	def edit_op(self,event,operation,wdg):
		a='joss/' if platform=='macosx' else ''
		
		def clean_fields():
			self.dialog.content_cls.ids.monto.text=''
			self.dialog.content_cls.ids.descripcion.text=''
		
		def registrar(object):
			global balance, actual
			monto=self.dialog.content_cls.ids.monto.text
			descripcion=self.dialog.content_cls.ids.descripcion.text
			if self.validacion('monto',monto) and self.validacion('descripcion',descripcion):
				crud.db.child(f'{a}ingre_egre/{actual}/{operation}/{event}').update({'monto':monto,'descripcion':descripcion})
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

if __name__=="__main__":
	Appson().run()
