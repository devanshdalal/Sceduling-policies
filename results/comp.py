import random as rand
import urllib2
import re
import copy as cp
import traceback
import numpy as np 
import matplotlib.pyplot as plt

freq=5
colors = ['b','g','r','c','m','y','k']
col_n = len(colors)

class host:
	def __init__(self , status , name ):
		self.status = status
		self.ram = 16
		self.cpu = 16
		self.name=name
		self.vm = []
		self.usedR=0
		self.usedC=0


class vm :
	def __init__(self,host,ram,name,cpu):
		self.host = int(host)
		self.ram = ram
		self.cpu = cpu
		self.name = name
		self.color = colors[(int)(rand.random() * col_n)]

################################################################################################################################

class node:
	def __init__(self,hlist):
		self.host_list = hlist
		self.victim=-1

state0=node([])

##########################################################   GRAPHS   ######################################################################################

def findMaxActive(w):
	maxm = -1
	for x in w.host_list:
		if (len(x.vm)>maxm):
			maxm=len(x.vm)
	return maxm

def graphWt(cpu,ram):
	return ram

def createGraph(w):
	plt.figure()
	rows , columns = findMaxActive(w),len(w.host_list)
	hostRamUsage = np.zeros((columns) )
	hostCpuUsage = np.zeros((columns) )
	g = np.zeros((2,rows,columns) )
	vmc = [['w']*columns]*rows
	vmc = np.array(vmc)
	for j,x in enumerate(w.host_list):
		activeVms=x.vm
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
	plt.xticks(indram+width , (hostNames) , rotation=45)
	plt.legend((p2[0],p3[0]) , ('RAM','CPU'))

#################################################################################################################################
def effRes(v):
	(n_r,n_c) = ( v.ram , v.cpu )
	return (1 if n_r<=1 else n_r , 1 if n_c<=1 else n_c  )

def printState(w):
	print 'Total Numbers of hosts: ' + str(len(w.host_list))
	activeHosts= filter(lambda c:c.status==1, w.host_list )
	print 'Total Numbers of active hosts: ' + str(len(  activeHosts ))
	count = 0
	for x in host_list:
		count+=len(x.vm)

	print 'Total Numbers of Active Vms: ' + str(count)
	mapp={}
	mapp["test1"]="string1"
	for x in w.host_list:
		activeVms =x.vm
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


def mCost(r,c):
	return r*0.9 + 0.1*c

def mCost1(v):
	return v[0]*0.9 + 0.1*v[1]

def eqwt(r,c):
	return (r)*0.5 + 0.5*c

def eqwt1(v):
	return v[0]*0.5 + 0.5*v[1]

def vCost(r,c,n):
	return 0.4*r + 0.4*c + 0.2*(0.5*r+0.5*c)/n

def findVic(w):
	mini=float("inf")
	ans=-1
	for j,i in enumerate(w.host_list):
		if i.status!=1 or i.usedR>i.ram or i.usedC>i.cpu:
			continue
		lenth=len(  i.vm )
		temp=vCost(i.usedR,i.usedC,lenth)
		if temp<mini:
			mini=temp
			ans=j
	return ans

def help(nod):
	nod.victim=findVic(nod)
	print "p1",nod.host_list[nod.victim].name
	
	activeVms=nod.host_list[nod.victim].vm
	nod.host_list[nod.victim].usedR,nod.host_list[nod.victim].usedC=0,0
	###
	victim_vms=map(lambda c:(c,1) ,activeVms)
	print "p2",map( lambda f:(f[0].name,f[0].ram,f[0].cpu) , victim_vms )

	while victim_vms!=[]:
		victim_vms=sorted(victim_vms,key=lambda x: eqwt1( effRes(x[0]) ),reverse=True)
		# ###################
		(head,lvl)=victim_vms[0]
		victim_vms=victim_vms[1:]
		print "-------------------------------------------------------------------------------------------------------------------------------"
		if(lvl>3):
			#########
			print "FAIL"
			raise Exception('failed', 'exiting')
		(n_r,n_c)=(head.ram,head.cpu)
		n_n=head.name
		print "vmName:",n_n
		fitted=False
		st=""

		#####
		host_l=sorted(nod.host_list,key=lambda c:mCost(c.usedR,c.usedC),reverse=True )##
		for x in host_l:
			j=x.name
			if (j==nod.victim or eqwt(x.usedR,x.usedC)<=0 or x.status!=1):
				continue
			freeC=x.cpu-x.usedC
			freeR=x.ram-x.usedR
			if freeC>=n_c and freeR>=n_r:
				print "inside"
				head.host = nod.host_list[j].name
				nod.host_list[j].vm+=[head]
				nod.host_list[j].usedC+=n_c
				nod.host_list[j].usedR+=n_r
				st+= head.name+ "("+str(n_r)+","+str(n_c)+")"  +" vm added successfully to "
				st+= str(x.name) + " : usedR " + str(x.usedR)+"/"+ str(x.ram) + " usedC " + str(x.usedC) + "/" + str(x.cpu) + '\n'
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
				if (j==nod.victim or eqwt(x.usedR,x.usedC)<=0 or freeR<=0 or freeC<=0 or x.status!=1):#############???
					continue
				vic2_vms = cp.deepcopy(x.vm)
				vic2_vms.sort(key=lambda c: mCost1( effRes(c) )  )
				print "c1",x.name,map(lambda c:(c.name,c.ram,c.cpu) , vic2_vms);
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
						nod.host_list[j].vm+=[head]
						nod.host_list[j].usedR+=(n_r - _ram)
						nod.host_list[j].usedC+=(n_c - _cpu)
						vic2_vms=vic2_vms[:k+1]
						found=True;
						break
				if found:
					vic2_vms=map(lambda c:(c,lvl+1) ,vic2_vms)
					victim_vms+=vic2_vms;
					print "c2",x.name,map(lambda c:(c[0].name,c[0].ram,c[0].cpu) , vic2_vms)
					fitted=True
					break
			if(not fitted) :
				print "Failed_Indirectly"
				raise Exception('failed', 'unable to fit')
	nod.host_list[nod.victim].status=0;
	nod.host_list[nod.victim].vm=[]

print "#####################################################################################################################################"

def firstFit(w,vm):
	# print "in firstFit "
	done = False
	(n_r,n_c)=effRes(vm)
	host_sorted = sorted(w.host_list , key = lambda c : -eqwt(c.usedR,c.usedC) )
	for x in (host_sorted):
		i = x.name
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
	if done==False:
		temp=host(1,len(w.host_list))

		temp.usedR=n_r
		temp.usedC=n_c
		vm.host=temp.name
		temp.vm+=[vm]
		w.host_list+=[temp]

def remVm1(w,vm):
	# print "in remVm1 "
	h=-1
	for i,x in enumerate(w.host_list):
		for y in x.vm:
			if vm.name==y.name:
				h=i
				break
		if h!=-1:
			break
	if h==-1:
		print "going wrong ?????????????????????????????"
		exit(0)
	for i,v in enumerate(w.host_list[h].vm):
		if (v.name == vm.name):
			(n_r,n_c) = effRes(v)
			w.host_list[h].vm.remove(v)
			w.host_list[h].usedR -= n_r
			w.host_list[h].usedC -= n_c
			if (len(w.host_list[h].vm) == 0):
				w.host_list[h].status = 0	
			break

def genVm():
	n_c = rand.choice([1,2,4,8]);
	if (n_c == 8): n_r = 8
	else: n_r = rand.choice([1,2])*n_c
	return vm(-1,n_r,"",n_c)

# def genVm():
# 	n_c = rand.choice([1,2,4,8]);
# 	n_r = rand.choice([1,2,4,8])
# 	return vm(-1,n_r,"",n_c)

def createVmList(n):
	l = []
	ma = {}
	for i in range(n):
		v = genVm()
		if (rand.uniform(0.0,9.0)<=5.0 or not ma):
			v.name="dvnk"+str(i)
			ma[i] = True		
		else:
			i = rand.choice(ma.keys())
			v.name = "dvnk"+str(i)
			v.ram = -1
			del ma[i]
		l+=[v]
	return l

def startSimFF(w,l):
	hav = 0
	h=len(l)/10
	for i,v in enumerate(l):
		if (v.ram == -1):
			remVm1(w,v)
		else:
			firstFit(w,v)
		# print "len", len(filter( lambda c:c.status==1  , w.host_list))
		hav += len(filter( lambda c:c.status==1  , w.host_list))
		if i%h==0:
			print "len", len(filter( lambda c:c.status==1  , w.host_list))
	return (1.0*hav)/len(l),len(filter( lambda c:c.status==1  , w.host_list))

def startSimFF2(w,l):
	ff = open('res.txt','w')
	hav = 0
	h=len(l)/10
	for i,v in enumerate(l):
		if (v.ram == -1):
			remVm1(w,v)
		else:
			firstFit(w,v)
		hav += len(filter( lambda c:c.status==1  , w.host_list))
		if i%freq==0:
			try:
				newNode=cp.deepcopy(w)
				newNode1=cp.deepcopy(w)
				help(newNode)
				w=newNode
				# createGraph(newNode1)
				# createGraph(w)
				# plt.show()
			except Exception, e:
				# createGraph(w)
				# print "???????????????///    " , w.victim
				# plt.show()
				print "Couldn't do it: %s" % e
				traceback.print_exc()

		if (i%200==0):
			writeToFile(w,i/200)
			ff.write(str(i) + " "+str(len(filter( lambda c:c.status==1  , w.host_list)))+"\n")


		if i%h==0:
			print "len", len(filter( lambda c:c.status==1  , w.host_list))
	ff.close()
	return (1.0*hav)/len(l),len(filter( lambda c:c.status==1  , w.host_list))

def writeToFile(w,count):
	jobs=0
	name = 'sim' + str(count) + '.txt'
	f = open(name,'w')
	stri=""
	for x in w.host_list:
		if (x.status != 1) : continue
		for v in x.vm:
			stri += str(v.ram) + "," + str(v.cpu) + ",\n"
			jobs+=1
	f.write(str(jobs)+"\n"+str(2)+"\n")
	f.write(stri)
	f.close()

test1=cp.deepcopy(state0)
test2=cp.deepcopy(state0)

n=1400
l=createVmList(n)
ll=cp.deepcopy(l)
remove=len(filter(lambda c:c.ram==-1,l))
print remove,n- remove


f1= startSimFF(test1,l)
# createGraph(test1)
f2= startSimFF2(test2,ll)

print "final ",f1,f2
plt.show()