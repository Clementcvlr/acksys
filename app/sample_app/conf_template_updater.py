#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
myconfig = {}
myconfig['country'] = ['France']
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
'''


class ConfUpdater():
	'''Cette Classe prend en entree un dictionnaire de config, un htmode et un country, et vient modifier la liste de canaux à tester en fonction du pays et du HTmode'''

	def __init__(self, myconfig, htmode, country):
		
		self.htmode = htmode
		self.country = country
		self.myconfig = myconfig
		self.my_new_config = self.myconfig.copy()
		
		self.my_new_config['country'] = country
		self.my_new_config['test_id'] = "{0}_{1}_{2}".format(self.myconfig['test_id'], self.htmode, self.country)

		ht_dict = {}
		ht_dict['vht80'] = ["11ac", "VHT80"]
		ht_dict['vht40'] = ["11ac", "VHT40"]
		ht_dict['vht20'] = ["11ac", "VHT20"]
		ht_dict['ht40+_5Ghz'] = ["11na", "HT40+"]
		ht_dict['ht20_5Ghz']  = ["11na", "HT20" ]
		ht_dict['ht40+_24Ghz'] = ["11no", "HT40+"]
		ht_dict['ht20_24Ghz']  = ["11no", "HT20" ]

		print(self.htmode)
		self.my_new_config['hwmode'] = ht_dict[self.htmode][0]
		self.my_new_config['htmode'] = ht_dict[self.htmode][1]

		country_updater = getattr(self, country)
		chan_dict = country_updater()	
		self.my_new_config['channels'] = chan_dict[self.htmode]

	def EU(self):
		chan_dict = {}
		chan_dict['vht80'      ] = ['36','52','100','116']
		chan_dict['vht40'      ] = ['36','44','52','60','100','108','116','124','132']
		chan_dict['vht20'      ] = ['36','40','44','48','52','56','60','64','100','104','108','112','116','120','124','128','132','136','140']
		chan_dict['ht40+_5Ghz' ] = ['36','44','52','60','100','108','116','124','132']
		chan_dict['ht20_5Ghz'  ] = ['36','40','44','48','52','56','60','64','100','104','108','112','116','120','124','128','132','136','140']
		chan_dict['ht40+_24Ghz'] = ['1','2','3','4','5','6','7','8','9']
		chan_dict['ht20_24Ghz' ] = ['1','2','3','4','5','6','7','8','9','10','11','12','13']
		return chan_dict


	def US(self):
		chan_dict = {}
		chan_dict['vht80'      ] = ['36','52','100','116','149']
		chan_dict['vht40'      ] = ['36','44','52','60','100','108','116','124','132','149','157']
		chan_dict['vht20'      ] = ['36','40','44','48','52','56','60','64','100','104','108','112','116','120','124','128','132','136','140','149','153','157','161','165']
		chan_dict['ht40+_5Ghz' ] = ['36','44','52','60','100','108','116','124','132','149','157']
		chan_dict['ht20_5Ghz'  ] = ['36','40','44','48','52','56','60','64','100','104','108','112','116','120','124','128','132','136','140','149','153','157','161','165']
		chan_dict['ht40+_24Ghz'] = ['1','2','3','4','5','6','7']
		chan_dict['ht20_24Ghz' ] = ['1','2','3','4','5','6','7','8','9','10','11']
		return chan_dict


	def JP(self):
		chan_dict = {}
		chan_dict['vht80'      ] = ['36','52','100','116']
		chan_dict['vht40'      ] = ['36','44','52','60','100','108','116','124','132']
		chan_dict['vht20'      ] = ['36','40','44','48','52','56','60','64','100','104','108','112','116','120','124','128','132','136','140']
		chan_dict['ht40+_5Ghz' ] = ['36','44','52','60','100','108','116','124','132']
		chan_dict['ht20_5Ghz'  ] = ['36','40','44','48','52','56','60','64','100','104','108','112','116','120','124','128','132','136','140']
		chan_dict['ht40+_24Ghz'] = ['1','2','3','4','5','6','7','8','9']
		chan_dict['ht20_24Ghz' ] = ['1','2','3','4','5','6','7','8','9','10','11','12','13','14']
		return chan_dict


	def get_conf(self):
		return self.my_new_config
	
#a = ConfUpdater(myconfig, "vht40", "EU").get_conf()
#print(a)
#for country in countries :

#	conf_template_updater(myconfig, country)
