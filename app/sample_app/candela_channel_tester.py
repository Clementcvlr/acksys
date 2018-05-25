#! /usr/bin/env python
# -*- coding: utf-8 -*-

import telnetlib, re, time, select, os, sys, errno, paramiko, subprocess
from time import sleep
import shutil, json, logging, textwrapper
from acksys_func import Ping, Get_SSH_Result, check_ssh, telnet
from scp import SCPClient
from pathlib2 import Path

#Init de la config. A terme, cela sera récupéré par l'interface web
myconfig ={}
#TODO : Dans le form, ajouter 3 booleans a cocher pour chaque htmode que l'on souhaite tester
#Ou un selectfield multiple
myconfig['HT20'] = True
myconfig['HT40'] = True
myconfig['HT80'] = True
myconfig['EUT'] = "192.168.100.20"
myconfig['test_id'] = "31"
myconfig['operator'] = "cc"
myconfig['htmode'] = "HT20"
myconfig['wifi_card'] = "0"
myconfig['channels'] = [ '1','2','3','4','5','6','7','8','9','10','11','36','40','44','48','52','56','60','64','100','104','108','112','116','120','124','128','132','136','140','149','153','157''161','165' ]
myconfig['attenuator'] = "39"
myconfig['mode'] = "ap"
myconfig['prot'] = "TCP"
myconfig['tid_ap'] = "TID_1-1-1-3"
myconfig['tid_client'] = "TID_1-1-2-3"
myconfig['tx_power'] = "10"
myconfig['reboot'] = False
myconfig['attn_list'] = ['200', '300', '400', '500', '600', '700', '800']
myconfig['attn_duration'] = "60000"

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

		#Show Config and print to file
		print("\n----Config-----")
		for key, value in Config.items() :
        		print("{0} : {1}".format(key, value))
		self.print_conf(Config, "/tmp/candela_channel/" + str(Config['test_id']) + "/config.txt")

		#Estimation de la duree du test
		end_of_test = self.Estimated_duration(Config)
		print("\nEnd of Test (Estimated) : {0}".format(end_of_test[1]))
		self.logger.info("\nEnd of Test (Estimated) : {0}".format(end_of_test[1]))

		#Creating Json File
		json_str = self.InitJson(Config)
		json_data = json.loads(json_str)
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

		#Config Initiale de l'EUT (enable radio card, setting mode, SSID..)
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
			#Set channel et 802.11 config par rapport à la config loadée
			print("Configuring EUT for channel {0}".format(channel))
			self.logger.debug("Configuring EUT with Channel {0}".format(channel))
			#TODO : Change hwmode + htmode avec les entrees du form
			ssh.exec_command("uci set wireless.radio" + str(Config['wifi_card']) + ".channel="+ str(channel) +" ; uci set wireless.radio" + str(Config['wifi_card']) + ".hwmode=" + Config['hwmode'] + " ; uci set wireless.radio" + str(Config['wifi_card']) + ".htmode=" + Config['htmode'] + " ; uci commit ; apply_config")
			#Sleep 8 : Wait network link up
			time.sleep(8)
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
			prot_list = [ Config['prot'] ]

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
			data[channel][Config['mode']][cx_prot][sens] = "In_Progress"
			f.seek(0)
			json.dump(data, f)
			f.truncate()
		#Arret et suppression du GUI

		
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
		self.logger.debug("Starting reporting manager")
		print("Starting reporting...")
		telnet("report /media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report YES YES YES YES")
		time.sleep(4)

		#Configuration de l'atténuateur pour la detection de l'association  avec le cross connect
		self.logger.debug("Setting Attenuator {0}".format(Config['attenuator']))
		print("Setting Attenuator {0}".format(Config['attenuator']))
		telnet("set_attenuator 1 1 " + str(Config['attenuator']) + " all 400")

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
			
			self.logger.info("Test {0} - Channel {1} is Running".format(cand_id, channel))

		#Running script monitoring v1
		ssh = check_ssh(Config['EUT'])
		print("Running Script script.sh in EUT")
		ssh.exec_command("rm /usr/monitoring_v1/DATA/*")
		time.sleep(2)
		#TODO : Voir pour driver parametre driver du script... 
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
			print(time.strftime("%H:%M:%S") + ": Test en cours : " + Config['test_id'] + " - " + channel + " - " + cand_id )
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
		scp.get('/usr/monitoring_v1/DATA', '/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + cand_id + '/',  recursive=True)
		scp.close()
		ssh.close()
		time.sleep(1)

		#Deplacement de tous les fichiers du dossier DATA vers son dossier parent (Pour conformite avec macro excel)
		data_files = os.listdir('/tmp/candela_channel/' + Config['test_id'] +     '/' + channel + '/' + cand_id + '/DATA')
		for data_file in data_files :
			shutil.move('/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + cand_id + '/DATA/'+data_file, '/tmp/candela_channel/' + Config['test_id'] + '/' + channel + '/' + cand_id)

		
		shutil.rmtree('/tmp/candela_channel/' + Config['test_id'] + '/' + channel +     '/' + cand_id + '/DATA')
		telnet("report " + "/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report" + "NO") #TODO : Creer variable pour le chemin du gui


		#Mise à jour du json, statut done
		with open("/tmp/candela_channel/" + str(Config['test_id']) + "/" + "jsonfile.json", 'r+') as f :
			data = json.load(f)
			data[channel][Config['mode']][cx_prot][sens] = "Done"
			f.seek(0)
			json.dump(data, f)
			f.truncate()
	

		#Copie des fichiers depuis dossier GUI
		#sleep 4  : Pour être sur que le cross connect est bien arrété et qu'il ne recréera pas de fichier     après l'arrêt du reporting manager
		time.sleep(4)
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

#if myconfig['HT20']:

#if myconfig['HT40']:

#if myconfig['HT80']:


a = CandelaChannelTester(myconfig_vht80)
a = CandelaChannelTester(myconfig_vht40)
a = CandelaChannelTester(myconfig_vht20)

a = CandelaChannelTester(myconfig_ht20)
a = CandelaChannelTester(myconfig_ht20_5G)


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



