#Simple max function
def max(a, b):
    if(a>b): return a
    else: return b

#Calculates the wastage of CPU,RAM by all the vms
def wastagecompu():
    import commands
    try:
        vms=db(db.vm.id>=0).select()
        for vm in vms:
            print "Wastage: "+vm.name
            outd=commands.getstatusoutput("/usr/bin/rrdtool fetch -r 300 -s -24h /var/www/cloudrrd1/"+vm.name+".rrd AVERAGE| /bin/grep -v nan | /bin/grep -v cpu | /bin/grep -v \"^\$\" | /usr/bin/awk -f /var/www/mail.pl |grep -v NR| sed 's/\([^0-9./]\+\)/ /g' | sed 's/\/\([ ]\+\)/\//g'")[1]
            outw=commands.getstatusoutput("/usr/bin/rrdtool fetch -r 300 -s -168h /var/www/cloudrrd1/"+vm.name+".rrd AVERAGE| /bin/grep -v nan | /bin/grep -v cpu | /bin/grep -v \"^\$\" | /usr/bin/awk -f /var/www/mail.pl |grep -v NR| sed 's/\([^0-9./]\+\)/ /g' | sed 's/\/\([ ]\+\)/\//g'")[1]
            outm=commands.getstatusoutput("/usr/bin/rrdtool fetch -r 18000 -s -720h /var/www/cloudrrd1/"+vm.name+".rrd AVERAGE| /bin/grep -v nan | /bin/grep -v cpu | /bin/grep -v \"^\$\" | /usr/bin/awk -f /var/www/mail.pl |grep -v NR| sed 's/\([^0-9./]\+\)/ /g' | sed 's/\/\([ ]\+\)/\//g'")[1]
            outy=commands.getstatusoutput("/usr/bin/rrdtool fetch -r 108000 -s -8640h /var/www/cloudrrd1/"+vm.name+".rrd AVERAGE| /bin/grep -v nan | /bin/grep -v cpu | /bin/grep -v \"^\$\" | /usr/bin/awk -f /var/www/mail.pl |grep -v NR| sed 's/\([^0-9./]\+\)/ /g' | sed 's/\/\([ ]\+\)/\//g'")[1]
            #If unable to get wastage values, keep them 101=ERROR
            (dcpu,dcpuf,dram,dramf,dtime,wcpu,wcpuf,wram,wramf,wtime,mcpu,mcpuf,mram,mramf,mtime,ycpu,ycpuf,yram,yramf,ytime)=(101,1,101,1,0,101,1,101,1,0,101,1,101,1,0,101,1,101,1,0)
            
            if not (outd.find('ERROR')>=0 or outd.find('fatal')>=0):
                if(outd.strip()==""):(dcpu,dcpuf,dram,dramf,dtime)=(0,0,0,0,0)
                else:
                    outd=outd.split()
                    (dcpu,dcpuf,dram,dramf,dtime)=(max(0,100-float(outd[0])),outd[1],max(0,100-float(outd[2])),outd[3],float(outd[4]))

            if not (outw.find('ERROR')>=0 or outw.find('fatal')>=0):
                if(outw.strip()==""):(wcpu,wcpuf,wram,wramf,wtime)=(0,0,0,0,0)
                else:
                    outw=outw.split()
                    (wcpu,wcpuf,wram,wramf,wtime)=(max(0,100-float(outw[0])),outw[1],max(0,100-float(outw[2])),outw[3],float(outw[4]))

            if not (outm.find('ERROR')>=0 or outm.find('fatal')>=0):
                if(outm.strip()==""):(mcpu,mcpuf,mram,mramf,mtime)=(0,0,0,0,0)
                else:
                    outm=outm.split()
                    (mcpu,mcpuf,mram,mramf,mtime)=(max(0,100-float(outm[0])),outm[1],max(0,100-float(outm[2])),outm[3],float(outm[4]))

            if not (outy.find('ERROR')>=0 or outy.find('fatal')>=0):
                if(outy.strip()==""):(ycpu,ycpuf,yram,yramf,ytime)=(0,0,0,0,0)
                else:
                    outy=outy.split()
                    (ycpu,ycpuf,yram,yramf,ytime)=(max(0,100-float(outy[0])),outy[1],max(0,100-float(outy[2])),outy[3],float(outy[4]))
            if(len(db(db.wastage.vm==vm.name).select())==1):
                db(db.wastage.vm==vm.name).update(dcpu=dcpu,dcpuf=dcpuf,dram=dram,dramf=dramf,dtime=dtime,wcpu=wcpu,wcpuf=wcpuf,wram=wram,wramf=wramf,wtime=wtime,mcpu=mcpu,mcpuf=mcpuf,mram=mram,mramf=mramf,mtime=mtime,ycpu=ycpu,ycpuf=ycpuf,yram=yram,yramf=yramf,ytime=ytime)
            else: db.wastage.insert(vm=vm.name,dcpu=dcpu,dcpuf=dcpuf,dram=dram,dramf=dramf,dtime=dtime,wcpu=wcpu,wcpuf=wcpuf,wram=wram,wramf=wramf,wtime=wtime,mcpu=mcpu,mcpuf=mcpuf,mram=mram,mramf=mramf,mtime=mtime,ycpu=ycpu,ycpuf=ycpuf,yram=yram,yramf=yramf,ytime=ytime)

    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Some Error Occured\n"+msg
    return
