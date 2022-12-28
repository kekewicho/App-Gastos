import pyrebase
import datetime

config= {'apiKey': "AIzaSyBD8qc4Ram3_kt1428HK9xmfj3oicwxYjM",
'authDomain': "gastos-ea1a1.firebaseapp.com",
'databaseURL': "https://gastos-ea1a1-default-rtdb.firebaseio.com",
'projectId': "gastos-ea1a1",
'storageBucket': "gastos-ea1a1.appspot.com",
'messagingSenderId': "96103399217",
'appId':"1:96103399217:web:5f5916a04a8f441adcba10"}

firebase=pyrebase.initialize_app(config)

db=firebase.database()

def quince_actual(state,traslado='next',value='no'):
	if state=='new':
		# Obtener la fecha y hora actuales
		now = datetime.datetime.now()

		# Obtener el año, el mes y el día de la semana actuales
		year = now.year
		month = now.month
		weekday = now.weekday()

		# Calcular la quincena actual
		if now.day <= 15:
			quincena = 1
		else:
			quincena = 2

	elif state=='valor':
		year = int(value[:4])
		month = int(value[4:6])
		quincena = int(value[6:7])

	if traslado=='next':
		# Generar el código para la próxima quincena
		if quincena == 1:
			# Si estamos en la primera quincena, la próxima quincena será la segunda
			quincena = 2
		else:
			# Si estamos en la segunda quincena, la próxima quincena será la primera del mes siguiente
			quincena = 1
			month += 1
			if month > 12:
				# Si el mes siguiente es enero, el año también debe aumentar
				month = 1
				year += 1
	elif traslado=='previous':
		if quincena==2:
			quincena=1
		else:
			quincena=2
			month-=1
			if month<1:
				month=12
				year-=1

	# Generar el código para la próxima quincena
	codigo = f"{year:04d}{month:02d}{quincena}"

	return codigo

def translate_codigo(codigo=quince_actual('new')):
	import calendar
	
	año=codigo[:4]
	mes=calendar.month_name[int(codigo[4:6])]
	quincena=codigo[6:7]
	
	trans=quincena+'era de '+mes+' del '+año
	return trans
