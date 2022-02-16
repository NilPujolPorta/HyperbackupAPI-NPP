import json
from lib2to3.pgen2.token import OP
import time
from datetime import datetime
import datetime
from os.path import exists
import os

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
import cv2 
import pytesseract
import argparse
import mysql.connector
import yaml
import wget
import keyboard

__version__ ="0.0.1"

def main(args=None):
	ruta = os.path.dirname(os.path.abspath(__file__))
	rutaJson = ruta+"/dadesHyperBackup.json"
	parser = argparse.ArgumentParser(description='')
	parser.add_argument('-q', '--quiet', help='Nomes mostra els errors i el missatge de acabada per pantalla.', action="store_false")
	parser.add_argument('--json-file', help='La ruta(fitxer inclos) a on es guardara el fitxer de dades json. Per defecte es:'+rutaJson, default=rutaJson, metavar='RUTA')
	parser.add_argument('-tr','--tesseractpath', help='La ruta fins al fitxer tesseract.exe', default=ruta+'/tesseract/tesseract.exe', metavar='RUTA')
	parser.add_argument('-g', '--graphicUI', help='Mostra el navegador graficament.', action="store_false")
	parser.add_argument('-v', '--versio', help='Mostra la versio', action='version', version='HyperBackupAPI-NPP v'+__version__)
	args = parser.parse_args(args)
	conf = ruta +"/config/config.yaml"
	if not(os.path.exists(ruta+"/config")):
		os.mkdir(ruta+"/config")
	if not(os.path.exists(ruta+"/errorLogs")):
		os.mkdir(ruta+"/errorLogs")
	if not(os.path.exists(ruta+"/chromedriver.exe")):
		wget.download("https://github.com/NilPujolPorta/HyperbackupAPI-NPP/blob/master/HyperBackupAPI/chromedriver.exe?raw=true", ruta+"/chromedriver.exe")
		print()

	if not(exists(conf)):
		print("Emplena el fitxer de configuracio de Base de Dades a config/config.yaml")
		article_info = [
			{
				'BD': {
				'host' : 'localhost',
				'user': 'root',
				'passwd': 'patata'
				}
			}
		]

		with open(conf, 'w') as yamlfile:
			data = yaml.dump(article_info, yamlfile)

	with open(conf, "r") as yamlfile:
		data = yaml.load(yamlfile, Loader=yaml.FullLoader)

	servidor = data[0]['BD']['host']
	usuari = data[0]['BD']['user']
	contrassenya = data[0]['BD']['passwd']

	try:
		mydb =mysql.connector.connect(
			host=servidor,
			user=usuari,
			password=contrassenya,
			database="Hyperbackup"
			)
		mycursor = mydb.cursor(buffered=True)
		print("Access BDD correcte")
	except:
		try:
			mydb =mysql.connector.connect(
				host=servidor,
				user=usuari,
				password=contrassenya
				)
			print("Base de dades no existeix, creant-la ...")
			mycursor = mydb.cursor(buffered=True)
			mycursor.execute("CREATE DATABASE Hyperbackup")
			mydb =mysql.connector.connect(
				host=servidor,
				user=usuari,
				password=contrassenya,
				database="Hyperbackup"
				)
			mycursor = mydb.cursor(buffered=True)
			mycursor.execute("CREATE TABLE credencials (usuari VARCHAR(255), contassenya VARCHAR(255));")
		except:
			print("Login BDD incorrecte")
			return

	mycursor.execute("SELECT * FROM credencials")
	resultatbd = mycursor.fetchall()
	url = "https://insight.synology.com/login"
	if not(os.path.exists(ruta+"/tesseract")):
		os.mkdir(ruta+"/tesseract")
	if os.path.exists("C:\Program Files\Tesseract-OCR"):
		pytesseract.pytesseract.tesseract_cmd =("C:\\Program Files\\Tesseract-OCR\\tesseract.exe")
	elif not(os.path.exists(args.tesseractpath)):
		wget.download("https://github.com/NilPujolPorta/HyperbackupAPI-NPP/blob/master/HyperbackupAPI/tesseract-ocr-w64-setup-v5.0.0-rc1.20211030.exe?raw=true", ruta+"/tesseract-ocr-w64-setup-v5.0.0-rc1.20211030.exe")
		print()
		print("=========================================================")
		print("INSTALA EL TESSERACT EN LA CARPETA HyperBackupAPI/tesseract")##revisar
		print("=========================================================")
		time.sleep(20)
		os.popen(ruta+"/tesseract-ocr-w64-setup-v5.0.0-rc1.20211030.exe")
		return
	else:
		pytesseract.pytesseract.tesseract_cmd=(args.tesseractpath)

	options = Options()
	if args.graphicUI:
		#options.headless = True
		#options.add_argument('--headless')
		#options.add_argument('--disable-gpu')
		options.add_argument('window-size=1200x600')
	browser = webdriver.Chrome(executable_path= ruta+"/chromedriver.exe", options = options)
	browser.get(url)
	time.sleep(3)
	find_login = browser.find_elements_by_class_name("v-btn")
	for boto in find_login:
		print(boto)
		boto.click()
	time.sleep(10)
	#find_user = browser.find_element(by='name', value="email")	#ERROR
	#find_user.send_keys(resultatbd[0][0])						#ERROR
	keyboard.write(resultatbd[0][0])
	find_login = browser.find_elements_by_class_name("btn-primary")
	for boto in find_login:
		print(boto)
		boto.click()
	time.sleep(10)
	#find_passwd = browser.find_element(by='name', value="password")
	#find_passwd.send_keys(resultatbd[0][1])
	keyboard.write(resultatbd[0][1])
	find_login = browser.find_elements_by_class_name("btn-primary")
	for boto in find_login:
		print(boto)
		boto.click()
	time.sleep(10)

	find_login = browser.find_elements_by_class_name("NavigatorItem_level2_1Np-l")
	for boto in find_login:
		boto.click()
	time.sleep(10)


	################################--EXCTRACCIÓ DE DADES--##############################

	

if __name__ =='__main__':
    main()