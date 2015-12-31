#This function only takes care of the vms which are there on some host
#but not for those which are there in database but not on any host
import time
import signal

def handler(signum, frame):
    raise Exception("Timeout")

def check_moved():
    import libvirt, string
#    signal.signal(signal.SIGALRM, handler)
    vmcheck=[]
    hosts=db(db.host.status==1).select()
    print hosts
    for host in hosts:
        try:
            #Establish a read only remote connection to libvirtd
            #find out all domains running and not running
            #Since it might result in an error add an exception handler
            print "Working on "+host.name
#           signal.alarm(7)
            conn = libvirt.openReadOnly('qemu+ssh://root@'+host.ip+'/system')
            domains=[]
            ids = conn.listDomainsID()
            for id in ids:
                domains.append(conn.lookupByID(id))
            names = conn.listDefinedDomains()
            for name in names:
                domains.append(conn.lookupByName(name))
	    #Lets fix those who are not where they should be
            for dom in domains:
                try:
                    name = dom.name()
                    print "Domain "+name
                    vm = db(db.vm.name == name).select(db.vm.hostid,db.vm.name)
                    status=vminfotostate(dom.info()[0])
                    if(len(vm)!=0):
                        vm=vm[0]
                        if(vm.hostid!=host.id):
                            vmcheck.append({'host':host.name,'vmname':vm.name,'status':status,'operation':'Moved from '+vm.hostid.name+' to '+host.name})#Stupid VMs
                            db(db.vm.name==name).update(hostid=host.id)
                        else:
                            vmcheck.append({'host':host.name,'vmname':vm.name,'status':status,'operation':'Is on expected host '+vm.hostid.name})#Good VMs
                    else:
                        vmcheck.append({'host':host.name,'vmname':dom.name(),'status':status,'operation':'Orphan, VM is not in database'})#Orphan VMs
                    dom=""
                except:vmcheck.append({'vmname':vm.name,'vmid':vm.id,'operation':'Some Error Occured'})
                   
            domains=[]
            names=[]
            print conn.close()
        except:
            print "Problem with host "+host.name+". Unable to connect !!"
    return vmcheck

#If some vm gets undefined due to redundant power failures, lets redefine it
def recover_undefined():
    import libvirt
    import os,commands
    from os.path import exists
    vmcheck=[]
    hosts=db(db.host.status==1).select()
    running_host=db(db.host.status==1).select()
    if(len(running_host)==0):
        print "No running host, exiting"
	return
    host1=running_host[0]
    conn1=libvirt.open("qemu+ssh://root@"+host1.ip+"/system")
    for host in hosts:
        vms=db(db.vm.hostid==host.id).select()
        try:
            conn = libvirt.openReadOnly('qemu+ssh://root@'+host.ip+'/system')
            conn=libvirt.open("qemu+ssh://root@"+host.ip+"/system")
            for vm in vms:
                try:
                    conn.lookupByName(vm.name)
                except:
                    print "Redefining the domain "+vm.name
		    path1="/root/migratexml/"+vm.name+".new"
		    print "Looking for XML file "+path1
                    #if not os.path.isfile(path1):
                    try:
                        f=open("applications/cloud/models/migratexml/"+vm.name+".new",'r')
                        print "XML File exists"
                        xmlfile=f.read()
                        #print xmlfile
                        dom=conn1.defineXML(xmlfile)
                        if(not dom.isActive()):
                            print "VM "+vm.name+" moved redefined on "+str(host1.ip)
                            db(db.vm.id==vm.id).update(hostid=host1.id)
                            vmcheck.append({'host':host.name,'vmname':vm.name,'status':'Off','operation':'VM moved to '+host1.name})
                        else:
                            print "Error "+str(dom.isActive())+" while redefining the vm on "+str(host1.ip)
                            vmcheck.append({'host':host.name,'vmname':vm.name,'status':'Off','operation':'ERROR: while redefining domain'})#Orphan VMs
                    except:
                        import sys, traceback
                        etype, value, tb = sys.exc_info()
                        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
                        print "XML File doesn't exists"
                        print "Couldn't find existing XML of "+vm.name+" in /root/migratexml. Best of Luck !!"
                        print commands.getstatusoutput("pwd")
                        #vmcheck.append({'host':host.name,'vmname':vm.name,'status':'Off','operation':'ERROR: No existing XML File found'})
                        vmcheck.append({'host':host.name,'vmname':vm.name,'status':'Off','operation':msg})
            conn.close() 
        except:
            print "Could not connect to host "+str(host.ip)
    conn1.close()
    return vmcheck

def sanity_check():
    vmcheck=check_moved() + recover_undefined() 
    return vmcheck
