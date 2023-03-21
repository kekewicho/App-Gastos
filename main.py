from kivy.lang import Builder
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton as bt
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard,MDCardSwipe
from kivymd.uix.expansionpanel import MDExpansionPanel,MDExpansionPanelTwoLine
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

balance=0
actual=''
ahorro=0
prestamos_list={}

'''
Nota importante: saber que para el caso de las cuentas quincenales, los ingresos y egresos si significan su valor literal
pero para el caso de las cuentas del ahorro, el calculo si se hace en referencia al monto del prestamo, es decir: un egreso
sería un abono a la cuenta y viceversa.
'''

class BtmSheet(MDBoxLayout):
	def get_data(self):
		data={
			'quien':self.ids.quien.text,
			'cantidad':float(self.ids.cantidad.text)
		}
		return data

class OPItem(MDCardSwipe):
	monto=StringProperty()
	descripcion=StringProperty()
	op=StringProperty()
	key=StringProperty()

class ContentNvoPrestamo(MDBoxLayout):
	pass

class ContentFondo(MDBoxLayout):
	pass

class Buttons(MDBoxLayout):
	who='luis' if platform!='macosx' else 'joss'
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
			who='luis' if platform!='macosx' else 'joss'
			if self.validacion('monto',monto) and self.validacion('descripcion',descripcion):
				ahorro+=eval(monto) if self.operation=='ingresos' else eval(monto)*-1
				if 'tarjeta' in self.target:
					saldo=prestamos_list['tarjeta']+eval(monto) if self.operation=='ingresos' else prestamos_list['tarjeta']-eval(monto)
					crud.db.child(f'fondo/{who}').update({'tarjeta':str(saldo)})
					clean_fields()
					prestamos_list['tarjeta']=saldo
				else:
					saldo=prestamos_list[self.target]+eval(monto) if self.operation=='ingresos' else prestamos_list[self.target]-eval(monto)
					tarjeta=prestamos_list['tarjeta']+eval(monto) if self.operation=='ingresos' else prestamos_list['tarjeta']-eval(monto)
					crud.db.child(f'fondo/{who}').child('prestamos').child(self.target).child(self.operation).push({'fecha':descripcion,'monto':monto})
					crud.db.child(f'fondo/{who}').update({'tarjeta':str(tarjeta)})
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
	who='luis' if platform!='macosx' else 'joss'
	def nuevo_prestamo(self):
		def clean_fields():
			self.dialog.content_cls.ids.descripcion.text=''
		
		def registrar(object):
			global prestamos_list
			nombre=self.dialog.content_cls.ids.descripcion.text
			who='luis' if platform!='macosx' else 'joss'
			crud.db.child(f'fondo/{who}').child('prestamos').child(nombre).set('')
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
		Thread(target=self.trasladar_quincena_que(direction)).start()
	
	def trasladar_quincena_que(self,direction):
		global actual,balance
		balance=0
		a=crud.quince_actual('valor',direction,actual)
		self.ids.quincena.text=crud.translate_codigo(a)
		actual=a
		who='luis' if platform!='macosx' else 'joss'
		for operation in ('ingresos','egresos'):
			self.ids[operation].clear_widgets()
			data=crud.db.child(f'ingre_egre/{who}').child(actual).child(operation).get()
			if data.each() is None:
				pass
			else:
				for value in data.each():
					if operation=='ingresos':
						balance+=eval(value.val()['monto'])
						MDApp.get_running_app().ingre_egre_init_construction('ingresos',value)
					elif operation=='egresos':
						balance-=eval(value.val()['monto'])
						MDApp.get_running_app().ingre_egre_init_construction('egresos',value)
		self.ids.balance.text="Balance: ${:,.2f}".format(balance)


	def registro(self,operation,edit=False):
		def clean_fields():
			self.dialog.content_cls.ids.monto.text=''
			self.dialog.content_cls.ids.descripcion.text=''
		
		def registrar(object):
			global balance, actual
			monto=self.dialog.content_cls.ids.monto.text
			descripcion=self.dialog.content_cls.ids.descripcion.text
			who='luis' if platform!='macosx' else 'joss'
			if self.validacion('monto',monto) and self.validacion('descripcion',descripcion):
				a=crud.db.child(f'ingre_egre/{who}').child(actual).child(operation).push({'monto':monto,'descripcion':descripcion})
				self.ids[operation].add_widget(MDSeparator())
				self.ids[operation].add_widget(OPItem(
					monto='$'+self.dialog.content_cls.ids.monto.text,
					descripcion=self.dialog.content_cls.ids.descripcion.text,
					op=operation,
					key=a['name']
					))
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
	who='luis' if platform!='macosx' else 'joss'

	def build(self):
		return Scr()

	def ingre_egre_init_consulta(self):
		#construyendo la pagina de las cuentas quincenales
		global balance
		global actual
		who='luis' if platform!='macosx' else 'joss'
		for operation in ('ingresos','egresos'):
			data=crud.db.child(f'ingre_egre/{who}').child(actual).child(operation).get()
			if data.each() is None:
				pass
			else:
				for value in data.each():
					if operation=='ingresos':
						balance+=eval(value.val()['monto'])
						self.ingre_egre_init_construction('ingresos',value)
					elif operation=='egresos':
						balance-=eval(value.val()['monto'])
						self.ingre_egre_init_construction('egresos',value)
		self.update_balance("${:,.2f}".format(balance))

	@mainthread
	def update_balance(self,text):
		self.root.ids.balance.text+="${:,.2f}".format(balance)

	@mainthread
	def ingre_egre_init_construction(self,operation,value):
		self.root.ids[operation].add_widget(MDSeparator())
		item=OPItem(
			monto='$'+value.val()['monto'],
			descripcion=value.val()['descripcion'],
			key=value.key(),
			op=operation
			)
		self.root.ids[operation].add_widget(item)
	
	def fondo_init_consulta(self):
		#construyendo la pagina de ahorros
		global ahorro,prestamos_list
		tarjeta=crud.db.child(f'fondo/{self.who}').child('tarjeta').get()
		self.update_tarjeta(tarjeta)
		prestamos=crud.db.child(f'fondo/{self.who}/prestamos').get()
		ahorro+=eval(tarjeta.val())
		prestamos_list['tarjeta']=eval(tarjeta.val())
		for i in prestamos.each():
			saldo=0
			for j in ('ingresos','egresos'):
				op=crud.db.child(f'fondo/{self.who}').child('prestamos').child(i.key()).child(j).get()
				if op.each() is None:
					pass
				else:
					for h in op.each():
						if j=='ingresos':saldo+=eval(h.val()['monto'])
						else: saldo-=eval(h.val()['monto'])
			ahorro+=abs(saldo)
			prestamos_list[i.key()]=saldo
			self.fondo_init_construction(i.key(),saldo)
		self.update_ahorrado(ahorro)

	@mainthread
	def update_ahorrado(self,ahorro):
		self.root.ids.ahorrado.text='Total ahorrado: '+"${:,.2f}".format(ahorro)
	
	@mainthread
	def update_tarjeta(self,tarjeta):
		card=Cards()
		content = Buttons()
		card.add_widget(
			MDExpansionPanel(
				content=content,
				panel_cls=MDExpansionPanelTwoLine(text='En tarjeta del banco',secondary_text='En esta cuenta: '+"${:,.2f}".format(eval(tarjeta.val()))),
			)
		)
		self.root.ids.layout_fondo.add_widget(card)


	@mainthread
	def fondo_init_construction(self,key,saldo):
		card=Cards()
		content = Buttons()
		card.add_widget(
			MDExpansionPanel(
			content=content,
			panel_cls=MDExpansionPanelTwoLine(text='Prestamo '+key,secondary_text='En esta cuenta: '+"${:,.2f}".format(saldo),
		)
		))
		self.root.ids.layout_fondo.add_widget(card)

	
	def on_start(self):
		Thread(target=self.starting_queue).start()

	def starting_queue(self):
		global balance,actual
		actual=crud.quince_actual('new')
		quincena_actual=crud.translate_codigo(actual)
		self.modify_labels(quincena_actual)
		Thread(target=self.ingre_egre_init_consulta).start()
		if platform=='macosx':return None
		Thread(target=self.fondo_init_consulta).start()

	@mainthread
	def modify_labels(self,quincena):
		self.root.ids.lblUser.text+='Luisito!' if platform!='macosx' else 'Joselincita! <3'
		self.root.ids.quincena.text=quincena

	def delete_op(self,event,op,monto):
		global actual,balance
		a='joss' if platform=='macosx' else 'luis'
		crud.db.child(f'ingre_egre/{a}/{actual}/{op}/{event}').remove()
		monto=monto.replace('$','').replace(',','')
		print(op,monto)
		if op=='ingresos': balance-=eval(monto)
		if op=='egresos': balance+=eval(monto)
		self.root.ids.balance.text='Balance: '+"${:,.2f}".format(balance)
		
	
	def edit_op(self,event,operation,wdg):
		a='joss' if platform=='macosx' else 'luis'
		monto_before=eval((wdg.monto).replace('$','').replace(',',''))
		def clean_fields():
			self.dialog.content_cls.ids.monto.text=''
			self.dialog.content_cls.ids.descripcion.text=''
		
		def registrar(object):
			global balance, actual
			monto=self.dialog.content_cls.ids.monto.text
			descripcion=self.dialog.content_cls.ids.descripcion.text
			if self.root.validacion('monto',monto) and self.root.validacion('descripcion',descripcion):
				if monto_before==monto:self.dialog.dismiss();return None
				crud.db.child(f'ingre_egre/{a}/{actual}/{operation}/{event}').update({'monto':monto,'descripcion':descripcion})
				clean_fields()
				dif=abs(monto_before-eval(monto))
				if monto_before>eval(monto):
					if operation=='egresos':balance+=dif
					if operation=='ingresos':balance-=dif
				if monto_before<eval(monto):
					if operation=='egresos':balance-=dif
					if operation=='ingresos':balance+=dif
				self.root.ids.balance.text='Balance: '+"${:,.2f}".format(balance)
				wdg.monto=str("$"+monto)
				wdg.descripcion=descripcion
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
		self.dialog.content_cls.ids.monto.text=(wdg.monto).replace('$','').replace(',','')
		self.dialog.content_cls.ids.descripcion.text=wdg.descripcion
		self.dialog.open()
	

#-------------- FUNCIONES DE CONCUBINOS -----------------
	custom_sheet = MDCustomBottomSheet(screen=BtmSheet())
	gastos_concubinos=[]

	def addGastoConcubino(self,data):
		data=self.custom_sheet.screen.get_data()
		self.custom_sheet.close()
		key=crud.db.child('concubinos/gastos').push(data)
		self.gastos_concubinos.append(data)
		self.add_gasto_widget(data,key)
		Snackbar(text='Gasto guardado con éxito').open()
	
	def update_balance(self):
		balance_luis,balance_joss=0,0
		for i in self.gastos_concubinos:
			if i['quien']=='joss':
				balance_joss+=i['cantidad']
			if i['quien']=='luis':
				balance_luis+=i['cantidad']
		diferencia=abs(balance_luis-balance_joss)
		if balance_luis>balance_joss:
			self.root.ids.balanceConcubino.text=f'La yos le debe al yoryis {"${:,.2f}".format(diferencia)}'
		if balance_joss>balance_luis:
			self.root.ids.balanceConcubino.text=f'El yoryis le debe a la yos {"${:,.2f}".format(diferencia)}'
		if balance_joss==balance_luis:
			self.root.ids.balanceConcubino.text='Ahorita estan a mano, no pelien'
	
	@mainthread
	def add_gasto_widget(self,data,key):
		item=OPItem(monto="${:,.2f}".format(data['cantidad']),descripcion=f'Pagó {data["quien"]}')
		item.ids.btnDelete.on_release=lambda x=key:self.delete_gasto_concubino(x)
		item.ids.btnEdit.on_release=lambda x=key:self.edit_gasto_concubino(x)
	
	def delete_gasto_concubino(self,key):
		print(key)
	
	def edit_gasto_concubino(self,key):
		pass


if __name__=="__main__":
	Appson().run()
