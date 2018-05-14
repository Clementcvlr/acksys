#!/usr/bin/env python
import re
from acksys_func import telnet, check_ssh
from time import sleep
import time
from scp import SCPClient

ssh_session = check_ssh("192.168.100.20", "root")
scp = SCPClient(ssh_session.get_transport()) 
scp.get('/usr/monitoring_v1/', '/tmp/candela_channel/monitoring/', recursive=True)
