'''
PREREQUISITES
Check constants in the db.py file and see if these exists.
'''
# -*- coding: utf-8 -*- 
@auth.requires_login()
def add_task():
    try:
        pid=request.args[0]
        process = db(db.queue.id==pid).update(status=0,rtime=putdate())
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    redirect(URL(r=request,f='queue'))

@auth.requires_login()
def ignore_task():
    try:
        pid=request.args[0]
        process = db(db.queue.id==pid).update(status=2)
    except:
        redirect(URL(c='default', f='error'))
    redirect(URL(r=request,f='queue'))

@auth.requires_login()
def switch_role():
    try:
        if ifModerator(auth.user.username):
            if(session.role != "admin"):
                session.role = "admin"
                session.flash = "Your role has been changed to Administrator"
            else:
                session.role = None
                session.flash = "Your role has been changed"
        else:
            session.flash = "You do not have enough privileges to change your role"
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))    
    redirect(URL(c='default', f='index'))

@auth.requires_login()
def ignore_task():
    try:
        pid=request.args[0]
        process = db(db.queue.id==pid).update(status=2,ftime=putdate())
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    redirect(URL(r=request,f='queue'))
    
@auth.requires_login()
def queue():
    requires_moderator()
    items_per_page=10
    page_p=0
    page_s=0
    page_f=0
    try: vmname=request.vars['vmname']
    except: vmname=""
    if(vmname <> ""):
        vmid=db(db.vm.name==vmname).select()
        if(len(vmid)==0):
            return dict(pending=[],success=[],failed=[],page_p=page_p,page_s=page_s,page_f=page_f,items_per_page=items_per_page)
        else:
            vmid=vmid[0].id
            pending = db(db.queue.status == 0)(db.queue.vm==vmid).select(orderby=~db.queue.ftime)
            success = db(db.queue.status == 1)(db.queue.vm==vmid).select(orderby=~db.queue.ftime)
            failed = db(db.queue.status == -1)(db.queue.vm==vmid).select(orderby=~db.queue.ftime)
            return dict(pending=pending,success=success,failed=failed,page_p=page_p,page_s=page_s,page_f=page_f,items_per_page=items_per_page)
    try:
        items_per_page=10
        try: page_p=int(request.vars['p'])
        except: page_p=0
        try: page_s=int(request.vars['s'])
        except: page_s=0
        try: page_f=int(request.vars['f'])
        except: page_f=0

        limitby_p=(page_p*items_per_page,(page_p+1)*items_per_page+1)
        limitby_s=(page_s*items_per_page,(page_s+1)*items_per_page+1)
        limitby_f=(page_f*items_per_page,(page_f+1)*items_per_page+1)

        pending = db(db.queue.status == 0).select(orderby=~db.queue.ftime,limitby=limitby_p)
        success = db(db.queue.status == 1).select(orderby=~db.queue.ftime,limitby=limitby_s)
        failed = db(db.queue.status == -1).select(orderby=~db.queue.ftime,limitby=limitby_f)
        return dict(pending=pending,success=success,failed=failed,page_p=page_p,page_s=page_s,page_f=page_f,items_per_page=items_per_page)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))

###################################### ADD TO ##########################################
#ADD USER TO VM
@auth.requires_login()
def add_user_vm():
    requires_privileges()
    try:
        form=FORM(TABLE(
                  TR('Username:',INPUT(_name='ldap_username',requires=IS_NOT_EMPTY())),
                  TR('VM Name:',INPUT(_name='virtual_machine_name',requires=IS_NOT_EMPTY())),
                  TR("",INPUT(_type='submit',_value="Add User!"))))
        if (form.accepts(request.vars, session) and isValid(form.vars.ldap_username) and check_perms_exists(form.vars.virtual_machine_name)): 
            vid=db(db.auth_user.username==form.vars.ldap_username).select(db.auth_user.id)[0]['id']
            #user=db(db.vmaccpermissions.userid==vid).select(db.vmaccpermissions.userid)[0]['userid']
            vmid=db(db.vm.name==form.vars.virtual_machine_name).select(db.vm.id)[0]['id']
            #vm=db(db.vmaccpermissions.vmid==vmid).select(db.vmaccpermissions.vmid)[0]['vmid']
            db.vmaccpermissions.insert(userid=vid,vmid=vmid)
            response.flash = 'User has been successfully added.'
        elif form.errors:
            response.flash = 'There seem to be some error in your form. Kindly recheck.'
        elif not isValid(form.vars.ldap_username):
            response.flash = 'Please fill in the form using LDAP username'
        elif not check_perms_exists(form.vars.virtual_machine_name):
            response.flash = 'VM with the name does not exists.'
        return dict(form=form)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))

#REMOVE USER PERMISSIONS FOR A VIRTUAL MACHINE
@auth.requires_login()
def delete_user_vm():
    try:
        #form=FORM(TABLE('Delete User from VM',
        #          TR('Username:',INPUT(_name='ldap_username',requires=IS_NOT_EMPTY())),
        #          TR('VM Name:',INPUT(_name='virtual_machine_name',requires=IS_NOT_EMPTY())),
        #          TR('',INPUT(_type='submit',_value="Remove"))))
        #if (form.accepts(request.vars, session) and isValid(form.vars.ldap_username) and check_perms_exists(form.vars.virtual_machine_name)):
        uid=db(db.auth_user.username==request.args[1]).select(db.auth_user.id)[0]['id']
        vmid=db(db.vm.name==request.args[0]).select(db.vm.id)[0]['id']
        db(db.vmaccpermissions.vmid==vmid and db.vmaccpermissions.userid==uid).delete()
        response.flash = 'User has been successfully removed.'
        #elif form.errors:
        #    response.flash = 'There seem to be some error in your form. Kindly recheck.'
        #elif not isValid(form.vars.ldap_username):
        #    response.flash = 'Please fill in the form using LDAP username'
        #elif not check_perms_exists(form.vars.virtual_machine_name):
        #    response.flash = 'VM with the name does not exists.'
    #redirect(URL(r=request,c='vmuser',f='list'))
        #return dict(form=form)
        redirect(URL(c='vmuser', f='list'))
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))

@auth.requires_login()
def delete_user():
    try:
        vm = request.args[0]
        username = request.args[1]
        if (isValid(username) and check_perms_exists(vm)):
            uid=db(db.auth_user.username==username).select(db.auth_user.id)[0]['id']
            vmid=db(db.vm.name==vm).select(db.vm.id)[0]['id']
            db(db.vmaccpermissions.vmid==vmid and db.vmaccpermissions.userid==uid).delete()
            response.flash = 'User has been successfully removed.'
        elif form.errors:
            response.flash = 'There seem to be some error in your form. Kindly recheck.'
        elif not isValid(username):
            response.flash = 'Please fill in the form using LDAP username'
        elif not check_perms_exists(vm):
            response.flash = 'VM with the name does not exists.'
        redirect(URL(r=request,c='vmuser', f='list'))
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    
@auth.requires_login()
def reject_request():
    try:
        requires_moderator()
        req = db(db.request.id == request.args[0]).select()[0]
        if not req.faculty == auth.user.username and not isModerator(auth.user.username):
            session.flash = 'Not authorized'
        else:
            db.logs_request.insert( vmname=req.vmname, \
            userid = req.userid, \
            RAM = req.RAM, \
            HDD = req.HDD, \
            vCPUs = req.vCPUs, \
            templateid = req.templateid, \
            status = "REJECTED", \
            purpose = req.purpose)#, \
    #        approverid = req.faculty)
        db(db.request.id == request.args[0]).delete()
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    redirect(URL(r = request, f = 'get_requests'))

@auth.requires_login()
def approve_request():
    try:
        requires_privileges()
        req = db(db.request.id==request.args[0]).select()[0]
        if (req.status == 0):
            db(db.request.id == request.args[0]).update(status = 1)
        elif req.status == 1:
            db.queue.insert(task='install',user=auth.user.id,status=0,parameters=[req['id'],req.vmname],rtime=putdate())
                #session.flash = "Your task has been queued. Please check your task list for status."
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    redirect(URL(r=request, f='get_requests'))



#FIND VMS ON THE HOSTS WHICH ARE NOT AVAILABLE IN THE DATABASE
@auth.requires_login()
def listorphans():
    try:
        requires_moderator()
        import libvirt,commands,string
        vmlist = []
        host = db(db.host.id == request.args[0]).select()[0]
        domains=[]    #will contain the domain information of all the available domains
        vdomains=[]
        ip = host.ip
        try: 
            conn = libvirt.openReadOnly('qemu+ssh://root@'+ip+'/system')
            ids = conn.listDomainsID()
            for id in ids:
                domains.append(conn.lookupByID(id))
            names = conn.listDefinedDomains()
            for name in names:
                domains.append(conn.lookupByName(name))
            for dom in domains:
                vdomains.append(dom)
            for dom in vdomains:
                intstate = dom.info()[0]
                if(intstate==0):  state="No_State"
                elif(intstate==1):state="Running"
                elif(intstate==2):state="Blocked"
                elif(intstate==3):state="Paused"
                elif(intstate==4):state="Being_Shut_Down"
                elif(intstate==5):state="Off"
                elif(intstate==6):state="Crashed"
                else: state="Unknown"
                name = dom.name()
                vm = db(db.vm.name == name).select()
                if len(vm)==0:
                    element = {'name':name,'state':state,'host':host.name,'hostid':host.id}
                    vmlist.append(element)
                dom=""
            conn.close()
        except:
            response.flash = "Some error occured"
        return dict(vmlist=vmlist)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))

#FIND THE DETAILS OF A VIRTUAL MACHINE
@auth.requires_login()
def machine_details():
    requires_moderator()
    try:
        hosts = db(db.host.id>=0).select()
        results=[]
        for host in hosts:
            results.append({'ip':host.ip,'id':host.id,'hostname':host.name,'status':host.status})
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    form=FORM('Host IP:',
        INPUT(_name='hostip',requires=IS_NOT_EMPTY()),
        INPUT(_type='submit', _value='Get Details'))
    if form.accepts(request.vars,session):
        session.flash='Check the details'
        redirect(URL(c='admin', f='add_machine',args=form.vars.hostip))
    elif form.errors:
        response.flash='Error in form'
    return dict(form=form,hosts=results)

@auth.requires_login()
def shut_boot_host():
    import commands
    requires_moderator()
    hostip=request.args[0]
    message=""
    out=""
    try:
	masterhost=db(db.host.status==1).select()
	if len(masterhost)==0:
	    message="Error: It requires atleast 1 running host."
        else:
	    cstatus=checkhoststatus(hostip)
	    host=db(db.host.ip==hostip).select()[0]
    	    if cstatus==0:
		message="Waking up "+hostip
		out=commands.getstatusoutput("ssh root@"+masterhost[0].ip+" wakeonlan "+str(host.mac))
	    else:
		message="Shutting down "+hostip
		out=commands.getstatusoutput("ssh root@"+host.ip+" shutdown -h now")
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    session.flash=message+" Request status="+str(out[0])+" "+str(out[1])
    redirect(URL(r = request, f = 'machine_details'))

def showmsg(msg):
    try:
        return dict(msg=msg)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))

#DELETE HOST FROM THE BAADAL DATABASE
@auth.requires_login()
def delete_host():
    try:
        requires_moderator()
        host = db(db.host.id == request.args[0]).select()[0]
        record="Deleted the host"+host.name
        log(record,1)
        db(db.host.id == request.args[0]).delete()
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    redirect(URL(r = request, f = 'machine_details'))

#PUT HOST IN MAINTENANCE MODE
@auth.requires_login()
def maintenance_host():
    try:
        requires_moderator()
        host = db(db.host.id == request.args[0]).select()[0]
	cstatus=checkhoststatus(host.ip)
        if(host.status==0):db(db.host.id==host.id).update(status=2)
        elif(host.status==2 and cstatus==1):db(db.host.id==host.id).update(status=1)
        elif(host.status==2 and cstatus==0):db(db.host.id==host.id).update(status=0)
        else:puthostinmaintmode(host.ip) 
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    redirect(URL(r = request, f = 'machine_details'))

#ADD MODERATOR TO THE BAADAL DATABASE
@auth.requires_login()
def add_machine():
    ifRedirect = False
    try:
        requires_moderator()
        hostip = request.args[0]
        import commands
        form_labels = {'HDD':'HDD size in GB:','RAM':'RAM size in GB:','CPUs':'No. of CPUs:','ip':'Host IP'}
        form=SQLFORM(db.host,labels=form_labels,submit_button='Add Host')
        form.vars.name = 'host'+str(hostip.split('.')[3])
        form.vars.ip = hostip
	form.vars.mac = commands.getstatusoutput("ssh root@"+hostip+" ifconfig -a | grep eth0 | head -n 1 | awk '{print $5}'")[1]
        form.vars.CPUs = int(commands.getstatusoutput('ssh root@'+hostip+' cat /proc/cpuinfo | grep processor | wc -l')[1])/2
        form.vars.RAM  = int(round((float(commands.getstatusoutput('ssh root@'+hostip+' cat /proc/meminfo | grep MemTotal | awk -F \' \' \'{print $2}\'')[1]))/(1024*1024),0))
        form.vars.HDD = '300'
        if form.accepts(request.vars,session):
            session.flash='Host added'
            ifRedirect = True
        elif form.errors:
            response.flash='Error in form'
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    if ifRedirect :
        redirect(URL(c='admin', f='machine_details'))
    else :
        return dict(form=form)

#ADD A TEMPLATE TO THE BAADAL DATABASE
@auth.requires_login()
def add_template():
    try:
        requires_moderator()
        form=SQLFORM(db.template)
        if form.accepts(request.vars,session):
            response.flash='New template Created'
        elif form.errors:
            response.flash='Error in form'
        return dict(form=form)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))

#ADD A TEMPLATE TO THE BAADAL DATABASE
@auth.requires_login()
def add_datastore():
    import commands
    try:
        requires_moderator()
        form_fields=['name','ip','capacity','username','password','type','other']
        form_labels={'name':'Name','ip':'Mount IP','capacity':'Capacity (GB)','type':'Type','username':'Username','password':'Password','other':'Additional Info'}
        form=SQLFORM(db.datastores,fields=form_fields,labels=form_labels,submit_button='Add Datastore')
        if form.accepts(request.vars,session):
            response.flash='New datastore added'
        elif form.errors:
            response.flash='Error in form'
        return dict(form=form)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))

#GET REQUESTS FROM THE USER
@auth.requires_login()
def get_requests():
    try:
        my_pending_requests = db(db.request.userid == auth.user_id).select()
        my_misc_requests = db(db.misc_requests.user == auth.user_id).select()
        pending_requests=[]
        pending_misc_requests=[]

        if isFaculty(auth.user.username):
            pending_requests = db((db.request.status == 0) & (db.request.faculty == auth.user.username)).select()
            pending_misc_requests = db((db.misc_requests.status == 0) & (db.misc_requests.vm == db.vm.name) & (db.vm.userid==auth.user_id)).select()

            
        if isModerator(auth.user.username):
            pending_requests = db(db.request).select()
            pending_misc_requests = db(db.misc_requests.status != 2).select()
            
        return dict(pending_requests=pending_requests,my_pending_requests=my_pending_requests,my_misc=my_misc_requests,pen_mreq=pending_misc_requests)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))

@auth.requires_login()
def get_errors():
    try:
        errors = db(db.errors.status==0).select()
        return dict(errors=errors)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))

def fixed_error():
    try:
        db(db.errors.id==int(request.args[0])).update(status=1,fixed_date=putdate())
        session.flash="Status changed to Fixed!"
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    redirect(URL(r=request,c='admin', f='get_errors'))


@auth.requires_login()
def approve_request_details():
    cloneof=None
    try:
        requires_privileges()
        form_fields = ['vmname','RAM','HDD','vCPUs','purpose']
        req = db(db.request.id==request.args[0]).select()[0]
        #if(req.cloneparentname!=None):cloneof=db(db.vm.name==req.cloneparentname).select(db.vm.name)[0].name
        suggested = findnewhost(3,req.RAM,req.vCPUs)#Intially all the hosts will be put up as level 3 hosts
        if(suggested!=None):
            form = SQLFORM(db.request, req.id, fields = form_fields)#, labels = form_labels)
            form.vars.kvmhost = suggested
            vmcount=len(db(db.vm.id>=0).select(db.vm.id))
        else: 
            session.flash="No appropriate host found for this new VM."
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    if (form.accepts(request.vars,session)):
        redirect(URL(c='admin', f='approve_request',args=request.args[0]))
    elif form.errors:
        response.flash='Error in Form'
    #return dict(form=form,requestor=req.userid,faculty=req.faculty,cloneof=cloneof)
    return dict(form=form,requestor=req.userid,faculty=req.faculty)

def checkifvmisoff(form):
    vm=form.vars.vmname
    if(getvmstate(vm)!=5):form.errors.vmname="VM is not Off. Turn it off first"

#edit vm configuration and redefine
@auth.requires_login()
def edit_vmconfig():
    import libvirt,time
    from lxml import etree
    requires_privileges()
    try:
        form=FORM(INPUT(_name='vmname',_type='hidden',requires=IS_NOT_EMPTY()),
                  TABLE(TR('New RAM(MB):',INPUT(_name='ram',requires=IS_NOT_EMPTY())),
                  TR('New vCPU:',INPUT(_name='cpu',requires=IS_NOT_EMPTY())),
                  TR("",INPUT(_type='submit',_value="Update!"))))
        form.vars.vmname=request.args[0]
        if (form.accepts(request.vars, session,onvalidation=checkifvmisoff)):
            vm=db(db.vm.name==request.args[0]).select()[0]
            conn=libvirt.open("qemu+ssh://root@"+vm.hostid.ip+"/system")
            dom=conn.lookupByName(vm.name)
            xmldata=dom.XMLDesc(0)
            timestamp = time.strftime('%Y_%m_%d_%H_%M_%S')
            f=open("/tmp/"+vm.name+timestamp+".old",'w')
            f.write(xmldata)    #Be on a safer side before editing
            f.close
            page=etree.fromstring(xmldata)
            doc=etree.ElementTree(page)
            #lets update memory,currentmemory and vcpu
            mem=doc.find("memory")
            mem.text=str(int(form.vars.ram)*1024)     #Converted to KBs
            cmem=doc.find("currentMemory")
            if(cmem!=None):cmem.text=str(int(form.vars.ram)*1024)    #Converted to KBs
            cpu=doc.find("vcpu")
            cpu.text=str(int(form.vars.cpu))
            f=open("/tmp/"+vm.name+timestamp+".new",'w')
            newxml=doc.write(f)
            f.close()
            f=open("/tmp/"+vm.name+timestamp+".new",'r')
            newxml=f.read()
            out=conn.defineXML(newxml)
            if(out.info()[1]==int(form.vars.ram)*1024 and out.info()[3]==int(form.vars.cpu)):
                db(db.vm.name==vm.name).update(RAM=int(form.vars.ram),vCPU=int(form.vars.cpu))
            response.flash="VM RAM changed to "+str(out.info()[1]/1024)+"MB and vCPUs to "+str(out.info()[3])
            conn.close()
        elif form.errors:
            if(form.errors.vmname!=None):response.flash='VM is not Off. Turn it off first'
            else:response.flash = 'There seem to be some error in your form. Kindly recheck.'
        return dict(form=form)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))

@auth.requires_login()
def wastage():
    from operator import itemgetter, attrgetter
    from math import floor
    import fractions
    #try:
    if(len(request.args)==0): sortby='wcpuf'
    else: sortby=request.args[0]
    data=db(db.wastage.id>=0).select()
    vms=db(db.vm.id>=0).select(db.vm.name,db.vm.vCPU,db.vm.RAM)
    mdata=[]
    for d in data:
        vm = get_elem_by_key(vms,'name',d.vm)
        if vm:
            cpu=vm.vCPU
            ram=vm.RAM/1024
            #(d.dcpu,d.dram,d.dtime)=(int(floor(d.dcpu*cpu/100)),int(floor(d.dram*ram/100)),int(floor(d.dtime*100/1440)))
            #(d.wcpu,d.wram,d.wtime)=(int(floor(d.wcpu*cpu/100)),int(floor(d.wram*ram/100)),int(floor(d.wtime*100/10080)))
            #(d.mcpu,d.mram,d.mtime)=(int(floor(d.mcpu*cpu/100)),int(floor(d.mram*ram/100)),int(floor(d.mtime*100/43200)))
            #(d.ycpu,d.yram,d.ytime)=(int(floor(d.ycpu*cpu/100)),int(floor(d.yram*ram/100)),int(floor(d.ytime*100/525600)))
            (d.dtime,d.wtime,d.mtime,d.ytime)=(int(floor(d.dtime*100/1440)),int(floor(d.wtime*100/10080)),int(floor(d.mtime*100/43200)),int(floor(d.ytime*100/525600)))
            (d.cpumax,d.rammax,d.dtimemax,d.wtimemax,d.mtimemax,d.ytimemax)=(cpu,ram,1440,10080,43200,525600)
            mdata.append(d) 
    data=mdata
    if(sortby=='vm'):data=sorted(data,key=itemgetter(sortby),reverse=False)
    else:data=sorted(data,key=itemgetter(sortby),reverse=True)
    #except:
    #    import sys, traceback
    #    etype, value, tb = sys.exc_info()
    #    msg = ''.join(traceback.format_exception(etype, value, tb, 10))
    #    session.flash='Some Error Occured'
    #    redirect(URL(r=request,c='default', f='error'))
    return dict(data=data,sortby=sortby)


@auth.requires_login()
def wastage1():
    import commands,sys,ast
    from operator import itemgetter, attrgetter
    if(len(request.args)==0):sortby='wcpu'
    else:sortby=request.args[0]
    try:
        if(len(request.args)==3):
	    if(sortby=="vm"): reversee=False
	    else: reversee=True    
	    datalist=ast.literal_eval(request.args[1])
	    errorlist=ast.literal_eval(request.args[2])
	    datalist=sorted(datalist,key=itemgetter(sortby),reverse=reversee)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    if(len(request.args)==3):return dict(data=datalist,error=errorlist,sortedby=sortby)
    try:
	vms=db(db.vm.id>=0).select()
	datalist=[]
	errorlist=[]
	for vm in vms:
	    errors=""
	    out1=commands.getstatusoutput("/usr/bin/rrdtool fetch -r 300 -s -24h /var/www/cloudrrd1/"+vm.name+".rrd AVERAGE| /bin/grep -v nan | /bin/grep -v cpu | /bin/grep -v \"^\$\" | /usr/bin/awk -f /var/www/mail.pl |grep -v NR| sed 's/\([^0-9./]\+\)/ /g' | sed 's/\/\([ ]\+\)/\//g'")
	    out2=commands.getstatusoutput("/usr/bin/rrdtool fetch -r 300 -s -168h /var/www/cloudrrd1/"+vm.name+".rrd AVERAGE| /bin/grep -v nan | /bin/grep -v cpu | /bin/grep -v \"^\$\" | /usr/bin/awk -f /var/www/mail.pl |grep -v NR| sed 's/\([^0-9./]\+\)/ /g' | sed 's/\/\([ ]\+\)/\//g'")
	    out3=commands.getstatusoutput("/usr/bin/rrdtool fetch -r 18000 -s -720h /var/www/cloudrrd1/"+vm.name+".rrd AVERAGE| /bin/grep -v nan | /bin/grep -v cpu | /bin/grep -v \"^\$\" | /usr/bin/awk -f /var/www/mail.pl |grep -v NR| sed 's/\([^0-9./]\+\)/ /g' | sed 's/\/\([ ]\+\)/\//g'")
	    out4=commands.getstatusoutput("/usr/bin/rrdtool fetch -r 108000 -s -8640h /var/www/cloudrrd1/"+vm.name+".rrd AVERAGE| /bin/grep -v nan | /bin/grep -v cpu | /bin/grep -v \"^\$\" | /usr/bin/awk -f /var/www/mail.pl |grep -v NR| sed 's/\([^0-9./]\+\)/ /g' | sed 's/\/\([ ]\+\)/\//g'")
            (hcpu,hram,dcpu,dram,wcpu,wram)=(0,0,0,0,0,0)
	    if(out1[1].find('ERROR')>=0 or out1[1].find('fatal')>=0):errorlist.append({'vm':vm.name,'error':out1[1]})
	    elif out1[1].strip()=="":(hcpu,hram)=(0,0)
	    else:(hcpu,hram)=(100-float(out1[1].split()[0]),100-float(out1[1].split()[2]))

	    if(out2[1].find('ERROR')>=0 or out2[1].find('fatal')>=0):errorlist.append({'vm':vm.name,'error':out2[1]})
	    elif out2[1].strip()=="":(dcpu,dram)=(0,0)
	    else:(dcpu,dram)=(100-float(out2[1].split()[0]),100-float(out2[1].split()[2]))

	    if(out3[1].find('ERROR')>=0 or out3[1].find('fatal')>=0):errorlist.append({'vm':vm.name,'error':out3[1]})
	    elif out3[1].strip()=="":(wcpu,wram)=(0,0)
	    else:(wcpu,wram)=(100-float(out3[1].split()[0]),100-float(out3[1].split()[2]))

	    element={'vm':vm.name,'hcpu':hcpu,'hram':hram,'dcpu':dcpu,'dram':dram,'wcpu':wcpu,'wram':wram}
	    datalist.append(element)
	datalist=sorted(datalist,key=itemgetter(sortby),reverse=True)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg+str(datalist)+'VM='+vm.name
        redirect(URL(r=request,c='default', f='error'))
    return dict(data=datalist,error=errorlist,sortedby=sortby)


@auth.requires_login()
def attach_disk():
    try:
        requires_moderator()
        form_fields=['vmname','size','addinfo']
        form_labels={'vmname':'Select VM','size':'Size (GB)','addinfo':'Additional Info'}
        form=SQLFORM(db.attacheddisks,fields=form_fields,labels=form_labels,submit_button='Attach Disk')
        if form.accepts(request.vars,session):
            vm=db(db.vm.id==form.vars.vmname).select()[0]
            out=attachdisk(vm.name,form.vars.size)
            db(db.vm.id==vm.id).update(HDD=vm.HDD+int(form.vars.size))
            response.flash=out#'Permanently Disk attached. Reboot the VM'
        elif form.errors:
            response.flash='Error in form'
        return dict(form=form)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))

def unique(data):
    newdata=[]
    try:
	data=sorted(data)
	prev=''
	for d in data:
	    if(d!=prev):newdata.append(d)
	    prev=d
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    return newdata


#MAILING FUNCTION USING GUI
@auth.requires_login()
def mailToGUI():
    try:
        import smtplib
        from email.mime.text import MIMEText
        form_fields=['subject','email_txt']
        form_labels={'subject':'Subject','email_txt':'Email Text'}
        form = SQLFORM(db.email,fields=form_fields,labels=form_labels,submit_button='Send')
	users=request.args(0)
    #uarray=['cloudgroup@cc.iitd.ernet.in']
        if users=="all_iitd":
            users=db(db.vmaccpermissions.id>=0).select()
            mailto=[]
            for user in users:
                mailto.append(db(db.auth_user.id==user.userid).select()[0].username)
            mailto.append('cloudgroup')
            unique(mailto)
            users='-'.join(mailto)

        if users:
            uarray=users.split('-')
            emails=""
            for i in range(0,len(uarray)-1):
                u = uarray[i]
                emails += user_email(u)+","
            u=uarray[len(uarray)-1]
            emails += user_email(u)
        form.vars.to_address=','.join(unique(emails.split(',')))
        
        subject=request.args(1)
        if subject != None :
            subject=subject.replace('_',' ')
            form.vars.subject=subject
        
        email_txt=request.args(2)
        if email_txt != None:
            email_txt=email_txt.replace('_',' ')
            form.vars.email_txt=email_txt

        form.vars.from_address=user_email(auth.user.username)#getconstant('email_from')
        
        if (form.accepts(request.vars,session)):
            msg = MIMEText(form.vars.email_txt)
            msg['Subject'] = form.vars.subject
            msg['From'] = form.vars.from_address
            s = smtplib.SMTP('localhost')
            msg['To'] =form.vars.to_address
            for user in uarray:
		if(user_email(user)!=''):s.sendmail(msg['From'], user_email(user), msg.as_string())
            s.quit()
            response.flash = "Mail sent successfully"
        elif form.errors:
            response.flash = 'Error in form'
        return dict(form=form)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg+form.vars.to_address+user+user_email(user)
        redirect(URL(r=request,c='default', f='error'))


@auth.requires_login()
def mailToAll():
    requires_moderator()
    userlist="all_iitd"
    redirect(URL(c='admin', f='mailToGUI',args=[userlist,'','']))

@auth.requires_login()
def check_sanity():
    output=sanity_check()
    return dict(vms=output)

@auth.requires_login()
def turnoffbaadal():
    requires_moderator()
    setconstant("ifbaadaldown","1")
    session.flash="Baadal Turned Off. Only Admin login Allowed"
    redirect(URL(r=request,c='default', f='index'))

@auth.requires_login()
def turnonbaadal():
    requires_moderator()
    setconstant("ifbaadaldown","0")
    session.flash="Baadal Turned On. Users can login"
    redirect(URL(r=request,c='default', f='index'))

@auth.requires_login()
def get_webvnc():
    requires_moderator()
    vm_name = request.args[0]
    vm_info = db(db.vm.name == vm_name).select()[0] 
    return dict(host=vm_info.hostid.ip, port=vm_info.sport)

def get_elem_by_key(elem,key,req):
    for a in elem:
        if(a[key]==req): return a
    return None
