import requests
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import requests_cache
import json
from config import URL_AGILE, API_KEY

requests_cache.install_cache('agile_cache')


def create_session(headers):
	session = Session()
	session.headers.update(headers)

	return session

# Funcion que recibe una API_KEY y devuelve su Token
def get_token():

	try:
		r = requests.post(URL_AGILE + 'auth', json={ "apiKey": API_KEY })
	except:
		return "Connection Error"

	# Chequeo que la conexion se establecio correctamente
	if r.status_code != 200:
		return r.status_code

	rJson = r.json()
	return rJson["token"]

# print(get_token("23567b218376f799415"))


# Funcion que devuelve una lista de todas las fotos recibidas de la API
def fetch_paginated_photo():

	try:
		pictures, total_page = fetch_photo_page(0)
	except:
		return f"We had a problem fetching the images, page : 0"

	all_pictures = []

	all_pictures += pictures
		# print(all_pictures)

	for page in range(1,4):

		try:
			pictures, total_page = fetch_photo_page(page)
			if pictures == False: return f"We had a problem fetching the images, page : {page}"
		except:
			return f"We had a problem fetching the images, page : {page}"

		all_pictures += pictures

	return all_pictures	

# Funcion que devuelve una lista con las imagenes de una pagina en particular y el total de paginas a iterar
def fetch_photo_page(page_num):

	token = get_token()

	url = f"{URL_AGILE}images?page={str(page_num)}"
	parameters = {
		
	}
	headers = {
		'Authorization' : f'Bearer {token}'
	}

	session = create_session(headers)

	try:
		response = session.get(url, params=parameters)
		data = json.loads(response.text) 
		
		return data['pictures'], data['pageCount']

	except (ConnectionError, Timeout, TooManyRedirects) as e:
			print(e)
			return False, False


# Funcion que devuelve un diccionario con el detalle de la foto
def fetch_picture_details(picture_id):

	token = get_token()

	url = F"{URL_AGILE}images/{picture_id}"

	headers = {
		'Authorization' : f'Bearer {token}'
	}

	session = create_session(headers)
	try:
		response = session.get(url)
		data = json.loads(response.text) 

		return data
	except (ConnectionError, Timeout, TooManyRedirects) as e:
		print(e)


# Buscar las fotos que tengan en su metadata la palabra buscada
def search_photo_by_tag(term):

	# Llevo la palabra a buscar a minuscula para evitar problemas de case sensitive en la comparacion
	lower_temp = term.lower()
	
	# voy a buscar las fotos de la base
	all_pictures = fetch_paginated_photo()
	if all_pictures == False: return "Error al intentar listar las fotos"

	all_details = []

	# me armo un contador para testear y no traer toda la info
	count = 0

	# me guardo el detalle de las fotos en una lista
	for picture in all_pictures:
		picture_details = fetch_picture_details(picture['id'])

		all_details += [picture_details]

		count +=1
		if count >10:
			break

	# me armo una lista con todos los detalles y el formato (id, metadataValue::tagName)
	tag_list = []
	for detailed in all_details:
		# print(detailed)
		image_id = detailed['id']
		for key, value in detailed.items():
			if key == 'id' : continue
			for word in value.split():
				tag_list.append((image_id,f"{word.replace('#','').lower()}::{key}"))

	# me armo una lista con los ID de las imagenes donde en alguno de sus tag tienen la palabra buscada
	images_id = set([image_id for (image_id, term) in tag_list if term.split(':')[0] == lower_temp])
	
	#me traigo el url de las fotos que cumplieron con la busqueda
	final_list = set([picture['cropped_picture'] for picture in all_pictures if picture['id'] in images_id])
	
	return final_list


print(search_photo_by_tag("beauty"))