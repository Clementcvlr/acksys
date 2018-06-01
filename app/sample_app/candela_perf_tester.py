#! /usr/bin/env python
# -*- coding: utf-8 -*-

import telnetlib, re, time, select, os, sys, errno, paramiko, subprocess
from time import sleep
import shutil, json, logging, textwrap
from acksys_func import Ping, Get_SSH_Result, check_ssh, telnet
from scp import SCPClient
from pathlib2 import Path
from conf_template_updater import ConfUpdater
import threading

#Init de la config. A terme, cela sera récupéré par l'interface web
myconfig ={}
#TODO : Dans le form, ajouter 3 booleans a cocher pour chaque htmode que l'on souhaite tester
#Ou un selectfield multiple
myconfig['EUT'] = "192.168.100.20"
myconfig['test_id'] = "33"
myconfig['operator'] = "cc"
myconfig['htmode'] = "VHT80"
myconfig['wifi_card'] = "1"
myconfig['channels'] = ['149']
myconfig['attenuator'] = "39"
myconfig['mode'] = ['AP', 'Client']
myconfig['prot'] = "TCP"
myconfig['tid_ap'] = "TID_1-1-1-3"
myconfig['tid_client'] = "TID_1-1-2-3"
myconfig['tx_power'] = "10"
myconfig['reboot'] = False
myconfig['attn'] = ['340']
myconfig['attn_duration'] = "60000"
myconfig['countries'] = ['US']
myconfig['hwmode'] = "11ac"


#--------Configs template pour tester différents modes (HT20, HT40, VHT40, VHT80...)---

#Config pour 802.11ac 5Ghz - VHT80
myconfig_vht80 = myconfig.copy()
#Ne pas modifier la liste suivante:
myconfig_vht80['channels'] = ['36','52','100','116','149']
myconfig_vht80['htmode'] = "VHT80"
myconfig_vht80['hwmode'] = "11ac"
myconfig_vht80['test_id'] = "{0}_VHT80".format(myconfig_vht80['test_id'])

#Config pour 802.11ac 5Ghz - VHT40
myconfig_vht40 = myconfig.copy()
#Ne pas modifier la liste suivante:
myconfig_vht40['channels'] = ['36','44','52','60','100','108','116','124','132','149','157']
myconfig_vht40['htmode'] = "VHT40"
myconfig_vht40['hwmode'] = "11ac"
myconfig_vht40['test_id'] = "{0}_VHT40".format(myconfig_vht40['test_id'])

#Config pour 802.11ac 5Ghz - VHT20
myconfig_vht20 = myconfig.copy()
#Ne pas modifier la liste suivante:
myconfig_vht20['channels'] = ['36','40','44','48','52','56','60','64','100','104','108','112','116','120','124','128','132','136','140','149','153','157','161','165']
myconfig_vht20['htmode'] = "VHT20"
myconfig_vht20['hwmode'] = "11ac"
myconfig_vht20['test_id'] = "{0}_VHT20".format(myconfig_vht20['test_id'])

#--------------------------------------

#Config pour Canaux 5Ghz - HT40+  (a + n) (Above)
myconfig_ht40_5G = myconfig.copy()
#Ne pas modifier la liste suivante:
myconfig_ht40_5G['channels'] = ['36','44','52','60','100','108','116','124','132','149','157']
myconfig_ht40_5G['hwmode'] = "11na" # a + n
myconfig_ht40_5G['htmode'] = "HT40+"
myconfig_ht40_5G['test_id'] = "{0}_HT40+_5G".format(myconfig_ht40_5G['test_id'])

#Config pour Canaux 5Ghz - HT20
myconfig_ht20_5G = myconfig.copy()
#Ne pas modifier la liste suivante:
myconfig_ht20_5G['channels'] = ['36','40','44','48','52','56','60','64','100','104','108','112','116','120','124','128','132','136','140','149','153','157','161','165']
myconfig_ht20_5G['hwmode'] = "11na" # a + n
myconfig_ht20_5G['htmode'] = "HT20"
myconfig_ht20_5G['test_id'] = "{0}_HT20_5G".format(myconfig_ht20_5G['test_id'])

#--------------------------------------

#Config pour Canaux 2,4Ghz - HT40+  (g + n) (Above)
myconfig_ht40 = myconfig.copy()
myconfig_ht40['channels'] = ['1','2','3','4','5','6','7']
myconfig_ht40['hwmode'] = "11no" # g + n
myconfig_ht40['htmode'] = "HT40+"
myconfig_ht40['test_id'] = "{0}_HT40+_24G".format(myconfig_ht40['test_id'])

#Config pour Canaux 2,4Ghz - HT20
myconfig_ht20 = myconfig.copy()
myconfig_ht20['channels'] = ['1','2','3','4','5','6','7','8','9','10','11']
myconfig_ht20['hwmode'] = "11no" # g + n
myconfig_ht20['htmode'] = "HT20"
myconfig_ht20['test_id'] = "{0}_HT20_24G".format(myconfig_ht20['test_id'])

#--------------------------------------

#Init du logger
logger = logging.getLogger('main')
logger.setLevel(logging.DEBUG)


class CandelaChannelTester():
	def __init__(self, Config):
		#Creating Test dir
		my_file = Path("/tmp/candela_channel/" + str(Config['test_id']))
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
		self.Config = Config
		#self.stop_event = stop_event
		#threading.Thread.__init__(self)

	def run(self):
		#Show Config and print to file
		Config = self.Config
		print("\n----Config-----")
		for key, value in Config.items() :
        		print("{0} : {1}".format(key, value))
		self.print_conf(Config, "/tmp/candela_channel/" + str(Config['test_id']) + "/config.txt")

		#Creating Json File
		#json_str = self.InitJson(Config)
		#json_data = json.loads(json_str)
		#with open("/tmp/candela_channel/" + str(Config['test_id']) + "/" + "jsonfile.json", 'w') as f :
		#	json.dump(json_data, f)

		#Arret et suppression du GUI
		telnet("report /media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report NO")
		for f in os.listdir("/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report"):
			os.remove("/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report/" + f)  

		
		#Wait For Ping
		Ping(Config['EUT'])

			#Ajout de cross connect UDP
		#TODO : Cet ajout est fait de cette manière dans le .sh, voir si c'est utile...
#		telnet("add_endp 901_-_Test_ModeAP_APtoClient_UDP-A 1 1 2 lf_udp -1 Yes 0")
#		telnet("add_endp 902_-_Test_ModeAP_ClienttoAP_UDP-A 1 1 2 lf_udp -1 Yes 0")
		#Conversion de la liste de valeurs d'attenuation en format comprehensible par Candela
#		attn_list_cand = ','.join(Config['attn_list'])	
		#Creation du script d'attenuation
#		telnet("set_script " + str(Config['attenuator']) + " my_script NA ScriptAtten '"+ str(Config['attn_duration']) + " " + attn_list_cand + "' NA NA")

			

		#Creation des dossiers de resultat pour chaque canal
		folder_list = [ "01-ModeAP_UDP_APtoC",
				"02-ModeAP_UDP_CtoAP",
				"03-ModeAP_TCP_APtoC",
				"04-ModeAP_TCP_CtoAP",
				"05-ModeClient_UDP_APtoC",
				"06-ModeClient_UDP_CtoAP",
				"07-ModeClient_TCP_APtoC",
				"08-ModeClient_TCP_CtoAP"]
		#for folder_name in folder_list:
		#	self.create_folder('/tmp/candela_channel/' + Config['test_id'] + '/' + folder_name
		ssh = check_ssh(Config['EUT'], 'root')
		ssh.exec_command("uci set wireless.radio" + str(int(Config['wifi_card'])) + ".disabled=0 ; uci set wireless.radio" + str(int(Config['wifi_card'])) + "w0.ssid=TestEtValidationCandela ; uci set wireless.radio" + str(int(Config['wifi_card']))  + "w0.mode=" + str(Config['mode']) + " ; uci commit ; apply_config")
		ssh.close()

	
		ssh = check_ssh(Config['EUT'])
		#Set channel et 802.11 config par rapport à la config loadée
		#print("Configuring EUT for channel {0}".format(channel))
		#self.logger.debug("Configuring EUT with Channel {0}".format(channel))
		ssh.exec_command("uci set wireless.radio"+ 
				 str(Config['wifi_card']) +
				 ".channel="+ str(Config['channels']) +
				 " ; uci set wireless.radio" +
				 str(Config['wifi_card']) +
				 ".hwmode=" + Config['hwmode'] +
				 " ; uci set wireless.radio" +
				 str(Config['wifi_card']) +
				 ".htmode=" + Config['htmode'] +
				 " ; uci commit ; apply_config")
		#Sleep 8 : Wait network link up
		time.sleep(8)
		ssh.close()

		self.logger.debug("Loading " + str(Config['tid_ap']) + " OVERWRITE")
		print("\nLoading " + str(Config['tid_ap']) + " OVERWRITE")
		telnet("load " + str(Config['tid_ap']) + " OVERWRITE")
		cxmode = "AP"

		#Creation des Tests groups
		telnet("add_group 001")
		telnet("add_group 002")
		telnet("add_group 003")
		telnet("add_group 004")

		#Ajout des Cross Connects aux Tests Groups
		telnet("add_tgcx 001 001_-_Mode" + cxmode +"_APtoClient_UDP")
		telnet("add_tgcx 002 002_-_Mode" + cxmode +"_ClienttoAP_UDP")
		telnet("add_tgcx 003 003_-_Mode" + cxmode +"_APtoClient_TCP")
		telnet("add_tgcx 004 004_-_Mode" + cxmode +"_ClienttoAP_TCP")


		for prot in Config['prot']:
			self.Start(Config,"001",cxmode)
			self.Start(Config,"002",cxmode)

		self.logger.debug("Loading " + str(Config['tid_client']) + " OVERWRITE")
		print("\nLoading conf CLient OVERWRITE")
		telnet("\nLoading " + str(Config['tid_client']) + " OVERWRITE")
		cxmode = "Client"

		#Creation des Tests groups
		telnet("add_group 001")
		telnet("add_group 002")
		telnet("add_group 003")
		telnet("add_group 004")

		#Ajout des Cross Connects aux Tests Groups
		telnet("add_tgcx 001 001_-_Mode" + cxmode +"_APtoClient_UDP")
		telnet("add_tgcx 002 002_-_Mode" + cxmode +"_ClienttoAP_UDP")
		telnet("add_tgcx 003 003_-_Mode" + cxmode +"_APtoClient_TCP")
		telnet("add_tgcx 004 004_-_Mode" + cxmode +"_ClienttoAP_TCP")

		for prot in Config['prot']:
			self.Start(Config,"003",cxmode)
			self.Start(Config,"004",cxmode)

			

			
		self.logger.debug("End of instance")
#def background_launcher(self):
	#	run_thread = threading.Thread(target=self.run)
    	#	run_thread.start()


	def csv_charts_creator(candela_report_path, chart_name):
		#Cette fonction va lire le fichier candela_report,
		#qui est le resultat du script de dichotomie,
		#Et va creer tous les fichier csv necessaires au post-traitement
		#Equivalent au resultat du graphical display du resultat du script
		with open(candela_report_path + "candela_report", "r") as f:
			mylist = [line.strip() for line in f]

		for line in mylist:
			if chart_name in line and (chart_name + " (No Constraints)") not in line:
				chart_spaces = []
					     
				for item in mylist[mylist.index(line) + 1 :len(mylist)]:
					if "</graph2d>" in item:
						break
					chart_spaces.append(item)
				  
		chart_csv = []
		for line in chart_spaces:
			chart_csv.append(line.replace('\t', ','))
		csv = open( candela_report_path + (chart_name.replace(' ','_')).replace('/','') + ".csv", "w")
		for a in chart_csv:
			csv.write(a + "\n")

	#Retourne la duee approximative du test en secondes ainsi que l'heure de fin associée
	def Estimated_duration(self, Config):
		dfs_channel_list = ["52","56","60","64","100","104","108","112","116","120","124","128","132","136","140"]
		dfs_chan_to_test_nb = 0 
		for channel in Config['channels']:
			if channel in dfs_channel_list:
				dfs_chan_to_test_nb += 1
		each_test_duration = (len(Config['attn_list']) *  ( int(Config['attn_duration']) / 1000 ))  
		print((each_test_duration * 45), len(Config['channels']), ( 60 * dfs_chan_to_test_nb ))
		estimated_duration = (((each_test_duration + 45) * 2 ) * len(Config['channels'])) + ( 60 * dfs_chan_to_test_nb )
		end_of_test = time.ctime(time.time() + estimated_duration)
		return estimated_duration, end_of_test	

	#Print la config dans un fichier conf_file et sur la sortie standard
	#Utilise textwrap pour une belle indentation de la conf
	#Modifier max_key_len et preferredWidth=60 si besoin
	def print_conf(self, Config, conf_file, max_key_len = 17, preferredWidth=60):
		self.logger.info("Writing Test Configuration to {0}".format(conf_file))

		with open(conf_file, 'w') as f:

			for key, value in Config.iteritems():

				nice_space = " " * (max_key_len - len(key))
				wrapper = textwrap.TextWrapper(initial_indent=key + nice_space + ":   ", width=preferredWidth,subsequent_indent=' '*len(key + nice_space + " "))
				f.write(wrapper.fill(str(value)) + "\n")
				print(wrapper.fill(str(value)))

	#Pas encore utilisée...
	def Get_Var_From_Form():
		#Mettre ChannelTesterForm(csrf_enabled=False) en paramètre au moment de l'appel
		form = form
		if form.is_submitted:
			print("a")	

	#Charge la configuration "conf" (exemple : "TID_1-1-1-3"). Attend 10 secondes pour que la conf soit chargée
	def load_config(conf):
		self.logger.debug("Loading Candela Conf :" + conf)
		print("Loading Candela Conf : " + conf)
		telnet("load " + conf + "OVERWRITE")
		time.sleep(10)


	#Creer un dossier
	def create_folder(self, directory):
		try:
			self.logger.debug("Creating Directory : {0}".format( directory))
			print("Creating Directory : {0}".format( directory))

			os.mkdir(directory)

		except OSError, e:

			if e.errno == errno.EEXIST:
				self.logger.debug("Folder {0} already exists".format(directory))	
				print("Folder {0} already exists".format(directory))
	
	#Get Candela lanforge server version
	def get_lf_version(self):
		lfversion = re.findall(r'.* Version: ([a-z0-9._-]+) ' , str(telnet("version")))
		if lfversion :
			return lf_version


	#Recupère le résultat de la commande show_endpoints du candela
	#Verifie le status grace à un regex sur ce résultat
	def Get_Endpoint_Status(self, Endpoint):
		status = re.findall(r'.*Endpoint \[.+\] \(([A-Z_]+)', str(telnet("show_endpoints " + Endpoint)))
		if status :
			return status[0]

	#Permet d'initier le contenu du fichier json	
	def InitJson(self, Config):

		if Config['mode'] == "BOTH":
			mode_list = ['ap', 'client']
		else :
			mode_list = [ Config['mode'] ]
		if Config['prot'] == "BOTH":
			prot_list = ['UDP', 'TCP']
		else :
			prot_list = Config['prot']

		sens_list = ['AP_vers_Client', 'Client_vers_AP']
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

	#Fonction prinicipale de test
	def Start(self, Config, cand_id, cxmode):

		#Definition du sens et du Endpoint en fonction du test en cours (901, 902, 903 ou 904)
		endpoint_sens = { 
			"001" : ["AP_vers_Client","001_-_Mode" + cxmode + "_APtoClient_UDP", 'UDP'],
			"002" : ["Client_vers_AP","002_-_Mode" + cxmode + "_ClienttoAP_UDP", 'UDP'],
			"003" : ["AP_vers_Client","003_-_Mode" + cxmode + "_APtoClient_TCP", 'TCP'],
			"004" : ["Client_vers_AP","004_-_Mode" + cxmode + "_ClienttoAP_TCP", 'TCP']
			}
		sens = endpoint_sens[cand_id][0]
		endpoint = endpoint_sens[cand_id][1]
		cx_prot = endpoint_sens[cand_id][2]

		#Creation dossier resultat
		self.create_folder('/tmp/candela_channel/' + Config['test_id'] + '/' + endpoint)


		#Mise à jour du json
		#with open("/tmp/candela_channel/" + str(Config['test_id']) + "/" + "jsonfile.json", 'r+') as f :
		#	data = json.load(f)
		#	data[channel][Config['mode']][cx_prot][sens] = "In_Progress"
		#	f.seek(0)
		#	json.dump(data, f)
		#	f.truncate()

		#Arrêt de tous les Cross Connects
		telnet("stop_group_all")
		time.sleep(2)

		#Suppression du dossier reporting manager
		for f in os.listdir("/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report"):
                        os.remove("/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report/" + f)

		#Demarrage du reporting manager
		self.logger.debug("Starting reporting manager")
		print("Starting reporting...")
		telnet("report /media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report YES YES YES YES")
		time.sleep(4)

		#Configuration de l'atténuateur pour la detection de l'association  avec le cross connect
		self.logger.debug("Setting Attenuator {0}".format(Config['attenuator']))
		print("Setting Attenuator {0}".format(Config['attenuator']))
		telnet("set_attenuator 1 1 " + str(Config['attenuator']) + " all " + str(Config['attn']))

		#sleep 4 : Pour pallier à l'erreur telnet
		time.sleep(4)
		
		#Demarrage du Cross Connect
		telnet("start_group " + cand_id)


		#On verifie que le Cross Connect passe au status "RUNNING"
		#Tant que endpoint status est différent de "RUNNING" et que time < timeout (90s)
		timeout = time.time() + 90
		while str(self.Get_Endpoint_Status(endpoint + "-B")) != "RUNNING" and time.time() <  timeout :
			print("{0}: Cross Connect is {1}".format(time.strftime("%H:%M:%S"), self.Get_Endpoint_Status(endpoint + "-B")))
			time.sleep(0.5)

		#On quitte la fonction si le statut du cx n'est toujours pas "RUNNING" après le timeout de la boucle ci-dessus
		if self.Get_Endpoint_Status(endpoint + "-B") != "RUNNING":
#TODO ------> vvvv Specifique au bug Data Bus Error sur Railtrack vvvvv------------
			ssh = check_ssh(Config['EUT'])
			logread = Get_SSH_Result(ssh, "logread |grep 'Data bus error'")
			if logread:
				time.sleep(1)
				print("Error, Product crashed ('Data Bus error'), Rebooting and going to next test")
				self.logger.error("Product crashed for channel {0} , test {1}, rebooting".format(channel, cand_id))
				ssh.exec_command("reboot")
				ssh.close()
				telnet("stop_group " + cand_id)
				Ping(Config["EUT"])
				time.sleep(70)
#TODO ------> ^^^^^^ Cette partie est à retirer ^^^^^--------

			else :
				print("Error, the Cross Connect is Not Running, Rebooting and going to next test")
				self.logger.error("Status not 'RUNNING' for channel {0}, test {1} , rebooting".format(channel , cand_id))
				ssh.exec_command("reboot")
				ssh.close()
				telnet("stop_group " + cand_id)
				Ping(Config["EUT"])
				time.sleep(70)
				return
				
		else :
			
			self.logger.info("Test {0} - Channel is Running".format(cand_id,))

		#test_timeout = time.time() +  len(Config['attn_list']) *  ( int(Config['attn_duration']) / 1000 ) 		
		#while time.time() < test_timeout :
		if cx_prot == "UDP":
			#UDP
			while self.Get_Endpoint_Status(endpoint + "-B") == "RUNNING":
				#Afficher un compte à rebours sur la page Web...
				print(time.strftime("%H:%M:%S") + ": Test en cours : " + Config['test_id'] + " - " + cand_id )
				time.sleep(1)
				
			
		
		elif cx_prot == "TCP":
			test_timeout = time.time() + 3600
			while time.time() < test_timeout:
				print(time.strftime("%H:%M:%S") + ": Test en cours : " + Config['test_id'] + " - " + cand_id )
				time.sleep(1)
				
		#Arret du Cross Connect
		print("Stopping Candela test group")
		telnet("stop_group " + cand_id)

		
		#Arret du reporting manager
		telnet("report " + "/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report" + "NO") #TODO : Creer variable pour le chemin du gui


		#Mise à jour du json, statut done
		#with open("/tmp/candela_channel/" + str(Config['test_id']) + "/" + "jsonfile.json", 'r+') as f :
		#	data = json.load(f)
		#	data[channel][Config['mode']][cx_prot][sens] = "Done"
		#	f.seek(0)
		#	json.dump(data, f)
		#	f.truncate()
	

		#Copie des fichiers depuis dossier GUI
		#sleep 4  : Pour être sur que le cross connect est bien arrété et qu'il ne recréera pas de fichier     après l'arrêt du reporting manager
		time.sleep(4)
		#TODO : Remplacer /tmp/candela_channel par le vrai dossier de resultat
		cand_report_files = os.listdir('/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report')
		for f in cand_report_files:
			shutil.move("/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report/" + f, "/tmp/candela_channel/" + str(Config['test_id']) + "/" + cand_id + "/" + f)

		script_result = telnet("show_script_result {0}-A".format(endpoint))
		candela_report_attenuator = open("/tmp/candela_channel/" + str(Config['test_id']) + "/" + cand_id + "/candela_report","w") 
		#Pour test dichotomie UDP:
		#Creation des fichiers csv pour etre conforme avec le Res du Graphical Display 
		charts_to_save = [ 
		"Max Peer RX-Bits-per-second v/s Payload Size",
		"Max Peer RX-Bits-per-second (Low Level) v/s Payload Size",
		"Max TX-Bits-per-second v/s Payload Size",
		"Max Peer RX-PDUs-per-second v/s Payload Size",
		"Max Peer RX-Pkts-per-second (Low Level) v/s Payload Size"
		]

		for chart in charts_to_save :
			csv_charts_creator("/tmp/candela_channel/" + str(Config['test_id']) + "/" + cand_id + "/", chart)


a = CandelaChannelTester(myconfig)
a.run()

'''	

for country in myconfig['countries'] :
	for htmode in myconfig['htmodes'] :
		new_conf = ConfUpdater(myconfig, htmode, country).get_conf()
		a = CandelaChannelTester(new_conf)
		a.background_launcher()
'''		
#print("ICCCCIII")

#-----------Looping this test----------
#i = 1
#while True :
#	print("Loop number {0}".format(i))
#	a = CandelaChannelTester(myconfig)
#	i += 1
#--------------------------------------

'''
a = CandelaChannelTester(myconfig_vht80)
a = CandelaChannelTester(myconfig_vht40)
a = CandelaChannelTester(myconfig_vht20)

a = CandelaChannelTester(myconfig_ht20)
a a CandelaChannelTester(myconfig_ht20_5G)
'''

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



