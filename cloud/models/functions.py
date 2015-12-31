####### Functions shared across controllers #########
def fullname(name):
    import ldap
    import string, re
    from traceback import print_exc
    if name==None:return "No Faculty mentioned"
    url="ldap://ldap1.iitd.ernet.in"
    dn="dc=iitd,dc=ernet,dc=in"
    l = ldap.initialize(url)
    l.bind_s("", "", ldap.AUTH_SIMPLE);
    attrs = ['username']
    filter = "(&(objectclass=IITDperson)(uid="+name+"))";
    if not l.search_s( dn, ldap.SCOPE_SUBTREE, filter, attrs ) :
        return name
    return l.search_s( dn, ldap.SCOPE_SUBTREE, filter, attrs )[0][1]['username'][0]
    l.unbind()

def isFaculty(name):
    if (name == "cs5090243"):
        return True
    if (name == None) :
        return False
    import ldap
    import string, re
    from traceback import print_exc
    url="ldap://ldap1.iitd.ernet.in"
    dn="dc=iitd,dc=ernet,dc=in"
    l = ldap.initialize(url)
    l.bind_s("", "", ldap.AUTH_SIMPLE);
    filter = "(&(objectclass=IITDperson)(uid="+name+"))";
    attrs = ['category']
    if not l.search_s( dn, ldap.SCOPE_SUBTREE, filter, attrs ) :
        return False
    if (l.search_s( dn, ldap.SCOPE_SUBTREE, filter, attrs )[0][1]['category'][0] == 'faculty'):
        return True
    elif (l.search_s( dn, ldap.SCOPE_SUBTREE, filter, attrs )[0][1]['category'][0] == 'vfaculty'):
        return True
    else:
        return False
    l.unbind()

def isModerator(name):
    if( session.role != "admin" or (not ifModerator(name))):
        return False
    return True

def ifModerator(name):
    if (name==None) :
        return False
    import ldap
    import string, re
    from traceback import print_exc
    url="ldap://ldap1.iitd.ernet.in"
    dn="dc=cc,dc=iitd,dc=ernet,dc=in"
    l = ldap.initialize(url)
    l.bind_s("", "", ldap.AUTH_SIMPLE);
    #filter = "&((objectclass=IITDlist)(cn=cloudgroup))" 
    filter="(cn=cloudgroup)"
    attrs = ['memberUid']
    admins = l.search_s( dn, ldap.SCOPE_SUBTREE, filter,attrs)[0][1]['memberUid']
    for admin in admins:
        if (admin == name):
            return True
    else:
        return False
    l.unbind()

#Returns current time
def putdate():
    import datetime
    return datetime.datetime.now()

#Assumption - functions called only if user is logged in
def requires_faculty():
    if not isFaculty(auth.user.username):
        session.vm_status = "Not authorized"
        redirect(URL(c='default', f='index'))

def requires_moderator():
     if (session.role != "admin"):
#    if not isModerator(auth.user.username):
        session.vm_status = "Not authorized"
        redirect(URL(c='default', f='index'))

def requires_privileges():
    if not (isModerator(auth.user.username) or isFaculty(auth.user.username)):
        session.vm_status = "Not authorized"
        redirect(URL(c='default', f='index'))

def isValid(name):
    if (name == None) :
        return False
    import ldap
    import string, re
    from traceback import print_exc
    url="ldap://ldap1.iitd.ernet.in"
    dn="dc=iitd,dc=ernet,dc=in"
    l = ldap.initialize(url)
    l.bind_s("", "", ldap.AUTH_SIMPLE);
    lastdn = dn
    dnlist = None
    ret=""
    for name,attrs in l.search_s(dn, ldap.SCOPE_SUBTREE,"uid="+name):
        for k,vals in attrs.items():
            if (k == "cn"):
                ret=vals[0]#if(vals[0]=="faculty"):
    l.unbind()
    if(ret!=""):
        return True
    return False
    
def user_email(usr):
    if usr=="cloudgroup":
        return "cloudgroup@cc.iitd.ernet.in"
    import ldap
    import string, re
    from traceback import print_exc

    url="ldap://ldap1.iitd.ernet.in"
    dn="dc=iitd,dc=ernet,dc=in"

    l = ldap.initialize(url)
    l.bind_s("", "", ldap.AUTH_SIMPLE)
    lastdn = dn
    dnlist = None

    for name,attrs in l.search_s(dn, ldap.SCOPE_SUBTREE,"uid="+usr):
        for k,vals in attrs.items():
            if (k == "mail"):
                return vals[0]
    l.unbind()
    return ''
    
def getconstant(constname):
    constant= db(db.constants.name == constname).select(db.constants.value)[0]['value']
    return constant

def setconstant(constname,constvalue):
    db(db.constants.name == constname).update(value=constvalue)
    return

# existsvm: check whether @vmname exists
def existsvm(vmname):
    query = 'select state from vm where name=\'' + vmname + '\''
    rs = db.executesql(query)
    return rs.__len__()

def getvmstate(vm_name):
    import libvirt
    try:
        hostid = db(db.vm.name == vm_name).select(db.vm.hostid)[0].hostid
        hostip = db(db.host.id == hostid).select(db.host.ip)[0].ip
        conn=libvirt.openReadOnly("qemu+ssh://root@"+hostip+"/system")
        dom=conn.lookupByName(vm_name)
        state=dom.info()[0]
        dom=""
        conn.close()
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Some Error Occured\n"+msg
    return state

def getactualvmlevel(vm_name):
    import libvirt
    try:
        hostid = db(db.vm.name == vm_name).select(db.vm.hostid)[0].hostid
        hostip = db(db.host.id == hostid).select(db.host.ip)[0].ip
        conn=libvirt.openReadOnly("qemu+ssh://root@"+hostip+"/system")
        dom=conn.lookupByName(vm_name)
        cpuused=dom.info()[3]
        runlevel=3
        vCPU=db(db.vm.name==vm_name).select()[0].vCPU
        if((int(vCPU)/cpuused)==1):runlevel=1
        elif((int(vCPU)/cpuused)==2):runlevel=2
        elif((int(vCPU)/cpuused)==4):runlevel=3
        if(dom.info()[0]==1 or dom.info()[0]==3):runlevel=runlevel
        else: runlevel=0
        dom=""
        conn.close()
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Some Error Occured\n"+msg
    return runlevel

#TODO - change require_* logic acc to this
def prelim_checks(vmname):
    # A VM could be deleted by another authorized user before this user does an
    # operation. But it will persist on his list until he refreshes the page.
    if check_perms(vmname) == False:
        session.vm_status = "Not authorized"
        redirect(URL(r=request,f='list'))

def ifValidVM(vmname):
    vms=db(db.vm.name==vmname).select(db.vm.id)
    if not vms:
        return False
    return True

def check_perms_exists(vmname):
    vms=db(db.vm.name==vmname).select(db.vm.id)
    if not vms:
        return False
    return True
    
# check_perms: check whether current user has permissions on @vmname (for admin list always return true)
def check_perms(vmname):
    if isModerator(auth.user.username):
        return True
    authvms = db(db.vmaccpermissions.userid == auth.user_id).select()
    for authvm in authvms:
        if authvm.vmid.name == vmname:
            return True
    return False


# check_perms_refined: check whether current user has permissions on @vmname (admin is not assumed to be a superuser here)
def check_perms_refined(vmname):
    authvms = db(db.vmaccpermissions.userid == auth.user_id).select()
    for authvm in authvms:
        if authvm.vmid.name == vmname:
            return True
    return False

#Returns the minimum used datastore directory name
def give_datastore():
    ds=db(db.datastores.id>=0).select()
    nds=[]
    minused=ds[0]
    for d in ds:
        if(d.used < minused.used):minused=d
    return minused
    
def error_notify_email(subject,email_txt):
    import smtplib
    from email.mime.text import MIMEText
    msg = MIMEText(email_txt)
    me = getconstant('email_from')
    #gid = db(db.auth_group.role == "mailing_list").select(db.auth_group.id)[0]['id']
    #users = db(db.auth_membership.group_id == gid).select(db.auth_membership.user_id)
    #emails=[]
    #for user in users:
        #emails.append(user['user_id'].email);
    msg['Subject'] = subject
    msg['From'] = "cs5090243@cse.iitd.ernet.in" 
    s = smtplib.SMTP('localhost')
    #for user_email in emails:
    user_email=getconstant('email_from')
    msg['To'] = user_email
    s.sendmail(me, user_email, msg.as_string())
    s.quit()

def append_error_infile(error):
    import os
    filename=os.path.join(request.folder,'private/ticket_errors')
    if os.access(filename,os.R_OK):
        #body=open(filename,'r').read()
        f = open(filename,'a')
        f.write(error)
        f.close()

def log(event,level):
    log_level=getconstant('log_level')
    if(level<=log_level):
        db.logs.insert(record=event)

def touch(dir,fname, times = None):
    import os,time,subprocess
    subprocess.call(["mkdir","-p",dir])
    lock = dir+fname
    with file(lock, 'a'):
        os.utime(lock, times)

def acquire(fname):
    timeout=600
    import os, time

    exists=os.path.isfile(getconstant("lock_loc")+fname)
    if(exists==False) :
        touch(getconstant("lock_loc"),fname)
        return True
        
    else :
        while (exists==True and timeout != 0):
            exists=os.path.isfile(getconstant("lock_loc")+fname)
            time.sleep(1)
            timeout-=1
            #TODO - send message waiting for lock
            pass
        return False

def release(fname):
    import os
    exists=os.path.isfile(getconstant("lock_loc")+fname)
    if(exists==True) :
        try :
            os.remove(getconstant("lock_loc")+fname)
        except Exception:
            pass

#first argument is hostid and second is vmname
def checkifvmisdefined(hostip,vmname):
    import libvirt,commands,string
    domains=[]    #will contain the domain information of all the available domains
    exists=False
    try:
        conn = libvirt.openReadOnly('qemu+ssh://root@'+hostip+'/system')
        ids = conn.listDomainsID()
        for id in ids:
            domains.append(conn.lookupByID(id))
        names = conn.listDefinedDomains()
        for name in names:
            domains.append(conn.lookupByName(name))
        for dom in domains:
            if(vmname==dom.name()):exists=True
        return exists
        conn.close()
    except:return False

@auth.requires_login()   
def gen_passwd():
    import random
    passwd = ''.join([random.choice(\
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890') \
        for i in range(6)])
    return passwd

#UPDATE VMCOUNT WHEN A VM IS MOVED FROM CHOST TO DHOST
def updatevmcount(chost,dhost):
    ccount=db(db.host.id==chost).select(db.host.vmcount)[0].vmcount
    dcount=db(db.host.id==dhost).select(db.host.vmcount)[0].vmcount
    db(db.host.id==chost).update(vmcount = ccount-1)
    db(db.host.id==dhost).update(vmcount = dcount+1)

#SEND CONFIRMATION EMAIL ON CREATION OF A VIRTUAL MACHINE
def send_confirmation_email(userid,faculty,vmname):
    import smtplib
    from email.mime.text import MIMEText

    username = db(db.auth_user.id == userid).select(db.auth_user.username)[0].username
    email_txt = \
'Hello ' + fullname(username) + ',\n\
\n\
Your virtual machine \''+ vmname + '\' has been approved. Please log on to \n\
https://baadal.iitd.ernet.in/cloud and note down the IP address of your VM. \n\
You can access your VM using ssh (linux) or rdesktop (Windows) as \n\
root (Linux)  or administrator (Windows) using the default password \'duolc\'. \n\
You will be required to change the password at first login. \n\
\n\
Please familiarize yourself thoroughly with the Baadal usage documentation at http://www.cc.iitd.ernet.in/CSC/index.php?option=com_content&view=article&id=123.\n\
Regards,\n\
The Baadal Team\n\
\n\
--\n\
This email was sent from an unmonitored alias. Please do not reply to this email.'
    msg = MIMEText(email_txt)
    me = getconstant('email_from')
    if(faculty!=None):useremail = user_email(username)+';'+user_email(str(faculty))
    else:useremail = user_email(username)
    CC = "cloudgroup@cc.iitd.ac.in"
    msg['Subject'] = 'Your virtual machine \'%s\' has been approved' % vmname
    msg['From'] = me
    msg['To'] = useremail
    msg['Cc'] = CC
    s = smtplib.SMTP('localhost')
    s.sendmail(me, [useremail, CC], msg.as_string())
    s.quit()

def addtocost(vm_name):
    import string
    from time import time
    vm = db(db.vm.name==vm_name).select()[0]
    oldtime = vm.laststarttime
    newtime = time()
    if(oldtime==None or len(oldtime.split('|'))>1):oldtime=newtime
    hours = float((float(newtime)-float(oldtime))/3600)
    if(vm.runlevel==0):scale=0
    elif(vm.runlevel==1):scale=1
    elif(vm.runlevel==2):scale=.5
    elif(vm.runlevel==3):scale=.25

    totalcost = float(hours*(vm.vCPU*float(getconstant('cost_cpu'))+vm.RAM*float(getconstant('cost_ram'))/1024)*float(getconstant('cost_scale'))*float(scale)) + float(vm.totalcost)
    db(db.vm.name == vm_name).update(laststarttime=time(),totalcost=totalcost)
    return totalcost

#def addtocostall():
#    import string
#    from time import time
#    vms=db(db.vm.id>=0).select()
#    query="update

def namerepcheck(vmname):
    vms=db(db.vm.id >= 0).select()
    found=False
    for vm in vms:
        if vmname==vm.name: found=True
    return found    

#def fullresusederror(vmid):
#    vm=db(db.vm.id==vmid).select()[0]
#    if(vm.RAM<
#    task=db((db.queue.vm==vmid)&((db.queue.task=="start")|(db.queue.task=="migrate")|(db.queue.task=="changelevel"))&(db.queue.status==-1)).select(db.queue.comments)[0] 
#    if(task.comments.find("info chardev">=0))

#Returns resources utilization of a host in MB,Count

def hostresourcesused(host):
    import math
    RAM = 0.0
    CPU = 0.0
    vms = db(db.vm.hostid == host).select(db.vm.RAM, db.vm.vCPU,db.vm.runlevel)
    for vm in vms:
        (ram,cpu)=computeeffres(vm.RAM,vm.vCPU,vm.runlevel)
        RAM = RAM + ram
        CPU = CPU + cpu
    hram = db(db.host.id == host).select(db.host.RAM)[0].RAM
    hcpu = db(db.host.id == host).select(db.host.CPUs)[0].CPUs
    return (math.ceil(RAM),math.ceil(CPU),hram,hcpu)

#Returns all the host running vms of particular run level
def findnewhost(runlevel,RAM,vCPU):
    hosts=db(db.host.status==1).select()
    hosts=sorted(hosts, key=lambda host: host.RAM)
    runlevel=int(runlevel)
    dhost=None
    for host in hosts:
        print "checking host="+host.name
        (uram,ucpu,hram,hcpu)=hostresourcesused(host.id)
        print "uram "+str(uram)+" ucpu "+str(ucpu)+" hram "+ str(hram)+" hcpu "+ str(hcpu)
        (effram,effvcpu)=computeeffres(RAM,vCPU,runlevel)
        if(dhost==None and (uram+effram)<=hram*1000 and (ucpu+effvcpu)<=hcpu):
            dhost=host
    if(dhost==None): return None
    else: return dhost.id

def findnewhostmigrate(vmid,runlevel,RAM,vCPU):
    vm=db(db.vm.id==vmid).select()[0]
    hosts=db(db.host.status==1).select()
    hosts=sorted(hosts, key=lambda host: host.RAM)
    runlevel=int(runlevel)
    dhost=None
    mincpuleft=100	#Idea is to pack the host which already has min resources left, CPU.
    for host in hosts:
        (uram,ucpu,hram,hcpu)=hostresourcesused(host.id)
        (effram,effvcpu)=computeeffres(RAM,vCPU,runlevel)
        if(mincpuleft>=(hcpu-ucpu) and (uram+effram)<=hram*1000 and (ucpu+effvcpu)<=hcpu):
            mincpuleft=hcpu-ucpu
            dhost=host
    if(dhost==None): return None
    else:
        print dhost
        return dhost.id

def currenttime():
    from time import time
    return time()

def get_orphan_details():
    import xml.dom.minidom,commands,sys,os
    vm=request.args[1]
    host=db(db.host.id == request.args[0]).select()[0]
    form=None
    try:
        commands.getstatusoutput('virsh --connect qemu+ssh://root@'+host.ip+'/system dumpxml '+vm+' >/tmp/'+vm+'.xml')
        doc = xml.dom.minidom.parse('/tmp/'+vm+'.xml')
        RAM=doc.getElementsByTagName("memory")[0].childNodes[0].data
        RAM=int(RAM)/1024
        raise HTTP(403,RAM)
        vCPUs=doc.getElementsByTagName("vcpu")[0].childNodes[0].data
        hddpath=doc.getElementsByTagName("disk")[0].getElementsByTagName("source")[0].getAttribute("file")
        out=commands.getstatusoutput('ssh root@'+host.ip+' du -sh '+hddpath)
        sport=doc.getElementsByTagName("graphics")[0].getAttribute("port")
        if(out[0]==0):
            hddsize=out[1].strip(' ')[0]
            form = FORM(TABLE(
                    TR('Username',INPUT(_name='user',_value=auth.user.username,requires=IS_NOT_EMPTY())),
                    TR('VMname',INPUT(_name='vmname',_value=vm,requires=IS_NOT_EMPTY())),
                    TR('RAM (in MB)',INPUT(_name='RAM',_value=RAM,requires=IS_NOT_EMPTY())),
                    TR('Path to HDD',INPUT(_name='ptHDD',_value=hddpath,requires=IS_NOT_EMPTY())),
                    TR('HDD (in GB))',INPUT(_name='HDD',_value=hddsize,requires=IS_NOT_EMPTY())),
                    TR('vCPUs',INPUT(_name='vCPUs',_value=vCPUs,requires=IS_NOT_EMPTY())),
                    TR('VNC Port',INPUT(_name='sport',_value=sport,requires=IS_NOT_EMPTY())),
                    TR('Host',INPUT(_name='host',_value=host.name,requires=IS_NOT_EMPTY())),
                    TR('Faculty',INPUT(_name='faculty',requires=IS_NOT_EMPTY(),_value=auth.user.username)),
                    TR("",INPUT(_type="submit",_value="Take Ownership!"))))
            if form.accepts(request.vars,session):
                session.flash=vm+' added to account of '+auth.user.username
                #TODO add all the rules needed while vm creation
                #Take care of harddisk name and vm name, Move hdd image if required
                db.vm.insert(name=vm,userid=auth.user.id,hostid=host.id,definedon=host.id,RAM=RAM,vCPU=vCPUs,HDD=hddsize, \
                            templateid=1,isofile=1,usingtemplate=1,sport=sport,status=request.args[2],runlevel=1)
                redirect(URL(r = request, f = 'machine_details'))
            elif form.errors:
                session.flash='Error in form'
            return(dict(form=form))
        else:
            session.flash='Check harddisk path '+hddpath
    except Exception as e:
        raise HTTP(403,e)
        session.flash='There seems to be some error'
    redirect(URL(r = request, f = 'machine_details'))

def isiso(filename):
    name = filename.split(".")
    lastname = name[len(name)-1]
    if (lastname=="iso"):
        return True
    else:
        return False

def namerepcheck(vmname):
    vms=db(db.vm.id >= 0).select()
    found=False
    for vm in vms:
        if vmname==vm.name: found=True
    return found

def maxportused():
    vms=db(db.vm.id >= 0).select(db.vm.sport)
    if len(vms)==0:
        return 5910
    else:
        return vms[len(vms)-1].sport

def new_mac_ip(vmcount):
    vmcount=int(vmcount)
    #mac=getconstant('mac_range')+str(hex(int(vmcount/256))[2:])+":"+str(hex(vmcount-int(vmcount/256)*256)[2:])
    mac=getconstant('mac_range')+str(int(vmcount/100))+":"+str(vmcount-int(vmcount/100)*100)
    ip=getconstant('ip_range')+str(int(1+vmcount/100))+"."+str(vmcount-int(vmcount/100)*100)
    port=str(int(getconstant('vncport_range'))+vmcount)
    return(mac,ip,port)

def redefinedomain(vmname):
    import libvirt
    from lxml import etree
    print "In redefinedomain with vmname="+vmname
    try:
        vm=db(db.vm.name==vmname).select()[0]
        f=open('/root/migratexml/'+vm.name,'w')
        newhost=findnewhostmigrate(vm.id,vm.nextrunlevel,vm.RAM,vm.vCPU)
        if newhost==None:return None
        conn=libvirt.open("qemu+ssh://root@"+vm.hostid.ip+"/system")
        dom=conn.lookupByName(vm.name)
        xmldesc=dom.XMLDesc(0)
        print "Original XML file is \n\n"+str(xmldesc)
        f.write(xmldesc)    #Be on safer side, save xml file
        f.close()
        out=dom.undefine()              #Undefine the vm
        dom=""
        conn.close()
        f=open("/root/migratexml/"+vm.name+".old",'w')
        f.write(xmldesc)    #Be on a safer side before editing
        f.close
        (newram,newcpu)=computevmres(vm.id,vm.nextrunlevel)
        page=etree.fromstring(xmldesc)
        doc=etree.ElementTree(page)
        #lets update memory,currentmemory and vcpu
        mem=doc.find("memory")
        mem.text=str(int(newram)*1024)     #Converted to KBs
        cmem=doc.find("currentMemory")
        if(cmem!=None):cmem.text=str(int(newram)*1024)    #Converted to KBs
        cpu=doc.find("vcpu")
        cpu.text=str(int(newcpu))
        f=open("/root/migratexml/"+vm.name+".new",'w')
        newxml=doc.write(f)
        f.close()
        f=open("/root/migratexml/"+vm.name+".new",'r')
        newxml=f.read()
        print "New XML file is \n\n"+str(newxml)
        dhostip=db(db.host.id==newhost).select(db.host.ip)[0].ip
        conn=libvirt.open("qemu+ssh://root@"+dhostip+"/system")
        if(out==0):
            print "Domain undefined Successfully from "+vm.hostid.ip
            dom=conn.defineXML(newxml) #Defining the vm
            out=dom.isActive()
            if(out==0):
                print "Domain successfully defined on "+dhostip+". Start it yourself"
                db(db.vm.id==vm.id).update(hostid=newhost)
            else: print "Error while defining domain on "+dhostip+" Error is:"+dom
        else:
            print "Some error while undefining the domain from "+vm.hostid.ip
        dom=""
        conn.close()
    except:
        import sys, traceback
        dom=""
        conn.close()
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Some Error Occured\n"+msg
    return newhost

def migrateoffdomain(vmname,hostid):
    import libvirt
    from lxml import etree
    print "In migrateoffdomain with vmname="+vmname
    try:
        vm=db(db.vm.name==vmname).select()[0]
        f=open('/tmp/'+vm.name,'w')
        newhost=hostid
        conn=libvirt.open("qemu+ssh://root@"+vm.hostid.ip+"/system")
        dom=conn.lookupByName(vm.name)
        xmldesc=dom.XMLDesc(0)
        print "Original XML file is \n\n"+str(xmldesc)
        f.write(xmldesc)    #Be on safer side, save xml file
        f.close()
        out=dom.undefine()              #Undefine the vm
        dom=""
        conn.close()
        dhostip=db(db.host.id==newhost).select(db.host.ip)[0].ip
        conn=libvirt.open("qemu+ssh://root@"+dhostip+"/system")
        if(out==0):
            print "Domain undefined Successfully from "+vm.hostid.ip
            dom=conn.defineXML(xmldesc) #Defining the vm
            out=dom.isActive()
            if(out==0):
                print "Domain successfully defined on "+dhostip+". Start it yourself"
                db(db.vm.id==vm.id).update(hostid=newhost)
            else: print "Error while defining domain on "+dhostip+" Error is:"+dom
        else:
            print "Some error while undefining the domain from "+vm.hostid.ip
        dom=""
        conn.close()
    except:
        import sys, traceback
        dom=""
        conn.close()
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Some Error Occured\n"+msg
    return out #If successful returns 0

def computevmres(vmid,runlevel):
    vm=db(db.vm.id==vmid).select()[0]
    effram=1024
    effcpu=1
    divideby=1
    if(runlevel==0): divideby=0
    elif(runlevel==1): divideby=1
    elif(runlevel==2): divideby=2
    elif(runlevel==3): divideby=4
    if(divideby!=0):
        if(vm.RAM/divideby>=1024):effram=vm.RAM/divideby
        if(vm.vCPU/divideby>=1): effcpu=vm.vCPU/divideby
    return (effram,effcpu)


def computeeffres(RAM,vCPU,runlevel):
    effram=1024
    effcpu=1
    divideby=1
    if(runlevel==0): divideby=0
    elif(runlevel==1): divideby=1
    elif(runlevel==2): divideby=2
    elif(runlevel==3): divideby=4
    if(divideby!=0):
        if(RAM/divideby>=1024):effram=RAM/divideby
        if(vCPU/divideby>=1): effcpu=vCPU/divideby
    if(divideby==0):
        effram=0
        effcpu=0
    return (effram,effcpu)

#size is in GB
def attachdisk(vmname,size):
    import libvirt,commands
    vm=db(db.vm.name==vmname).select()[0]
    out="Error attaching disk"
    try:
        conn=libvirt.open("qemu+ssh://root@"+vm.hostid.ip+"/system")
        dom=conn.lookupByName(vmname)
        alreadyattached=len(db(db.attacheddisks.vmname==vm.id).select(db.attacheddisks.id))
        if(dom.isActive()!=1):return "Cannot attach disk to Inactive domain"
        else:
            diskpath=getconstant('vmfiles_path')+getconstant('datastore_int')+vm.datastore.name+"/"+vmname+"/"+vmname+str(alreadyattached+1)+".raw"
            print commands.getstatusoutput("sudo qemu-img create -f raw "+diskpath+" "+str(size)+"G")
            command="ssh root@"+vm.hostid.ip+" virsh attach-disk "+vmname+" "+diskpath+" vd"+chr(97+alreadyattached+1)+" --type disk"
            out=commands.getstatusoutput(command)
            print out
            xmlfile=dom.XMLDesc(0)
            dom=conn.defineXML(xmlfile)
            out1=dom.isActive()
            if(out1==1): 
                print "Most probably the disk has been attached successfully. Reboot your vm to see it"
        conn.close()
        return out[1].strip()
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Some Error Occured\n"+msg
    return

#CUSTOM FUNCTION TO HANDLE VM RELATED OPERATIONS
def pyshell(vm_name,command):
    import commands, string
    host = db(db.vm.name == vm_name).select()
    ip = host[0].hostid.ip
    if (command == "delete"):
        if not getvmstate(vm_name) == 5:     #state (0,shutoff), (1,running), (2, paused)
            out = commands.getstatusoutput('virsh --connect qemu+ssh://root@'+ip+'/system destroy '+ vm_name)
            if not out[0] == 0:
                return out

        out = commands.getstatusoutput('virsh --connect qemu+ssh://root@'+ip+'/system undefine '+ vm_name)
        if not out[0] == 0:
            session.flash=out+'Problem while undefining the virtual machine.'
        else:
            datastore_id = db(db.vm.name == vm_name).select(db.vm.datastore)[0]['datastore']
            datastore = db(db.datastores.id == datastore_id).select()[0]
            vm_loc = getconstant('vmfiles_path')+getconstant('datastore_int')+datastore.name+'/'+vm_name+'/'
            out = commands.getstatusoutput('rm -rf '+vm_loc)
            print "VM deleted : "+out[1]
        
        vm_id = db(db.vm.name == vm_name).select(db.vm.id)[0].id
        countp1 = db(db.host.ip == ip).select(db.host.vmcount)[0].vmcount -1
        db(db.host.ip == ip).update(vmcount = countp1) 
        db(db.vm.name == vm_name).delete()
        db(db.vmaccpermissions.vmid == vm_id).delete()    
        #i = db.executesql('select id from vm where name like \'' + vm_name + '\'', as_dict=True)
        #vm_id = i[0]['id']
        #c = db.executesql('select vmcount from host where ip like \'' + ip + '\'', as_dict=True)
        #cminus1 = c[0]['vmcount'] - 1
        #db.executesql('update host set vmcount = \'' + str(cminus1) + '\'')
        #db.executesql('delete from permissions where vmid = \'' + str(vm_id) + '\'')
        #db.executesql('delete from vm where name like \'' + vm_name + '\'')
    else:
        out = commands.getstatusoutput('virsh --connect qemu+ssh://root@'+ip+'/system '+command+' '+ vm_name)
    #In case the host goes down during operation, it should automatically start the VMs that were running
    #when it went down, when it comes back up again.
    if((command == "destroy") or (command == "shutdown")):
        commands.getstatusoutput('virsh --connect qemu+ssh://root@'+ip+'/system autostart --disable ' + vm_name)
    elif(command == "start"):
        #host=migratebeforestart(vm_id)        #It will migrate if it cannot be started at the required runlevel on the same host
        commands.getstatusoutput('virsh --connect qemu+ssh://root@'+ip+'/system autostart ' + vm_name)
    session.vm_status = out[1] + '(code: ' + str(out[0]) + ')'
    return out

def listtemplates():
    temps = db(db.template.id >= 0).select(db.template.id, db.template.name,db.template.ostype,db.template.hdd)
    return dict(temps=temps)

def listisos():
    isos = db(db.isofile.id >=0).select(db.isofile.id,db.isofile.name,db.isofile.ostype)
    return dict(isos=isos)

@auth.requires_login()
def listhosts():
    hosts = db(db.host.id >=0).select(db.host.id,db.host.name,db.host.ip)
    return dict(hosts=hosts)

#@auth.requires_login()
def ldapsync():
    import ldap
    import string, re
    from traceback import print_exc
    url="ldap://ldap1.iitd.ernet.in"
    dn="dc=iitd,dc=ernet,dc=in"
    l = ldap.initialize(url)
    l.bind_s("uid=ldapadmin,ou=People,dc=iitd,dc=ernet,dc=in", "PASSWORD", ldap.AUTH_SIMPLE);
    lastdn = dn
    dnlist = None
    array=[]
    for name,attrs in l.search_s(dn, ldap.SCOPE_SUBTREE,"objectclass=posixAccount"):
        uid=attrs['uid'][0]
        fullname=attrs['gecos'][0]
        user=db(db.auth_user.username==uid).select(db.auth_user.id)
        if not user:
            print "Inserting a new user with username "+str(uid)
            db.auth_user.insert(first_name=fullname,username=uid,password=None)
    db.commit()
    l.unbind()
    return

def faculty_sync():
    import ldap
    import string, re
    from traceback import print_exc
    url="ldap://ldap1.iitd.ernet.in"
    dn="dc=iitd,dc=ernet,dc=in"
    l = ldap.initialize(url)
    l.bind_s("uid=ldapadmin,ou=People,dc=iitd,dc=ernet,dc=in", "PASSWORD", ldap.AUTH_SIMPLE);
    lastdn = dn
    dnlist = None
    array=[]
    for name,attrs in l.search_s(dn, ldap.SCOPE_SUBTREE,"objectclass=IITDperson"):
        for k,vals in attrs.items():
            if (k == "category"  and vals[0]=="faculty"):
                for k,vals in attrs.items():
                    if (k == "uid"):
                        faculty=db(db.faculty.name==vals[0]).select()
                        if not faculty:
                            print "Inserting a new faculty with name "+str(vals[0])
                            db.faculty.insert(name=vals[0])
    db.commit()
    l.unbind()

def vminfotostate(intstate):
    if(intstate==0):  state="No_State"
    elif(intstate==1):state="Running"
    elif(intstate==2):state="Blocked"
    elif(intstate==3):state="Paused"
    elif(intstate==4):state="Being_Shut_Down"
    elif(intstate==5):state="Off"
    elif(intstate==6):state="Crashed"
    else: state="Unknown"
    return state

def myrequests(requests,vms,num):
    ctr=0
    array=[]
    for request in requests:
        for vm in vms:
            if (request['vm'] == vm['vmid']):
                array.append(request)
                ctr+=1
                if(ctr == num):
                    return array
    return array

def myfraction(frac):
    a=str(frac).split('/')
    if(len(a)==1): return float(a[0])
    else:return float(float(a[0])/float(a[1]))

#Setup iptables rules for given machine name
def insert_iptable_rules(vmname):
    import commands
    vm=db(db.vm.name==vmname).select()[0]

    ws_ip = getconstant('webserver_ip')
    ws_if = getconstant('webserver_interface')
    host_port = str(vm.sport)
    host_ip = vm.hostid.ip
    sport = str(int(vm.sport)+29)	#29 is an arbit constant    
    
    iptables = getconstant('iptables_path')
    commands.getstatusoutput('sudo '+iptables + ' -A PREROUTING  -t nat -p tcp -i ' + ws_if + ' -d ' + ws_ip + ' --dport ' + sport + ' -j DNAT --to ' + host_ip + ':' + host_port)
    commands.getstatusoutput('sudo '+iptables + ' -A POSTROUTING -t nat -p tcp -o ' + ws_if + ' -d ' + host_ip + ' --dport ' + host_port + ' -j SNAT --to-source ' + ws_ip)
    commands.getstatusoutput('sudo '+iptables + ' -A FORWARD -p tcp  -d ' + host_ip + ' --dport ' + host_port + ' -j ACCEPT')
    return int(sport)

#Clean iptable rules for given machine name
def remove_iptable_rules(vmname):
    import commands
    vm=db(db.vm.name==vmname).select()[0]

    ws_ip = getconstant('webserver_ip')
    ws_if = getconstant('webserver_interface')
    host_port = str(vm.sport)
    host_ip = vm.hostid.ip
    sport = str(int(vm.sport)+29)	#29 is an arbit constant    
    
    iptables = getconstant('iptables_path')
    commands.getstatusoutput('sudo '+iptables + ' -D PREROUTING  -t nat -p tcp -i ' + ws_if + ' -d ' + ws_ip + ' --dport ' + sport + ' -j DNAT --to ' + host_ip + ':' + host_port)
    commands.getstatusoutput('sudo '+iptables + ' -D POSTROUTING -t nat -p tcp -o ' + ws_if + ' -d ' + host_ip + ' --dport ' + host_port + ' -j SNAT --to-source ' + ws_ip)
    commands.getstatusoutput('sudo '+iptables + ' -D FORWARD -p tcp  -d ' + host_ip + ' --dport ' + host_port + ' -j ACCEPT')

#Auto remove iptable rules after X time of insert
def auto_remove_iptable_rules():
    import datetime
    import commands
    #Check if the iptables table in db is out of sync with actual iptable rules
    ports=commands.getstatusoutput("iptables --line-numbers -L -n| grep 'dpt:6'| awk '{print $1" "$8}' | sed 's/dpt://g'")[1]
    ports=ports.split('\n')
    skipports=[]

    vms=db(db.iptables.id>=0)(db.iptables.active==True).select()
    curtime=datetime.datetime.now()
    for vm in vms:
        prev=datetime.datetime.strptime(str(vm.insert_time),'%Y-%m-%d %H:%M:%S')
        if(datetime.timedelta(minutes=30)<(curtime-prev)):
            print "Removing iptable rules for VM:"+str(vm.vm)
            remove_iptable_rules(vm.vm)
            db(db.iptables.id==vm.id).update(delete_time=putdate(),active=False)
        else:
            port=db(db.vm.name==vm.vm).select(db.vm.sport)[0].sport
            skipports.append(int(port)+29)
    #Remove iptable rules which are not present in db table
    for port in ports:
        rulenum=int(port.split(' ')[0])
        port=int(port.split(' ')[1])
        if(port in skipports): continue
        vmport=port-29
        vm=db(db.vm.sport==vmport).select()
