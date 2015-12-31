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

################################# cost-aware VM placement  ########################################################################


st=""
taar=-1;
def fit(n_r,n_c,n_l,forbid,nod,vm_num):
	st=""
	bestR=float("inf")
	bestC=float("inf")
	taar=target=-1
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
		print "gggggg", nod.host_list[target].vm
		nod.host_list[target].vm+=[vm_num]
		print "gggggg", nod.host_list[target].vm
		nod.vm_list[vm_num].host=nod.host_list[target].name
		nod.host_list[target].usedC+=n_c/(2**(nod.vm_list[vm_num].level-1))
		nod.host_list[target].usedR+=n_r/(2**(nod.vm_list[vm_num].level-1))
		nod.host_list[target].vm.remove(vm_num)
		st+= nod.vm_list[vm_num].name+"("+str(vm_num)+")" +"vm added successfully to "
		th=nod.host_list[target]
		st+= th.name + " : usedR " + str(th.usedR)+"/"+ str(th.ram) + " usedC " + str(th.usedC) + "/" + str(th.cpu) + '\n'
		print st
		taar=target;
		return 1
	return 0


def mCost(ur,uc):
	return 0.9*(ur/1024)+0.1*uc

def findVic(nod):
	minCost=float("inf")
	costList=map( lambda x: mCost(x.usedR,x.usedC) , nod.host_list )
	avg=sum(costList)/len(costList)

	victim_list=[]
	for i,x in enumerate(costList):
		if (x<avg*2.0/3 and x>0):
			victim_list+=[i]
	print "victim_list:" , map(lambda x: nod.host_list[x].name, victim_list)
	return victim_list


# node_list=map(lambda c:node(cp.deepcopy(host_list),cp.deepcopy(vm_list),cp.deepcopy(host_map),c),victim_list)

# for x in node_list:
# 	victim=x.victim
# 	victim_vms,x.host_list[victim].vm=sorted(filter( lambda v:x.vm_list[v].level>0 ,x.host_list[victim].vm),key=lambda v:mCost(x.vm_list[v].ram , x.vm_list[v].cpu )),[]
# 	x.host_list[victim].usedC=x.host_list[victim].usedR=0
# 	print map(lambda p:x.vm_list[p].name,victim_vms)
# 	succ=True
# 	for j,y in enumerate(victim_vms):
# 		success=fit(x.vm_list[y].ram,x.vm_list[y].cpu,x.vm_list[y].level,victim,x,y)
# 		if(taar!=-1):
# 			print "pppp", x.host_list[taar].vm
# 		if(success==0):
# 			print "failed: at vm",j
# 			succ=False
# 			break
# 	if succ:
# 		print x.host_list[victim].name,"conslidated"
# 		printState(x)
# 	else:
# 		print "No space"

# print map( lambda f:(f.name,f.ram,f.cpu,f.level) ,filter(lambda c:c.host=="host34" and c.level>0,state0.vm_list ) ) 

##########################################################   GRAPHS   ######################################################################################

import numpy as np 
import matplotlib.pyplot as plt 

colors = ['b','g','r','c','m','y','k','w']

def findMaxActive(w):
	max = -1
	for x in w.host_list:
		activeVms=filter( (lambda y: w.vm_list[y].level>0 ) , x.vm)
		if (len(activeVms)>max):
			max=len(activeVms)
	return max

def graphWt(cpu,ram):
	return ram/1024.0

def createGraph(w):
	plt.figure()
	rows , columns = findMaxActive(w),len(w.host_list)
	hostRamUsage = np.zeros((columns) )
	hostCpuUsage = np.zeros((columns) )
	g = np.zeros((2,rows,columns) )
	for j,x in enumerate(w.host_list):
		activeVms=filter( (lambda y: w.vm_list[y].level>0 ) , x.vm)
		for i,z in enumerate(activeVms):
			ucpu = (1.0*w.vm_list[z].cpu)/(2**(w.vm_list[z].level-1))
			uram = (1.0*w.vm_list[z].ram)/(2**(w.vm_list[z].level-1))
			g[0][i][j] = graphWt(ucpu , uram)
			g[1][i][j] = ucpu
		hostRamUsage[j] = graphWt(x.cpu,x.ram)
		hostCpuUsage[j] = x.cpu


	width = 0.5
	ind = np.arange(columns)
	indram = 2*ind
	indcpu = indram+width
	hghtRam = [0]*(columns)
	hghtCpu = [0]*(columns)
	for i in range(rows):
		p = plt.bar(indram,g[0][i],width,color=colors[i%8],bottom=hghtRam,alpha=0.5)
		p = plt.bar(indcpu,g[1][i],width,color=colors[i%8],bottom=hghtCpu,alpha=0.5)
		for k in range(columns):
			hghtRam[k] += g[0][i][k]
			hghtCpu[k] += g[1][i][k]

	p2 = plt.bar(indram,hostRamUsage,width,fill=False,linestyle='dashed',edgecolor='#050002')
	p3 = plt.bar(indcpu,hostCpuUsage,width,fill=False,linestyle='dotted',edgecolor='#050002')

	hostNames = map( (lambda h : h.name) , w.host_list)
	plt.xlabel('Hosts')
	plt.ylabel('VMs')
	plt.title('Resource Usage : Baadal')
	plt.xticks(indram+width/2. , (hostNames) , rotation=45)
	plt.legend((p2[0],p3[0]) , ('RAM','CPU'))
	# print g


#########################################################################################################################################################################
print "##########################################################################################################################################################"

def ncost(ram,cpu,num):
	return int(0.5*ram+0.1*cpu+0.4*num)




def help(nod):

	activeVms=filter( (lambda y: nod.vm_list[y].level>0 ) , nod.host_list[nod.victim].vm)
	
	nod.host_list[nod.victim].vm=filter(lambda c:nod.vm_list[c].level==0 ,  nod.host_list[nod.victim].vm )
	nod.host_list[nod.victim].usedR,nod.host_list[nod.victim].usedC=0,0

	victim_vms=sorted(activeVms,cmp=lambda x,y:int(mCost(nod.vm_list[x].ram,nod.vm_list[x].cpu))-int(mCost(nod.vm_list[y].ram,nod.vm_list[y].cpu)),reverse=True)
	victim_vms=map(lambda c:(c,1) ,victim_vms)
	print "p1",nod.host_list[nod.victim].name
	print "p2",map( lambda f:(f.name,f.ram,f.cpu,f.level) ,filter(lambda c:c.host==nod.host_list[nod.victim].name and c.level>0,nod.vm_list ) )

	while victim_vms!=[]:
		(head,lvl)=victim_vms[0]
		victim_vms=victim_vms[1:]
		print "---------------------------------------------------------------------------------------------------------------------------"
		if(lvl>4):
			print "FAIL"
			raise Exception('failed', 'exiting')
		n_l=nod.vm_list[head].level
		n_r=1.0*nod.vm_list[head].ram/(2**(n_l-1))
		n_c=1.0*nod.vm_list[head].cpu/(2**(n_l-1))
		n_n=nod.vm_list[head].name
		print n_n
		bestR=float("inf")
		bestC=float("inf")
		target=-1
		fitted=False
		st=""
		for j,x in enumerate(nod.host_list):
			if (j==nod.victim or wt(x.usedR,x.usedC)<=0 or x.status!=1):
				continue
			freeC=x.cpu-x.usedC
			freeR=x.ram-x.usedR
			if freeC>=n_c and freeR>=n_r:
				print "inside"
				nod.host_list[j].vm+=[head]
				nod.vm_list[head].host=nod.host_list[j].name
				nod.host_list[j].usedC+=n_c
				nod.host_list[j].usedR+=n_r
				# nod.host_list[j].vm.remove(head)
				st+= nod.vm_list[head].name+"("+str(head)+")" +"vm added successfully to "
				th=nod.host_list[j]
				st+= th.name + " : usedR " + str(th.usedR)+"/"+ str(th.ram) + " usedC " + str(th.usedC) + "/" + str(th.cpu) + '\n'
				print "here",st
				fitted=True
				break
		if(fitted==False):
			print "not fitted"
			vic2_vms=[]
			for j,x in enumerate(nod.host_list):
				freeC=x.cpu-x.usedC
				freeR=x.ram-x.usedR
				if (i==nod.victim or wt(x.usedR,x.usedC)<=0 or freeR<=0 or freeC<=0 or x.status!=1):
					continue
				vic2_vms = cp.deepcopy(filter(lambda c : nod.vm_list[c].level>0 ,x.vm)) 
				vic2_vms.sort(cmp=lambda c,d:int(mCost(nod.vm_list[c].ram/(2**(nod.vm_list[c].level-1)),nod.vm_list[c].cpu/(2**(nod.vm_list[c].level-1)))-mCost(nod.vm_list[d].ram/(2**(nod.vm_list[d].level-1)),nod.vm_list[d].cpu/(2**(nod.vm_list[d].level-1)))) )
				print "c1",x.name,map(lambda c:(nod.vm_list[c].name,nod.vm_list[c].ram,nod.vm_list[c].cpu,nod.vm_list[c].level) , vic2_vms);
				_ram,_cpu=0,0
				found=False
				for k,z in enumerate(vic2_vms):
					_newRam=nod.vm_list[z].ram/(2**(nod.vm_list[z].level-1))
					_newCpu=nod.vm_list[z].cpu/(2**(nod.vm_list[z].level-1))
					if _newRam>=n_r or _newCpu>n_c:
						break;                              ##  remember to change
					_ram+=_newRam
					_cpu+=_newRam
					if _ram+freeR>=n_r and _cpu+freeR>=n_c:
						nod.host_list[j].vm=vic2_vms[k+1:]
						nod.host_list[j].vm+=[head]
						nod.vm_list[head].host=nod.host_list[j].name
						nod.host_list[j].usedR+=(n_r - _ram)
						nod.host_list[j].usedC+=(n_c - _cpu)
						vic2_vms=vic2_vms[:k+1]
						found=True;
						break
				if found:

					vic2_vms=map(lambda c:(c,lvl+1) ,vic2_vms)
					victim_vms+=vic2_vms;
					victim_vms.sort( cmp=lambda c,d:int(mCost(nod.vm_list[c[0]].ram/(2**(nod.vm_list[c[0]].level-1)),nod.vm_list[c[0]].cpu/(2**(nod.vm_list[c[0]].level-1)))-mCost(nod.vm_list[d[0]].ram/(2**(nod.vm_list[d[0]].level-1)),nod.vm_list[d[0]].cpu/(2**(nod.vm_list[d[0]].level-1)))),reverse=True )
					print "c2",x.name,map(lambda c:(nod.vm_list[c[0]].name,nod.vm_list[c[0]].ram,nod.vm_list[c[0]].cpu,nod.vm_list[c[0]].level) , vic2_vms);
					break
	nod.host_list[nod.victim].status=0;

test1=cp.deepcopy(state0)


potential_vics=findVic(test1)
potential_vics.sort(cmp = lambda c,d:-1 if(mCost(test1.host_list[c].usedR,test1.host_list[c].usedC)-mCost(test1.host_list[d].usedR,test1.host_list[d].usedC))<0 else 1 )
print "potential_vics",map(lambda c:test1.host_list[c].name ,potential_vics)

mini=float("inf")
index=-1
for ele in potential_vics:
	_temp=mCost(test1.host_list[ele].usedR,test1.host_list[ele].usedC)
	if _temp>0 and _temp<=mini:
		# print test1.host_list[ele].name,_temp,test1.host_list[ele].usedR
		mini=_temp
		index=ele

test1.victim=index
# print index,test1.victim

createGraph(test1)
_level=0
# while _level<=2:
# 	test1.victim=potential_vics[_level]
# 	try:
# 		help(test1)
# 		createGraph(test1)
# 	except Exception, e:
# 		print "finally failed for",_level,"hosts"                   
# 		exit(0)
# 	_level+=1

# printState(test1)

# createGraph(test1)
plt.show()