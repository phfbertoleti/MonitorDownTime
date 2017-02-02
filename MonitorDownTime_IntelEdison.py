import httplib
import urllib
import os
import time
import mraa
import pyupm_i2clcd as lcd

#variaveis globais
ContaTwetterDoSeuProvedorDeInternet = "@NEToficial"
NomeDaSuaCidade = "Sao Bernardo do Campo - SP"
APIKeyThingSpeak = 'KKKKKKKKKKKKKKKK'   #substitua KKKKKKKKKKKKKKKK pela sua api_key
WriteAPIKey = 'WWWWWWWWWWWWWWWW'   #substitua WWWWWWWWWWWWWWWW pela sua write api key do seu canal

#Downtime monitor variables
TimestampInicial_DownTime = 0
EstaOffline = 0
DownTimeTotal = 0
ArquivoRelatorioDowntime = "DownTimeReport.txt"
NumeroDowntimesDetectados = 0
NumeroTentativas = 1

def VerificaERegistraDowntime(res):
	global EstaOffline
	global TimestampInicial_DownTime
	global DownTimeTotal
	global ArquivoRelatorioDowntime
	global NumeroDowntimesDetectados
	global NumeroTentativas

	if (res == 0):
		print " "
		print "Internet esta on!"
	else:
		print " "
		print "Internet esta off..."

        #Verifica se internet estava on e agora esta off
	if ((res!=0) and (EstaOffline == 0)):
		TimestampInicial_DownTime = time.time()
		EstaOffline = 1
	        return

        #Verifica se internet estava off e agora esta on
	if ((res == 0) and (EstaOffline == 1)):
		DownTimeTotal = time.time() - TimestampInicial_DownTime
		
		if (DownTimeTotal > (1800)):  #se maior que 30min, deve ser descontada da fatura
			StringDT =  "DownTime detectado (>30min): "+str(DownTimeTotal)+" segundos offline\n"
		else:	
			StringDT =  "DownTime detectado (<30min): "+str(DownTimeTotal)+" segundos offline\n"
	        print StringDT
		TxtFile = open(ArquivoRelatorioDowntime,"a")
		TxtFile.write(StringDT)
		TxtFile.close()
        	NumeroDowntimesDetectados = NumeroDowntimesDetectados + 1
		EstaOffline = 0
		EscreveDowntimesDisplay()
	        EnviaTweet(DownTimeTotal)
		EnviaDownTimeThingSpeak(DownTimeTotal)
		return

def EnviaTweet(DuracaoDT):
	global ContaTwetterDoSeuProvedorDeInternet
	global NomeDaSuaCidade
	global APIKeyThingSpeak
        
        
        StringParaTwettar = ContaTwetterDoSeuProvedorDeInternet+", foi detectado um downtime de "+str(DuracaoDT)+" segundos. Estou na cidade de "+NomeDaSuaCidade+". #DownTimeDetectado"
	params = urllib.urlencode({'api_key': APIKeyThingSpeak, 'status': StringParaTwettar})  
	conn = httplib.HTTPConnection("api.thingspeak.com:80")
	try:
		conn.request("POST","/apps/thingtweet/1/statuses/update",params)
		resp = conn.getresponse()
		conn.close()
	except: 
		print "Falha na requisicao HTTPS"

def EnviaTweetDownTimeIniciado():
	global APIKeyThingSpeak

    	StringParaTwettar = "Monitor de DownTime iniciado!"
	params = urllib.urlencode({'api_key': APIKeyThingSpeak, 'status': StringParaTwettar})  
	conn = httplib.HTTPConnection("api.thingspeak.com:80")
	try:
		conn.request("POST","/apps/thingtweet/1/statuses/update",params)
		resp = conn.getresponse()
		conn.close()
	except:
		print "Falha na requisicao HTTPS"

def EnviaDownTimeThingSpeak(DuracaoDT):	  	
	global WriteAPIKey

	params = urllib.urlencode({'field1': str(DuracaoDT),'key':WriteAPIKey})
    	headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
	conn = httplib.HTTPConnection("api.thingspeak.com:80")
	try:
    		conn.request("POST", "/update", params, headers) # Tenta fazer uma requisicao
		resp = conn.getresponse()
		conn.close()
	except:
		print "Falha na requisicao HTTPS"		

def EscreveDowntimesDisplay():
	global NumeroDowntimesDetectados
	global lcdDisplay

	lcdDisplay.clear()
	lcdDisplay.setColor(60,200,247)
	lcdDisplay.setCursor(0, 0)
	lcdDisplay.write("Total: ")	
	lcdDisplay.setCursor(0, 8)
	lcdDisplay.write(str(NumeroDowntimesDetectados))
	return

#----------------------
#  PROGRAMA PRINCIPAL
#----------------------

time.sleep(20)  #tempo para o Linux subir todos os servicos necessarios a execucao dest projeto

lcdDisplay = lcd.Jhd1313m1(0, 0x3E, 0x62)     #Configura e inicializa comunicacao com display LCD
     	                                      #0x3E: endereco i2c do controlador LCD 
					      #0x62: endereco i2c do controlador responsavel pelo RGB 

EscreveDowntimesDisplay()
EnviaTweetDownTimeIniciado()

while True:
	try:
		os.system("clear")
       		print "---------------------------"
	    	print "     DownTime Monitor      "
      		print "---------------------------"
	        print " "
		print "Tentativa #"+str(NumeroTentativas)+" - "+str(NumeroDowntimesDetectados)+" downtime(s) detectados"
	        print " "

		PingResult = os.system("ping -c 1 8.8.8.8")
	        VerificaERegistraDowntime(PingResult)
		time.sleep(20) 
      		NumeroTentativas = NumeroTentativas + 1
	except (KeyboardInterrupt):
		print "Aplicacao encerrada."
		exit(1)
