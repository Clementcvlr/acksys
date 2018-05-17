#!/bin/ash

# Initialisation des constantes
# carte radio a monitorer
carte_radio=$1 

# driver de la carte radio 
driver=$2

#Vide si pas de synchronisation
IP_serv_ntp=""
nom_fichier_data_entete="monitoring_v1"
nom_fichier_conf_entete="conf_product"
nom_dossier_data="DATA"

# temps d'execution du script en minute
temps_script="60" 
echantillonnage="1"

# separateur fichier resultat
s=','

# separateur unite (virgule)
p='.'
# Synchronisation date server ntp
if [ ! -e $IP_serv_ntp ]; then
	ntpclient -h $IP_serv_ntp -c 1 -s >/dev/null
	#export TZ=GMT-1
fi
ln -sf localtime /usr/share/zoneinf<o/Europe/Paris /tmp/localtime

# valeurs generales
chemin=$(pwd)
date=$(date "+%Y/%m/%d %H:%M:%S")
date_nom_fichier=$(date "+%Y%m%d-%H%M%S")
if [ ! -e /mnt/product_serial_number  ]; then
	echo "Le numero de serie n'est pas indique dans le produit"
	#read retour
	#if [ $retour = "Y" ];then
	SN_produit="ND"
	#elif [ $retour = "N" ];then
	#	exit 1
	#fi
else
	SN_produit=$(cat /mnt/product_serial_number |sed -n '/product_serial_number=/{s/[^0-9-]*//p}')
fi
IP_produit=$(ifconfig |sed -n '/br-lan/,2p' |sed -n '/inet addr:/{s/[^0-9-]*//; s/ .*//p}') 
Product_ID=$(cat /etc/config/product |sed -n "/option 'product_id'\|option product_id/p" |cut -d " " -f3 |sed "s/'//g")


# adaptation et reglage de la carte radio 
if [ "$carte_radio" = "wlan0" ]; then
        phy="phy0"
elif [ "$carte_radio" = "wlan1" ]; then
        phy="phy1"
fi

#MAC_carte=$(cat /sys/kernel/debug/ieee80211/$phy/ath9k/base_eeprom |sed -n '/MacAddress:=/{s/[^0-9-]*//p}')
if [ "$driver" = "ath9k" ]; then
	MAC_carte=$(cat /sys/kernel/debug/ieee80211/$phy/$driver/base_eeprom |sed -n '/MacAddress/p' )
	MAC_carte=${MAC_carte##*: }
elif [ "$driver" = "ath10k" ];then
	
	MAC_carte=$(cat /sys/class/ieee80211/$phy/macaddress)
fi
cmd_pulse_dfs="/sys/kernel/debug/ieee80211/$phy/$driver/dfs_stats"


# fichier de resultat
nom_fichier_data=$nom_dossier_data'/'$nom_fichier_data_entete'_'$SN_produit'_'$date_nom_fichier'.csv'
echo $nom_fichier_data

nom_fichier_conf=$nom_dossier_data'/'$nom_fichier_conf_entete'_'$SN_produit'_'$date_nom_fichier'.tgz'
echo $nom_fichier_conf

# enregistrement de la configuration du produit
. /lib/lib_acksys/lib_acksys.sh; ackbackup_build_tarfile>$nom_fichier_conf 2>/dev/null 

# en-tete fichier de data
echo 'date: '$date 
echo 'date:'$s$date > $nom_fichier_data
echo 'chemin: '$chemin 
echo 'chemin:'$s$chemin >> $nom_fichier_data
echo 'Product_ID: '$Product_ID
echo 'Product_ID:'$s$Product_ID >> $nom_fichier_data
echo 'IP produit: '$IP_produit
echo 'IP produit:'$s$IP_produit >> $nom_fichier_data
echo 'Mac '$phy': '$MAC_carte
echo 'Mac '$phy':'$MAC_carte >> $nom_fichier_data
echo 'SN produit: '$SN_produit
echo 'SN produit:'$s$SN_produit >> $nom_fichier_data

# Configuration de l'enregistrement
#shopt -s extglob
#ensemble_product_ID="@(60|40)"
execution_temps=0
execution_occupation_CPU=0
execution_memoire_libre=0
execution_temperature_1=0
execution_temperature_2=0
execution_signal_level_global=0
execution_signal_level_antenne1=0
execution_signal_level_antenne2=0
execution_signal_level_antenne3=0
execution_noise_level=0
execution_mcs=0
execution_pulses=0
execution_radars=0
execution_throughput_RX=0
execution_throughput_TX=0
# 60 RailBox-21A0
# 52 RailBox-22AY
# 100 EmbedAir
# 101 EmbedAir 100
case $Product_ID in
	60|52|80|109 )
	execution_temps=1
	execution_occupation_CPU=1
	execution_memoire_libre=1
	execution_temperature_1=1
	execution_temperature_2=1
	execution_signal_level_global=1
	execution_signal_level_antenne1=1
	execution_signal_level_antenne2=1
	execution_signal_level_antenne3=1
	execution_noise_level=1
	execution_mcs=1
	execution_pulses=1
	execution_radars=1
	execution_throughput_RX=1
	execution_throughput_TX=1
	;;
	31|44 )
	execution_temps=1
	execution_occupation_CPU=0
	execution_memoire_libre=0
	execution_temperature_1=0
	execution_temperature_2=0
	execution_signal_level_global=1
	execution_signal_level_antenne1=1
	execution_signal_level_antenne2=1
	execution_signal_level_antenne3=1
	execution_noise_level=1
	execution_mcs=0
	execution_pulses=1
	execution_radars=1
	execution_throughput_RX=0
	execution_throughput_TX=0
	;;
	100|101|102|103 )
	execution_temps=1
	execution_occupation_CPU=1
	execution_memoire_libre=1
	execution_temperature_1=1
	execution_signal_level_global=1
	execution_signal_level_antenne1=1
	execution_signal_level_antenne2=1
	execution_signal_level_antenne3=1
	execution_noise_level=1
	execution_mcs=1
	execution_pulses=1
	execution_radars=1
	execution_throughput_RX=1
	execution_throughput_TX=1

	;;
esac

# configuration des titres du fichiers d'enregistrement
titre_colonnes=""
[ $execution_temps = 1 ] && titre_colonnes=$titre_colonnes'temps(s)'$s
[ $execution_occupation_CPU = 1 ] && titre_colonnes=$titre_colonnes'occupation_CPU(%)'$s
[ $execution_memoire_libre = 1 ] && titre_colonnes=$titre_colonnes'memoire_libre(Ko)'$s
[ $execution_temperature_1 = 1 ] && titre_colonnes=$titre_colonnes'Temperature_1(C)'$s
[ $execution_temperature_2 = 1 ] && titre_colonnes=$titre_colonnes'Temperature_2(C)'$s
[ $execution_signal_level_global = 1 -o $execution_signal_level_antenne1 = 1 -o $execution_signal_level_antenne2 = 1 -o $execution_signal_level_antenne3 = 1  ] && titre_colonnes=$titre_colonnes'Signal_level_global(dB)'$s
[ $execution_signal_level_antenne1 = 1 ] && titre_colonnes=$titre_colonnes'Signal_level_antenne1(dB)'$s
[ $execution_signal_level_antenne2 = 1 ] && titre_colonnes=$titre_colonnes'Signal_level_antenne2(dB)'$s
[ $execution_signal_level_antenne3 = 1 ] && titre_colonnes=$titre_colonnes'Signal_level_antenne3(dB)'$s
[ $execution_noise_level = 1 ] && titre_colonnes=$titre_colonnes'Noise_level(dB)'$s
[ $execution_mcs = 1 ] && titre_colonnes=$titre_colonnes'MCS'$s
[ $execution_pulses = 1 ] && titre_colonnes=$titre_colonnes'Pulses'$s
[ $execution_radars = 1 ] && titre_colonnes=$titre_colonnes'Radars'$s
[ $execution_throughput_RX = 1 ] && titre_colonnes=$titre_colonnes'Throughput_RX_with_header'$s
[ $execution_throughput_TX = 1 ] && titre_colonnes=$titre_colonnes'Throughput_TX_with_header'$s

echo $titre_colonnes >>$nom_fichier_data

# Verification de que le fichier de resultat est cree
if [ -e $nom_fichier_data ]; then
	echo "Fichier de DATA cree"
else
	echo "Le fichier de DATA n'a pas ete cree."
	exit 1
fi






# boucle d'aquisition
i=1
read rx_byte_tm1 < /sys/class/net/$carte_radio/statistics/rx_bytes
while [ $i -le $(($temps_script*60)) ] 
do

record=""
#date debut aquisition
if [ $execution_temps = 1 ];then
	date_deb=$(date +'%s')
	record=$record$date_deb$s
fi

# occupation_CPU
if [ $execution_occupation_CPU = 1 ];then
	data_top=$(top -bn1)
	#echo $data_top
	#data_cpu=$(echo $data_top |sed -n '/CPU:/p' |sed q)
	data_cpu=$(echo $data_top |sed 2d)
	data_cpu=${data_cpu%% idle*}
	data_cpu=${data_cpu##*nic }
	data_cpu=$(echo $data_cpu |sed 's/\%//')
	data_cpu=$((100-$data_cpu))
	#echo $data_cpu
	#data_cpu=$(top -bn1 |sed -n '/CPU:/p' |sed q |cut -c  33-35)
	record=$record$data_cpu$s
fi

# memoire disponible
if [ $execution_memoire_libre = 1 ];then
	data_mem=$(echo $data_top |sed q)
	data_mem=${data_mem%% free*}
	data_mem=${data_mem##*used, }
	data_mem=$(echo $data_mem |sed 's/\K//')
	#echo $data_mem
	record=$record$data_mem$s
fi

# Temperature 1
if [ $execution_temperature_1 = 1 ];then
case $Product_ID in
	60|80|109)
	read temp1 < /sys/devices/soc.0/1180000001000.i2c/i2c-0/0-004c/temp1_input
	;;
	100|101|102|103|31)
	temp1=`acksys_get_temperature.sh board`
	;;
esac
	longueur_chaine=${#temp1}
	num_carac=$(($longueur_chaine-3))
	debut_chaine=$(echo $temp1 |cut -c-$num_carac)
	fin_chaine=$(echo $temp1 |cut -c$(($num_carac+1))-)
	temp1=$debut_chaine$p$fin_chaine
	record=$record$temp1$s
fi

# Temperature 2
if [ $execution_temperature_2 = 1 ];then
	case $Product_ID in
		60|80|109)
		read temp2 < /sys/devices/soc.0/1180000001000.i2c/i2c-0/0-004c/temp2_input
		;;
		100)
		temp2=`acksys_get_temperature.sh cpu`
		;;
	esac
	longueur_chaine=${#temp2}
	num_carac=$(($longueur_chaine-3))
	debut_chaine=$(echo $temp2 |cut -c-$num_carac)
	fin_chaine=$(echo $temp2 |cut -c$(($num_carac+1))-)
	temp2=$debut_chaine$p$fin_chaine
	record=$record$temp2$s
fi

# Signal level
if [ $execution_signal_level_global = 1 -o $execution_signal_level_antenne1 = 1 -o $execution_signal_level_antenne2 = 1 -o $execution_signal_level_antenne3 = 1  ];then
	signal_level=$(iw $carte_radio station dump | sed -n '/signal:/p')
	signal_level_global=$(echo $signal_level |cut -d ' ' -f2) 

	record=$record$signal_level_global$s
fi

# Signal level antenne1
if [ $execution_signal_level_antenne1 = 1 ];then
	if [ "$driver" = "ath9k" ]; then
		signal_level_antenne1=$(echo $signal_level |cut -d ' ' -f3 |sed 's/\[//' |sed 's/\,//' ) 
	elif [ "$driver" = "ath10k" ]; then
		signal_level_antenne1="NA" 
	fi
	record=$record$signal_level_antenne1$s
fi

# Signal level antenne2
if [ $execution_signal_level_antenne2 = 1 ];then
	if [ "$driver" = "ath9k" ]; then
		#signal_level_antenne2=$(echo $signal_level |cut -d ' ' -f4 |sed 's/\,//' ) 
		signal_level_antenne2=$(echo $signal_level |cut -d ' ' -f4 |sed 's/,\|]//' ) 
	elif [ "$driver" = "ath10k" ]; then
		signal_level_antenne2="NA"
	fi
	record=$record$signal_level_antenne2$s
fi

# Signal level antenne3
if [ $execution_signal_level_antenne3 = 1 ];then
	if [ "$driver" = "ath9k" ]; then
		#signal_level_antenne3=$(echo $signal_level |cut -d ' ' -f5 |sed 's/\]//' ) 
		signal_level_antenne3=$(echo $signal_level |cut -d ' ' -f5 |sed 's/]\|dBm//' ) 
	elif [ "$driver" = "ath10k" ]; then
		signal_level_antenne3="NA" 
	fi
	record=$record$signal_level_antenne3$s
fi

# Noise level
if [ $execution_noise_level = 1 ];then
	if [ "$driver" = "ath9k" ]; then
		noise_level=$(iwinfo $carte_radio i |sed -n '/Noise/p')
		noise_level=${noise_level##*Noise: }
		noise_level=${noise_level%% dBm*}
	elif [ "$driver" = "ath10k" ]; then
		noise_level="NA"
	fi
	record=$record$noise_level$s
fi

#MCS
if [ $execution_mcs = 1 ];then
	rc=/sys/kernel/debug/ieee80211/$phy/netdev:$carte_radio/stations/*/rc_stats
	mcs=$(sed -n '/ A[ B]/s/.*MCS//p' $rc)
	mcs=$(echo $mcs |cut -d ' ' -f1)
	record=$record$mcs$s
fi

# Pulse DFS
if [ $execution_pulses = 1 ];then
	if [ "$driver" = "ath9k" ]; then
		pulse_dfs=$(sed -n '/Pulse events processed/p' $cmd_pulse_dfs)
	elif [ "$driver" = "ath10k" ]; then 	
		pulse_dfs=$(sed -n '/DFS pulses detected/p' $cmd_pulse_dfs)
	fi
	pulse_dfs=${pulse_dfs##*: }
	#echo $pulse_dfs
	record=$record$pulse_dfs$s
fi

# DFS
if [ $execution_radars = 1 ];then
	dfs=$(sed -n '/Radars detected/p'  $cmd_pulse_dfs)
	dfs=${dfs##*: }
	#echo $dfs
	record=$record$dfs$s
fi

#Bande passsante rx et tx
if [ $execution_throughput_RX = 1 -o $execution_throughput_TX = 1 ];then
	read rx_byte_tm1 < /sys/class/net/$carte_radio/statistics/rx_bytes 
	read tx_byte_tm1 < /sys/class/net/$carte_radio/statistics/tx_bytes 
	sleep $echantillonnage 
	read rx_byte_t0 < /sys/class/net/$carte_radio/statistics/rx_bytes 
	read tx_byte_t0 < /sys/class/net/$carte_radio/statistics/tx_bytes 
	if [ $execution_throughput_RX = 1 ];then
		rx_byte_diff=$(($rx_byte_t0-$rx_byte_tm1))
		bandwidth_rx=$(($rx_byte_diff*8/$echantillonnage))
		record=$record$bandwidth_rx$s
	fi
	if [ $execution_throughput_TX = 1 ];then	
		tx_byte_diff=$(($tx_byte_t0-$tx_byte_tm1))
		bandwidth_tx=$(($tx_byte_diff*8/$echantillonnage))
		record=$record$bandwidth_tx$s
	fi
else	
	sleep $echantillonnage
fi


echo $record |tee -a $nom_fichier_data


#sleep $echantillonnage # le temps d'Ãchantilonnag est utilise pour mesurer la bandepassante
i=`expr $i + $echantillonnage`

done

