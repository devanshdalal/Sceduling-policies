import os
import json
import datetime

vms = db(db.vm.id>=0).select()
hosts = db(db.host.id>=0).select()
data = []
dumpLoc = '/var/www/rrd/vm_positions.txt'
info = []
info.append('VM Level: 0->Shutdown, {1,2,3}->Running')
info.append('VM RAM & CPU shown are the max resources that VM can have. Level 1 means same, 2 means halfed resources, 3 means 1/4 resources. Minimum 1GB, 1CPU')
info.append('Host status defines if the host is being used. 1-> IN_USE, Others->IGNORE')

for vm in vms:
    properties = {'name': vm['name'], 'cpu': vm['vCPU'], 'ram': vm['RAM'], 'host': vm.hostid.name, 'level': vm['runlevel']}
    data.append(properties)

hostData = []
for host in hosts:
    properties = {'name': host['name'], 'cpu': host['CPUs'], 'ram': host['RAM'], 'status': host['status']}
    hostData.append(properties)

with open(dumpLoc, 'w') as dumpFile:
    mydata = {'date': datetime.datetime.now().isoformat(' '),
              'info': info,
	      'vm_data': sorted(data, key=lambda t: t['name']),
              'host_data': sorted(hostData, key=lambda t: t['name'])}
    dumpFile.write(json.dumps(mydata, indent=4))

os.chmod(dumpLoc, 0755)
