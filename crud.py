import requests
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

config={
    'apiKey': os.getenv("API_KEY"),
    'authDomain': os.getenv("AUTH_DOMAIN"),
    'projectId': os.getenv("PROJECT_ID"),
    'storageBucket': os.getenv("STORAGE_BUCKET"),
    'messagingSenderId': os.getenv("MESSAGING_SENDER_ID"),
    'appId': os.getenv("APP_ID"),
    'databaseURL': os.getenv("DATABASE_URL")
    }

# Función para agregar un nuevo registro a la base de datos
def push(child,data):
    url = f"{config['databaseURL']}/{child}.json"
    response = requests.post(url, json=data)
    return response.json()

# Función para obtener un registro específico de la base de datos
def get(child):
    url = f"{config['databaseURL']}/{child}.json"
    response = requests.get(url)
    return response.json()

# Función para actualizar un registro específico de la base de datos
def update(child, data):
    url = f"{config['databaseURL']}/{child}.json"
    response = requests.patch(url, json=data)
    return response.json()

# Función para eliminar un registro específico de la base de datos
def remove(child):
    url = f"{config['databaseURL']}/{child}.json"
    response = requests.delete(url)
    return response.json()

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

