import random as rand
import copy as co

class host:
	def __init__(self , ram , cpu  ):
		self.ram = ram
		self.cpu = cpu
		self.vm = []
		self.usedR=0
		self.usedC=0

class vm :
	def __init__(self,host,ram,cpu):
		self.host = host
		self.ram = ram
		self.cpu = cpu
		self.on =True if rand.random()<=0.5 else False

def wt(r,c):
	return r*0.75 + 0.25*c

N,M=1000,400
host_list = []
vm_list = []

for x in xrange(0,N):
	host_list+=[host( 0.5*(1+rand.random()), 0.5*(1+rand.random())  )]

for x in xrange(0,M):
	h=int(100*rand.random())
	vm1 = vm( h  , 0.25*rand.random() , 0.25*rand.random() )
	host_list[h].vm+=[x]
	host_list[h].usedR+=vm1.ram
	host_list[h].usedC+=vm1.cpu
	vm_list+=[vm1]

def addFF(r,c,num):
	global host_list,vm_list,N,M
	done = False
	for i,x in enumerate(host_list):
		if wt(x.usedR,x.usedC)==0:
			continue
		if (x.ram-x.usedR)>r and x.cpu-x.usedC>c:
			host_list[i].usedR+=r
			host_list[i].usedC+=c
			host_list[i].vm+=[num]
			vm_list[num].on=True
			done=True
			break
	if done==False:
		for i,x in enumerate(host_list):
			if wt(x.usedR,x.usedC)==0 and r<x.ram and c<x.cpu:
				host_list[i].usedR+=r
				host_list[i].usedC+=c
				host_list[i].vm+=[num]
				vm_list[num].on=True
				done=True
	return done


def addBF(r,c,num):
	global host_list,vm_list,N,M
	bestr=1
	bestn=-1
	for i,x in enumerate(host_list):
		if wt(x.usedR,x.usedC)==0:
			continue
		if (x.ram-x.usedR)>r and (x.cpu-x.usedC>c) and bestr>wt(x.ram-x.usedR,x.cpu-x.usedC):
			bestr=wt(x.ram-x.usedR,x.cpu-x.usedC)
			bestn=i
	if bestn!=-1:
		host_list[bestn].usedR+=r
		host_list[bestn].usedC+=c
		host_list[bestn].vm+=[num]
		# print "here"
		vm_list[num].on=True
		return True
	else:
		for i,x in enumerate(host_list):
			if x.usedR==0 and r<x.ram and c<x.cpu and bestr<wt(x.ram,x.cpu):
				bestr=wt(x.ram,x.cpu)
				bestn=i
		if bestn!=-1:
			host_list[bestn].usedR+=r
			host_list[bestn].usedC+=c
			host_list[bestn].vm+=[num]
			vm_list[num].on=True
			print "here"
			return True
		# else:
			# print "3333"
	return bestn!=-1

requests1,requests2=[],[]
for x in xrange(1,20000):
	requests1+=[0.25*rand.random()]
	requests2+=[0.25*rand.random()]

ff1,f1=0,0
vm_l=co.deepcopy(vm_list)
host_l=co.deepcopy(host_list)

for i,x in enumerate(vm_list):
	if x.on==False:
		req=addFF(requests1[i],requests2[i],i)
		if req:
			ff1+=1
		else:
			f1+=1

print "passFF:", ff1 , "failFF" , f1

ff2,f2=0,0
vm_list=co.deepcopy(vm_l)
host_list=co.deepcopy(host_l)

for i,x in enumerate(vm_list):
	if x.on==False:
		req=addBF(requests1[i],requests2[i],i)
		if req:
			ff2+=1
		else:
			f2+=1

print "passBF:", ff2 , "failBF" , f2