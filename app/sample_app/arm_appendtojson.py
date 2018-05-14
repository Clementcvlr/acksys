#!/usr/bin/env python

import json

with open("static/arm_myjson.json", 'a') as f:
		mydata = { "67" : {"36" :{ "TCP" : {"ClienttoAP" : "In Progress"}}}}
		f.write(json.dumps(mydata))
		f.close
		#print(f_data)


#with open("static/arm_myjson.json", 'a') as f:
#		json.dump(f_data,f)	
