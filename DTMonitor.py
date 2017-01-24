import httplib
import urllib
import os
import time
import pyping

#variaveis globais
ContaTwetterDoSeuProvedorDeInternet = "@NEToficial"
NomeDaSuaCidade = "Sao Bernardo do Campo - SP"
APIKeyThingSpeak = 'KKKKKKKKKKKKKKKK'   #substitua KKKKKKKKKKKKKKKK pela sua api_key

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
		print "Internet está on!"
	else:
		print " "
		print "Internet está off..."

    #Verifica se internet estava on e agora esta off
	if ((res!=0) and (EstaOffline == 0)):
		TimestampInicial_DownTime = time.time()
		EstaOffline = 1
        return

    #Verifica se internet estava off e agora esta on
	if ((res == 0) and (EstaOffline == 1)):
		DownTimeTotal = time.time() - TimestampInicial_DownTime
		StringDT =  "DownTime detectado: "+str(DownTimeTotal)+" segundos offline\n"
        print StringDT
		TxtFile = open(ArquivoRelatorioDowntime,"a")
		TxtFile.write(StringDT)
		TxtFile.close()
        NumeroDowntimesDetectados = NumeroDowntimesDetectados + 1
		EstaOffline = 0
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
	conn.request("POST","/apps/thingtweet/1/statuses/update",params)
	resp = conn.getresponse()
	conn.close()

def EnviaTweetDownTimeIniciado():
	global APIKeyThingSpeak

    StringParaTwettar = "Monitor de DownTime iniciado!"
	params = urllib.urlencode({'api_key': APIKeyThingSpeak, 'status': StringParaTwettar})  
	conn = httplib.HTTPConnection("api.thingspeak.com:80")
	conn.request("POST","/apps/thingtweet/1/statuses/update",params)
	resp = conn.getresponse()
	conn.close()
	
def EnviaDownTimeThingSpeak(DuracaoDT):	  	
	global APIKeyThingSpeak

	params = urllib.urlencode({'field1': str(DuracaoDT),'key': APIKeyThingSpeak})
    headers = {"Content-typZZe": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    conn.request("POST", "/update", params, headers) # Tenta fazer uma requisicao
    resp = conn.getresponse() # Recebe e imprimi na tela a resposta


#----------------------
#  PROGRAMA PRINCIPAL
#----------------------

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
	