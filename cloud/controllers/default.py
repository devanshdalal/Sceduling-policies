# -*- coding: utf-8 -*-     
def user():
    """
    exposes:
    http://..../[app]/default/user/login 
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

def error():
    users=""
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
    for i in range(0,len(admins)-1):
        users+=admins[i]+"-"
    users+=admins[len(admins)-1]
    return dict(users=users)
    
#regex check function for new vm name
import re
def vmname_regexchk(strg, search=re.compile(r'[^a-z0-9A-Z_]').search):
    return not bool(search(strg))

def set_RAM_CPU(form):
    try:
        cpu_ram = {'1 CPU, 1GB RAM, 40GB HDD'     :   [1,1],
            '1 CPU, 2GB RAM, 40GB HDD'     :   [1,2],
            '2 CPU, 2GB RAM, 40GB HDD'     :   [2,2],
            '2 CPU, 4GB RAM, 40GB HDD'     :   [2,4],
            '4 CPU, 4GB RAM, 40GB HDD'     :   [4,4],
            '4 CPU, 8GB RAM, 40GB HDD'     :   [4,8],
            '8 CPU, 8GB RAM, 40GB HDD'     :   [8,8],
            '8 CPU, 16GB RAM, 40GB HDD'    :   [8,16]}
        form.vars.RAM = int(cpu_ram[form.vars.config][1])*1024
        form.vars.vCPUs = int(cpu_ram[form.vars.config][0])
        if(form.vars.RAM>8197):form.errors.RAM="RAM size should be in range"
        if(form.vars.vCPUs>8):form.errors.RAM="No. of CPU should be in range"
        if(not vmname_regexchk(form.vars.vmname)):form.errors.vmname="VM name should contain only a-zA-Z0-9_"
        return
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))

@auth.requires_login()
def request_vm_template():
    help_text=db(db.help.token=="request_vm_template").select(db.help.text)[0]['text']
    form_fields = ['vmname','config','HDD','templateid','purpose','expire_date']
    form_labels = {'vmname':'Name of VM','config':'Configuration','HDD':'Optional Additional Harddisk(GB)','templateid':'Template Image','purpose':'Purpose of this VM','expire_date':'Timeline till when VM is required'}
    # Add approver field to form if user is not faculty or moderator
    if not isModerator(auth.user.username) and not isFaculty(auth.user.username):
        form_fields += ['faculty']
        form_labels['faculty'] = 'Faculty Approver LDAP Username'
    form = SQLFORM(db.request, fields = form_fields, labels = form_labels)
    form.vars.userid = auth.user.id
    
    if isModerator(auth.user.username):
        form.vars.status = 1 
        form.vars.faculty = auth.user.username
    elif isFaculty(auth.user.username):
        form.vars.status = 1
        form.vars.faculty = auth.user.username
    else:
        form.vars.status = 0
    if form.accepts(request.vars,session, onvalidation=set_RAM_CPU):
        session.flash = 'VM creation request waiting for approval'
        redirect(URL(c='default', f='index'))
    else :
       session.flash = 'Error in form'
       return dict(form=form,help_text=help_text)

@auth.requires_login()
def request_clonevm():
    help_text="Select appropriate configuration."
    form_fields = ['vmname','config','HDD','purpose','expire_date']
    form_labels = {'vmname':'Name of VM','HDD':'No. of Clones','config':'Configuration','HDD':'Optional Additional Harddisk(GB)','purpose':'Purpose of this VM','expire_date':'Timeline till when VM is required'}
    form_labels = {'vmname':'Name of VM','HDD':'No. of Clones','config':'Configuration','purpose':'Purpose of this VM','expire_date':'Timeline till when VM is required'}
    # Add approver field to form if user is not faculty or moderator
    if not isModerator(auth.user.username) and not isFaculty(auth.user.username):
        form_fields += ['faculty']
        form_labels['faculty'] = 'Faculty Approver LDAP Username'
    form = SQLFORM(db.request, fields = form_fields, labels = form_labels)
    form.vars.userid = auth.user.id
    form.vars.cloneparentname=request.args[0]
    if isModerator(auth.user.username):
        form.vars.status = 1
        form.vars.faculty = auth.user.username
    elif isFaculty(auth.user.username):
        form.vars.status = 1
        form.vars.faculty = auth.user.username
    else:
        form.vars.status = 0
    if form.accepts(request.vars,session, onvalidation=set_RAM_CPU):
        session.flash = 'VM creation request waiting for approval'
        redirect(URL(c='default', f='index'))
    else :
       session.flash = 'Error in form'
       return dict(form=form,help_text=help_text,vmname=request.args[0])

def index():
    if auth.user!=None:
        if getconstant("ifbaadaldown")=="1":
            if not ifModerator(auth.user.username):
                redirect(URL(r=request,c='default', f='user/logout'))
            else:
                response.flash="Baadal is in Maintenance Mode"
    return dict(request=request)

@cache('about')
def about():
   return response.render()

@cache('documentation')
def documentation():
    try:
        return response.render()
    except:
        import sys, traceback
        etype, value, tb = sys.exc_info()
        msg = ''.join(traceback.format_exception(etype, value, tb, 10))
        session.flash=msg
        redirect(URL(c='default', f='error'))

def dummy():
    return dict(a="Dummy")
