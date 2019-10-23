import requests
from flask import current_app

# Email Configuration Options:
company_name = current_app.config['APP_NAME']
company_address = ""
company_logo_url = current_app.config['APP_LOGO_URL']
company_link = current_app.config['APP_URL']
unsubscribe_link = '%unsubscribe_url%'

# API
API_ENDPOINT = current_app.config['API_ENDPOINT']

# Mailer Configuration:

MAILER_NAME = current_app.config['MAILER_NAME']
MAILER_ADDRESS = current_app.config['MAILER_ADDRESS']
# Full Mailing Address:
MAILING_ADDRESS = MAILER_NAME + " <" + MAILER_ADDRESS + ">"

# Mailer API Key
MAILGUN_API_KEY = current_app.config['MAILGUN_API_KEY']
MAILGUN_MESSAGES_ENDPOINT = current_app.config['MAILGUN_MESSAGES_ENDPOINT']


def get_email_template():
    return open('lib/email_template.html', 'r').read()


def sender(to_address, subject, email_content, from_address=MAILING_ADDRESS):
	return requests.post(MAILGUN_MESSAGES_ENDPOINT,
		auth=("api", MAILGUN_API_KEY),
		data={"from": from_address, "to": [to_address], "subject": subject, "html": email_content})


def create_email_template(address, options, email_title, button_text, preheader, email_text, email_text_2=None):
    email_content = get_email_template()

    # To Replace:
    user_name = options.get('name', None)
    token = options.get('token', None)

    # Replace user's name:
    if user_name:
        email_content = email_content.replace('{_USER_NAME_}', " " + user_name)
    else:
        email_content = email_content.replace('{_USER_NAME_}', "")
    
    # If email_text_2 exists (optional text)
    if email_text_2:
        email_content = email_content.replace('{_CTA_PARAGRAPH_2_}', email_text_2)
    else:
        email_content = email_content.replace('{_CTA_PARAGRAPH_2_}', "")
    
    # Preheader:
    email_content = email_content.replace('{_PREHEADER_}', preheader)
    
    # Company Details
    email_content = email_content.replace('{_COMPANY_LOGO_URL_}', company_logo_url)
    email_content = email_content.replace('{_COMPANY_NAME_}', company_name)
    email_content = email_content.replace('{_COMPANY_ADDRESS_}', company_address)
    email_content = email_content.replace('{_COMPANY_LINK_}', company_link)
    
    # The button and link for the email:
    email_content = email_content.replace('{_CTA_LINK_}', API_ENDPOINT + token)
    email_content = email_content.replace('{_CTA_NAME_}', button_text)
    email_content = email_content.replace('{_CTA_PARAGRAPH_1_}', email_text)
    
    # A unsubscribe link, good to include it!
    email_content = email_content.replace('{_UNSUBSCRIBE_LINK_}', unsubscribe_link)
    
    # Send the email
    sender(address, email_title, email_content)


def verification_email(address, options):   
    title = "Verify Email Address"
    button = "Verify Email Address"
    preheader = "Please verify your email address."
    email_text = f"Welcome to {company_name}, it is a pleasure to have you on board! <br /><br /> Click the button below to verify your email address:"

    create_email_template(address, options, title, button, preheader, email_text, None)


def recovery_email(address, options):
    title = 'Reset Your Password'
    button = "Change Your Password"
    preheader = "Please change your password."
    email_text = "It seems you have requested a password change! Click the button below to proceed:"
    email_text_2 = "If this was NOT requested by you, kindly ignore this email. Thank you!"

    create_email_template(address, options, title, button, preheader, email_text, email_text_2)


def send_email(address, options, type_of_email):
	if type_of_email == "verification":
		verification_email(address, options)
	elif type_of_email == "recovery":
		recovery_email(address, options)
