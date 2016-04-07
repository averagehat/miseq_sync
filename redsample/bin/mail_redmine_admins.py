#!/usr/bin/env python

import smtplib
from email.mime.text import MIMEText

import sys
import argparse

from redsample import redminerest, defaults

def main( args ):
    admin_emails = get_admin_emails()
    subject = '{} has system updates that need to be applied'.format(defaults['URL'])
    message = 'Nothing for now'
    mail_message( admin_emails, subject, message, defaults['EMAIL_ADDRESS'], defaults['EMAIL_PASSWORD'] )

def get_admin_emails( ):
    admins = get_admins()
    return [a['mail'] for a in admins]

def get_admins( ):
    rest = redminerest.RedmineREST( defaults['URL'], defaults['KEY'] )
    url = rest.url + '/users.json?group_id={}'.format(defaults['SYSADMIN_GROUP_ID'])
    admins = rest.do_get_request( url )['users']
    return admins

def mail_message( toaddrs, subject, message, guser, gpassword ):
    GMAIL_SMTP = 'smtp.gmail.com:587'
    FROM_ADDR = guser

    sender = toaddrs[0]
    recipients = toaddrs

    msg = MIMEText( message )
    msg['Subject'] = subject
    msg['From'] = FROM_ADDR
    msg['To'] = ", ".join(recipients)

    server = smtplib.SMTP( GMAIL_SMTP )
    server.starttls()
    server.login( guser, gpassword )
    server.sendmail( FROM_ADDR, recipients, msg.as_string() )

def parse_args( args=sys.argv[1:] ):
    parser = argparse.ArgumentParser()

    return parser.parse_args( args )

if __name__ == '__main__':
    main(parse_args())
