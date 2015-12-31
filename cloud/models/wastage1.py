#Calculates the wastage of CPU,RAM by all the vms
def wastagecompu1():
    import commands
    livehosts=db(db.host.status==1).select()
    #logfile='/var/log/baadal/utilization.log'
    try:
        for host in livehosts:
            print "\nChecking vms on host "+str(host.ip)+"\n================================\n"
            vms=db(db.vm.hostid==host.id).select()
            for vm in vms:
                result=commands.getstatusoutput("/usr/bin/rrdtool fetch /var/www/cloudrrd1/"+vm.name+".rrd AVERAGE| /bin/grep -v nan | /bin/grep -v cpu | /bin/grep -v \"^\$\" | /usr/bin/awk -f /root/nck/mail.pl")
                print "Wastage by "+vm.name+": "+result[1]
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        print "Some Error Occured\n"+msg
    return
