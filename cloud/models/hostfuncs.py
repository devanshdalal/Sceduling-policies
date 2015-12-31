#Returns {DOWN=0, UP=1}
def checkhoststatus(hostip):
    import commands
    #print "\nChecking status of host "+hostip+"\n--------------------------------\n"
    out=commands.getstatusoutput("ping -c 2 -W 1 "+hostip)[0]
    if(out==0):return 1
    else: return 0

#hoststatussanitycheck
def hoststatussanitycheck():
    hosts=db(db.host.id>=0).select()
    notify=[]
    for host in hosts:
        print "Working on "+host.name
        status=checkhoststatus(host.ip)
        dbstatus=db(db.host.id==host.id).select(db.host.status)[0].status
        if(status!=dbstatus and dbstatus!=2):
            if(status==0 and dbstatus !=2):
                notify.append(host.name)
            print "Changing status of "+host.name+" to "+str(status)
            db(db.host.id==host.id).update(status=status)
    if len(notify)!=0:
        hosts=','.join(notify)
        print "Sending notification email for "+hosts
        error_notify_email("Baadal: "+str(len(notify))+" hosts not responding","Host(s) "+hosts+" is/are not responding. Please check.\nSetting status off in database. Please rectify! the status shall change automatically if necessary.")

#Returns {ANY_FOUND=1, NOT_FOUND=0}
def checkanyrunningvm(hostip):
    import libvirt
    #print "\nLooking for any running vms on "+hostip+"\n-----------------------------------\n"
    found=False
    if not checkhoststatus(hostip):
        print "\nHost is down\n"
        return False
    try:
        conn = libvirt.openReadOnly('qemu+ssh://root@'+hostip+'/system')
        domains=[]
        ids = conn.listDomainsID()
        for id in ids:
            domains.append(conn.lookupByID(id))
        names = conn.listDefinedDomains()
        for name in names:
            domains.append(conn.lookupByName(name))
        for dom in domains:
            print "Checking "+str(dom.name())
            if(dom.info()[0]!=5):
                #print dom.name()+" is not off. Please check"
                found=True
        dom=None
        ids=None
        names=None
        domains=None
        conn.close()
    except:
        import sys, traceback
        found=True
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Some Error Occured\n"+msg
    return found

#Move all dead vms of this host to the host first in list of hosts
def movealldeadvms(hostip):
    import libvirt,commands
    print "\nMoving all dead vms of this host "+hostip+"\n-----------------------------------\n"
    if not checkhoststatus(hostip):
        print "\nHost is down\n"
        return
    if(checkanyrunningvm(hostip)):
        print "All the vms on this host are not Off"
        return
    try:
        conn = libvirt.openReadOnly('qemu+ssh://root@'+hostip+'/system')
        domains=[]
        host1=db(db.host.status==1).select()[0]
        ids = conn.listDomainsID()
        for id in ids:
            domains.append(conn.lookupByID(id))
        names = conn.listDefinedDomains()
        for name in names:
            domains.append(conn.lookupByName(name))
        for dom in domains:
            print "Moving "+str(dom.name())+" to "+host1.name
            migrateoffdomain(dom.name(),host1.id)
        print "All the vms moved Successfully. Host is empty"
        print commands.getstatusoutput("ssh root@"+hostip+" virsh list --all")
        domains=None
        names=None
        ids=None
        conn.close()
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Some Error Occured\n"+msg
    return

#Save Power, turn off extra hosts and turn on if required
def hostpoweroperation():
    import commands
    print "\nIn host power operation function\n-----------------------------------\n"
    livehosts=db(db.host.status==1).select()
    freehostscount=0
    freehosts=[]
    try:
        for host in livehosts:
            if not checkanyrunningvm(host.ip):
                freehostscount=freehostscount+1
                freehosts.append(host.ip)
        if(freehostscount==2):print "Everything is Balanced. Green Cloud :)"
        elif(freehostscount<2):
            print "Urgently needed "+str(2-freehostscount)+" more live hosts."
            livehostcount=len(livehosts)
            newhosts=db(db.host.status==0).select() #Select only Shutoff hosts
            #sortedhosts=sorted(newhosts, key=lambda host: host.RAM)
            #newhosts=[sortedhosts[0],sortedhosts[-1]] #One with highest, one with lowest RAM, then select 
            newhosts=newhosts[0:(2-freehostscount)]
            for host in newhosts:
                print "Sending magic packet to "+host.name
                print commands.getstatusoutput("ssh root@kvm1 wakeonlan "+str(host.mac))
        elif(freehosts>2):
            print "Sending shutdown signal to total "+str(freehostscount-2)+" no. of host(s)"
            extrahosts=freehosts[2:]
            for host in extrahosts:
		print "Moving any dead vms to first running host"
		movealldeadvms(host)
                print "Sending kill signal to "+host
                print commands.getstatusoutput("ssh root@"+host+" shutdown -h now")
                db(db.host.ip==host).update(status=0)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Some Error Occured\n"+msg
    return

#Put the host in maintenance mode, migrate all running vms and redefine dead ones
def puthostinmaintmode(hostip):
    import libvirt,commands
    error=1
    db(db.host.ip==hostip).update(status=2)
    try:
        conn = libvirt.openReadOnly('qemu+ssh://root@'+hostip+'/system')
        domains=[]
        host1=db(db.host.status==1).select()[0]
        ids = conn.listDomainsID()
        for id in ids:
            domains.append(conn.lookupByID(id))
        names = conn.listDefinedDomains()
        for name in names:
            domains.append(conn.lookupByName(name))
        for dom in domains:
            if dom.info()[0]==5:    #If the vm is in Off state, move it to host1
                print "Moving "+str(dom.name())+" to "+host1.name
                out=migrateoffdomain(dom.name(),host1.id)
                if out!=0:
                    print "Some error occured. Please check"
                    conn.close()
                    return
            else:
                vm=db(db.vm.name==dom.name()).select()[0]
                newhost=findnewhost(vm.runlevel,vm.RAM,vm.vCPU)
                parameters="--live --persistent --undefinesource "+vm.name
                print "Inserting migrate request for running vm "+str(dom.name())+" to appropriate host in queue"
		print vm
		print auth.user.id
                db.queue.insert(task="migrate",vm=vm.id,chost=vm.hostid,dhost=newhost,parameters=parameters,status=0,user=auth.user.id,rtime=putdate())
            dom=""
	movealldeadvms(hostip)
        domains=None
        ids=None
        names=None
        conn.close()
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Some Error Occured\n"+msg
    return
