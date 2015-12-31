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

def notify_error(subject,email_txt):
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