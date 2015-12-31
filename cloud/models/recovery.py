def recover():
    import libvirt, string,commands
    vmcheck=[]
    hosts=db(db.host.id>=0).select()
    for host in hosts:
        #Establish a read only remote connection to libvirtd
        #find out all domains running and not running
        #Since it might result in an error add an exception handler
        print "working on "+host.name
        conn = libvirt.openReadOnly('qemu+ssh://root@'+host.ip+'/system')
        domains=[]
        ids = conn.listDomainsID()
        for id in ids:
            #print conn.lookupByID(id)
            domains.append(conn.lookupByID(id))
        names = conn.listDefinedDomains()
        for name in names:
            #print conn.lookupByName(name)
            domains.append(conn.lookupByName(name))
        for dom in domains:
            print "working on VM="+dom.name()
            name = dom.name()
            request=db(db.logs_request.vmname==name).select()[0]
            user=request.faculty
            if user==None:userid=request.userid
            else:userid=db(db.auth_user.username==user).select(db.auth_user.id)[0]
            hostid=host.id
            definedon=host.id
            RAM=request.RAM
            vCPU=request.vCPUs
            HDD=request.HDD
            templateid=request.templateid
            mac=str(commands.getstatusoutput("ssh root@"+host.ip+" virsh dumpxml "+name+" |grep 'mac address'|awk -F \"'\" '{print $2}'")[1])
            print mac
            ip=str("10.17."+str(int(mac.split(":")[4])+1)+"."+str(int(mac.split(":")[5])))
            print ip
            dsname=commands.getstatusoutput("ssh root@"+host.ip+" virsh dumpxml "+name+" |grep 'source file'|awk -F '\/' '{print $3}'")[1].split("_")[1]
            print dsname
            if(dsname=="kvm1"):datastore=1
            else: datastore=2
            print datastore
            #datastore=db(db.datastores.name==str(dsname.strip())).select(db.datastores.id)[0]
            purpose=request.purpose
            expire_date=request.expire_date
            sport=commands.getstatusoutput("ssh root@"+host.ip+" virsh dumpxml "+name+" |grep 'graphics'|awk -F \"'\" '{print $4}'")[1]
            cloneparentname=request.cloneparentname
            locked=0
            totalcost=0
            laststarttime=str(currenttime())
            lastrunlevel=3
            cpuused=dom.info()[3]
            if((int(vCPU)/cpuused)==1):nextrunlevel=1
            elif((int(vCPU)/cpuused)==2):nextrunlevel=2
            elif((int(vCPU)/cpuused)==4):nextrunlevel=3
            if(dom.info()[0]==1):runlevel=nextrunlevel
            else: runlevel=0
            db.vm.insert(name=name,userid=userid,hostid=hostid,RAM=RAM,vCPU=vCPU,HDD=HDD,templateid=templateid,ip=ip,mac=mac,datastore=datastore,purpose=purpose,expire_date=expire_date,sport=sport,cloneparentname=cloneparentname,locked=locked,totalcost=0,laststarttime=laststarttime,lastrunlevel=lastrunlevel,runlevel=runlevel,nextrunlevel=nextrunlevel)
            dom=""
        conn.close()
