def install(pid,vmid=None,chost_id=None,dhost_id=None,parameters=None):
    import sys
    try:
        reqid = parameters.split("|")[1]
        vmname = parameters.split("|")[2]
        req = db(db.request.id == reqid).select()[0]
        if(ifValidVM(req.cloneparentname)):
            origvm=db(db.vm.name==req.cloneparentname).select()[0]
            db(db.request.id==reqid).update(templateid=origvm.templateid)
            if(getvmstate(origvm.name)!=5):
                db(db.queue.id==pid).update(status=-1,comments="Original VM "+origvm.name+" is not Off. Turn it off first",ftime=putdate())
                db(db.request.id==req.id).update(status=1)
                return
	errormsg=""
        datastore=give_datastore()
        vmname=req.vmname
        vmcount=int(getconstant("defined_vms"))+1
        if(vmcount%100 ==0): vmcount=vmcount+1
        setconstant("defined_vms",vmcount)
        (newmac,newip,vncport)=new_mac_ip(vmcount)
        print "VMCount="+str(vmcount)+" MAC:"+str(newmac)+" NEW IP:"+newip+" VNCPort:"+vncport
        #Check if a vm with same name already exists
        if namerepcheck(vmname) == False:
            print "Start the process. No vm with the same name exists already in the database"
            machine=db(db.host.id==req.kvmhost).select()[0]
            import time,os,commands
            from paramiko import SSHClient, SSHException

            print "Creating directory"
            if not os.path.exists (getconstant('vmfiles_path')+getconstant('datastore_int')+datastore.name+'/'+vmname):
                os.makedirs(getconstant('vmfiles_path')+getconstant('datastore_int')+datastore.name+'/'+vmname)

            vm_loc = getconstant('vmfiles_path')+getconstant('datastore_int')+datastore.name+'/'+vmname+'/'+ vmname + '.qcow2'
            if(not ifValidVM(req.cloneparentname)):
                template = db(db.template.id == req.templateid).select()[0]
                template_hdfile = template.hdfile
                template_loc=getconstant('vmfiles_path')+getconstant('datastore_int')+datastore.name+'/'+getconstant('templates_path')+template_hdfile
                print "Netapp Copy and Move in progress"
                command='sudo ssh '+datastore.ip+' ndmpcopy -d '+datastore.path+'/'+getconstant("templates_dir")+'/'+template_hdfile+' '+datastore.path+'/'+getconstant("templates_dir")+'/tmp'
                print command
                a=commands.getstatusoutput(command)
		print a
		errormsg = errormsg + a[1]
                command='sudo ssh '+datastore.ip+' mv '+datastore.path+'/'+getconstant("templates_dir")+'/tmp/'+template_hdfile+' '+datastore.path+'/'+vmname+'/'+vmname+'.qcow2'
                print command
		myparent=""
                a=commands.getstatusoutput(command)
		print a
		errormsg=errormsg+a[1]


            if(ifValidVM(req.cloneparentname)):
                template = db(db.template.id == origvm.templateid).select()[0]
                origvm=db(db.vm.name==req.cloneparentname).select()[0]
                template_loc=getconstant('vmfiles_path')+getconstant('datastore_int')+origvm.datastore.name+'/'+origvm.name +"/"+origvm.name+".qcow2"
                print "Netapp Copy and Move in progress"
                command='sudo ssh '+datastore.ip+' ndmpcopy -d -sa '+origvm.datastore.username+':'+origvm.datastore.password+' '+origvm.datastore.ip+':'+origvm.datastore.path+'/'+origvm.name+'/'+origvm.name+'.qcow2 '+datastore.path+'/'+getconstant("templates_dir")+'/tmp'
                print command
		myparent=origvm.name
                a=commands.getstatusoutput(command)
		print a
		errormsg=errormsg+a[1]
                command='sudo ssh '+datastore.ip+' mv '+datastore.path+'/'+getconstant("templates_dir")+'/tmp/'+origvm.name+'.qcow2 '+datastore.path+'/'+vmname+'/'+vmname+'.qcow2'
                a=commands.getstatusoutput(command)
		print a
		errormsg=errormsg+a[1]

            (ram,vcpus)=computeeffres(req.RAM,req.vCPUs,3)
            optional = ' --import --os-type='+ template.ostype
            if(template.arch!='amd64'):optional = optional+' --arch='+template.arch+' '
            install_cmd = 'virt-install \
                    --name=' + vmname + ' \
                    --ram=' + str(ram) + ' \
                    --vcpus='+str(vcpus)+optional+' \
                    --disk path=' + vm_loc+',bus=virtio \
                    --network bridge=br0,model=virtio,mac='+newmac+' \
                    --graphics vnc,port='+vncport+',listen=0.0.0.0,password=iitdcloud \
                    --noautoconsole \
                    --description \
                    --force'

            print "Installation started"
            print "Host is "+machine.ip
            print install_cmd
            out = commands.getstatusoutput("sudo ssh "+machine.ip+" "+install_cmd)
            print out
	    errormsg=errormsg+out[1]
            print "Check if VM has been successfully created"
            if (checkifvmisdefined(machine.ip,vmname)):
                faculty=db(db.auth_user.username == req.faculty).select(db.auth_user.id)[0]['id']
                db.vm.insert( \
                  userid=faculty, \
                  name=req.vmname, \
                  RAM=req.RAM, \
                  HDD=int(req.HDD)+int(template.hdd), \
                  hostid=machine.id, \
                  datastore=datastore.id, \
                  definedon=machine.id, \
                  mac=newmac,ip=newip,sport=vncport, \
                  laststarttime=currenttime(), \
                  templateid=template, \
                  runlevel=3, \
                  lastrunlevel=3, \
                  vCPU=req.vCPUs, \
		  cloneparentname=myparent, \
                  purpose=req.purpose, \
                  expire_date=req.expire_date)
                vm=db(db.vm.name==req.vmname).select(db.vm.id)[0]
                db.vmaccpermissions.insert(userid=req.userid, vmid=vm.id)
                faculty=None
                if(req.faculty!=None and req.faculty!=""):
                    faculty=db(db.auth_user.username==req.faculty).select()[0]
                    if(faculty.id != req.userid):
                        db.vmaccpermissions.insert(userid=faculty.id, vmid=vm.id)
                    faculty=faculty.username
                if(int(req.HDD)!=0):
                    attachdisk(req.vmname,int(req.HDD))
                    vmid=db(db.vm.name==req.vmname).select(db.vm.id)[0].id
                    db.attacheddisks.insert(vmname=vmid,size=int(req.HDD))
                user_id = req.userid
                vm_name = req.vmname
                count = db(db.host.id == machine.id).select(db.host.vmcount)[0].vmcount
                send_confirmation_email(user_id,faculty,vm_name)
                db(db.host.id==machine.id).update(vmcount=count+1)
                db.logs_request.insert( vmname=req.vmname, userid = req.userid, RAM = req.RAM, expire_date=req.expire_date, HDD = req.HDD, vCPUs = req.vCPUs, templateid = req.templateid, status = 1, \
                purpose = req.purpose, faculty = req.faculty)
                db(db.request.id==req.id).delete()
                 
                vmid=db(db.vm.name == req.vmname).select()[0]['id']
                db(db.queue.id==pid).update(status=1,vm=vmid,ftime=putdate())
                db(db.datastores.id==datastore.id).update(used=int(datastore.used)+int(req.HDD)+int(template.hdd))
            else: 
                db(db.queue.id==pid).update(status=-1,comments="Some Problem occured while executing "+install_cmd+" on host "+machine.ip+" FULL LOG: "+errormsg,ftime=putdate())
        else:
            db(db.queue.id==pid).update(status=-1,comments="VM with same name already exists"+" FULL LOG: "+errormsg,ftime=putdate())
    except :
        import traceback
        etype, value, tb = sys.exc_info()
        msg=''.join(traceback.format_exception(etype, value, tb, 10))
        db(db.queue.id==pid).update(status=-1,comments=msg,ftime=putdate())
