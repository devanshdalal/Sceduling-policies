def start(pid,vmid,chost_id=None,dhost_id=None,parameters=None):
    from time import time
    vm=db(db.vm.id==vmid).select()[0]
    vmname = vm['name']
    newhost=redefinedomain(vmname)
    #migratebeforestart(pid,vmid)
    if(vm['locked']):
	print "VM is locked"
        db(db.queue.id==pid).update(status=-1,comments="VM Locked by Administrator. Contact Administrators",ftime=putdate())
    elif(newhost==None):
        db(db.queue.id==pid).update(status=-1,comments="No appropriate host found. Try later",ftime=putdate())
    else:
        output = pyshell(vmname, "start")
        if(output[0] == 0) :
            db(db.vm.name==vmname).update(runlevel=vm.nextrunlevel,laststarttime=time())
            db(db.queue.id==pid).update(status=1,comments="VM Started. Switch to required Runlevel yourself",ftime=putdate())
        else:
            db(db.queue.id==pid).update(status=-1,comments=output[1],ftime=putdate())
    return
    
def destroyold(pid,vmid,chost_id=None,dhost_id=None,parameters=None):
    import commands
    vm = db(db.vm.id == vmid).select()[0]
    vmname = vm['name']
    if(vm['ip']==None):
        db(db.queue.id==pid).update(comments="IP of vm is None. Use 'shutdown -h now' from inside vm",status=1,ftime=putdate())
    else:
	try:
	    #output=commands.getstatusoutput('ssh cscroot@'+vm['ip']+' shutdown -h now')
    	    output = pyshell(vmname, "destroy")
    	    if(output[0] == 0) :
        	addtocost(vmname)
        	db(db.vm.name == vmname).update(lastrunlevel=db(db.vm.name==vmname).select(db.vm.runlevel)[0].runlevel,runlevel=0)
        	db(db.queue.id==pid).update(status=1,ftime=putdate())
	    else:
        	db(db.queue.id==pid).update(comments="Tried ssh shutdown."+output[1],status=-1,ftime=putdate())
	except:
            db(db.queue.id==pid).update(comments="ssh exception.Try 'shutdown -h now' from inside vm.",status=-1,ftime=putdate())
    return

def shutdown(pid,vmid,chost_id=None,dhost_id=None,parameters=None):
    vmname = db(db.vm.id == vmid).select(db.vm.name)[0]['name']
    output = pyshell(vmname, "shutdown")
    if(output[0] == 0) :
        addtocost(vmname)
        db(db.vm.name == vmname).update(lastrunlevel=db(db.vm.name==vmname).select(db.vm.runlevel)[0].runlevel)
        db(db.queue.id==pid).update(status=1,ftime=putdate())
    else:
        db(db.queue.id==pid).update(status=-1,comments=output[1],ftime=putdate())
    return


def destroy(pid,vmid,chost_id=None,dhost_id=None,parameters=None):
    vmname = db(db.vm.id == vmid).select(db.vm.name)[0]['name']
    output = pyshell(vmname, "destroy")
    if(output[0] == 0) :
        addtocost(vmname)
        db(db.vm.name == vmname).update(lastrunlevel=db(db.vm.name==vmname).select(db.vm.runlevel)[0].runlevel,runlevel=0)
        db(db.queue.id==pid).update(status=1,ftime=putdate())
    else:
        db(db.queue.id==pid).update(status=-1,comments=output[1],ftime=putdate())
    return


def suspend(pid,vmid,chost_id=None,dhost_id=None,parameters=None):
    vmname = db(db.vm.id == vmid).select(db.vm.name)[0]['name']
    output = pyshell(vmname, "suspend")
    if(output[0] == 0) :
        db(db.queue.id==pid).update(status=1,ftime=putdate())
    else:
        db(db.queue.id==pid).update(status=-1,comments=output[1],ftime=putdate())
    return

def delete(pid,vmid,chost_id=None,dhost_id=None,parameters=None):
    vm = db(db.vm.id == vmid).select()[0]
    vmname = vm.name
    datastore = db(db.vm.id == vm.id).select(db.vm.datastore)[0].datastore
    hdd = datastore.used-vm.HDD

    output = pyshell(vmname, "delete")
    if(output[0] == 0) :
        db(db.queue.id==pid).update(status=1,ftime=putdate())
        db(db.datastores.id == datastore).update(used=hdd)
        print "VM Has been deleted"
    else:
        db(db.queue.id==pid).update(status=-1,comments=output[1],ftime=putdate())
        print "VM couldn't be deleted"
    return

def resume(pid,vmid,chost_id=None,dhost_id=None,parameters=None):
    vmname = db(db.vm.id == vmid).select(db.vm.name)[0]['name']
    output = pyshell(vmname, "resume")
    if(output[0] == 0) :
        db(db.queue.id==pid).update(status=1,ftime=putdate())
    else:
        db(db.queue.id==pid).update(status=-1,comments=output[1],ftime=putdate())
    return


def migrate(pid,vmid,chost_id,dhost_id,parameters):
    print chost_id
    print dhost_id
    vm=db(db.vm.id==vmid).select()[0]
    chost = db(db.vm.id == vmid).select(db.vm.hostid)[0].hostid.ip
    print chost

    import commands
    dhost = db(db.host.id == dhost_id).select()[0].ip
    print "Taking backup of xml file in /root/migratexml of Baadal"
    print commands.getstatusoutput("ssh root@"+chost+" virsh dumpxml "+vm.name+" >>/root/migratexml/"+vm.name+".xml")
    if(vm.runlevel==0):parameters="--persistent --undefinesource "+vm.name
    command = 'virsh --connect qemu+ssh://root@'+chost+'/system migrate '+parameters+' qemu+ssh://root@'+dhost+'/system tcp://'+dhost+':48160'
    print command
    output = commands.getstatusoutput(command)
    print output[0]
    print output[1]

    if(output[0]==0):
        db(db.vm.id == vmid).update(hostid = dhost_id)
        updatevmcount(chost_id,dhost_id)
        db(db.queue.id==pid).update(status=1,ftime=putdate())
    else:
        db(db.queue.id==pid).update(status=-1,comments="On executing "+command+" got the error "+output[1],ftime=putdate())
    return

def changelevel(pid,vmid,chost_id,dhost_id=None,parameters=None): #PARAMETER AKA LEVEL
    db(db.vm.id==vmid).update(nextrunlevel=parameters)
    db(db.queue.id==pid).update(status=1,comments="Next Start will effect the VM Resources. Now you can start your vm.",ftime=putdate())
    return

def newchangelevel(pid,vmid,chost_id,dhost_id=None,parameters=None): #PARAMETER AKA LEVEL
    import libvirt
    from lxml import etree
    try:
        vm=db(db.vm.id==vmid).select()[0]
        vmname=vm.name
        cost=addtocost(vmname)
        f=open('/tmp/'+vm.name,'w')
        newhost=findnewhostmigrate(vm.id,parameters,vm.RAM,vm.vCPU)
        if(newhost==None):
            db(db.queue.id==pid).update(status=-1,comments="No appropriate Host Found",ftime=putdate())
        elif(newhost==vm.hostid):
            db(db.queue.id==pid).update(status=1,comments="Migration not needed",ftime=putdate())
            db(db.vm.name == vmname).update(lastrunlevel=vm['runlevel'],runlevel=parameters,hostid=newhost)
        elif(newhost!=vm.hostid):
            conn=libvirt.open("qemu+ssh://root@"+vm.hostid.ip+"/system")
            dom=conn.lookupByName(vm.name)
            xmldata=dom.XMLDesc(0)
            f.write(xmldata)    #Be on safer side, save xml file
            f.close()
            out=dom.undefine()              #Undefine the vm
            conn.close()
            f=open("/tmp/"+vm.name+".old",'w')
            f.write(xmldata)    #Be on a safer side before editing
            f.close
            (newram,newcpu)=computevmres(vmid,parameters)
            page=etree.fromstring(xmldata)
            doc=etree.ElementTree(page)
            #lets update memory,currentmemory and vcpu
            mem=doc.find("memory")
            mem.text=str(int(newram)*1024)     #Converted to KBs
            cmem=doc.find("currentMemory")
            if(cmem!=None):cmem.text=str(int(newram)*1024)    #Converted to KBs
            cpu=doc.find("vcpu")
            cpu.text=str(int(newcpu))
            f=open("/tmp/"+vm.name+".new",'w')
            newxml=doc.write(f)
            f.close()
            f=open("/tmp/"+vm.name+".new",'r')
            newxml=f.read()
            dhostip=db(db.host.id==newhost).select(db.host.ip)[0].ip
            conn=libvirt.open("qemu+ssh://root@"+dhostip+"/system")
            if(out==0):
                print "Domain undefined Successfully from "+vm.hostid.ip
                dom=conn.defineXML(newxml) #Defining the vm
                out=dom.isActive()
                if(out==0):
                    print "Domain successfully defined on "+dhostip+". Start it yourself"
                    db(db.vm.name == vmname).update(lastrunlevel=vm['runlevel'],runlevel=parameters,hostid=newhost)
                    db(db.vm.id==vm.id).update(hostid=newhost)
                    db(db.queue.id==pid).update(status=1,ftime=putdate())
            
                else: 
                    error="Error while defining domain on "+dhostip+" Error is:"+dom
                    print error
                    db(db.queue.id==pid).update(status=-1,comments=error,ftime=putdate())
            else:
                error="Some error while undefining the domain from "+vm.hostid.ip
                print error
                db(db.queue.id==pid).update(status=-1,comments=error,ftime=putdate())
            conn.close()
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Some Error Occured\n"+msg
    return

def oldchangelevel(pid,vmid,chost_id,dhost_id=None,parameters=None): #PARAMETER AKA LEVEL
    import os, commands
    vm = db(db.vm.id == vmid).select()[0]
    vmname = vm['name']
    #print "parameters="+parameters+" vmname="+vmname
    dhost_id = findnewhostmigrate(vmid,parameters,vm['RAM'],vm['vCPU'])
    #print "parameters="+parameters+" dhost_id="+str(dhost_id)+" vmname="+vmname
    chost_id = vm.hostid
    lastlevel=vm.runlevel
    dhost = db(db.host.id == dhost_id).select(db.host.ip)
    #dhost_name = db(db.host.id == dhost_id).select(db.host.name)[0]['name']
    cost=addtocost(vmname)
    vmram=vm['RAM']
    vmcpu=vm['vCPU']
    if(len(dhost)==0):
        db(db.queue.id==pid).update(status=-1,comments="No appropriate Host Found",ftime=putdate())
    else:
        dhost=dhost[0]['ip']
        #Migrate the vm to that host
        if (vm.hostid.ip == dhost):
            db(db.queue.id==pid).update(status=1,comments="Migration not needed",ftime=putdate())
            db(db.vm.name == vmname).update(lastrunlevel=vm['runlevel'],runlevel=parameters,hostid=dhost_id)
        else :
            options = ' --live --undefinesource --persistent '
            command = 'virsh --connect qemu+ssh://root@'+vm.hostid.ip+'/system migrate '+options+vmname+' qemu+ssh://root@'+dhost+'/system tcp://'+dhost+':48160'
            output = commands.getstatusoutput(command)
        
            #Make changes in the database
            db(db.vm.name == vmname).update(lastrunlevel=vm['runlevel'],runlevel=parameters,hostid=dhost_id)
            if(output[0]==0):
                cost=addtocost(vmname)
                updatevmcount(vm.hostid.id,dhost_id)
                db(db.queue.id==pid).update(status=1,ftime=putdate())
            else:
                db(db.queue.id==pid).update(status=-1,comments="On executing "+command+" got the error "+output[1],ftime=putdate())
