# -*- coding: utf-8 -*-
@auth.requires_login()
def add_task():
    try:
        pid=request.args[0]
        process = db(db.queue.id==pid).update(status=0)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))
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
def queue():
    try:
        vms=db(db.vmaccpermissions.userid == auth.user.id).select(db.vmaccpermissions.vmid)
        pending = db(db.queue.status == 0).select(orderby=~db.queue.ftime)
        success = db(db.queue.status == 1).select(orderby=~db.queue.ftime)
        failed = db(db.queue.status == -1).select(orderby=~db.queue.ftime)

        success=myrequests(success,vms,10)
        failed=myrequests(failed,vms,10)
        pending=myrequests(pending,vms,10)

        return dict(pending=pending,success=success,failed=failed)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))

@auth.requires_login()
#List all the virtual machines based on the user roles
def list():
    try:
        import libvirt,commands,string
        session.prev_url = "list"
        #vms = db(db.vm.userid==auth.user.id).select()
        vms = db(db.vmaccpermissions.userid==auth.user.id).select()
        vmlist=[]
        for vm in vms:
	    vm=vm.vmid                  
	    addtocost(vm.name)
            element = {'name':vm.name,'ip':vm.ip,'RAM':vm.RAM,'vcpus':vm.vCPU,'level':vm.runlevel,'hostip':vm.hostid.ip,'owner':vm.userid.first_name,'id':vm.id,'cost':vm.totalcost}
            vmlist.append(element)
        return dict(vmlist=vmlist)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))

@auth.requires_login()
#List all the virtual machines based on the user roles
def list_all():
    try:
        import libvirt,commands,string
        session.prev_url = "list_all"
        vms = db(db.vm.id>=0).select()
        vmlist=[]
        for vm in vms:
            addtocost(vm.name)
            vm=db(db.vm.name==vm.name).select()[0]
            owner = db(db.auth_user.id == vm.userid).select(db.auth_user.username)[0].username
            element = {'name':vm.name,'ip':vm.ip,'RAM':vm.RAM,'vcpus':vm.vCPU,'level':vm.runlevel,'hostip':vm.hostid.ip,'owner':owner,'id':vm.id,'cost':vm.totalcost}
            vmlist.append(element)
        return dict(vmlist=vmlist)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))

@auth.requires_login()
def dominfo():
    import libvirt
    try:
        vmname=request.args[0]
        content=""
        state=vminfotostate(getvmstate(vmname))
        #if(vminfo.runlevel!=0 and state=='Off'):db(db.vm.name==vmname).update(runlevel=0)  #Fix error cases to least runlevel
        if(state=='Off'):
            content=content+"<a href=\"/cloud/vmuser/start_machine/"+vmname+"\" title=\"Turn on this virtual machine\" alt=\"Turn on this virtual machine\"><img src=\"/cloud/static/images/on-off.png\" height=\"15\" width=\"15\" /></a>"
        #if(state=='Paused'):
        #    content=content+"<a href=\"/cloud/vmuser/resume_machine/"+vmname+"\" title=\"Resume this virtual machine\" alt=\"Pause this virtual machine\"><img src=\"/cloud/static/images/play1.png\" height=\"15\" width=\"15\" /></a>"
        #if(state=='Running'):
        #    content=content+"<a href=\"/cloud/vmuser/suspend_machine/"+vmname+"\" title=\"Pause this virtual machine\" alt=\"Resume this virtual machine\"><img src=\"/cloud/static/images/pause1.png\" height=\"15\" width=\"15\" /></a>"
        if(state!='Off'):
            content=content+"<a href=\"/cloud/vmuser/shutdown_machine/"+vmname+"\" title=\"Gracefully shut down this virtual machine\" alt=\"Gracefully shut down this virtual machine\"><img src=\"/cloud/static/images/shutdown1.png\" height=\"15\" width=\"15\" /></a>"
        if(state=='Running' or state=='Paused'):
            content=content+"<a href=\"/cloud/vmuser/destroy_machine/"+vmname+"\" title=\"Forcefully power off this virtual machine\" alt=\"Forcefully power off this virtual machine\"><img src=\"/cloud/static/images/on-off.png\" height=\"15\" width=\"15\" /></a>"
        content=content+"<a href=\"/cloud/vmuser/settings/"+vmname+"\" title=\"Settings\" alt=\"Settings\"><img src=\"/cloud/static/images/settings.png\" height=\"15\" width=\"15\" /></a>" 
        content=content+"<img alt=\"Operations\" title=\"Operations\" src=\"../static/images/lock.png\" height=\"18\" onclick=\"ajax('{{=URL('dominfo/"+vmname+")}}', ['"+vmname+"'],'"+vmname+"');\"/>"
        if(len(db(db.errors.error==vmname)(db.errors.status==0).select())==1):
            content=content+"<a href=\"/cloud/vmuser/allow_display/"+vmname+"\" title=\"Fix this machine\" alt=\"Fix this machine\"><img src=\"/cloud/static/images/faulty.png\" height=\"15\" width=\"15\" /></a>"
	return content
    except: 
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
	return 'Some Error Occured'

def plotgraphs():
    if((request.args[1]).find("level")>=0):keyword=" Setting"
    else: keyword=request.args[1]
    if(request.args[1]=="all"):
        data="<table>\n<tr><td><h4>Daily Level Setting</h4><img src=\"https://baadal.iitd.ernet.in/cloudrrd1/"+request.args[0]+"/level-d.png\"/></td></tr>\n<tr><td><h4>Daily CPU Utilization</h4><img src=\"https://baadal.iitd.ernet.in/cloudrrd1/"+request.args[0]+"/cpu-d.png\"/></td></tr>\n<tr><td>><h4>Daily MEMORY Utilization</h4><img src=\"https://baadal.iitd.ernet.in/cloudrrd1/"+request.args[0]+"/mem-d.png\"/></td></tr>\n<tr><td><h4>Daily DISK Utilization</h4><img src=\"https://baadal.iitd.ernet.in/cloudrrd1/"+request.args[0]+"/disk-d.png\"/></td></tr>\n<tr><td><h4>Daily NETWORK Utilization</h4><img src=\"https://baadal.iitd.ernet.in/cloudrrd1/"+request.args[0]+"/net-d.png\"/></td></tr>\n</table>"
    else:
        data="<table>\n<tr><td><h4>Daily "+request.args[2]+" Utilization</h4><img src=\"https://baadal.iitd.ernet.in/cloudrrd1/"+request.args[0]+"/"+request.args[1]+"-d.png\"/></td></tr>\n<tr><td><h4>Weekly "+request.args[2]+" Utilization</h4><img src=\"https://baadal.iitd.ernet.in/cloudrrd1/"+request.args[0]+"/"+request.args[1]+"-w.png\"/></td></tr>\n<tr><td><h4>Monthly "+request.args[2]+" Utilization</h4><img src=\"https://baadal.iitd.ernet.in/cloudrrd1/"+request.args[0]+"/"+request.args[1]+"-m.png\"/></td></tr>\n<tr><td><h4>Yearly "+request.args[2]+" Utilization</h4><img src=\"https://baadal.iitd.ernet.in/cloudrrd1/"+request.args[0]+"/"+request.args[1]+"-y.png\"/></td></tr>\n</table>"
    return data

#REMOVE USER PERMISSIONS FOR A VIRTUAL MACHINE
@auth.requires_login()
def delete_user_vm():
    import sys, traceback
    requires_faculty()
    try:
        uid=db(db.auth_user.username==request.args[1]).select(db.auth_user.id)[0]['id']
        vmid=db(db.vm.name==request.args[0]).select(db.vm.id)[0]['id']
        rids = db(db.vmaccpermissions.userid==uid).select()
	for rid in rids:
	    if(rid.vmid==vmid):db(db.vmaccpermissions.id==rid.id).delete()
        #return rid#db(db.vmaccpermissions.id == rid).delete()
        response.flash = 'User has been successfully removed.'
    except:
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(r=request,c='default', f='error'))
    redirect(URL(r=request,c='vmuser', f='settings/'+request.args[0]))

@auth.requires_login()
#List all the virtual machines based on the user roles
def old_list():
    try:
        import libvirt,commands,string
        vmlist = []
        notreachable = "Error connecting "
        hosts = db(db.host.id >=0).select()
        for host in hosts:
            domains=[]    #will contain the domain information of all the available domains
            vdomains=[]
            ip = host.ip
            try: 
                #Establish a read only remote connection to libvirtd
                #find out all domains running and not running
                #Since it might result in an error add an exception handler
                conn = libvirt.openReadOnly('qemu+ssh://root@'+ip+'/system')
                ids = conn.listDomainsID()
                for id in ids:
                    domains.append(conn.lookupByID(id))
                names = conn.listDefinedDomains()
                for name in names:
                    domains.append(conn.lookupByName(name))                    
                for dom in domains:
                    if check_perms_refined(dom.name()):
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
                    if len(vm)==1:
                        vm = vm[0]
                        if vm.hostid == host.id:
                            hostid = vm.hostid
                            ram = vm.RAM
                            vmid = vm.id
                            sport = vm.sport
                            hostip = vm.hostid.name
                            owner = db(db.auth_user.id == vm.userid).select(db.auth_user.username)[0].username
                            #db(db.vm.name == name).update(status=state)
                            element = {'name':name,'RAM':ram,'hostip':hostip,'owner':owner,'sport':sport,'state':state,'id':vmid}
                            vmlist.append(element)
                    dom=""
                conn.close()
            except:notreachable = notreachable+ip+' '
        #if notreachable == "Error connecting ":
        #    response.flash = "All hosts active"
        #else:
        #    response.flash = extra#notreachable
        return dict(vmlist=vmlist,flash=response.flash)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))

#LIST ALL VIRTUAL MACHINES
@auth.requires_login()
def old_list_all():
    try:
        import libvirt,commands,string
        vmlist = []
        notreachable = "Error connecting "
        hosts = db(db.host.id >=0).select()
        for host in hosts:
            domains=[]    #will contain the domain information of all the available domains
            vdomains=[]
            ip = host.ip
            try: 
                #Establish a read only remote connection to libvirtd
                #find out all domains running and not running
                #Since it might result in an error add an exception handler
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
                    if len(vm)==1:
                        vm = vm[0]
                        if vm.hostid == host.id:
                            hostid = vm.hostid
                            ram = vm.RAM
                            sport = vm.sport
                            hostip = ip
                            vmid = vm.id
                            owner = db(db.auth_user.id == vm.userid).select(db.auth_user.username)[0].username
                            element = {'name':name,'RAM':ram,'hostip':hostip,'owner':owner,'sport':sport,'state':state, 'id':vmid}
                            vmlist.append(element)
                    dom=""
                conn.close()
            except:notreachable = notreachable+ip+' '
        #if notreachable == "Error connecting ":
        #    response.flash = "All hosts active"
        #else:
        #    response.flash = notreachable
        return dict(vmlist=vmlist,flash=response.flash)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))

#HOST BASED VIEW OF VMS
@auth.requires_login()
def list_hosts():
    try:
        import libvirt,commands,string
        session.prev_url = "list_hosts"
        vms = db(db.vm.id>=0).select()
        vmlist=[]
        for vm in vms:
            #if(vm.runlevel!=0):
	    #	addtocost(vm.name)
            element = {'name':vm.name,'ip':vm.ip,'RAM':vm.RAM,'vcpus':vm.vCPU,'level':vm.runlevel,'hostip':vm.hostid.ip,'owner':vm.userid.first_name,'id':vm.id,'cost':vm.totalcost}
            vmlist.append(element)
        return dict(vmlist=vmlist)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))
    
#START VIRTUAL MACHINE
@auth.requires_login()
def start_machine():
    try:
        vmname = request.args[0]
        prelim_checks(vmname)
        vm=db(db.vm.name==vmname).select()[0]
        chost=db(db.host.id == vm['hostid']).select()[0]['id']
        db.queue.insert(task='start',vm=vm['id'],user=auth.user.id,chost=chost,status=0,rtime=putdate())
        session.flash = "Your task has been queued. Please check your task list for status."
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))
    if (session.prev_url != None):
        redirect(URL(r=request,f=session.prev_url))
    else :
        redirect(URL(r=request,f='list_all'))

#SHUT-DOWN VIRTUAL MACHINE
@auth.requires_login()
def shutdown_machine():
    try:
        vmname = request.args[0]
        prelim_checks(vmname)
        vm=db(db.vm.name==vmname).select()[0]
        chost=db(db.host.id == vm['hostid']).select()[0]['id']
        db.queue.insert(task='shutdown',vm=vm['id'],user=auth.user.id,chost=chost,status=0,rtime=putdate())
        session.flash = "Your task has been queued. Please check your task list for status."
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))
    if (session.prev_url != None):
        redirect(URL(r=request,f=session.prev_url))
    else :
        redirect(URL(r=request,f='list_all'))

#DESTROY VIRTUAL MACHINE
@auth.requires_login()
def destroy_machine():
    try:
        vmname = request.args[0]
        prelim_checks(vmname)
        vm=db(db.vm.name==vmname).select()[0]
        chost=db(db.host.id == vm['hostid']).select()[0]['id']
        db.queue.insert(task='destroy',vm=vm['id'],user=auth.user.id,chost=chost,status=0,rtime=putdate())
        session.flash = "Your task has been queued. Please check your task list for status."
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))
    if (session.prev_url != None):
        redirect(URL(r=request,f=session.prev_url))
    else :
        redirect(URL(r=request,f='list_all'))

#RESUME VM
@auth.requires_login()
def resume_machine():
    try:
        vmname = request.args[0]
        prelim_checks(vmname)
        vm=db(db.vm.name==vmname).select()[0]
        chost=db(db.host.id == vm['hostid']).select()[0]['id']
        db.queue.insert(task='resume',vm=vm['id'],user=auth.user.id,chost=chost,status=0,rtime=putdate())
        session.flash = "Your task has been queued. Please check your task list for status."
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))
    if (session.prev_url != None):
        redirect(URL(r=request,f=session.prev_url))
    else :
        redirect(URL(r=request,f='list_all'))

#SUSPEND VM
@auth.requires_login()
def suspend_machine():
    try:
        vmname = request.args[0]
        prelim_checks(vmname)
        vm=db(db.vm.name==vmname).select()[0]
        chost=db(db.host.id == vm['hostid']).select()[0]['id']
        db.queue.insert(task='suspend',vm=vm['id'],user=auth.user.id,chost=chost,status=0,rtime=putdate())
        session.flash = "Your task has been queued. Please check your task list for status."
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))
    if (session.prev_url != None):
        redirect(URL(r=request,f=session.prev_url))
    else :
        redirect(URL(r=request,f='list_all'))

#DELETE A VIRTUAL MACHINE
@auth.requires_login()
def delete_machine():
    requires_moderator()
    try:
        vmname = request.args[0]
        prelim_checks(vmname)
        vm=db(db.vm.name==vmname).select()[0]
        chost=db(db.host.id == vm['hostid']).select()[0]['id']
        db.queue.insert(task='delete',vm=vm['id'],user=auth.user.id,chost=chost,status=0,rtime=putdate())
        session.flash = "VM has been queued for deletion. Please check your task list for status."
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))
    if (session.prev_url != None):
        redirect(URL(r=request,f=session.prev_url))
    else :
        redirect(URL(r=request,f='list_all'))

#MIGRATE VM HOST1 TO HOST2
@auth.requires_login()
def migrate_vm():
    ifRedirect=False
    try:
        requires_moderator()
        import string, os
        form_fields = ['vm','chost','dhost']
        form_labels = {'vm':'VM Name','chost':'Current Host','dhost':'Destination Host'}

        form = SQLFORM(db.migrate, fields = form_fields, labels =form_labels)
        vmname=request.args[0]
        vm=db(db.vm.name==vmname).select()[0]
        chost=db(db.vm.name == vmname).select(db.vm.hostid)[0].hostid.ip
        prelim_checks(vmname)
        form.vars.vm = vmname
        form.vars.chost = chost
        options = ""
        if form.accepts(request.vars, session):
            chost_id = db(db.vm.name == vmname).select(db.vm.hostid)[0]['hostid']
            options = options + "--live --persistent --undefinesource "
            #if(form.vars.suspend): options = options + "--suspend "
            db.queue.insert(task='suspend',vm=vm['id'],user=auth.user.id,chost=chost_id,status=0,rtime=putdate())
            db.queue.insert(task='migrate',vm=vm['id'],user=auth.user.id,chost=chost_id,dhost=form.vars.dhost,parameters=options+vmname,status=0,rtime=putdate())
            db.queue.insert(task='resume',vm=vm['id'],user=auth.user.id,chost=None,status=0,rtime=putdate())
            session.flash = "Your task has been queued. Please check your task list for status."
            ifRedirect=True
        elif form.errors:
            response.flash = 'Error in form'
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))
    if ifRedirect == True:
        if (session.prev_url != None):
            redirect(URL(r=request,f=session.prev_url))
        else :
            redirect(URL(r=request,f='list_all'))
    else:
        return dict(form=form)

@auth.requires_login()
def lockvm():
    try:
        requires_moderator()
        vmname = request.args[0]
        prelim_checks(vmname)
        vm=db(db.vm.name==vmname).select()[0]
	if(not vm['locked']):
	    chost=db(db.host.id == vm['hostid']).select()[0]['id']
            db.queue.insert(task='destroy',vm=vm['id'],user=auth.user.id,chost=chost,status=0,rtime=putdate())
            session.flash = "VM has will be force Shutoff and locked. Check the task queue."
            db(db.vm.name==vmname).update(locked=True)
	else:
            db(db.vm.name==vmname).update(locked=False)
            session.flash = "Lock Released. Start VM yourself."
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))
    if (session.prev_url != None):
        redirect(URL(r=request,f=session.prev_url))
    else :
        redirect(URL(r=request,f='list_all'))

#ADJUST THE RUN LEVEL OF THE VIRTUAL MACHINE
@auth.requires_login()
def adjrunlevel():
    try:
        vm_name=request.args[0]
        prelim_checks(vm_name)
        vm=db(db.vm.name == vm_name).select()[0]
        response.flash='VM runlevel is '+str(vm.runlevel)
        return dict(vm=vm)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))

#TODO - Review
@auth.requires_login()
def changelevel():
    try:
        vmname = request.args[0]
        level=request.args[1]
        vm=db(db.vm.name==vmname).select()[0]
	chost_id=db(db.host.id == vm['hostid']).select()[0]['id']
        dhost_id = findnewhost(level,vm['RAM'],vm['vCPU'])
        db.queue.insert(task='changelevel',vm=vm['id'],user=auth.user.id,chost=chost_id,status=0,parameters=level,rtime=putdate())
        session.flash = "Request for level change to "+level+" has been inserted in task queue."
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))
    if (session.prev_url != None):
        redirect(URL(r=request,f=session.prev_url))
    else :
        redirect(URL(r=request,f='list_all'))        

#SETTINGS FOR A VIRTUAL MACHINE
@auth.requires_login()
def settings():
    try:
        import libvirt
        vmname=request.args[0]
        prelim_checks(vmname)
        vminfo = db(db.vm.name == vmname).select()[0]
        hostip=db(db.host.id==vminfo.hostid).select()[0].ip
        conn = libvirt.openReadOnly('qemu+ssh://root@'+hostip+'/system')
        dom = conn.lookupByName(vmname)
        state=vminfotostate(dom.info()[0])
	isstuck=False
        if(len(db(db.errors.error==vmname)(db.errors.status==0).select())==1):
            isstuck=True

        data={'name':vmname,'hdd':vminfo.HDD,'ram':vminfo.RAM,'vcpus':vminfo.vCPU,'status':state,'ip':vminfo.ip,'hostip':vminfo.hostid.ip,'port':vminfo.sport,'ostype':vminfo.templateid.ostype,'owner':vminfo.userid.first_name,'cost':vminfo.totalcost,'level':vminfo.runlevel, 'isstuck':isstuck}
        users=[]
        vmid=db(db.vm.name==vmname).select(db.vm.id)[0]['id']
        uids=db(db.vmaccpermissions.vmid==vmid).select(db.vmaccpermissions.userid)
        for uid in uids:
            uid=uid['userid']
            users.append(db(db.auth_user.id==uid).select(db.auth_user.username)[0]['username'])
        dom=""
        conn.close()
        return dict(data=data,users=users)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))

@auth.requires_login()
def clonevm():
    requires_moderator()
    try:
        vmname=request.args[0]
        number=0
        number=request.args(1)

        vm=db(db.vm.name==vmname).select()[0]
        #for i in range(number):
            #db.request.insert(vmname=vm.name,userid=vm.userid)
            #db.queue.insert(task='install',user=auth.user.id,status=0,parameters=[req['id'],req.vmname],rtime=putdate())

    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))


#ACCESS THE CONSOLE OF VIRTUAL MACHINE
@auth.requires_login()
def vncconsole():
    requires_moderator()
    try:
        vmname = request.args[0]
        prelim_checks(vmname)
        data=[]
        vm=db(db.vm.name==vmname).select()[0]
        data.append(vm.hostid.ip)
        data.append(vm.sport)
        return dict(data=data)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))

#MAKE A TEMPLATE OUT OF A VIRTUAL MACHINE
#TODO - To be changed to forking
@auth.requires_login()
def maketemplate():
    try:
        requires_moderator()
        import commands,time
        from paramiko import SSHClient, SSHException
        form=FORM('Template Name:  ',
                    INPUT(_name='name',requires=IS_NOT_EMPTY()),
                    INPUT(_type='submit', _value='Make template'))

        message=[]
        vmname = request.args[0]
        if form.accepts(request.vars, session):
            acquire(form.vars.name)
            
            tname=form.vars.name
            if (len(db(db.template.name == tname).select()) != 0):
                message.append("Template with this name already exists")
                #redirect(URL(r=request,f='settings',args=vmname))
            else:
                tname = form.vars.name
                prelim_checks(vmname)
                vm = db(db.vm.name == vmname).select()[0]
                ip = vm.definedon.ip
                error=0
                if(vm.templateid==None):
                    temptype = vm.isofile.ostype
                    temphdd = vm.HDD
                    tempother = 'This template was created from a vm with manual installation'
                else:
                    temptype = vm.templateid.ostype
                    temphdd = vm.templateid.hdd
                    tempother = vm.templateid.other_details
                    hdfile = getconstant('templates_path')+tname+'.qcow2'
                s = SSHClient()
                s.load_system_host_keys()
                try:
                    s.connect(hostname=ip, username='root')
                except SSHException:
                    session.flash="ssh to remote server failed. Please retry."
                else:
                    command = 'virsh suspend '+vm.name
                    ssh_stdin, ssh_stdout, ssh_stderr = s.exec_command(command)
                    exit_status = ssh_stdout.channel.recv_exit_status()
                    if(exit_status != 0):
                        message.append(vm.name+' could not be paused.'+str(ssh_stderr)+' '+str(exit_status))
                        error=1
                    time.sleep(1)
                    
                    command = 'ssh root@'+ip+' virt-clone -o '+vmname+' -n '+tname+' -f '+hdfile+' --force'
                    out=commands.getstatusoutput(command)
                    if(out[0] != 0):
                        message.append('An error occured while cloning'+out[1])
                        error=1
                    time.sleep(2)

                    command = 'virsh resume '+vm.name
                    ssh_stdin, ssh_stdout, ssh_stderr = s.exec_command(command)
                    exit_status = ssh_stdout.channel.recv_exit_status()
                    if(exit_status != 0):
                        message.append(vm.name+' could not be resumed.'+str(ssh_stderr)+' '+str(exit_status))
                        error=1
                    time.sleep(1)

                    s.exec_command('cp '+hdfile+' '+hdfile+'.copy')


                    if(error==0):db.template.insert(name=tname,ostype=temptype,hdd=temphdd,hdfile=hdfile,other_details=tempother)

                    s.close()
                                
                if(error != 0): response.flash = message
                else: response.flash = 'New template '+tname+' successfully created'
            release(form.vars.name)
        return dict(form=form)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))

def mailToGUI():
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        help_text=db(db.help.token=="postman").select(db.help.text)[0]['text']
        users=request.args[0]
        uarray=users.split('-')
        emails=""
        for i in range(0,len(uarray)-1):
            u = uarray[i]
            emails += user_email(u)+","
        u=uarray[len(uarray)-1]
        emails += user_email(u)
        
        subject=request.args[1]
        subject=subject.replace('_',' ')
        email_txt=request.args[2]
        email_txt=email_txt.replace('_',' ')
        form = SQLFORM(db.email)
        form.vars.from_address=getconstant('email_from')
        form.vars.to_address=emails
        form.vars.subject=subject
        form.vars.email_txt=email_txt
        
        if (form.accepts(request.vars,session)):
            msg = MIMEText(form.vars.email_txt)
            msg['Subject'] = form.vars.subject
            msg['From'] = form.vars.from_address
            s = smtplib.SMTP('localhost')
            msg['To'] =form.vars.to_address
            for user in uarray:
                s.sendmail(msg['From'], user_email(user), msg.as_string())
                s.quit()
            response.flash = "Mail sent successfully"
        elif form.errors:
            response.flash = 'Error in form'
        return dict(form=form,help_text=help_text)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))

#Setup and iptable port forwarding rule
@auth.requires_login()
def allow_display():
    try:
        vmname=request.args(0)
        ostype=db(db.vm.name==vmname).select()[0].templateid.ostype
        remove_iptable_rules(vmname)
       
        #Avoid vms which are not reported stuck in errors table
        isfaulty=len(db(db.errors.error==vmname and db.errors.type=='STUCK').select())
        if(not isfaulty): return 0
    
        ws_ip = getconstant('webserver_ip')
        port=insert_iptable_rules(vmname)
        db.iptables.insert(vm=vmname,insert_time=putdate(),active=True)
        return dict(ip=ws_ip,port=port,vmtype=ostype,vmname=vmname)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))


@auth.requires_login()
def disallow_display():
    try:
        vmname=request.args(0)
        remove_iptable_rules(vmname)
        db(db.iptables.vm==vmname).update(delete_time=putdate(),active=False)
        session.flash="Redirected to home page"
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))
    redirect(URL(r=request,c='default', f='index'))


@auth.requires_login()
def misc_requests():
    try:
        form_fields = ['request','reason']
        form_labels = {'request':'Category','reason':'Reason'}

        form = SQLFORM(db.misc_requests, fields = form_fields, labels =form_labels)
        form.vars.status=0
        form.vars.vm=request.args(0)
        form.vars.request_date=putdate()
        form.vars.user=auth.user.id
        msg="Get the request approved from vm owner"
        if(isFaculty(auth.user.username) or isModerator(auth.user.username)):
            form.vars.status=1
            msg="Request waiting for admin approval"

        if form.accepts(request.vars, session):
            response.flash = msg 
        return dict(form=form)
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))
