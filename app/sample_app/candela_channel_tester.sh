#!/bin/bash
	
#CC le 06/05/2017
#Ce script a pour but de tester automatiquement tous les canaux (2.4Ghz et 5Ghz) des produits WiFi Acksys. Le matériel de test Candela CT-525 est utilisé. 
#Il est également utilisé pour les tests de validation de performance de WaveOs 

#----------------------------
#Prérequis : SSH doit être activé sur ce produit et l'accès doit être effectué sans mot de passe, en utilisant uniquement des paires de clé publiques privées. 
#Le script ssh_without_password.sh permet d'effectuer cet échange de clé automatiquement.
#----------------------------

#Récupération des données de configuration à partir du fichier config
#Ce fichier est à modifier pour chaque configuration d'essai

. config

#Attente de demarrage de l'EUT
function wait_for_ssh ()
{

while true;
do

  ssh root@$EUT 'echo SSH server ready' &>/dev/null
  if [ $? -eq 0 ]
  then
        echo -e "\n${pat}SSH server enable pour $EUT --------------- \n"
        sleep 3
        break
  fi

echo -en "\n${pat} Wait for SSH Server...\n"
sleep 1

done

}

#Définition de la fonction de reboot. A activer ou non dans le fichier de config --> $reboot_EUT
function reboot_EUT ()
{

#Reboot de l'EUT pour remettre à 0 le compteur de pulse DFS
echo -e "\n${pat}Reboot de l'EUT...\n"
ssh root@$EUT "reboot"

#On attend quelques secondes pour être sur que le client SSH verra le link-down du produit
sleep 3 

wait_for_ssh 

}

#Definition de la fonction permettant l'envoi de mail automatique
function sendmail ()
{

#Test de la presence de l'utilitaire mail-utils
if ! [ -x "$(command -v mailutils)" ]; then
	
	echo -e "\n${pat}Pas de serveur de mail--------\n"

else

	echo "$2" | mail -s "$1" $dest
	echo -e "\n${pat}Rapport de mail envoyé a ${dest}--------\n"

fi

}

#Définition de la fonction de test
function start ()
#-----------------------------------------------------------------------------------------------
{

#Definition du sens en fonction du paramètre passe a la fonction
case "$1" in
	"901")
		sens="AP_vers_Client"
		endp="901_-_Test_Mode${cxmode}_APtoClient_UDP"
	;;
	"902")
		sens="Client_vers_AP"
		endp="902_-_Test_Mode${cxmode}_ClienttoAP_UDP"
	;;
	"903")
		sens="AP_vers_Client"
		endp="903_-_Test_Mode${cxmode}_APtoClient_TCP"
	;;
	
	"904")
		sens="Client_vers_AP"
		endp="904_-_Test_Mode${cxmode}_ClienttoAP_TCP"
	;;
esac
	

if [ "$reboot_EUT" -eq "1" ]
then 

	reboot_EUT

fi

#Arrêt de tous les Tests Groups existants (Au cas ou le script avait ete arrete avant la fin)
echo -e "\n${pat}Arret de tous les cross_connects --------\n"
{ echo "stop_group all"; sleep 1; } | $cmd &>/dev/null
sleep 2
 
#Suppression du reporting manager
echo -e "${pat}Suppression du contenu dossier de reporting $gui_path_PC --------------------------"
rm $gui_path_PC/*

#Demarrage du reporting manager
echo -e "\n${pat}Demarrage du reporting manager------------------------\n"
{ echo "report $gui_path_cand YES YES YES YES"; sleep 1; } | $cmd &>/dev/null

#Configuration de l'atténuateur pour la detection de l'association  avec le cross connect
{ echo "set_attenuator 1 1 $attenuateur all 400"; sleep 1; } | $cmd &>/dev/null
{ echo "set_attenuator 1 1 $attenuateur all START"; sleep 1; } | $cmd &>/dev/null

#Lancement du Cross-connect
echo -e "\n${pat}Demmarrage du cross connect $1------------------------\n"
{ echo "start_group $1"; sleep 1; } | $cmd &>/dev/null

#On attend que le cross connect ai le status "RUNNING avant de lancer le script de monitoring
for i in `seq 1 $wait_cx` 

do

	#Lecture du status du Cross connect (STOPPED ou RUNNING) 
	status=`{ echo "show_endpoints ${endp}-B"; sleep 1; } | $cmd 2>/dev/null | sed -n '/Endpoint /s/.*[(]\([^,]*\).*$/\1/p'` 

	if [ "$status" = "RUNNING" ]

	then

		echo -e "\n${pat}Cross Connect $1 is $status, Ok------------------------\n"
		break

	fi

	echo -e "\n${pat}$i - Cross Connect $1 is $status...------------------------\n"
	fail_val=$i

done

#Si le Cross Connect n'est pas passé RUNNING au bout de wait_cx, on envoie un mail d'erreur et on quitte
if [ "$fail_val" == "$wait_cx" ]

then

	echo -e "\n${pat}ERREUR : Cross Connect $1 is $status------------------------\n"

	echo -e "\n${pat}Envoi du rapport d erreur a $dest------------------------\n"

	sendmail "ERREUR durant test canal $chan" "Cross Connect $1 is $status" 

	continue

fi


#Demarrage du script de monitoring sur l'EUT Si l'option est activée dans le fichier de config
echo -e "\n${pat}Demarrage du script de monitoring sur L'EUT------------------\n"
ssh root@$EUT "cd /usr/monitoring_v1 ; ./script.sh & sleep 1"


#--------------------------------TEST DU MODE UDP (Sans dichotomie)---------------------------------

#Création d'un tableau contenant les différents valeurs d'atténuation à tester
attn_tab=(`echo $attn |sed 's/,/ /g'`)

#Mode UDP sans dichotomie ( En utilisant les valeurs de tx renseignées dans tx_rate 
if [ $prot = "UDP" ] && [ $dicho = "0" ]

then

	echo -e "\n${pat}Détermination du tx_rate en fonction du sens (ApToClient ou ClientToAP----\n"
	if [ $1 = "901" ] 
	then
		tx_rate=(${tx_rate_901[@]})
	elif [ $1 = "902" ]
	then
		tx_rate=(${tx_rate_902[@]})
	fi

	echo -e "\n${pat}Configuration manuelle du débit UDP et de l'atténuation------------------\n"
	#Si la taille des tableaux tx_rate et attn n'est pas la même, on quitte (car 1 atténuation = 1 débit)
	if ! [ "${#attn_tab[@]}" == "${#tx_rate[@]}" ]
	then
		echo "Le nombre de paliers d'atténuation (${#attn_tab[@]} testé n'est pas le même que le nombre de Tx_rate testé (${#tx_rate[@]})"
		exit 1
	fi

	#Création de l'en-tête du fichier de rapport d'atténuation manuelle
	echo "Iteration,Attenuator,TimeStamp,Duration,Paused,Attenuation" >> $result_path/$chan/$1/candela_report_attenuator

	#Définition du temps d'attente avant de modifier le débit et l'atten. ( moins le temps d'exec de la boucle (environ 2.1 secondes))
	mysleep=$(echo "(($attn_duration/1000)) - 2.12" | bc )

	#Entrée dans la boucle de reglage manuel de l'atténuation (lancée en background)
	length=${#attn_tab[@]}
	for ((i=0;i<${length};i++))

	do
		echo "$i - Changement manuel : , ${tx_rate[$i]}bps, ${attn_tab[$i]}ddB"
		#Modification du débit Emis par $endp
        	{ echo "add_endp ${endp}-A 1 1 2 lf_udp 1 Yes ${tx_rate[$i]}"; sleep 1; } | $cmd &>/dev/null
       		#Modification manuelle de l'attenuation 
        	{ echo "set_attenuator 1 1 $attenuateur all ${attn_tab[$i]}"; sleep 1; } | $cmd &>/dev/null
        
        	sleep $mysleep
	
		#Ajout d'une ligne dans fichier candela_report_attenuator
		echo "$i,$attenuateur,`date +%s%3N`,$attn_duration,${attn_tab[$i]}" >> $result_path/$chan/$1/candela_report_attenuator
	done &

else

	#Lancement du script d'atténuation
	echo -e "\n${pat}Demarrage du script d'attenuation-----------------------------\n"
	{ echo "set_attenuator 1 1 $attenuateur all START"; sleep 1; } | $cmd &>/dev/null

fi

#-------------------------------------------------------------------

echo -e "\n${pat}`date +%Y_%m_%d_%H%M` -- Test du canal $chan $sens -------------\n"

#Détermination de la durée de l'essai (nombre de paliers d'atténuation * la durée de chaque palier)
duration=$((${#attn_tab[@]} * $((attn_duration/1000))))

#sleep $duration avec compte à rebours
until [ $duration -lt 0 ]
do 
	m=$((duration/60))
	s=$((duration%60))
	echo -en "${pat}Fin du test channel $chan - $sens dans $m:$s -------------\r" 
	let duration-=1
	sleep 1
done

#Recuperation du fichier candela_report_attenuator (Seulement si on ne teste pas UDP sans dicho
if ! [ $prot = "UDP" ] && [ $dicho = "0" ]
then
	echo -e "\n${pat}Recuperation du resultat du script d'attenuation vers fichier candela_report_attenuator\n"
	{ echo "show_script_result"; sleep 1; } | $cmd > $result_path/$chan/$1/candela_report_attenuator
fi


echo -e "\n${pat}Arret du cross_connect $1 --------\n"
{ echo "stop_group $1"; sleep 1; } | $cmd &>/dev/null

#Arrêt du script de monitoring script.sh dans l'EUT
echo -e "\n${pat}Arret du script de monitoring sur $EUT-------------------------------\n"
ssh root@$EUT "killall script.sh"

#Lancement du script de recuperation des datas de l'EUT
echo -e "\n${pat}Récupération des datas-------------------------------\n"
bash $recup_script_data_path /$chan/$1

#Note : Le script de recuperation des donnees copiera les données depuis le produit vers le dossier défini au début du script script_recuperation_data_candela.sh
#Note : Verifier l'adresse IP de l'EUT configurée dans le script de récupération

#sleep  : Pour être sur que le cross connect est bien arrété et qu'il ne recréera pas de fichier après l'arrêt du reporting manager
sleep 4 

echo -e "\n${pat}Arret du GUI reporting manager-------------------------------\n"
{ echo "report $gui_path_cand NO"; sleep 1; } | $cmd &>/dev/null

sleep 2 
#copie du reporting manager dans le dossier de resultat
cp $gui_path_PC/* $result_path/$chan/$1

#Suppression du reporting manager
echo -e "${pat}Suppression du contenu dossier de reporting $gui_path_PC --------------------------"
rm $gui_path_PC/*

}

#-------------------------------------MAIN--------------------------------------
#Test de la présence du fichier de config 
if ! [ -e config ]
then

	echo -e "\n${pat}ERREUR : Fichier de configuration "config"  non trouve, exit------------\n"
	exit 1

fi

#Test de la présence du fichier script.sh , dossier DATA et config dans /usr/monitoring_v1
ssh root@$EUT ls /usr/monitoring_v1* 1> /dev/null

if ! [ $? -eq 0 ]
then
        echo -e "\n${pat}Erreur : Pas de fichiers de monitoring dans l'EUT, Exit --------------- \n"
        exit 1
fi



#Modif Auto de chemin_resultat_essai dans script_recuperation_data_candela.sh
sed -i "s|\(chemin_dossier_essai=\).*|\1\"$result_path\"|" $recup_script_data_path 
if [ $? -ne 0 ]
then
	echo "Erreur : sed nok pour modif du script_recuperation_data_candela.sh"
	exit 1
fi

#Creation du dossier de test
if [ -d $result_path ]; then
	echo -e "\n${pat}Le dossier de resultat $result_path existe deja------------------\n"
	exit 1
else
	echo -e "\n${pat}Creation du dossier de resultat =  $result_path------------------\n"
	mkdir $result_path
fi


#Suppression du dossier reporting manager
echo -e "\n${pat}Suppression et Arret du dossier reporting manager------------------------\n"
{ echo "report $gui_path_cand NO"; sleep 1; } | $cmd &>/dev/null
rm $gui_path_PC/*

#Creation du fichier de log dans le dossier result_path
exec &> >(tee ${result_path}/script_log_`date +%Y_%m_%d_%H%M`.log)

#Affichage du fichier Config (pour trace dans fichier de log)
echo -e "\n${pat}Configuration : ------------\n"
cat config

#Récupération du nombre d'antennes et passage en format compréhensible par le candela (voir commande set_wifi_radio/antenna dans le cli user guide de candela http://www.candelatech.com/lfcli_ug.php )
case "$nbr_ant" in
        "1")
                nbr_ant="1"
        ;;
        "2")
                nbr_ant="4"
        ;;
        "3")
                nbr_ant="0"
        ;;
esac


#Configuration de l'EUT : Enable radio $wlan , cherge le mode $mode et change le SSID en TestEtValidationCandela
echo -e "\n${pat}Config du produit: Enable radio ${wlan}, mode ${mode}, SSID TestEtValidationCandela\n"
ssh root@$EUT "uci set wireless.radio${wlan}.disabled=0 ; uci set wireless.radio${wlan}w0.ssid=TestEtValidationCandela ; uci set wireless.radio${wlan}w0.mode=$mode ; uci commit ; apply_config"

wait_for_ssh 


#Chargement de la configuration 1-1-1-2 ou 1-1-2-2 en fonction du mode du produit
if [ $mode = "ap" ]
then
	
	echo -e "\n${pat}Load Candela Config $tid_ap (mode AP)-----------------------\n"
	{ echo "load $tid_ap OVERWRITE"; sleep 1; } | $cmd &>/dev/null
	cxmode="AP"
elif [ $mode = "sta" ]
then
	echo -e "\n${pat}Load Candela Config $tid_client (mode Client)--------------------\n"
	{ echo "load $tid_client OVERWRITE"; sleep 1; } | $cmd &>/dev/null
	cxmode="Client"
fi

sleep 6 

#A Modifier !!! (Modif du débit TX du test UDP)
{ echo "add_endp 901_-_Test_ModeAP_APtoClient_UDP-A 1 1 2 lf_udp -1 Yes 0"; sleep 1; } | $cmd &>/dev/null
{ echo "add_endp 902_-_Test_ModeAP_ClienttoAP_UDP-A 1 1 2 lf_udp -1 Yes 0"; sleep 1; } | $cmd &>/dev/null


#Creation du script d'attenuation
echo -e "\n${pat}Creation du script d'attenuation---------------------------\n"
{ echo "set_script $attenuateur my_script NA ScriptAtten '$attn_duration $attn' NA NA"; sleep 1; } | $cmd &>/dev/null


#Creation des Tests_groups sur le Candela (qui permettront de demarrer les Cross_Connects associés)
echo -e "\n${pat}Création des test_group---------------------------\n"
{ echo "add_group 901"; echo "add_group 902"; echo "add_group 903"; echo "add_group 904"; sleep 1; } | $cmd &>/dev/null


#Ajout des Cross Connects aux Tests_groups précédemment créés
{ echo "add_tgcx 901 901_-_Test_Mode${cxmode}_APtoClient_UDP"; sleep 1; } | $cmd &>/dev/null
{ echo "add_tgcx 902 902_-_Test_Mode${cxmode}_ClienttoAP_UDP"; sleep 1; } | $cmd &>/dev/null
{ echo "add_tgcx 903 903_-_Test_Mode${cxmode}_APtoClient_TCP"; sleep 1; } | $cmd &>/dev/null
{ echo "add_tgcx 904 904_-_Test_Mode${cxmode}_ClienttoAP_TCP"; sleep 1; } | $cmd &>/dev/null



#Affichage des canaux testés (référencés dans fichier de conf) 
echo -e "\n${pat}Liste des canaux references dans le fichier de conf: -------------------------\n"

for i in "${channel_list[@]}"

	do

	echo -ne "$i ; "

done 

#-------------------Demarrage de la boucle--------------------------

echo -e "\n\n${pat}Demarrage de la boucle--------------------------\n"

for t in "${channel_list[@]}"


do
chan=$t

echo -e "\n${pat}Création du dossier du canal $chan --------------------\n"

if [ ! -d $result_path/$chan ]; then
	mkdir $result_path/$chan
	if [ $prot = "UDP" ];then
		mkdir $result_path/$chan/901
		mkdir $result_path/$chan/902
	elif [ $prot = "TCP" ];then
		mkdir $result_path/$chan/903
		mkdir $result_path/$chan/904
	elif [ $prot = "BOTH" ];then
		mkdir $result_path/$chan/901
		mkdir $result_path/$chan/902
		mkdir $result_path/$chan/903
		mkdir $result_path/$chan/904
	fi
fi


echo -e "\n${pat}Configuration du canal $chan sur l'EUT et sur le Candela... ----------------\n"

#Changement du canal sur l'EUT via la commande UCI set, reglage du hwmode en fonction du canal testé . application de la config 
#Note : On doit pouvoir accéder à ssh sur le produit SANS MOT DE PASS (voir script ssh_without_password.sh dans 004_scripts_de_tests)


if (( $chan < 15 ))
then
	ssh root@$EUT "uci set wireless.radio${wlan}.channel=$chan ; uci set wireless.radio${wlan}.hwmode=11no ; uci set wireless.radio${wlan}.htmode=HT40 ; uci commit ; apply_config" 
elif (( $chan > 15 ))
then
	ssh root@$EUT "uci set wireless.radio${wlan}.channel=$chan ; uci set wireless.radio${wlan}.hwmode=$hwmode ; uci set wireless.radio${wlan}.htmode=$htmode ; uci commit ; apply_config" 
fi

sleep 8

#Chargement de la configuration de la carte radio du Candela
{ echo "set_wifi_radio 1 1 $cand_radio_card 8 $chan"; sleep 1; } | $cmd &>/dev/null
{ echo "set_wifi_radio 1 1 $cand_radio_card 8 $chan NA NA NA NA NA $tx_power NA $nbr_ant"; sleep 1; } | $cmd &>/dev/null 

case "${prot}" in
        "TCP")
#Démarrage du sens AP_vers_Client _ Appel de la fonction
start 903
#Démarrage du sens client_vers_AP _ Appel de la fonction
start 904

;;

        "UDP")
#Démarrage du sens AP_vers_Client _ Appel de la fonction
start 901
#Démarrage du sens client_vers_AP _ Appel de la fonction
start 902
        
;;

        "BOTH")
#Démarrage du sens AP_vers_Client _ Appel de la fonction
start 901
#Démarrage du sens client_vers_AP _ Appel de la fonction
start 902
#Démarrage du sens AP_vers_Client _ Appel de la fonction
start 903
#Démarrage du sens client_vers_AP _ Appel de la fonction
start 904        

;;

esac


done

echo "\n${pat}FIN DU TEST${pat}\n"
