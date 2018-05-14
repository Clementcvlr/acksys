#! /usr/bin/env python
# -*- coding: utf-8 -*-
import telnetlib, re, time, select, os, sys, errno, paramiko, subprocess
from time import sleep
from shutil import copy

#execfile("config_py")

def Get_Var_From_Form():
	#Mettre ChannelTesterForm(csrf_enabled=False) en paramètre au moment de l'appel
	form = form
	if form.is_submitted
	

#Cette fonction permet d'attendre la connection SSH au produit
def check_ssh(ip, user, initial_wait=0, interval=2, retries=10):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    sleep(initial_wait)

    for x in range(retries):
        try:
	    print("1")
            #ssh.connect(ip, username=user, key_filename=key_file)
            ssh.connect(ip, username=user)
	    print("SSH Ok")
            return ssh
        except Exception, e:
            print e
            sleep(interval)
    print("Not Ok")
    return False

def Set_Sens_Endp(test_id):

        mycase = { 
                "901" : ["AP_vers_Client", "901_-_Test_Mode" + cxmode + "_APtoClient_UDP"],
                "902" : ["Client_vers_AP","902_-_Test_Mode" + cxmode + "_ClienttoAP_UDP"],
                "903" : ["AP_vers_Client","903_-_Test_Mode" + cxmode + "_APtoClient_TCP"],
                "904" : ["Client_vers_AP","904_-_Test_Mode" + cxmode + "_ClienttoAP_TCP"]
                }   




#Envoie une commande telnet telnet et retourne la sortie standard de la commande
def telnet( cmd, host="192.168.1.100", port=4001, prompt_line="default@btbits>>"):
        tn = telnetlib.Telnet(host, port)

        tn.read_until(prompt_line)
        tn.write(cmd + "\n")
	time.sleep(0.5)
        tn.write("exit\n")

        return tn.read_all()
#Charge la configuration "conf" (exemple : "TID_1-1-1-3"). Attend 10 secondes pour que la conf soit chargée
def load_config(conf):

	telnet("load " + conf + "OVERWRITE")

	time.sleep(10)

def create_folder(directory):
	try:

    		os.mkdir(directory)

	except OSError, e:

    		if e.errno == errno.EEXIST:
			answer = raw_input("Folder already exists, continue? ")
			if answer == "O":
			
				print("continue")
			else:
				sys.exit(0)
		else :
        		raise("Error while creating folder")



def Get_SSH_Result(ssh_session, cmd=None, stin=None, stout=None, sterr=None):
        if cmd is not None:
                stdin, stdout, stderr = ssh_session.exec_command(cmd)
        else:
                #If cmd is None, args stin, stout, sterr MUST be defined previously
                #This can be useful for getting data from a continuous ssh stream
                stdin, stdout, stderr = stin, stout, sterr
        while True:
        # Only print data if there is data to read in the channel
                if stdout.channel.recv_ready():
                        rl, wl, xl = select.select([stdout.channel], [], [], 0.0)
                        if len(rl) > 0:
                                # Print data from stdout
                                output = stdout.channel.recv(1024),
                                if output == (): 
                                        continue
                                else:
                                        break
                else:
                        time.sleep(0.01)
        return output

def Ping(EUT, timeout=400):

        start = time.time()
        while time.time() < start + timeout :

                response = os.system("ping -c 1 " + EUT)
                if response == 0:
                        return True
                else:
                        time.sleep(0.2)

        return False

def Get_Endpoint_Status(Endpoint):


	status = re.findall(r'.*Endpoint \[.+\] \(([A-Z_]+)', telnet("show_endpoints " + Endpoint))

	if status :
		return status[0]
	#else :
		#raise("No Match in Get_Endpoint_Status Fonction")




def Start(cand_id, cxmode):

	#Definition du sens et du Endpoint en fonction du test en cours (901, 902, 903 ou 904)
	endpoint_sens = { 
                "901" : ["AP_vers_Client", "901_-_Test_Mode" + cxmode + "_APtoClient_UDP"],
                "902" : ["Client_vers_AP","902_-_Test_Mode" + cxmode + "_ClienttoAP_UDP"],
                "903" : ["AP_vers_Client","903_-_Test_Mode" + cxmode + "_APtoClient_TCP"],
                "904" : ["Client_vers_AP","904_-_Test_Mode" + cxmode + "_ClienttoAP_TCP"]
                }
	endpoint = endpoint_sens[cand_id][0]
	sens = endpoint_sens[cand_id][1]

	#Open SSH Session	
	ssh_session = check_ssh(EUT)
	
	#On reboot l'EUT si requis par le formulaire (Reboot_request est un boolean)
	if reboot_request :
		#TODO:Voir si stdin, stdout, stderr sont utiles
		stdin, stdout, stderr = ssh_session.exec_command("reboot")


	#Arrêt de tous les Cross Connects
	telnet("stop_group_all")

	#Suppression du dossier reporting manager
	os.remove("/media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_test/GUI_report/*")

	#Demarrage du reporting manager
	telnet("report /media/data/TESTS_ET_VALIDATION/ISO700/003_-_Tests_en_cours/004_-_Scripts_de_t    est/GUI_report YES YES YES YES")

	#Configuration de l'atténuateur pour la detection de l'association  avec le cross connect
	telnet("set_attenuator 1 1 " + attenuateur  + " all 400")
	time.sleep(0.5)
	telnet("set_attenuator 1 1 " + attenuateur  + " all START")
	
	#Demarrage du Cross Connect
	telnet("start_group " + cand_id)


	#On verifie que le Cross Connect passe au status "RUNNIN"
	timeout = time.time() + 40
	while Get_Endpoint_Status(endpoint + "-B") != "RUNNING" or time.time() <  timeout :
		time.sleep(0.3)

	if Get_Endpoint_Status(endpoint) != "RUNNING":
	
		raise("The cross connect didn't start before timeout")


	#if prot == "UDP" and dicho == "0":
		#TODO

	#Lancement du script d'atténuation si besoin
	if len(attn) > 1 :
		telnet("set_attenuator 1 1 " + attenuator + " all START")

	#Détermination du temps de l'essai	
	test_timeout = time.time() - ( len(attn) * ( attn_duration / 1000 ) )
	
	while time.time() < test_timeout :
		#Afficher un compte à rebours sur la page Web
		
	#Récupération du fichier candela_report_attenuator Si besoin
	
	if prot != "UDP" or dicho != "0":
		#TODO : Change testfile.txt to result path...
		script_result = telnet("show_script_result")
		candela_report_attenuator = open(“testfile.txt”,”w”) 
		candela_report_attenuator.write(script_result)		
 	
	#Arret du Cross Connect
	telnet("stop_group " + cand_id)

	#Arret du script de monitoring sur EUT
	ssh_session.exec_command("killall script.sh")	
	
	#Lancement du script de récupération des DATAS de l'EUT
	#TODO: Remplacer sleep.sh par le vrai PATH du script de recup. Voir si on peut pas copier directement le script à la racine de l'app...
	subprocess.call("sleep.sh/" + chan + "/" + cand_id , shell=True)
	#sleep  : Pour être sur que le cross connect est bien arrété et qu'il ne recréera pas de fichier     après l'arrêt du reporting manager
	time.sleep(4)
	telnet("report " + gui_path_cand + "NO") #TODO : Creer variable pour le chamin du gui


	#TODO: COPIE DES FICHIERS DEPUIS DOSSIER GUI
}








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



