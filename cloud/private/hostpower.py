import time,sys,commands
i=0
while True:
    db.commit()
    try :
        print commands.getstatusoutput('date')[1]
        print "\nChecking Required no. of hosts\n-------------------------------------"
        hostpoweroperation()
        print "\nSanity check for host status in database\n-----------------------------------------"
        hoststatussanitycheck()
        db.commit()
        time.sleep(10)
        if i%15==0:
            print "Running recover_undefined()\n"
            recover_undefined()
        i=i+1
    except :
        import traceback
        etype, value, tb = sys.exc_info()
        msg=''.join(traceback.format_exception(etype, value, tb, 10))
        print msg
        time.sleep(10)
