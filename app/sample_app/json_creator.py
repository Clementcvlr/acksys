#!/usr/bin/env python
import json
"""
channel_list = ['1','2','3','4']
prot_list = ['TCP','UDP']
sens_list = ['903', '904']
mode_list = ['AP', 'Client']
"""
myconfig ={}
myconfig['EUT'] = "192.168.100.20"
myconfig['test_id'] = "20"
myconfig['operator'] = "cc"
myconfig['htmode'] = "HT40"
myconfig['wifi_card'] = "0"
#myconfig['channels'] = [ '1','2','3','4','5','6','7','8','9','10','11','36','52','56','60','100','104','108','112','116','120','124','128','149','165' ]
myconfig['channels'] = ['1','2']
myconfig['attenuator'] = "39"
myconfig['mode'] = "ap"
myconfig['prot'] = "TCP"
myconfig['tid_ap'] = "TID_1-1-1-3"
myconfig['tid_client'] = "TID_1-1-2-3"
myconfig['tx_power'] = "10"
myconfig['reboot'] = False
myconfig['attn_list'] = ['320']
myconfig['attn_duration'] = "10"

Config = myconfig

def InitJson(Config):

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
			

mylog = InitJson(myconfig)
#data['3']['AP']['UDP']['903'] = "Done"
print(mylog)
print(type(mylog))
data = json.loads(mylog)
data["1"]["ap"]["TCP"]["AP to Client"] = "In Progress"
data_json = json.dumps(data, indent = 12)
#print(data_json)
with open("/tmp/candela_channel/" + str(Config['test_id']) + "_HT20_24G/" + "myjsonfile.json", 'w') as f :
			json.dump(data, f)


sens = "AP_vers_Client"
cxmode = "ap"
cx_prot ="TCP"
channel = "2"

with open("/tmp/candela_channel/" + str(Config['test_id']) + "_HT20_24G/" + "myjsonfile.json", 'r+') as f :
	data = json.load(f)
	print(type(data))
	#data[channel][cxmode][cx_prot][sens] = "In_Progress"
	#json.dumps(data, f)
	print( data["1"])
	data[channel][cxmode][cx_prot][sens] = "TOTO"
	json.dump(data,f)

