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
vhmap={}

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
	vhmap[name] = host_map[host]
	return None

for i,s in enumerate(vm_data):
	extractvm(i,s)

################################################################################################################################

class node:
	def __init__(self,hlist,hmap,vic,v_hmap):
		self.host_list = hlist
		self.host_map = hmap
		self.victim=vic
		self.vhmap=v_hmap

state0=node(host_list,host_map,-1,vhmap)

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
	for x in host_list:
		count+=len(filter(lambda c:c.level>0,x.vm))

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
def mCost(r,c):
	return r*0.9 + 102.4*c

def mCost1(v):
	return v[0]*0.9 + 102.4*v[1]

def vCost(r,c,n):
	return 0.4*r + 0.4*1024*c - 0.2*1024*n

def findVic(w):
	mini=float("inf")
	ans=-1
	for j,i in enumerate(w.host_list):
		if i.status!=1:
			continue
		lenth=len( filter(lambda c:c.level>0, i.vm) )
		# print "len:",i.name,i.usedR,i.usedC,lenth
		temp=vCost(i.usedR,i.usedC,lenth)
		if temp<mini:
			mini=temp
			ans=j
	return ans

def help(nod):
	nod.victim=findVic(nod)
	print nod.host_list[nod.victim].name

	activeVms=filter( (lambda y: y.level>0 ) , nod.host_list[nod.victim].vm)
	
	nod.host_list[nod.victim].vm=filter(lambda c: c.level==0 ,  nod.host_list[nod.victim].vm )
	nod.host_list[nod.victim].usedR,nod.host_list[nod.victim].usedC=0,0
	# nod.host_list[nod.victim].status=0
	###
	victim_vms=map(lambda c:(c,1) ,activeVms)
	print "p1",nod.host_list[nod.victim].name
	print "p2",map( lambda f:(f[0].name,f[0].ram,f[0].cpu,f[0].level) , victim_vms )

	while victim_vms!=[]:
		victim_vms=sorted(victim_vms,key=lambda x:mCost1( effRes(x[0]) ),reverse=True)
		(head,lvl)=victim_vms[0]
		victim_vms=victim_vms[1:]
		print "-------------------------------------------------------------------------------------------------------------------------------"
		if(lvl>3):
			#########
			print "FAIL"
			raise Exception('failed', 'exiting')
		n_l=head.level
		n_r=1.0*head.ram/(2**(n_l-1))
		n_c=1.0*head.cpu/(2**(n_l-1))
		n_n=head.name
		print "vmName:",n_n
		bestR=float("inf")
		bestC=float("inf")
		target=-1
		fitted=False
		st=""
		host_l=sorted(nod.host_list,key=lambda c:eqwt(c.usedR,c.usedC),reverse=True )##
		for x in host_l:
			j=nod.host_map[x.name]
			if (j==nod.victim or wt(x.usedR,x.usedC)<=0 or x.status!=1):
				continue
			freeC=x.cpu-x.usedC
			freeR=x.ram-x.usedR
			if freeC>=n_c and freeR>=n_r:
				print "inside"
				head.host= nod.host_list[j].name
				nod.vhmap[n_n]=j
				nod.host_list[j].vm+=[head]
				nod.host_list[j].usedC+=n_c
				nod.host_list[j].usedR+=n_r
				st+= head.name+ "("+str(n_r)+","+str(n_c)+")"  +" vm added successfully to "
				st+= x.name + " : usedR " + str(x.usedR)+"/"+ str(x.ram) + " usedC " + str(x.usedC) + "/" + str(x.cpu) + '\n'
				print "here:",st
				fitted=True
				break
		if(not fitted):
			print "not fitted"
			vic2_vms=[]
			####################sort or not?
			for j,x in enumerate(nod.host_list):
				freeC=x.cpu-x.usedC
				freeR=x.ram-x.usedR
				if (i==nod.victim or wt(x.usedR,x.usedC)<=0 or freeR<=0 or freeC<=0 or x.status!=1):#############???
					continue
				vic2_vms = cp.deepcopy(filter(lambda c : c.level>0 ,x.vm))
				vic2_vms.sort(key=lambda c:mCost1( effRes(c) )  )
				print "c1",x.name,map(lambda c:(c.name,c.ram,c.cpu,c.level) , vic2_vms);
				_ram,_cpu=0,0
				found=False
				for k,z in enumerate(vic2_vms):
					(_newRam,_newCpu)=effRes(z)
					if _newRam>=n_r or _newCpu>=n_c:
						break;                              ##  remember to change
					_ram+=_newRam
					_cpu+=_newRam
					if _ram+freeR>=n_r and _cpu+freeC>=n_c:

						nod.host_list[j].vm=vic2_vms[k+1:]
						head.host=nod.host_list[j].name
						nod.vhmap[n_n]=j
						nod.host_list[j].vm+=[head]
						nod.host_list[j].usedR+=(n_r - _ram)
						nod.host_list[j].usedC+=(n_c - _cpu)
						vic2_vms=vic2_vms[:k+1]
						found=True;
						break
				if found:
					vic2_vms=map(lambda c:(c,lvl+1) ,vic2_vms)
					victim_vms+=vic2_vms;
					print "c2",x.name,map(lambda c:(c[0].name,c[0].ram,c[0].cpu,c[0].level) , vic2_vms)
					fitted=True
					break
			if(not fitted) :
				print "Failed_Indirectly"
				raise Exception('failed', 'unable to fit')
	nod.host_list[nod.victim].status=0;


print "####################################################################################################################################################"

def eqwt(r,c):
	return r/2 + 512*c

def firstFit(w,vm):
	done = False
	(n_r,n_c)=effRes(vm)
	host_sorted = sorted(w.host_list , key = lambda c : -eqwt(c.usedR,c.usedC) )
	for x in (host_sorted):
		i = w.host_map[x.name]
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
	if (done) : w.vhmap[vm.name] = w.host_map[vm.host]
	return done

def bestFit(w,vm):
	done = False
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
		done= True
	else:
		for i,x in enumerate(w.host_list):
			if x.status!=1 and n_r<=x.ram and n_c<=x.cpu:
				w.host_list[i].status=1
				w.host_list[i].usedR=n_r
				w.host_list[i].usedC=n_c
				vm.host=x.name
				w.host_list[i].vm=[vm]
				done= True
				break
	if (done) : w.vhmap[vm.name] = w.host_map[vm.host]
	return done

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
	if (done) : w.vhmap[vm.name] = w.host_map[vm.host]
	return done

def remVm1(w,vm):
	done = False
	h=-1
	for i,x in enumerate(w.host_list):
		for y in x.vm:
			if vm.name==y.name:
				h=i
				break
		if h!=-1:
			break
	if h==-1:
		print "faillllll in remVm1"
		return 0,True
	hh=False
	for i,v in enumerate(w.host_list[h].vm):
		if (v.name == vm.name):
			(n_r,n_c) = effRes(v)
			w.host_list[h].vm.remove(v)
			w.host_list[h].usedR -= n_r
			w.host_list[h].usedC -= n_c
			if (len(w.host_list[h].vm) == 0):
				w.host_list[h].status = 0	
			if (vm.level != 0):
				v.level = vm.level
				done = firstFit(w,v)
			else:
				done=True
			hh=True
			break
	return 0 if done else 1,hh

def genVm():
	level = rand.choice([1,2,3])
	n_c = rand.choice([1,2,4,8]);
	if (n_c == 8): n_r = 8*1024
	else: n_r = 1024*(rand.choice([1,2]))*n_c
	return vm("",n_r,"",level,n_c)

def createVmList(w,n):
	l = []
	ma={}
	for x in w.host_list:
		for y in x.vm:
			if y.level!=0:
				ma[y.name]=y.level
	for i in range(n):
		v = genVm()
		if (rand.random()<0.25 or not(ma) ):
			v.name="dvnk"+str(i)
		else:
			v.name = rand.choice(ma.keys()) 
			lchoice = [0,1,2,3]
			lchoice.remove(ma[v.name])
			v.level = rand.choice(lchoice)
			v.ram = -1
		if v.level!=0 : ma[v.name] = v.level
		else: del ma[v.name]
		l+=[v]
	return l

def checkExists(w,v):
	h=w.host_list[w.vhmap[v.name]]
	for vms in h.vm:
		if (vms.name == v.name):
			return True
	return False

def startSimFF(w,l):
	fail,f1,f2 = 0,0,0
	hav = 0
	for v in l:
		if (v.ram == -1):
			temp=remVm1(w,v)
			fail+=temp[0]
			f1+=temp[0]
		else:
			if not firstFit(w,v):
				fail+=1
				f2+=1
		hav += len(filter( lambda c:c.status==1  , w.host_list))
	return fail,(1.0*hav)/len(l),f1,f2

def startSimFF2(w,l):
	fail,f1,f2 = 0,0,0
	hav = 0
	for i,v in enumerate(l):
		if (v.ram == -1):
			temp=remVm1(w,v)
			fail+=temp[0]
			f1+=temp[0]
		else:
			if not firstFit(w,v):
				fail+=1
				f2+=1
		hav += len(filter( lambda c:c.status==1  , w.host_list))
		if i%30==0:
			newNode=cp.deepcopy(w)
			try:
				help(newNode)
				w=cp.deepcopy(newNode)
			except:
				print "failing in sff2",i
				pass
	return fail,(1.0*hav)/len(l),f1,f2

def startSimBF(w,l):
	fail = 0
	hav = 0
	for v in l:
		if (v.ram == -1):
			fail+=remVm1(w,v)[0]
		else:
			if not bestFit(w,v):
				fail+=1
		hav += len(filter( lambda c:c.status==1  , w.host_list))
	return (fail,(1.0*hav)/len(l))

def startSimRF(w,l):
	fail = 0
	hav = 0
	for v in l:
		if (v.ram == -1):
			fail+=remVm1(w,v)[0]
		else:
			if not randFit(w,v):
				fail+=1
		hav += len(filter( lambda c:c.status==1  , w.host_list))
	return (fail,(1.0*hav)/len(l))


test1=cp.deepcopy(state0)
test2=cp.deepcopy(state0)
test3=cp.deepcopy(state0)
createGraph(test1)

l = createVmList(state0, 20000)
ll = cp.deepcopy(l)

# v1=vm("",8024,"hfd",1,8);
# # randFit(test1,v1)
# firstFit(test1,genVm())
f = startSimFF(test1,l)
# createGraph(test1)
# print "******FIRST FIT******* ",f

# b = startSimBF(test2,l)
# createGraph(test2)
# print "******BEST FIT****** ",b

# r = startSimRF(test3,l)
# createGraph(test3)
# print "******RANDOM FIT****** ",r

#-----------------------------------------------------------------------------------------------------------------------------------------

f2 = startSimFF2(test2,ll)
# createGraph(test2)
print "******FIRST FIT******* ",f
print "******FIRST FIT2******* ",f2


# test3.victim=test3.host_map['host51']
# help(test3)

# createGraph(test3)
# plt.show()

