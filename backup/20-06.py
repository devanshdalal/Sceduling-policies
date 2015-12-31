import random as rand
import urllib2
import re
import copy as cp
import numpy as np 
import matplotlib.pyplot as plt

content = ""
host_list = []
host_map = {}
colors = ['b','g','r','c','m','y','k']
col_n = len(colors)

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
		self.cpu = cpu
		self.name = name
		self.vm = []
		self.usedR=0
		self.usedC=0


class vm :
	def __init__(self,host,ram,name,level,cpu):
		self.host = host
		self.ram = ram
		self.cpu = cpu
		self.name = name
		self.level = level
		self.color = colors[(int)(rand.random() * col_n)]

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

	host_list[host_map[host]].vm += [vm(host , int(l[1]) , name, int(l[3]) , int(cpu))]
	return None

for i,s in enumerate(vm_data):
	extractvm(i,s)

################################################################################################################################

class node:
	def __init__(self,hlist,hmap,vic):
		self.host_list = hlist
		self.host_map = hmap
		self.victim=vic

state0=node(host_list,host_map,-1)

#################################################################################################################################
def effRes(v):
	if v.level==0:
		return (0,0)
	(n_r,n_c) = ( v.ram/(1<<(v.level-1)) , v.cpu/(1<<(v.level-1)) )
	return (1024 if n_r<=1024 else n_r , 1 if n_c<=1 else n_c  )


def printState(w):
	print 'Total Numbers of hosts: ' + str(len(w.host_list))
	activeHosts= filter(lambda c:c.status==1, w.host_list )
	print 'Total Numbers of active hosts: ' + str(len(  activeHosts ))
	count = 0 
	# for v in w.vm_list:
	# 	if (v.level != 0):
	# 		count += 1
	count = 0

	print 'Total Numbers of Active Vms: ' + str(count)
	mapp={}
	mapp["test1"]="string1"
	for x in w.host_list:
		activeVms=filter( (lambda v: v.level>0 ) , x.vm)
		#print str(len(activeVms)) + " " +str(len(x.vm))
		x.usedC=0
		x.usedR=0
		mapp[x.name]=""
		for z in activeVms:
			mapp[x.name]=mapp[x.name]+ ("  ("+'{0:6}'+","+'{1:5}'+","+'{2:2}'+","+'{3:1}'+")").format(z.name,str(z.ram),str(z.cpu),str(z.level))
			(n_r,n_c) = effRes(z)
			x.usedR+=n_r
			x.usedC+=n_c

	for x in w.host_list:
		print ('{0:7}' + " : usedRam " + '{1:5}' + "/"+ '{2:5}' + " usedCpu " + '{3:2}' + "/" + '{4:2}' ).format(x.name,str(x.usedR),str(x.ram),str(x.usedC),str(x.cpu)),mapp[x.name] 

printState(state0)

##########################################################   GRAPHS   ######################################################################################


def findMaxActive(w):
	max = -1
	for x in w.host_list:
		activeVms=filter( (lambda v: v.level>0 ) , x.vm)
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
	vmc = [['w']*columns]*rows
	vmc = np.array(vmc)
	for j,x in enumerate(w.host_list):
		activeVms=filter( (lambda v: v.level>0 ) , x.vm)
		for i,z in enumerate(activeVms):
			(uram,ucpu) = effRes(z)
			g[0][i][j] = graphWt(ucpu , uram)
			g[1][i][j] = ucpu
			vmc[i][j] = z.color

		hostRamUsage[j] = graphWt(x.cpu,x.ram)
		hostCpuUsage[j] = x.cpu


	width = 0.5
	ind = np.arange(columns)
	indram = 2*ind
	indcpu = indram+width
	hghtRam = [0]*(columns)
	hghtCpu = [0]*(columns)
	for i in range(rows):
		p = plt.bar(indram,g[0][i],width,color=vmc[i],bottom=hghtRam,alpha=0.5)
		p = plt.bar(indcpu,g[1][i],width,color=vmc[i],bottom=hghtCpu,alpha=0.5)
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


#########################################################################################################################################################################
print "####################################################################################################################################################"

def eqwt(r,c):
	return r/2 + 512*c

def firstFit(w,vm):
	done = False
	(n_r,n_c)=effRes(vm)
	host_sorted = sorted(w.host_list , cmp = lambda c,d : -eqwt(c.usedR,c.usedC) + eqwt(d.usedR,d.usedC))
	for x in (host_sorted):
		i = host_map[x.name]
		if x.status!=1:
			continue
		if (x.ram-x.usedR)>=n_r and x.cpu-x.usedC>=n_c:
			w.host_list[i].usedR+=n_r
			w.host_list[i].usedC+=n_c
			vm.host=x.name
			w.host_list[i].vm+=[vm]
			done=True
			break
	if done==False:
		for i,x in enumerate(w.host_list):
			if x.status!=1 and n_r<=x.ram and n_c<=x.cpu:
				w.host_list[i].status=1
				w.host_list[i].usedR=n_r
				w.host_list[i].usedC=n_c
				vm.host=x.name
				w.host_list[i].vm=[vm]
				done=True
				break
	return done

def bestFit(w,vm):
	(n_r,n_c)=effRes(vm)
	bestW=float("inf")
	bestH=-1
	for i,x in enumerate(w.host_list):
		if x.status!=1:
			continue
		if (x.ram-x.usedR)>=n_r and (x.cpu-x.usedC>=n_c) and eqwt(x.ram-x.usedR,x.cpu-x.usedC)<bestW:
			bestH=i
			bestW=eqwt(x.ram-x.usedR,x.cpu-x.usedC)
	if bestH!=-1:
		w.host_list[bestH].usedR+=n_r
		w.host_list[bestH].usedC+=n_c
		vm.host=w.host_list[bestH].name
		w.host_list[bestH].vm+=[vm]
		return True
	else:
		for i,x in enumerate(w.host_list):
			if x.status!=1 and n_r<=x.ram and n_c<=x.cpu:
				w.host_list[i].status=1
				w.host_list[i].usedR=n_r
				w.host_list[i].usedC=n_c
				vm.host=x.name
				w.host_list[i].vm=[vm]
				return True
				break
	return False

def randFit(w,vm):
	done = False
	(n_r,n_c)=effRes(vm)
	host_l=cp.deepcopy(w.host_list)
	while done==False and len(host_l)!=0:
		x=rand.choice(host_l)
		i=w.host_map[x.name]
		if x.status==1 and (x.ram-x.usedR)>=n_r and x.cpu-x.usedC>=n_c:
			w.host_list[i].usedR+=n_r
			w.host_list[i].usedC+=n_c
			vm.host=x.name
			w.host_list[i].vm+=[vm]
			done=True
		host_l.remove(x)
	if done==False:
		for i,x in enumerate(w.host_list):
			if x.status!=1 and n_r<=x.ram and n_c<=x.cpu:
				w.host_list[i].status=1
				w.host_list[i].usedR=n_r
				w.host_list[i].usedC=n_c
				vm.host=x.name
				w.host_list[i].vm=[vm]
				done=True
				break
	return done

def remVm(w):
	done = False
	while done==False :
		x=rand.choice(w.host_list)
		if x.status!=1:
			continue
		i=w.host_map[x.name]
		v = rand.choice(x.vm)
		(n_r,n_c) = effRes(v)
		w.host_list[i].vm.remove(v)
		w.host_list[i].usedR -= n_r
		w.host_list[i].usedC -= n_c
		if (len(w.host_list[i].vm) == 0):
			w.host_list[i].status = 0
		done = True

def genVm():
	level = rand.choice([1,2,3])
	n_c = rand.choice([1,2,4,8]);
	if (n_c == 8): n_r = 8*1024
	else: n_r = 1024*(rand.choice([1,2]))*n_c
	return vm("",n_r,"",level,n_c)

def createVmList(n):
	l = []
	for i in range(n):
		v = genVm()
		if (rand.random()<0.5):
			v.level = -1
		l+=[v]
	return l

def startSimFF(w,l):
	fail = 0
	hav = 0
	for v in l:
		if (v.level == -1):
			remVm(w)
		else:
			if not firstFit(w,v):
				fail+=1
		hav += len(filter( lambda c:c.status==1  , w.host_list))

	return (fail,(1.0*hav)/len(l))

def startSimBF(w,l):
	fail = 0
	hav = 0
	for v in l:
		if (v.level == -1):
			remVm(w)
		else:
			if not bestFit(w,v):
				fail+=1
		hav += len(filter( lambda c:c.status==1  , w.host_list))

	return (fail,(1.0*hav)/len(l))

def startSimRF(w,l):
	fail = 0
	hav = 0
	for v in l:
		if (v.level == -1):
			remVm(w)
		else:
			if not randFit(w,v):
				fail+=1
		hav += len(filter( lambda c:c.status==1  , w.host_list))
	
	return (fail,(1.0*hav)/len(l))


test1=cp.deepcopy(state0)
test2=cp.deepcopy(state0)
test3=cp.deepcopy(state0)
# createGraph(test1)

# v1=vm("",1024,"hfd",1,2);
# # randFit(test1,v1)
# # remVm(test1)
# firstFit(test1,genVm())
l = createVmList(10000)
f = startSimFF(test1,l)
# createGraph(test1)
print "******FIRST FIT******* ",f

b = startSimBF(test2,l)
# createGraph(test2)
print "******BEST FIT****** ",b

r = startSimRF(test3,l)
# createGraph(test3)
print "******RANDOM FIT****** ",r

# plt.show()