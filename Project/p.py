import urllib2
import re
import copy as cp
# import threading

content = ""
host_list = []
vm_list = []
host_map = {}

def wt(r,c):
	return (r/1024)*0.75 + 0.25*c

def saveFile():
	# threading.Timer(60*20,saveFile).start()
	global content
	response = urllib2.urlopen('https://baadal.iitd.ac.in/rrd/vm_positions.txt')
	content = response.read()

	with open('baadal.txt','w') as f:
		f.write(content)

saveFile()
date = (re.findall( "\"date\": \"(.+)\"" , content))[0]
info = (re.findall( '"info": [\[](.+?)[\]]' , content , re.DOTALL))[0].strip()

host_data = (re.findall( '"host_data": [\[](.*?)[\]]' , content , re.DOTALL ))[0].split('},')
vm_data = (re.findall( '"vm_data": [\[](.*?)[\]]' , content , re.DOTALL ))[0].split('},')

class host:
	def __init__(self , status , ram , name , cpu):
		self.status = status
		self.ram = ram
		self.name = name
		self.cpu = cpu
		self.vm = []
		self.usedR=0
		self.usedC=0


class vm :
	def __init__(self,host,ram,name,level,cpu):
		self.host = host
		self.ram = ram
		self.name = name
		self.level = level
		self.cpu = cpu

def extracthost(i,s):
	global host_list
	global host_map
	l = re.findall( ': (.*),' , s)
	name = re.findall('"(.*)"' , l[2])[0]
	cpu = re.findall( '"cpu": (.*)' , s)[0]
	host_list += [host(int(l[0]),1024*int(l[1]),name,int(cpu))]

	host_map[name]=i
	return None


for i,s in enumerate(host_data):
	extracthost(i,s)

def extractvm(c,s):
	global vm_list
	l = re.findall( ': (.*),' , s)
	host = re.findall('"(.*)"' , l[0])[0]
	name = re.findall('"(.*)"' , l[2])[0]
	cpu = re.findall('"cpu": (.*)' , s)[0]

	vm_list += [vm(host , int(l[1]) , name, int(l[3]) , int(cpu))]

	host_list[host_map[host]].vm += [c]
	return None

for i,s in enumerate(vm_data):
	extractvm(i,s)

################################################################################################################################

class node:
	def __init__(self,hlist,vlist,hmap,vic):
		self.host_list = hlist
		self.vm_list = vlist
		self.host_map = hmap
		self.victim=vic

state0=node(host_list,vm_list,host_map,-1)
#################################################################################################################################

def printState(w):
	print 'Total Numbers of Vms: ' + str(len(w.vm_list))
	print 'Total Numbers of hosts: ' + str(len(w.host_list))
	count = 0 
	for v in w.vm_list:
		if (v.level != 0):
			count += 1

	print 'Total Numbers of Active Vms: ' + str(count)
	mapp={}
	mapp["test1"]="string1"
	for x in w.host_list:
		activeVms=filter( (lambda y: w.vm_list[y].level>0 ) , x.vm)
		#print str(len(activeVms)) + " " +str(len(x.vm))
		x.usedC=0
		x.usedR=0
		mapp[x.name]=""
		for z in activeVms:
			mapp[x.name]=mapp[x.name]+ ("  ("+'{0:6}'+","+'{1:5}'+","+'{2:2}'+","+'{3:1}'+")").format(w.vm_list[z].name,str(w.vm_list[z].ram),str(w.vm_list[z].cpu),str(w.vm_list[z].level))
			x.usedC+=w.vm_list[z].cpu/(2**(w.vm_list[z].level-1))
			x.usedR+=w.vm_list[z].ram/(2**(w.vm_list[z].level-1))

	for x in w.host_list:
		print ('{0:7}' + " : usedRam " + '{1:5}' + "/"+ '{2:5}' + " usedCpu " + '{3:2}' + "/" + '{4:2}' ).format(x.name,str(x.usedR),str(x.ram),str(x.usedC),str(x.cpu)),mapp[x.name] 

printState(state0)

############################### Best Fit Algorithm #################################################################################

def place():
	global vm_list,host_list
	print "New Request: name cpu ram level....:"
	while True:
		req=raw_input().split(' ')
		if(len(req)<4):
			break
		[n_n,n_c,n_r,n_l]=req[0],float(req[1]),float(req[2]),float(req[3])
		bestR=float("inf")
		bestC=float("inf")
		target=-1
		for i,x in enumerate(host_list):
			freeC=x.cpu-x.usedC
			freeR=x.ram-x.usedR
			if(freeC>(n_c/2**(n_l-1)) and freeR>(n_r/2**(n_l-1)) and (wt(freeR,freeC)<wt(bestR,bestC)) ):
				bestR=freeR
				bestC=freeC
				target=i
		vm_list+=[vm( host_list[target].name , n_r , n_n , n_l , n_c )]
		last=len(vm_list)-1
		host_list[target].vm+=[last]
		host_list[target].usedC+=vm_list[last].cpu/(2**(vm_list[last].level-1))
		host_list[target].usedR+=vm_list[last].ram/(2**(vm_list[last].level-1))
		print "vm added successfully. Want to start a new... ?"

		th=host_list[target]
		print th.name + " : usedR " + str(th.usedR)+"/"+ str(th.ram) + " usedC " + str(th.usedC) + "/" + str(th.cpu)

# place()

################################# cost-aware VM placement  ########################################################################


st=""
def fit(n_r,n_c,n_l,forbid,nod,vm_num):
	st=""
	bestR=float("inf")
	bestC=float("inf")
	target=-1
	for i,x in enumerate(nod.host_list):
		# print "ghdsaaaaaaaaaaaaaaaaaagdsjagdhsjadghsahgdgashgdaskjfvbxcmv,xcvnxc,vcnx"
		if (i==forbid or wt(x.usedR,x.usedC)<=0 or x.status!=1):
			continue
		# print "wt:",wt(x.ram,x.cpu)
		freeC=x.cpu-x.usedC
		freeR=x.ram-x.usedR
		if( freeC>(n_c/2**(n_l-1)) and freeR>(n_r/2**(n_l-1)) and (wt(freeR,freeC)<wt(bestR,bestC)) ):
			bestR=freeR
			bestC=freeC
			target=i
		# print "target:",target
	# vm_list+=[vm( host_list[target].name , n_r , "n_n" , n_l , n_c )]
	
	if target!=-1:
		nod.host_list[target].vm+=[vm_num]
		nod.vm_list[vm_num].host=nod.host_list[target].name
		nod.host_list[target].usedC+=n_c/(2**(nod.vm_list[vm_num].level-1))
		nod.host_list[target].usedR+=n_r/(2**(nod.vm_list[vm_num].level-1))
		nod.host_list[target].vm.remove(vm_num)
		st+= nod.vm_list[vm_num].name +"vm added successfully to "
		th=nod.host_list[target]
		st+= th.name + " : usedR " + str(th.usedR)+"/"+ str(th.ram) + " usedC " + str(th.usedC) + "/" + str(th.cpu) + '\n'
		print st
		return 1
	return 0


def mCost(ur,uc):
	return 0.9*(ur/1024)+0.1*uc

minCost=float("inf")
costList=map( lambda x: mCost(x.usedR,x.usedC) , host_list )
avg=sum(costList)/len(costList)

victim_list=[]
for i,x in enumerate(costList):
	if (x<avg and x>0):
		victim_list+=[i]

print "victim_list:" , map(lambda x: host_list[x].name,victim_list)

node_list=map(lambda c:node(cp.deepcopy(host_list),cp.deepcopy(vm_list),cp.deepcopy(host_map),c),victim_list)


for x in node_list:
	victim=x.victim
	victim_vms,x.host_list[victim].vm=sorted(filter( lambda v:x.vm_list[v].level>0 ,x.host_list[victim].vm),key=lambda v:mCost(x.vm_list[v].ram , x.vm_list[v].cpu )),[]
	x.host_list[victim].usedC=x.host_list[victim].usedR=0
	print map(lambda p:x.vm_list[p].name,victim_vms)
	succ=True
	for j,y in enumerate(victim_vms):
		success=fit(x.vm_list[y].ram,x.vm_list[y].cpu,x.vm_list[y].level,victim,x,y)
		if(success==0):
			print "failed: at vm",j
			succ=False
			break
	if succ:
		print x.host_list[victim].name,"conslidated"
		printState(x)
	else:
		print "No space"

print map
print map( lambda f:(f.name,f.ram,f.cpu,f.level) ,filter(lambda c:c.host=="host34" and c.level>0,state0.vm_list ) ) 