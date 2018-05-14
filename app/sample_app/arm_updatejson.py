#!/usr/bin/env python

import json

with open("static/arm_myjson.json", 'r+') as f:
        	f_data = json.loads(f.read())
		#print(f_data["12"])
		print(f_data["108"])
		print(type(f_data))
		
		#print(type(f_data["12"])  )
		#print(type(f_data["12"]["UDP"])  )
		#f_data["12"]["UDP"]["APtoClient"] = "Done"
		f_data["108"] = {"UDP" : { "APtoClient" : "In Progress" }} 
		#f_data["108"]["TCP"] = { "APtoClient" : "In Progress" } 
		
		print(f_data)
		#f_data['65']['1']['TCP']['ClienttoAP'] = "Done"

		f.close()

with open("static/arm_myjson_init.json", 'w') as f:
#with open("static/arm_myjson.json", 'w') as f:
		f_data2 = {"1" : {'UDP' : {"APtoClient" : "In Progress"}}}
		
		#json.dump(f_data2,f)	
