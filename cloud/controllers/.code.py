#def add_user_to_vm():
#    form=SQLFORM(db.vmaccpermissions)
#    vmarray=db(db.vmaccpermissions.userid==form.vars.userid).select(db.vmaccpermissions.vmid)
#    for vm in vmarray:
#        if form.vars.vm==vm:
#            response.flash="You cannot add the same user"
#            redirect(URL(r=request,f='add_user_to_vm'))
#    if form.accepts(request.vars,session):
#        response.flash='User added to the Virtual Machine'
#    elif form.errors:
#        response.flash='Error in form'
#    return dict(form=form)
##################################### FIREWALL HANDLING ###############################
def insert_firewall_rules(host_ip):
    import commands

    # Selection of source and destination ports
    vncdport = int(getconstant('vncdport'))+1
    vncsport = vncdport+int(getconstant('diffports'))
    setconstant('vncdport',vncdport)

    # Creation and insertion of iptables rules into the running kernel
    sport = str(vncsport)
    dport = str(vncdport)

    ws_ip = getconstant('webserver_ip')
    ws_if = getconstant('webserver_interface')

    iptables = getconstant('iptables_path')
    rules = []
    rule = 'sudo '+iptables + ' -A PREROUTING  -t nat -p tcp -i ' + ws_if + ' -d ' + ws_ip + ' --dport ' + sport + \
          ' -j DNAT --to ' + host_ip + ':' + dport
    rules.insert(0, rule)
    rule = 'sudo '+iptables + ' -A POSTROUTING -t nat -p tcp -o ' + ws_if + ' -d ' + host_ip + ' --dport ' + dport + \
          ' -j SNAT --to-source ' + ws_ip
    rules.insert(0, rule)
    rule = 'sudo '+iptables + ' -A FORWARD -p tcp  -d ' + host_ip + ' --dport ' + dport + ' -j ACCEPT'
    rules.insert(0, rule)

    for r in rules:
        commands.getstatusoutput(r)
    iptsave_cmd = 'sudo iptables-save > ' + getconstant('iptables_backup_path')
    commands.getstatusoutput(iptsave_cmd)
    return sport, dport

@auth.requires_login()
@requires_moderator(auth.user.username)
def add_to_group():
    form=SQLFORM(db.auth_membership)
    if form.accepts(request.vars,session):
        response.flash='Added the user to the group'
    elif form.errors:
        response.flash='Error in form'  
    return dict(form=form)

#ADD USER TO THE MAILING LIST
@auth.requires_login()
@requires_moderator(auth.user.username)
def add_user_to_mailing_list():
    #form=SQLFORM(db.auth_membership)
    #return gid
    form = SQLFORM(db.auth_membership, submit_button='Add User',deletable=True, delete_label='Check to delete:',record=None)
    gid = db(db.auth_group.role == "mailing_list").select(db.auth_group.id)[0]['id']
    #db("mailing_list").select()
    usersid=db(db.auth_membership.group_id == gid).select(db.auth_membership.user_id)
    users=[]
    for userid in usersid:
        users.append(db(db.auth_user.id == userid['user_id']).select()[0])
    form.vars.group_id = gid
    if form.accepts(request.vars,session):
        response.flash='Added the user to the mailing list'
    elif form.errors:
        response.flash='Error in form'
    return dict(form=form,users=users)


@auth.requires_login()
@requires_moderator(auth.user.username)
def delete_user_from_mailing_list():
    gid = db(db.auth_group.role == "mailing_list").select(db.auth_group.id)[0]['id']
    membership = db(db.auth_membership.user_id == request.args[0] and db.auth_membership.group_id == gid).select()[0]
    record="Deleted the user "+membership.user_id.username+" from the mailing list"
    log(record,1)
    db(db.auth_membership.user_id == request.args[0] and db.auth_membership.group_id == gid).delete()
    redirect(URL(r = request, f = 'add_user_to_mailing_list'))

@auth.requires_login()
@requires_moderator(auth.user.username)
def add_group():
    form=SQLFORM(db.auth_group)
    if form.accepts(request.vars,session):
        response.flash='Added the group'
    elif form.errors:
        response.flash='Error in form'  
    return dict(form=form)

#GENERATE A RANDOM PASSWORD FOR THE VNC CONSOLE
@auth.requires_login()
@requires_moderator(auth.user.username)
def gen_passwd():
    import random
    passwd = ''.join([random.choice(\
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890') \
        for i in range(6)])
    return passwd

###################################### EMAIL  ##########################################
def notify_email(subject,email_txt):
    import smtplib
    from email.mime.text import MIMEText
    msg = MIMEText(email_txt)
    me = getconstant('email_from')
    gid = db(db.auth_group.role == "mailing_list").select(db.auth_group.id)[0]['id']
    users = db(db.auth_membership.group_id == gid).select(db.auth_membership.user_id)
    emails=[]
    for user in users:
        emails.append(user['user_id'].email);
    msg['Subject'] = subject
    msg['From'] = me
    s = smtplib.SMTP('localhost')
    for user_email in emails:
        msg['To'] = user_email
        s.sendmail(me, user_email, msg.as_string())
    s.quit()
    
#def create_vm_manual(vmname, mem, iso, ownerid, userid, vcpu, hdd, vncpasswd):
    #Check if a vm with same name already exists
#    if namerepcheck(vmname) == False:
#        machine=db(db.host.id>0).select()
#        count=[]
#        for mac in machine:
#            count.append(mac.vmcount)
#        count.sort()
#        machine=db(db.host.vmcount==count[0]).select()[0]
#        (sport, dport) = insert_firewall_rules(machine.ip)
#        deploy_vm_new(machine.ip, None, 0, iso, None, vmname, mem, hdd, dport, vncpasswd, vcpu)
#        db.vm.insert(userid=ownerid, name=vmname, RAM=mem, mac='', HDD=hdd, vCPU=vcpu, \
#          templateid=None,usingtemplate=0, isofile=iso,hostid=machine.id, \
#          sport=sport, dport=dport, \
#          definedon=machine.id,runlevel=3,lastrunlevel=3,laststarttime=currenttime())  #sport is the port on server and destination port is port on host
#        vm=db(db.vm.name==vmname).select(db.vm.id)[0]
#        db.vmaccpermissions.insert(userid=ownerid, vmid=vm.id)
#        db.vmaccpermissions.insert(userid=userid, vmid=vm.id)
#        db(db.host.id==machine.id).update(vmcount=count[0]+1)
#        send_confirmation_email(ownerid, vmname, sport, vncpasswd)
#    else:
#        session.flash = "VM with same name already exits"
#    return


###################################### CREATE VM #######################################
#def create_vm(vmname, mem, templateid, ownerid, hdd, vcpu, vncpasswd):
    ## Select host (TODO: make separate function)
    
    ##Check if a vm with same name already exists
    #if namerepcheck(vmname) == False:
        #machine=db(db.host.id>0).select()
        #count=[]
        #for mac in machine:
            #count.append(mac.vmcount)
        #count.sort()
        #machine=db(db.host.vmcount==count[0]).select()[0]
        #template = db(db.template.id == templateid).select()[0]
        #template_hdfile = template.hdfile
        #template_ostype = template.ostype
        #(sport, dport) = insert_firewall_rules(machine.ip)
        #deploy_vm(machine.ip, template_hdfile, template_ostype, vmname, mem, hdd, dport, vncpasswd, vcpu)
        #db.vm.insert(userid=ownerid, name=vmname, RAM=mem, mac='', \
          #templateid=templateid, hostid=machine.id, \
          #sport=sport, dport=dport, \
          #runningon=machine.id,runlevel=3,lastrunlevel=3,laststarttime=currenttime())  #sport is the port on server and destination port is port on host
        #vm=db(db.vm.name==vmname).select(db.vm.id)[0]
        #db.vmaccpermissions.insert(userid=ownerid, vmid=vm.id)
        #db.vncpassword.insert(vmname=vmname,hostip=machine.ip,vncport=sport,password=str(vncpasswd))
        #db(db.host.id==machine.id).update(vmcount=count[0]+1)
        #session.flash = "VM created successfully. VNC port is " + str(sport) + ". VNC password is " + str(vncpasswd)
        #send_confirmation_email(ownerid, vmname, sport, vncpasswd)
    #else:
        #session.flash = "VM with same name already exits"
    #return
    
@auth.requires_login()
def approve_request_details1():
    req = db(db.request.id==request.args[0]).select()[0]
    suggested = findnewhost(3,req.RAM,req.vCPUs)#Intially all the hosts will be put up as level 3 hosts
    #Find corresponding hostname
    if(suggested!=None):
        suggested=db(db.host.id==suggested).select(db.host.name)[0].name
        allhosts=["select"]
        allhosts.append([OPTION(host.name, _value=host.id) for host in db().select(db.host.ALL)])
        form = FORM(TABLE(
                TR('Username',INPUT(_name='user',_value=req.userid.username,requires=IS_NOT_EMPTY())),
                TR('VMname',INPUT(_name='vmname',_value=req.vmname,requires=IS_NOT_EMPTY())),
                TR('RAM',INPUT(_name='RAM',_value=req.RAM,requires=IS_NOT_EMPTY())),
                TR('HDD',INPUT(_name='HDD',_value=req.HDD,requires=IS_NOT_EMPTY())),
                TR('vCPUs',INPUT(_name='vCPUs',_value=req.vCPUs,requires=IS_NOT_EMPTY())),
                TR('Template',INPUT(_name='template')),
                TR('Faculty',INPUT(_name='faculty',requires=IS_NOT_EMPTY(),_value=req.faculty)),
                TR('Suggested Host',INPUT(_name='suggested_host',_value=suggested)),
                TR('Select Host',SELECT(allhosts,_name='desthost',requires=IS_NOT_EMPTY())),
                TR("",INPUT(_type="submit",_value="Create it!"))))
        form.element('input[name=template]')['_value']=req.templateid.name
        if (isModerator(auth.user.username)) or (isFaculty(auth.user.username)):
            if req.faculty != None:
                form.element('input[name=faculty]')['_value']=req.faculty
        if (form.accepts(request.vars,session) and form.vars.desthost != "select"):
            db(db.request.id == request.args[0]).update(kvmhost=form.vars.desthost)
            redirect(URL(c='admin', f='approve_request',args=request.args[0]))
        if (form.accepts(request.vars,session)):# and form.vars.desthost == "select"):
            raise HTTP(403,"There seems to be some error. Please specify the host"+form.vars.desthost)
        elif form.errors:response.flash='Error in Form'
        return dict(form=form)
    else: 
        session.flash="No appropriate host found for this new VM."
        redirect(URL(r=request, f='get_requests'))
        
#LIST THE USER'S VIRTUAL MACHINES
#ONLY READING THE HOSTS, SO NEED FOR LOCKS
@auth.requires_login()
@requires_moderator(auth.user.username)
def list():
    import libvirt,commands,string
    vmlist = []
    notreachable = "Error connecting "
    hosts = db(db.host.id >=0).select()
    for host in hosts:
        domains=[]    #will contain the domain information of all the available domains
        vdomains=[]
        ip = host.ip
        try: 
            #Establish a read only remote connection to libvirtd, find out all domains running and not running, Since it might result in an error add an exception handler
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
                        db(db.vm.name == name).update(status=state)
                        element = {'name':name,'RAM':ram,'hostip':hostip,'owner':owner,'sport':sport,'state':state, 'id':vmid}
                        vmlist.append(element)
        except:notreachable = notreachable+ip+' '
    if notreachable == "Error connecting ":
        response.flash = "All hosts active"
    else:
        response.flash = notreachable
    return dict(vmlist=vmlist,flash=response.flash)

#REQUIRED FOR THE HOST BASED LIST OF THE VIRTUAL MACHINES
@auth.requires_login()
@requires_moderator(auth.user.username)
def list_hosts():
    return list()

#@auth.requires_login()
#def create_snapshot():
#    vm_name=request.args[0]
#    prelim_checks(vm_name)
#    vmach = db(db.vm.name == vm_name).select()
#    ip = vmach[0].hostid.ip
#    import libvirt
#    from time import gmtime, strftime
#    snapname=strftime("%d-%b-%Y_%H-%M-%S", gmtime())
#    conn = libvirt.open('qemu+ssh://root@'+ip+'/system')
#    dom = conn.lookupByName(vm_name)
#    session._unlock(response)
#    snap=dom.snapshotCreateXML('<domainsnapshot>\n  <name>'+snapname+'</name>\n</domainsnapshot>',0)
#    session._unlock(response)
#    db.snapshots.insert(name=snapname,vm=vmach[0].id)
#    session.vm_status = "Snapshot Created (code: 0)"
#    redirect(URL(r=request,f='list_all'))    


#@auth.requires_login()
#def delete_snapshot():
#    snapname = request.args[0]
#    snap_prelim_checks(snapname)
#    snap=db(db.snapshots.name == snapname).select()[0]
#    hostip=snap['vm'].hostid.ip
#    import libvirt
#    conn = libvirt.open('qemu+ssh://root@'+hostip+'/system')
#    dom = conn.lookupByName(snap.vm.name)
#    snap = dom.snapshotLookupByName(snap.name,0)
#    snap.delete(0)
#    db(db.snapshots.name == snapname).delete()
#    session.vm_status = "Snapshot deleted (code: 0)"
#    redirect(URL(r=request,f='list'))

#@auth.requires_login()
#def revert_to_snapshot():
#    snapname = request.args[0]
#    snap_prelim_checks(snapname)
#    snap=db(db.snapshots.name == snapname).select()[0]
#    hostip=snap['vm'].hostid.ip
#    import libvirt
#    conn = libvirt.open('qemu+ssh://root@'+hostip+'/system')
#    dom = conn.lookupByName(snap.vm.name)
#    snap = dom.snapshotLookupByName(snap.name,0)
#    dom.revertToSnapshot(snap,0)
#    db(db.snapshots.name == snapname).delete()
#    session.vm_status = "Snapshot deleted (code: 0)"
#    redirect(URL(r=request,f='list'))

@auth.requires_login()
def view_snapshots():
    vm_name=request.args[0]
    prelim_checks(vm_name)
    import libvirt
    from lxml import etree #for parsing xml trees
    from StringIO import StringIO
    
    host = db(db.vm.name == vm_name).select()
    ip = host[0].hostid.ip
    conn = libvirt.openReadOnly('qemu+ssh://root@'+ip+'/system')
    dom = conn.lookupByName(vm_name)
    snapshots=dom.snapshotListNames(0)
    snap_info=[]
    for snap in snapshots:
        snapinstance = dom.snapshotLookupByName(snap,0)
        tree =  etree.parse(StringIO(snapinstance.getXMLDesc(0)))
        snap_info.append(dict(name=tree.findtext("name"),state=tree.findtext("state"),parent=tree.findtext("parent/name"),time=tree.findtext("creationTime"),status=tree.findtext("state")))
        #snapshot['name']=tree.findtext("name")
        #snapshot['state']=tree.findtext("state")
        #snapshot['parent']=tree.findtext("parent/name")
        #snapshot['created']=tree.findtext("creationTime")
    for snap_name in snap_info:
        status=True
        for snap_parent in snap_info:
            if (snap_name['name']==snap_parent['parent']) :
                status=False
        if (status==False) :
            snap_name['canDelete']=False
        else :
            snap_name['canDelete']=True
    return dict(snapshots=snap_info)

#CLONE THE VM
@auth.requires_login()
def clonevm():
    import commands, string, time,commands
    from xml.etree.ElementTree import ElementTree #XML parsing module for editing port
    form=FORM(TABLE(TR(TD('Cloned VM Name:'),TD(INPUT(_name='name',requires=IS_NOT_EMPTY()))),
              TR(TD('VNC Password:'),TD(INPUT(_name='vncp',_type='password',requires=IS_NOT_EMPTY()))),
               TR(TD(),TD(INPUT(_type='submit', _value='Clone it!')))))

    vmname=request.args[0]
    prelim_checks(vmname)
    message=[]
    if form.accepts(request.vars, session):
        newname=form.vars.name
        if namerepcheck(newname):message.append("VM with this name already exists")
        else:
            vm = db(db.vm.name == vmname).select()[0]
            ip = vm.definedon.ip
            hddfile=getconstant('vmfiles_path')+newname+'.qcow2'
            #mac=form.vars.mac
            prelim_checks(vmname)
            from paramiko import SSHClient, SSHException
            s = SSHClient()
            s.load_system_host_keys()
            try:
                s.connect(hostname=ip, username='root')
            except SSHException:
                message.append("ssh to remote server failed. Please retry.")
            else:
                (sport,dport)=insert_firewall_rules(vm.definedon.ip)
                error=0
                command = 'virsh suspend '+vm.name
                ssh_stdin, ssh_stdout, ssh_stderr = s.exec_command(command)
                exit_status = ssh_stdout.channel.recv_exit_status()
                if(exit_status != 0):
                    message.append(vm.name+' could not be paused.'+str(ssh_stderr)+' '+str(exit_status))
                    error=1
                time.sleep(1)
                
                command = 'ssh root@'+vm.definedon.ip+' virt-clone -o '+vmname+' -n '+newname+' -f '+hddfile+' --force'
                out = commands.getstatusoutput(command)
                #ssh_stdin, ssh_stdout, ssh_stderr = s.exec_command(command)
                #exit_status = ssh_stdout.channel.recv_exit_status()
                if(out[0] != 0): message.append('An error occured while cloning'+out[1])
                time.sleep(2)
                
                a='/etc/libvirt/qemu/'
                commands.getstatusoutput('scp root@'+vm.definedon.ip+':'+a+newname+'.xml /tmp/.')
                tree = ElementTree()
                tree.parse('/tmp/'+newname+'.xml')
                p = tree.find("devices/graphics")
                p.attrib["port"]=dport
                p.attrib["passwd"]=form.vars.vncp
                tree.write('/tmp/'+newname+'.xml')
                commands.getstatusoutput('scp /tmp/'+newname+'.xml root@'+vm.definedon.ip+':'+a+newname+'.xml')
                ##command = 'cat '+a+newname+'.xml | sed \'s/'+vm.dport+'/'+dport+'/g\' > '+a+newname+'.xml'
                #s.exec_command(command)
                #message.append(command)

                ssh_stdin, ssh_stdout, ssh_stderr =s.exec_command('virsh define '+a+newname+'.xml')
                exit_status = ssh_stdout.channel.recv_exit_status()
                if(exit_status != 0):
                    message.append('Error occured while defining new vm')
                    error=1
                time.sleep(2)

                ssh_stdin, ssh_stdout, ssh_stderr =s.exec_command('virsh start '+newname)
                exit_status = ssh_stdout.channel.recv_exit_status()
                if(exit_status != 0):
                    message.append('Error occured while starting '+newname)
                    error=1
                time.sleep(2)
                
                ssh_stdin, ssh_stdout, ssh_stderr =s.exec_command('virsh resume '+vm.name)
                exit_status = ssh_stdout.channel.recv_exit_status()
                if(exit_status != 0):
                    message.append('Error occured while starting '+vm.name)
                    error=1
                time.sleep(2)

                if(error == 0):
                    db.vm.insert(name=newname,userid=vm.userid,hostid=vm.definedon,definedon=vm.definedon,RAM=vm.RAM, \
                    templateid=vm.templateid,usingtemplate=vm.usingtemplate,isofile=vm.isofile,sport=sport,dport=dport, \
                    status='Off',totalcost=0,laststarttime=currenttime(),lastrunlevel=3,runlevel=3, HDD=vm.HDD,vCPU=vm.vCPU)
                    vmscount=db(db.host.id==vm.hostid).select(db.host.vmcount)[0].vmcount
                    db(db.host.id==vm.hostid).update(vmcount=vmscount)
                    vmm=db(db.vm.name==newname).select()[0]
                    db.vmaccpermissions.insert(userid=vmm.userid, vmid=vmm.id)
                    vncdetails=db(db.vncpassword.vmname==vmname).select()[0]
                    db.vncpassword.insert(vmname=newname,hostip=vm.definedon,password=vncdetails.password,vncport=sport)
                    #db(db.host.id==vm.definedon).update(vmcount=vm.hostid.vmcount+1)
                    message.append("VM created successfully. VNC port is " + str(sport) + ". VNC password is " + str(vncdetails.password))
                    send_confirmation_email(vm.userid, newname, sport, vncdetails.password)
                s.close()
        response.flash = message
    elif form.errors:
        response.flash = 'Error in form'
    return dict(form=form)

#def onerror(function):
#  def __onerror__(*a,**b):
#    try:
#        return function(*a,**b)
#    except HTTP, e:
#        import os
#        status=int(e.status.split(' ')[0])
#        filename=os.path.join(request.folder,'views/onerror%i.html'%status)
#        if os.access(filename,os.R_OK):
#            e.body=open(filename,'r').read()
#        raise e
#    except Exception:
        #db.errors.insert(error='Error')
        #error=True
#        import os, gluon.restricted
#        e=gluon.restricted.RestrictedError(function.__name__)
#        ticket=e.log(request)
#        SQLDB.close_all_instances(SQLDB.rollback)
#        head='https://10.20.254.39/admin/default/ticket/'
#        append_error_infile(head+ticket)
#        error_notify_email("Error",head+ticket)
#        filename=os.path.join(request.folder,'views/onerror.html')
#        if os.access(filename,os.R_OK):
#            body=open(filename,'r').read()
#        else:
#            body="""<html><body><h1>Internal ERROR</h1>Ticket issued:
#            <a href="/admin/default/ticket/%(ticket)s" target="_blank">%(ticket)s</a></body></html>"""
#        body=body % dict(ticket=ticket)
#        redirect(URL(c='default', f='index'))
#        sesison.flash='Some error occured'
        #raise HTTP(200,body=body)
        #if(error):db.errors.insert(error='Error')
#  return __onerror__

def requires_faculty(fn,name=None):
    def decorator(action):
        def f(*a, **b):
#            if auth.settings.allow_basic_login_only and not auth.basic():
#                if current.request.is_restful:
#                    raise HTTP(403,"Not authorized")
#                return call_or_redirect(auth.settings.on_failed_authorization)

#            if not auth.basic() and not auth.is_logged_in():
#                if current.request.is_restful:
#                    raise HTTP(403,"Not authorized")
#                request = current.request
#                next = URL(r=request,args=request.args,
#                           vars=request.get_vars)
#                session.flash = response.flash
#                return call_or_redirect(
#                    auth.settings.on_failed_authentication,
#                    auth.settings.login_url + '?_next='+urllib.quote(next)
#                    )
            if not isFaculty(auth.user.username):
                session.flash = auth.messages.access_denied
                raise HTTP(403,"Not authorized")
#                return call_or_redirect(auth.settings.on_failed_authorization)
            return action(*a, **b)
        f.__doc__ = action.__doc__
        f.__name__ = action.__name__
        f.__dict__.update(action.__dict__)
        return f
    return decorator

def requires_moderator(fn,name=None):
    def decorator(action):
        def f(*a, **b):
#            if auth.settings.allow_basic_login_only and not auth.basic():
#                if current.request.is_restful:
#                    raise HTTP(403,"Not authorized")
#                return call_or_redirect(auth.settings.on_failed_authorization)

#            if not auth.basic() and not auth.is_logged_in():
#                if current.request.is_restful:
#                    raise HTTP(403,"Not authorized")
#                request = current.request
#                next = URL(r=request,args=request.args,
#                           vars=request.get_vars)
#                session.flash = response.flash
#                return call_or_redirect(
#                    auth.settings.on_failed_authentication,
#                    auth.settings.login_url + '?_next='+urllib.quote(next)
#                    )
            if not isModerator(auth.user.username):
                session.flash = auth.messages.access_denied
                raise HTTP(403,"Not authorized")
#                return call_or_redirect(auth.settings.on_failed_authorization)
            return action(*a, **b)
        f.__doc__ = action.__doc__
        f.__name__ = action.__name__
        f.__dict__.update(action.__dict__)
        return f
    return decorator


'''
    def decorator():
        if (name == None) :
            raise HTTP(403,"Not authorized")
        import ldap
        import string, re
        from traceback import print_exc

        url="ldap://ldap1.iitd.ernet.in"
        dn="dc=iitd,dc=ernet,dc=in"

        l = ldap.initialize(url)
        l.bind_s("", "", ldap.AUTH_SIMPLE);
        lastdn = dn
        dnlist = None

        for name,attrs in l.search_s(dn, ldap.SCOPE_SUBTREE,"uid="+name):
            for k,vals in attrs.items():
                if (k == "category"):
                    if(vals[0]=="faculty"):
                        return
        raise HTTP(403,"Not authorized")
        l.unbind()
    return decorator
'''

#ADD AN ISO TO THE BAADAL DATABASE
@auth.requires_login()
def add_isofile():
    requires_moderator()
    form=SQLFORM(db.isofile,labels={'cdimage':'Complete Name'})
    if form.accepts(request.vars,session):
        response.flash='New template Created'
    elif form.errors:
        response.flash='Error in form'
    return dict(form=form)
    
@auth.requires_login()
def error_solved():
    requires_moderator()
    db(db.errors.id == request.args[0]).update(status=False)
    redirect(URL(c='admin', f='get_errors'))

#FIND ERRORS IN THE BAADAL
@auth.requires_login()
def get_errors():
    requires_moderator()
    import os
    filename=os.path.join(request.folder,'private/ticket_errors')
    if os.access(filename,os.R_OK):
        #body=open(filename,'r').read()
        f = open(filename,'r')
        for line in f:
            db.errors.insert(error=line)
        f.close()
        f =open(filename,'w')
        f.write('')
        f.close()
    errors=db(db.errors.status == True).select()
    return dict(errors=errors)
    db(db.errors.id == request.args[0]).update(status=False)
    redirect(URL(c='admin', f='get_errors'))

@auth.requires_login()
def log_error():
    requires_moderator()
    db.errors.insert(error=request.args[0],status=True)
    redirect(URL(c='admin', f='get_errors'))

@auth.requires_login()
def clonevm():
    requires_moderator()
    vmname = request.args[0]
    prelim_checks(vmname)
    vm = db(db.vm.name == vmname).select()[0]
    ip = vm.runningon.ip
    form_fields = ['name','mac']
    form_labels = {'name':'New VM Name','mac':'Mac Address'}
    # Add approver field to form if user is not faculty or moderator
    form = SQLFORM(db.clonevm, fields = form_fields, labels =form_labels)
    newname=form.vars.name

    if namerepcheck(newname):
        session.flash="VM with this name already exists"
    else:
        hddfile=getconstant('vmfiles_path')+vmname+'.qcow2'
        mac=form.vars.mac
        prelim_checks(vm_name)
        from paramiko import SSHClient, SSHException
        s = SSHClient()
        s.load_system_host_keys()
        try:
            s.connect(hostname=ip, username='root')
        except SSHException:
            session.flash="ssh to remote server failed. Please retry."
        else:
            (sport,dport)=insert_firewall_rules(vm.runningon)
            db.vm.insert(name=tname,userid=vm.userid,hostid=vm.runningon,runningon=vm.runningon,RAM=vm.RAM,templateid=vm.templateid,sport=sport,dport=dport,status='Off')
            command = 'virt-clone -o '+vmname+' -n '+newname+' -f '+hddfile+' --clone-running'
            s.exec_command(command)
            a='/etc/libvirt/qemu/'
            #s.exec_command('cat '+a+vmname+'.xml | sed \'s/'+vm.dport+'/'+dport'/g\' > '+a+newname+'.xml')
            s.exec_command('virsh define '+a+newname+'.xml')
            vmm=db(db.vm.name==newname).select()[0]
            db.vmaccpermissions.insert(userid=vmm.userid, vmid=vmm.id)
            #vncdetails=db(db.vncpassword.vmname==vmname).select()[0]
            #db.vncpassword.insert(vmname=newname,hostip=vm.runningon,vncpassword=vncdetails.vncpassword,vncport=sport)
            db(db.host.id==vm.runningon).update(vmcount=count[0]+1)
            session.flash = "VM created successfully. VNC port is " + str(sport) + ". VNC password is " + str(vncpasswd)+'. Start it !'
            send_confirmation_email(vm.userid, newname, sport, vncdetails.vncpassword)
            s.close()
    redirect(URL(r=request,f='settings',args=vmname))

#GENERIC MAIL TO FUNCTION - NOT TESTED PROPERLY
def mailTo(user=None,subject=None,email_txt=None):
    requires_moderator()
    user=request.args[0]
    subject=request.args[0]
    email_txt=request.args[1]
    import smtplib
    from email.mime.text import MIMEText
    msg = MIMEText(email_txt)
    me = getconstant('email_from')
    msg['Subject'] = subject
    msg['From'] = me
    s = smtplib.SMTP('localhost')
    msg['To'] =user_email(user)
    s.sendmail(me, user_email, msg.as_string())
    s.quit()
    
@auth.requires_login()
def request_vm_manual():
    help_text=db(db.help.token=="request_vm_manual").select(db.help.text)[0]['text']
    form_fields = ['vmname', 'RAM', 'HDD', 'vCPUs','isofile', 'VNCPassword', 'purpose']
    form_labels = {'vmname':'Name of VM', 'ram':'RAM (in MB)', 'hdd':'Harddisk (in GB)','vCPUs':'No. of Virtual CPUs','isofile':'CD Image', 'purpose':'Purpose of this VM', 'VNCPassword':'Set Preferred VNC Password'}
    # Add approver field to form if user is not faculty or moderator
    if not ifModerator(auth.user.username) and not isFaculty(auth.user.username):
        form_fields += ['faculty']
        form_labels['faculty'] = 'Faculty Approver Username'
    form = SQLFORM(db.request, fields = form_fields, labels = form_labels)
    form.vars.userid = auth.user.id
    form.vars.usingtemplate=0
    form.vars.templateid=None
    if ifModerator(auth.user.username):
        form.vars.status = 1  #TODO
    elif isFaculty(auth.user.username):
        form.vars.status = 1
    else:
        form.vars.status = 0 
    if (form.accepts(request.vars, session)):
        if(isFaculty(form.vars.faculty) or ifModerator(auth.user.username) or isFaculty(auth.user.username)):
            session.flash = 'VM creation request waiting for approval'
            redirect(URL('index'))
            response.flash = 'Invalid username for the faculty'
    elif form.errors:
        response.flash = 'Error in form'
    return dict(form=form,help_text=help_text)
    

def edit():
    #row = db.vm.name
    form = SQLFORM(db.request,['vmname'], deletable=True)
    if form.accepts(request.vars, session):
        response.flash = 'Record Updated'
    return dict(form=form)
    
            import commands,os
            machine=db(db.host.id==req.kvmhost).select(db.host.ip)[0]['ip']
            msg=commands.getstatusoutput("ssh root@"+machine+" tail -n 10 /var/log/libvirt/qemu/"+req.vmname+".log")[1]
            filename=os.path.join('/var/log/libvirt/qemu/'+req.vmname+'.log')
            if os.access(filename,os.R_OK):
                f = open(filename,'r')
                for line in f:
                    msg+=line
                f.close()
            return (False,msg) 
    else:
        db(db.queue.id==pid).update(status=-1,comments="VM with same name already exists")
