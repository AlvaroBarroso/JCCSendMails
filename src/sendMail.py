import smtplib, imaplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import make_msgid
from email.message import EmailMessage
from email.headerregistry import Address
from enum import Enum
import json

class ContactType(Enum):
    PERSONAL = 1
    LISTA = 2

class Contact:
    def __init__(self, email , name, emailType):
        self.name = name
        self.email = email
        self.emailType = emailType

def getVariables():
    with open('parameters.json') as parametersFile:
        VARIABLES = json.load(parametersFile)
    return VARIABLES

def getContactFromLine(line,contactsType):
    splitted = line.split(' ')
    if(len(splitted)==1):
        return Contact(splitted[0], None, contactsType)
    if(len(splitted)==2):
        return Contact(splitted[0],splitted[1],contactsType)
    if(len(splitted)==3):
        return Contact(splitted[0], (splitted[1] + ' ' + splitted[2]),contactsType)
    print ("No se pudo parsear linea del contacto")  

def getPersonalContactList():
    with open(VARIABLES['personalContactFilePath'],'r') as personalContactFilePath:
        lines = personalContactFilePath.read().splitlines()
    contacts = []
    for line in lines:
        contacts.append(getContactFromLine(line,ContactType.PERSONAL))
    return contacts
    
def getListaContactList():
    with open(VARIABLES['listaContactFilePath'],'r') as listaContactFilePath:
        lines = listaContactFilePath.read().splitlines()
    contacts = []
    for line in lines:
        contacts.append(getContactFromLine(line,ContactType.LISTA))
    return contacts

def getMailTemplate(typeMail):
    path = ''
    if(typeMail == ContactType.PERSONAL):
        path = VARIABLES['personalMailContentFilePath']
    if(typeMail == ContactType.LISTA):
        path = VARIABLES['listaMailContentFilePath']
    with open(path,'r') as mailContent:
        return mailContent.read()
    return None
    
def sendEmailStartSession():
    try:
        senderAddress = VARIABLES['email']
        senderPassword = VARIABLES['email_password']
        print("Intentando crear session con el host")
        session = smtplib.SMTP("fceia.unr.edu.ar", 25) #use gmail with port

        print("Intentando logear")
        session.login(senderAddress,senderPassword) #login with mail_id and password
        print("Conectado al mail")
        return session
    except ValueError:
        print("Error inicializando la session")
        print(ValueError)
        return None

def sendMailEndSession(session):
    try:
        print("cerrando la session")
        session.quit()
        print("session cerrada")
    except ValueError:
        print("Error al cerrar la session")
        print(ValueError)

def sendMail(session,subject, finalMimeContent,receiverAddress):
    try:
        senderAddress = VARIABLES['email']
        senderAlias = VARIABLES['email_alias']
        message            = EmailMessage()
        message['From']    = Address(senderAlias,"jcc","fceia.unr.edu.ar")
        message['To']      = receiverAddress
        message['Subject'] = subject   #The subject line

        message.set_content(finalMimeContent)
        message.add_alternative(finalMimeContent,subtype='html')
        message.get_payload()[1].add_related(banner,'image','png',cid=imgFooterCid)
        
        text = message.as_string()
        session.sendmail(senderAddress, receiverAddress, text)

        print('Mail to {email} sended'.format(email=receiverAddress))
    except ValueError:
        print("Error al enviar el mail.")
        print(senderAddress)
        print(receiverAddress)
        print(ValueError)

def setFinalMimeContent(mailTemplate,contact):
    try:

        if(contact.emailType == ContactType.PERSONAL):
            if(contact.name!=None):
                mailTemplate = mailTemplate.format(ourName='Alvaro Barroso',theirName=' '+contact.name,imgFooterCid=imgFooterCid[1:-1])
            else:
                mailTemplate = mailTemplate.format(ourName='Alvaro Barroso',theirName='',imgFooterCid=imgFooterCid[1:-1])

        if(contact.emailType == ContactType.LISTA):
            mailTemplate = mailListaTemplate.format(imgFooterCid=imgFooterCid[1:-1]   )
            pass 
        finalMimeContent = mailTemplate

        return finalMimeContent

    except ValueError:
        print("Error setting final mime content")
        print(ValueError)

VARIABLES = getVariables()

personalContactList = getPersonalContactList()
listaContactList    = getListaContactList()

mailPersonalTemplate = getMailTemplate(ContactType.PERSONAL)
mailListaTemplate    = getMailTemplate(ContactType.LISTA)

banner = open('src/testjcc9.png','rb').read()
subject = 'JCC 2020' #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

session = sendEmailStartSession()
imgFooterCid = make_msgid()

for i,contact in enumerate(personalContactList):
    print("Personal mail {} de {}".format(i+1,len(personalContactList)))
    finalMimeContent = setFinalMimeContent(mailPersonalTemplate,contact)
    sendMail(session,subject,finalMimeContent,contact.email)

for i,contact in enumerate(listaContactList):
    print("Lista mail {} de {}".format(i+1,len(listaContactList)))
    finalMimeContent = setFinalMimeContent(mailListaTemplate,contact)
    sendMail(session,subject,finalMimeContent,contact.email)

sendMailEndSession(session)


# def runn():
#     exec(open('src/sendMail.py').read())