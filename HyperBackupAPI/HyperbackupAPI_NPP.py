from __future__ import barry_as_FLUFL
import json
import time
from os.path import exists
import os

from selenium import webdriver 
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import pytesseract
import argparse
import mysql.connector
import yaml
import wget

__version__ ="0.1.0"

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
		options.headless = True
		options.add_argument('--headless')
		options.add_argument('--disable-gpu')
		options.add_argument('window-size=1720x980')
	browser = webdriver.Chrome(executable_path= ruta+"/chromedriver.exe", options = options)
	browser.get(url)
	time.sleep(3)
	find_login = browser.find_elements(by="class name", value="v-btn")
	for boto in find_login:
		boto.click()
		break
	time.sleep(10)
	actions = ActionChains(browser)
	actions.send_keys(resultatbd[0][0])
	actions.perform()

	find_login = browser.find_elements(by="class name", value="btn-primary")
	for boto in find_login:
		boto.click()
		break
	time.sleep(10)
	actions = ActionChains(browser)
	actions.send_keys(resultatbd[0][1])
	actions.perform()
	
	find_login = browser.find_elements(by="class name", value="btn-primary")
	for boto in find_login:
		boto.click()
		break
	time.sleep(10)

	find_login = browser.find_elements(by="class name", value="NavigatorItem_level2_1Np-l")
	for boto in find_login:
		boto.click()
		break
	time.sleep(10)


	################################--EXCTRACCIÓ DE DADES--##############################

	statusTots = browser.find_elements(by="class name", value='Card_statusCount_O6wZ9')
	arrayStatus = []
	for estatus in statusTots:
		pare = estatus.find_element(by="xpath", value='..')
		if  estatus.get_attribute("class") == pare.get_attribute('class'):
			time.sleep(0)
		else:
			arrayStatus.append(estatus.text)
	
	arrayNom = []
	nomTots = browser.find_elements(by="class name", value='Card_host_3CH4Z')
	for nom in nomTots:
		arrayNom.append(nom.text)


	arrayUs = []
	x= 1
	while x <= len(arrayNom):
		arrayUs.append(browser.find_elements(by="xpath", value='//*[@id="app"]/div[2]/div[2]/div[2]/div/div[3]/div['+str(x)+']/div/div[2]/div/div[2]/div/div[3]/p[2]/a')[0].text)
		x += 1

	arrayCopia = []
	expandir = browser.find_elements(by="class name", value="CollapseButton_root_2be8O")
	for fletxa in expandir:
		fletxa.click()
		time.sleep(1)
		copia=browser.find_elements(by="class name", value="content-cell")[4]
		arrayCopia.append(copia.text)
		fletxa.click()

	



	i = 0
	while i < len(arrayNom):
		print(arrayNom[i]+" |  Us "+arrayUs[i] + "  | Ultima copia "+ arrayCopia[i])
		print("Correctes: " + arrayStatus[i].split("\n")[0])
		print("Erronis: " + arrayStatus[i].split("\n")[1])
		print("Warnings: " + arrayStatus[i].split("\n")[2])
		print()
		i += 1

if __name__ =='__main__':
    main()