#! /usr/bin/env python
# -*- coding: utf-8 -*-
import telnetlib, re, time, select, os, sys, errno, paramiko, subprocess
from time import sleep
import shutil, json
from acksys_func import Ping, Get_SSH_Result, check_ssh, telnet
from scp import SCPClient
from pathlib2 import Path
import logging

myconfig ={}
myconfig['EUT'] = "192.168.100.20"
myconfig['test_id'] = "12"
myconfig['operator'] = "cc"
myconfig['htmode'] = "VHT80"
myconfig['wifi_card'] = "0"
myconfig['channels'] = [ '1','2','3','4','5','6','7','8','9','10','11','36','40','44','48','52','56','60','64','100','104','108','112','116','120','124','128','132','136','140','149','161','165' ]
myconfig['attenuator'] = "39"
myconfig['mode'] = "ap"
myconfig['prot'] = "TCP"
myconfig['tid_ap'] = "TID_1-1-1-3"
myconfig['tid_client'] = "TID_1-1-2-3"
myconfig['tx_power'] = "10"
myconfig['reboot'] = False
myconfig['attn_list'] = ['200', '300', '400', '500', '600', '700', '800']
myconfig['attn_duration'] = "30000"


logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)


class CandelaChannelTester():
	def __init__(self, Config):
		my_file = Path("/tmp/candela_channel/" + str(Config['test_id']))
		#Creating Test dir
		if not my_file.is_dir():
			os.makedirs('/tmp/candela_channel/' + str(Config['test_id']))

		#Definition du logger pour ma classe et ajout d'un handler pour fichier de log
		formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
		self.logger = logging.getLogger('main.CandelaChannelTester')
		fh = logging.FileHandler("/tmp/candela_channel/" + str(Config['test_id']) + "/mylogfile.log")
		fh.setFormatter(formatter)
		fh.setLevel(logging.DEBUG)
		self.logger.addHandler(fh)
		#self.logger.info("Loop number {0}".format(i))

		print("\n----Config-----")
		for key, value in myconfig.items() :
        		print("{0} : {1}".format(key, value))
		#Creating Json File
		json_data = self.InitJson(Config)
		with open("/tmp/candela_channel/" + str(Config['test_id']) + "/" + "jsonfile.json", 'w') as f :
			json.dump(json_data, f)
		#Arret et suppression du GUI
		telnet("report /media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report NO")
		for f in os.listdir("/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report"):
			os.remove("/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report/" + f)  

		
		#Wait For Ping
		Ping(Config['EUT'])

		ssh = check_ssh(Config['EUT'], 'root')

		#Copie script Monitoring (Equivalent au script d'implantation monitoring_v1)
		ssh.exec_command("mkdir -p /usr/monitoring_v1/DATA")
		scp = SCPClient(ssh.get_transport()) 
		scp.put("script.sh", "/usr/monitoring_v1/script.sh")

		#Config de l'EUT
		self.logger.debug("Config de l'EUT par uci")
		ssh.exec_command("uci set wireless.radio" + str(int(Config['wifi_card'])) + ".disabled=0 ; uci set wireless.radio" + str(int(Config['wifi_card'])) + "w0.ssid=TestEtValidationCandela ; uci set wireless.radio" + str(int(Config['wifi_card']))  + "w0.mode=" + str(Config['mode']) + " ; uci commit ; apply_config")
		scp.close()
		ssh.close()

		if Config['mode'] == "ap" :
			self.logger.debug("Loading " + str(Config['tid_ap']) + " OVERWRITE")
			print("\nLoading " + str(Config['tid_ap']) + " OVERWRITE")
			telnet("load " + str(Config['tid_ap']) + " OVERWRITE")
			cxmode = "AP"
		else :
			self.logger.debug("Loading " + str(Config['tid_client']) + " OVERWRITE")
			telnet("\nLoading " + str(Config['tid_client']) + " OVERWRITE")
			cxmode = "Client"
		#Ajout de cross connect UDP
		#TODO : Cet ajout est fait de cette manière dans le .sh, voir si c'est utile...
		telnet("add_endp 901_-_Test_ModeAP_APtoClient_UDP-A 1 1 2 lf_udp -1 Yes 0")
		telnet("add_endp 902_-_Test_ModeAP_ClienttoAP_UDP-A 1 1 2 lf_udp -1 Yes 0")
		#Conversion de la liste de valeurs d'attenuation en format comprehensible par Candela
		attn_list_cand = ','.join(Config['attn_list'])	
		#Creation du script d'attenuation
		telnet("set_script " + str(Config['attenuator']) + " my_script NA ScriptAtten '"+ str(Config['attn_duration']) + " " + attn_list_cand + "' NA NA")

		#Creation des Tests groups
		telnet("add_group 901")
		telnet("add_group 902")
		telnet("add_group 903")
		telnet("add_group 904")

		#Ajout des COrss Connects aux Tests Groups
		telnet("add_tgcx 901 901_-_Test_Mode" + cxmode +"_APtoClient_UDP")
		telnet("add_tgcx 902 902_-_Test_Mode" + cxmode +"_ClienttoAP_UDP")
		telnet("add_tgcx 903 903_-_Test_Mode" + cxmode +"_APtoClient_TCP")
		telnet("add_tgcx 904 904_-_Test_Mode" + cxmode +"_ClienttoAP_TCP")
			


		#Demarrage de la boucle principale
		for channel in Config['channels']:
			
			self.logger.debug("Testing Channel {0}".format(channel))
			print("Channel :   {0}".format(channel))
			self.create_folder('/tmp/candela_channel/' + Config['test_id'] + '/' + channel)

			#Creation des dossiers de resultat pour chaque canal
			if str(Config['prot']) == 'UDP' :
				self.create_folder('/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + '901')
				self.create_folder('/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + '902')
			elif str(Config['prot']) == 'TCP' :
				self.create_folder('/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + '903')
				self.create_folder('/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + '904')
			elif str(Config['prot']) == 'Both' :
				self.create_folder('/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + '901')
				self.create_folder('/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + '902')
				self.create_folder('/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + '903')
				self.create_folder('/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + '904')
			
	                #TODO : Lancer le script monitoring dans le produit...
				
			ssh = check_ssh(Config['EUT'])
			#Set channel et 802.11 config sur EUT
			print("Configuring EUT for channel {0}".format(channel))
			if int(channel) < 15 :
				self.logger.debug("Configuring EUT with Channel {0}".format(channel))
				ssh.exec_command("uci set wireless.radio" + str(Config['wifi_card']) + ".channel="+ str(channel) +" ; uci set wireless.radio" + str(Config['wifi_card']) + ".hwmode=11no ; uci set wireless.radio" + str(Config['wifi_card']) + ".htmode=HT40+ ; uci commit ; apply_config")
			elif int(channel) > 15 :
			#TODO : Change hwmode + htmode avec les entrees du form
				self.logger.debug("Configuring EUT with Channel {0}".format(channel))
				ssh.exec_command("uci set wireless.radio" + str(Config['wifi_card']) + ".channel=" + str(channel) +" ; uci set wireless.radio" + str(Config['wifi_card']) + ".hwmode=11ac ; uci set wireless.radio" + str(Config['wifi_card']) + ".htmode=VHT80 ; uci commit ; apply_config")
			time.sleep(8)
			scp = SCPClient(ssh.get_transport()) 
        	        scp.get('/usr/monitoring_v1/', '/tmp/candela_channel/monitoring/', recursive=True)
			scp.close()

			ssh.close()
			
			#Set channel et 802.11 config sur candela
			#TODO : ajouter form pour wiphy0 et pour nombre antennes sur cand
			telnet("set_wifi_radio 1 1 wiphy0 8 " + str(channel))
			time.sleep(3)
			telnet("set_wifi_radio 1 1 wiphy0 8 " + str(channel) + " NA NA NA NA NA " + str(Config['tx_power']) + " NA 0")


			if Config['prot'] == 'TCP' :
				print("Start the Test 903")
				self.Start(Config, "903", cxmode, channel)
				print("Start the Test 904")
				self.Start(Config, "904", cxmode, channel)
			elif Config['prot'] == 'UDP' :

				
				print("Start the Test 901")
				self.Start(Config, "901", cxmode, channel)
				print("Start the Test 902")
				self.Start(Config, "902", cxmode, channel)
			else :
				print("Start the Test 903")
				self.Start(Config, "903", cxmode, channel)
				print("Start the Test 904")
				self.Start(Config, "904", cxmode, channel)
				print("Start the Test 901")
				self.Start(Config, "901", cxmode, channel)
				print("Start the Test 902")
				self.Start(Config, "902", cxmode, channel)
				print("End of test")
				
				self.logger.debug("End of instance")


############################################################################


	def Get_Var_From_Form():
		#Mettre ChannelTesterForm(csrf_enabled=False) en paramètre au moment de l'appel
		form = form
		if form.is_submitted:
			print("a")	

	#Envoie une commande telnet telnet et retourne la sortie standard de la commande
#Charge la configuration "conf" (exemple : "TID_1-1-1-3"). Attend 10 secondes pour que la conf soit chargée
	def load_config(conf):
		self.logger.debug("Loading Candela Conf :" + conf)
		print("Loading Candela Conf :" + conf)
		telnet("load " + conf + "OVERWRITE")
		time.sleep(10)

	def create_folder(self, directory):
		try:
			self.logger.debug("Creating Directory : {0}".format( directory))
			print("Creating Directory : {0}".format( directory))

			os.mkdir(directory)

		except OSError, e:

			if e.errno == errno.EEXIST:
				self.logger.debug("Folder {0} already exists".format(directory))	
				print("Folder {0} already exists".format(directory))
	#		else :
	#			raise("Error while creating folder")

	def Get_Endpoint_Status(self, Endpoint):


		status = re.findall(r'.*Endpoint \[.+\] \(([A-Z_]+)', str(telnet("show_endpoints " + Endpoint)))

		if status :
			return status[0]
		#else :
			#raise("No Match in Get_Endpoint_Status Fonction")

	
	def InitJson(self, Config):

		if Config['mode'] == "BOTH":
			mode_list = ['ap', 'client']
		else :
			mode_list = [ Config['mode'] ]
		if Config['prot'] == "BOTH":
			prot_list = ['UDP', 'TCP']
		else :
			prot_list = [ Config['prot'] ]

		sens_list = ['AP to Client', 'Client to AP']
		channel_list = Config['channels']
		

		data = {}

		for channel in channel_list:
			data[channel] = {}
			for mode in mode_list:
				data[channel][mode] = {}
				for prot in prot_list :
					data[channel][mode][prot] = {}
					for sens in sens_list:
						data[channel][mode][prot][sens] = "to do"



		data_json = json.dumps(data, indent=12)
		return data_json
				


	def Start(self, Config, cand_id, cxmode, channel):

		#Definition du sens et du Endpoint en fonction du test en cours (901, 902, 903 ou 904)
		endpoint_sens = { 
			"901" : ["AP_vers_Client", "901_-_Test_Mode" + cxmode + "_APtoClient_UDP", 'UDP'],
			"902" : ["Client_vers_AP","902_-_Test_Mode" + cxmode + "_ClienttoAP_UDP", 'UDP'],
			"903" : ["AP_vers_Client","903_-_Test_Mode" + cxmode + "_APtoClient_TCP", 'TCP'],
			"904" : ["Client_vers_AP","904_-_Test_Mode" + cxmode + "_ClienttoAP_TCP", 'TCP']
			}
		sens = endpoint_sens[cand_id][0]
		endpoint = endpoint_sens[cand_id][1]
		cx_prot = endpoint_sens[cand_id][2]

		#Mise à jour du json
		with open("/tmp/candela_channel/" + str(Config['test_id']) + "/" + "jsonfile.json", 'r+') as f :
			data = json.load(f)
			#TODO : Il faut créer une variable pour "mode" --> remplacer "ap" par cette variable.
			#data[channel]['ap'][cx_prot][sens] = "In Progress"
			#json.dump(data, f)
		#Arret et suppression du GUI



		#Open SSH Session	
		#ssh_session = check_ssh(Config['EUT'])
		
		#On reboot l'EUT si requis par le formulaire (Reboot_request est un boolean)
		if Config['reboot'] :
			ssh = check_ssh(Config['EUT'])
			ssh.exec_command("reboot")
			ssh.close()


		#Arrêt de tous les Cross Connects
		telnet("stop_group_all")
		time.sleep(2)

		#Suppression du dossier reporting manager
		for f in os.listdir("/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report"):
                        os.remove("/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report/" + f)


		#Demarrage du reporting manager
		self.logger.debug("Starting reporting...")
		print("Starting reporting...")
		telnet("report /media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report YES YES YES YES")
		time.sleep(4)

		#Configuration de l'atténuateur pour la detection de l'association  avec le cross connect
		self.logger.debug("Setting Attenuator {0}".format(Config['attenuator']))
		print("Setting Attenuator {0}".format(Config['attenuator']))
		telnet("set_attenuator 1 1 " + str(Config['attenuator']) + " all 400")
		#print("Starting Attenuators...")
		time.sleep(4)
		
		#Demarrage du Cross Connect
		telnet("start_group " + cand_id)


		#On verifie que le Cross Connect passe au status "RUNNING"
		#Tant que endpoint status est différent de "RUNNING" et que time < timeout (90s)
		timeout = time.time() + 90
		while str(self.Get_Endpoint_Status(endpoint + "-B")) != "RUNNING" and time.time() <  timeout :
			print("Cross Connect is {0}".format(self.Get_Endpoint_Status(endpoint + "-B")))
			time.sleep(0.5)

		#On quitte la fonction si le statut du cx n'est toujours pas "RUNNING" après le timeout de la boucle ci-dessus
		if self.Get_Endpoint_Status(endpoint + "-B") != "RUNNING":
#TODO ------> Cette partie est à retirer------------
			ssh = check_ssh(Config['EUT'])
			logread = Get_SSH_Result(ssh, "logread |grep 'Data bus error'")
			if logread:
				time.sleep(1)
				self.logger.error("Product crashed for channel {0} , test {1}, rebooting".format(channel, cand_id))
				ssh.exec_command("reboot")
				ssh.close()
#TODO ------> Cette partie est à retirer^^^^^--------
			else :
				self.logger.error("Status not 'RUNNING' for channel {0}, test {1} , rebooting".format(channel , cand_id))
				print("Error, the Cross Connect is Not Running, Rebbooting and going to next test")
				ssh.exec_command("reboot")
				ssh.close()
				telnet("stop_group " + cand_id)
				return
				
		else :
			
			self.logger.info("Test {0} - Channel {1} is Running".format(cand_id, channel))
		#Running script monitoring v1
		ssh = check_ssh(Config['EUT'])
		print("Running Script script.sh in EUT")
		ssh.exec_command("rm /usr/monitoring_v1/DATA/*")
		time.sleep(2)
		print("Radio_Card : ",str(Config['wifi_card']))
		ssh.exec_command("cd /usr/monitoring_v1 ; ./script.sh wlan{0} ath10k > /dev/null".format(str(Config['wifi_card'])))
		time.sleep(2)
		ssh.close()
		#if prot == "UDP" and dicho == "0":
			#TODO

		#Lancement du script d'atténuation 
		telnet("set_attenuator 1 1 " + str(Config['attenuator']) + " all START")

		#Détermination du temps de l'essai	
		test_timeout = time.time() +  len(Config['attn_list']) *  ( int(Config['attn_duration']) / 1000 ) 		
		while time.time() < test_timeout :
			#Afficher un compte à rebours sur la page Web...
			print("Test en cours : " + cand_id + " " + channel + " " + str(time.time()))
			time.sleep(1)
			
		#Récupération du fichier candela_report_attenuator Si besoin
		
		telnet("set_attenuator 1 1 " + str(Config['attenuator']) + " all STOP")
		time.sleep(1)
		if str(Config['prot']) != "UDP" or dicho != "0":
			#TODO : Change testfile.txt to result path...
			script_result = telnet("show_script_result 1.1.{0}".format(str(Config['attenuator'])))
			candela_report_attenuator = open("/tmp/candela_channel/" + str(Config['test_id']) + "/" + channel + "/" + cand_id + "/candela_report_attenuator","w") 
			candela_report_attenuator.write(script_result)		
		
		#Arret du Cross Connect
		print("Stopping Candela test group")
		telnet("stop_group " + cand_id)

		#Arret du script de monitoring sur EUT
		print("Stopping monitoring Script in EUT")
		ssh = check_ssh(Config['EUT'])
		time.sleep(1)
		ssh.exec_command("killall script.sh")	
		
		#Lancement du script de récupération des DATAS de l'EUT
		#TODO: Remplacer /tmp/candela... par le vrai PATH du script de recup. Voir si on peut pas copier directement le script à la racine de l'app...
		scp = SCPClient(ssh.get_transport()) 
		#TODO : Lancer le script monitoring dans le produit...
		scp.get('/usr/monitoring_v1/DATA', '/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + cand_id + '/',  recursive=True)
		scp.close()
		ssh.close()
		time.sleep(1)
		#Deplacement de tus les fichiers du dossier DATA vers son dossier parent
		data_files = os.listdir('/tmp/candela_channel/' + Config['test_id'] +     '/' + channel + '/' + cand_id + '/DATA')
		for data_file in data_files :
			shutil.move('/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + cand_id + '/DATA/'+data_file, '/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + cand_id)
		shutil.rmtree('/tmp/candela_channel/' + Config['test_id'] + '/' + channel +     '/' + cand_id + '/DATA')
		#sleep  : Pour être sur que le cross connect est bien arrété et qu'il ne recréera pas de fichier     après l'arrêt du reporting manager
		#time.sleep(4)
		telnet("report " + "/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report" + "NO") #TODO : Creer variable pour le chamin du gui

		#Update du fichier json avec le statut done pour le test fini

		#Mise à jour du json
		with open("/tmp/candela_channel/" + str(Config['test_id']) + "/" + "jsonfile.json", 'r+') as f :
			data = json.load(f)
			#TODO : Il faut créer une variable pour "mode" --> remplacer "ap" par cette variable.
			#data[channel]['ap'][cx_prot][sens] = "Done"
			#json.dump(data, f)
	

		#COPIE DES FICHIERS DEPUIS DOSSIER GUI
		#TODO : Remplacer /tmp/candela_channel par le vrai dossier de resultat
		cand_report_files = os.listdir('/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report')
		for f in cand_report_files:
			shutil.move("/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report/" + f, "/tmp/candela_channel/" + str(Config['test_id']) + "/" + channel +"/" + cand_id + "/")
	




#-----------Looping this test----------
#i = 1
#while True :
#	print("Loop number {0}".format(i))
#	a = CandelaChannelTester(myconfig)
#	i += 1
#--------------------------------------
a = CandelaChannelTester(myconfig)


#-----------------------------Ma LIB --------------------------------------
#-------COPIER FICHIER---------
#mydir = '/home/chevalier/flask/arma'
#for files in os.listdir('/home/chevalier/flask/arma'):
#        print( files)
#        shutil.copy(mydir + "/" + files, '/home/chevalier/flask/armb/' + files )


#---------CREATE FOLDER-------------
#create_folder("my_new_folder")
#create_folder("my_new_folder2")

#---------MOVE FILE----------------
#os.rename("my_new_folder/a", "my_new_folder2/a")

#---------DELETE FILE--------------
#os.remove("myfolder/a")

#---------CHECK_SSH------------------
#session = check_ssh("192.168.100.20","root", 0, 1 , 5)

#---------GET PRODUCT FIRMWARE VERSION
#version_firmware = Get_SSH_Result(session , "uci get ack_firmware.current.firmware_version")

#----------REBOOT---------------------
#stdin, stdout, stderr = session.exec_command("reboot")

#----------CANDELA CMD - TELNET-------
#status = telnet("show_endpoints tcp--1.eth4-01.sta10-B")

#---------CANDELA, GET CROSS CONNECT STATUS
#status = Get_Endpoint_Status("tcp--1.eth4-01.sta10-B")
#print(status)


#---------CHECK FOR PING--------------
#if Ping("192.168.100.21") :
#        print("Ping Ok")
#else :
#        print("Ping Nok")

#--------SHOW ENDPOINT ET SENS EN FONCTION DU TEST (901, 902, 903, 904)
#Set_Sens_Endp("901")
#Set_Sens_Endp("902")



