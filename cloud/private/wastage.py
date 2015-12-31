#Calculates the wastage of CPU,RAM by all the vms
def wastagecompu():
    import commands
    #logfile='/var/log/baadal/datadump.log'
    livehosts=db(db.host.status==1).select()
    print commands.getstatusoutput("date")[1]
    try:
        for host in livehosts:
            vms=db(db.vm.hostid==host.id).select()
            for vm in vms:
                result=commands.getstatusoutput("/usr/bin/rrdtool fetch -r 300 -s -1h /var/www/cloudrrd1/Akumar-001.rrd AVERAGE| /bin/grep -v nan | /bin/grep -v cpu | /bin/grep -v \"^\$\" | /usr/bin/awk -f /root/nck/mail.pl")
                print "HOSTIP:"+host.ip+" NAME:"+vm.name+result[1]
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Some Error Occured\n"+msg
    return
wastagecompu()
