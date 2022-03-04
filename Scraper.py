from operator import indexOf
from urllib import request
import requests
import bs4
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url_inicial='https://www.boe.es/boe/dias/2022/03/02/'

r=requests.get(url_inicial)
s=BeautifulSoup(r.text, 'lxml')

#metodo para recolectar las descripciones
def get_descripciones(url):
    r_item=requests.get(url)
    s_item=BeautifulSoup(r_item.text, 'lxml')
    listas_publicaciones=s_item.find('div', class_='enlacesDoc')
    lista_descripcion=listas_publicaciones.find('h3').get_text(strip=True)
    return lista_descripcion

#metodo para recolectar las urls de las publicaciones
def get_urls(soup):
    url_root='https://www.boe.es/boe/dias/2022/03/02/'
    listas_publicaciones=s.find('div', class_='sumario')
    lista_urls=listas_publicaciones.find_all('li', class_='puntoHTML')
    urls=[urljoin(url_root,x.find('a').get('href')) for x in lista_urls]
    return urls

#metodo para recolectar las id
def get_ids(url):
    r_item=requests.get(url)
    s_item=BeautifulSoup(r_item.text, 'lxml')
    contenedor = s_item.find('dl')
    columna_dd= contenedor.find_all('dd')
    id=columna_dd[3].text
    return id

#metodo para recolectar las provincias
def get_provincias(url):
    r_item=requests.get(url)
    s_item=BeautifulSoup(r_item.text, 'lxml')
    provinciasycomunidades=['Álava', 'Albacete', 'Alicante', 'Almería', 'Asturias', 'Ávila', 'Badajoz', 'Barcelona', 'Burgos', 'Cáceres', 'Cádiz', 'Cantabria',
    'Castellón', 'Ciudad Real', 'Córdoba', 'Cuenca', 'Gerona', 'Granada', 'Guadalajara', 'Guipúzcoa', 'Huelva', 'Huesca', 'Islas Baleares', 'Jaén',
    'La Coruña', 'La Rioja', 'Las Palmas', 'León', 'Lérida', 'Lugo', 'Madrid', 'Málaga', 'Murcia', 'Navarra', 'Orense', 'Palencia', 'Pontevedra', 
    'Salamanca', 'Santa Cruz de Tenerife', 'Segovia', 'Sevilla', 'Soria', 'Tarragona', 'Teruel', 'Toledo', 'Valencia', 'Valladolid', 'Vizcaya', 
    'Zamora', 'Zaragoza',"Andalucía", "Aragón", "Canarias", "Cantabria", "Castilla y León", "Castilla-La Mancha", "Cataluña", "Ceuta", 
    "Comunidad Valenciana", "Comunidad de Madrid", "Extremadura", "Galicia", "Islas Baleares", "La Rioja", "Melilla", "Navarra", "País Vasco", 
    "Principado de Asturias", "Región de Murcia"]
    contenedor = s_item.find('div', id='textoxslt')
    posibles_provincias = contenedor.find_all('p')
    nombres_provinciasycomunidades=[]
    for i in posibles_provincias:
        nombres_provinciasycomunidades.append(i.text.strip().split())
    
    localidades=[]

    for p in provinciasycomunidades:
        for n in nombres_provinciasycomunidades:       
            for o in n: 
                if re.search(p,o):
                    localidades.append(p)

    lugares=[]

    for l in localidades:
        if l not in lugares:
            lugares.append(l)
    return lugares

#metodo para recolectar los nombres propios
def get_firmas(url):
    r_item=requests.get(url)
    s_item=BeautifulSoup(r_item.text, 'lxml')
    contenedor = s_item.find('div', id='textoxslt')
    lista_nombres = contenedor.find_all('p', class_=re.compile('^firma'))
    firmas=[]
    for i in lista_nombres:
            firmas.append(i.text)   
    if len(firmas)>0:
        firmas.pop(1)
    return firmas

#metodo para recolectar las fechas
def get_fechas(url):
    r_item=requests.get(url)
    s_item=BeautifulSoup(r_item.text, 'lxml')
    contenedor = s_item.find('div', id='textoxslt')
    texto = contenedor.find_all('p', class_=re.compile('^parrafo'))
    posible_fecha='\d{1,2}?\s\w{1,2}?\s\w{3,9}?\s\w{1,2}?\s\d{4}?'
    posible_fecha2='\d{1,2}?(\/)\d{4}?'
    posible_fecha3='\d{1,2}?[\/\-]\d{4}?'
    fch=[]
    for i in texto:
        if re.search(posible_fecha,i.text):
            fch.append(re.search(posible_fecha,i.text).group().replace(u'\xa0', u' '))
        elif re.search(posible_fecha2,i.text):
            fch.append(re.search(posible_fecha2,i.text).group())
        elif re.search(posible_fecha3,i.text):
            fch.append(re.search(posible_fecha3,i.text).group())

    fechas=[]

    for f in fch:
        if f not in fechas:
            fechas.append(f)

    return fechas

#Creamos el esquema que va a contener el json
def esquema_scraper(url):
    content_book={}
    #id
    id=get_ids(url)
    if len(id)>0 :
        content_book['ID']=id
    else:
       content_book['ID']=None

    descripcion=get_descripciones(url)
    if len(descripcion)>0 :
        content_book['Descripción']=descripcion
    else:
       content_book['Descripción']=None

    if len(url)>0 :
        content_book['Url']=url
    else:
       content_book['Url']=None
    
    firmas=get_firmas(url)
    if len(firmas)>0 :
        content_book['Nombres']=firmas
    else:
       content_book['Nombres']=None

    lugares=get_provincias(url)
    if len(lugares)>0 :
        content_book['Lugares']=lugares
    else:
       content_book['Lugares']=None

    fechas=get_fechas(url)
    if len(fechas)>0 :
        content_book['Fecha']=fechas
    else:
       content_book['Fecha']=None

    return content_book

#creamos el archivo
archivo=[]
urls=get_urls(url_inicial)
for idx, u in enumerate(urls):
    print(f'Estamos trabajando en el scrapeo... Documentos scrapeados {idx}')
    archivo.append(esquema_scraper(u)) 

with open('ScraperBoe.json', 'w') as file:
    str(archivo).encode('utf-8')
    json.dump(archivo, file, ensure_ascii= False, indent= 4)
    print('Se ha creado el archivo "ScraperBoe.json"')