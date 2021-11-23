
import requests
import sys
import os
import re

from datetime import datetime
import telnetlib
import ftplib


#
# Credenciais para backup dos switches
#
SW_FTP_ADDRESS  = "1.1.1.1"
SW_FTP_PASSWORD = "username"
SW_FTP_USERNAME = "password"

#
# Credenciais para backup dos OLTs
#
OLT_FTP_ADDRESS = "1.1.1.1"
OLT_FTP_PASSWORD= "username"
OLT_FTP_USERNAME= "password"

#
# Credenciais para consumir JSON do Zabbix 
#
ZABBIX_API_URL  = "http://zbxaddress/zabbix/api_jsonrpc.php"
UNAME           = "zabbix-user" 
PWORD           = "zabbix-pwd"

#
# Credenciais para acesso a OLT 
#
DEFAULT_OLT_USR = "GEPON"
DEFAULT_OLT_PWD = "olt-password"


#
# Credenciais para acesso a OLT user enable 
#
DEFAULT_OLT_EN = "EN"
DEFAULT_OLT_ENPWD = "olt-passwd"
SHOW_DEBUG      = 0

#
# Credenciais usuario no switch com permissoes FTP 
#
DEFAULT_SW_USR = "username"
DEFAULT_SW_PWD = "passwd"



class Backup:

    def __init__(self):

        Query = requests.post(ZABBIX_API_URL,
                        json={
                            "jsonrpc": "2.0",
                            "method": "user.login",
                            "params": 
                            {
                                "user": UNAME,
                                "password": PWORD
                            },
                            "id": 1
                        })
        Query.json()
        self.AUTHTOKEN = Query.json()["result"]

        self.getDateFile = datetime.now().strftime("%d%m%Y%H%M%S")

        if(SHOW_DEBUG):
            print("(Backup) Feito Login no ZBX (TOKEN: {})". 
                                                format(self.AUTHTOKEN))

    def __del__(self):

        Query = requests.post(ZABBIX_API_URL,
                            json={
                                "jsonrpc": "2.0",
                                "method": "user.logout",
                                "params": {},
                                "id": 2,
                                "auth": self.AUTHTOKEN
                            })

        if(SHOW_DEBUG):
            print("(Backup) Feito Logout no ZBX (TOKEN: {})". 
                                                format(self.AUTHTOKEN))

    def getgroupidbyname(self, name):
        Query = requests.post(ZABBIX_API_URL,
                            json={
                                "jsonrpc": "2.0",
                                "method": "hostgroup.get",
                                "params": {
                                    "output": [ "groupid"],
                                    "filter":{
                                        "name":[str(name)],
                                        "selectInterfaces": ["groupid"]
                                        }
                                },
                                "id": 2,
                                "auth": self.AUTHTOKEN
                                })
        return Query.json()['result'][0]['groupid']

    def getmaxhosts(self, groupid):
        Query = requests.post(ZABBIX_API_URL,
                            json={
                                "jsonrpc": "2.0",
                                "method": "host.get",
                                "params": 
                                {
                                    "countOutput": 'true',
                                    "groupids":[str(groupid)]
                                },
                                "id": 2,
                                "auth": self.AUTHTOKEN
                                })

        TotalOlts = int(Query.json()['result'])-1

        if(SHOW_DEBUG):
            print("(OLT) Quantidade de OLTS Cadastradas no ZBX: {}".
                                                format(TotalOlts))
        
        return int(TotalOlts)


    def gethosts(self, groupid):
        if(SHOW_DEBUG):
            self.getmaxhosts(groupid)

        Query = requests.post(ZABBIX_API_URL,
                        json={
                            "jsonrpc": "2.0",
                            "method": "host.get",
                            "params": {
                                    "output": ["name","description"],
                                    "selectInterfaces": ["name", "ip"],
                                    "groupids":[str(groupid)]
                            },
                            "id": 2,
                            "auth": self.AUTHTOKEN
                        })

        return (Query.json())

    @staticmethod
    def getfiledate():
        getDate = datetime.now().strftime("%b%d%Y") #%d%m%Y%H%M%S
        return getDate
     

    def upload(devip, ipaddr, user, password, name, filename):

        try:

            
            ___str = "{}-{}-{}.{}". format(name, devip, 
                        Backup.getfiledate(), (filename.split(".")[1]))

            ftp = ftplib.FTP(ipaddr)
            ftp.login (user, password)
            fin = open ('/root/zbxapi/tmpfiles/' + filename, 'rb')
            ftp.storbinary (('STOR {}'. format(___str)), fin)
            file = open('/root/zbxapi/tmpfiles/' + filename,'rb')      
            fin.close()                         
            ftp.quit()
            
            print("(Backup) Enviando arquivo {} para o FTP!". 
                                    format(___str))
            os.remove(filename)
            return 1
        except Exception as e:
            print("(Backup)Erro: {}{}". format(filename,e))
            return 0
 

class OLT:
    def __init__(self, ipaddr, nomeolt):
        self.oltaddr = ipaddr
        self.filename = nomeolt
        pass

    def login(self):
        if(SHOW_DEBUG):
            print("(OLT) Tentando realizar Login na OLT {}". 
                                                    format(self.oltaddr))
        try:
            self.acessa_olt = telnetlib.Telnet( 
                                        self.oltaddr, 23, timeout = 2)
        except Exception as e:
            print("OLT-Erro: {}".format(e))
            sys.exit("nao acessou telnet: {}".format(e))
        
        self.acessa_olt.read_until(b"Login:", timeout = 2)
        self.acessa_olt.write(("{}\n". format(DEFAULT_OLT_USR))
                                                    .encode('ascii'))
        self.acessa_olt.read_until(b"Password:", timeout = 2)
        self.acessa_olt.write(("{}\n". format(DEFAULT_OLT_PWD))
                                                    .encode('ascii'))
        self.acessa_olt.read_until(b"User", timeout = 2)
        self.acessa_olt.write(("terminal length 0\n")
                                                    .encode('ascii'))
        self.acessa_olt.read_until(b"#", timeout = 2)
        self.acessa_olt.write(("{}\n". format(DEFAULT_OLT_EN))
                                                    .encode('ascii'))
        self.acessa_olt.read_until(b"Password:", timeout = 2)
        self.acessa_olt.write(("{}\n".format(DEFAULT_OLT_ENPWD))
                                                    .encode('ascii'))

        if(str(self.acessa_olt.read_until(b"#", timeout = 2))
                                                    .find("#") != -1):
            if(SHOW_DEBUG):
                print("OLT-{}: Acessado OLT com sucesso!". 
                                                    format(self.oltaddr))

            self.oltstts = 1

        else:
            if(SHOW_DEBUG):
                print("OLT-{}: Erro ao acessar OLT". 
                                                    format(self.oltaddr))

            self.oltstts = 0
        
        return self.oltstts

    def backupolt(self, comment = ""):

        if(self.oltstts != 1):
            return 0

        if(SHOW_DEBUG):
            print("OLT: Iniciando Backup da OLT")

        try:
            # self.acessa_olt.write((iStr).encode('ascii'))
            self.acessa_olt.write("upload ftp config {} {} {} {}-{}.cfg\n". 
                        format(OLT_FTP_ADDRESS, OLT_FTP_USERNAME, 
                                OLT_FTP_PASSWORD, self.filename, 
                                    Backup.getfiledate()). 
                                        encode('ascii'))
        except EOFError as e:
            if(SHOW_DEBUG):
                print("OLT-{}: Erro fatal: {}". format(self.oltaddr, e))

        


        print("OLT-{}: Nome do arquivo de backup {}-{}.cfg".
                    format(self.oltaddr, self.filename,
                        Backup.getfiledate()))

    def logout(self):

        if(SHOW_DEBUG):
            print("OLT-{}: Feito logout na OLT com sucesso". 
                                                    format(self.oltaddr))
        self.acessa_olt.close()
        pass



class SW:
    def __init__(self, address, name):
        self.swaddr = address
        self.swname = name.replace(" ", "_")

        #
        self.swalive = 1

        if(SHOW_DEBUG):
            print("(SW){}: Nova instancia do SW iniciada". 
                                                    format(self.swaddr))
        pass

    def login(self):
        if(self.swalive != 1):
            return 0

       
        self.ftp = ftplib.FTP(self.swaddr)
        self.ftp.login(DEFAULT_SW_USR, DEFAULT_SW_PWD)

        if(SHOW_DEBUG):
            print("(SW){}: Feito login no SW!". format(self.swaddr))
        return 1

    def backup(self, filename = "vrpcfg.zip"):
        if(SHOW_DEBUG):
            print("(SW){}: Tentando backup para o FTP!". format(self.swaddr))

        try:
            self.ftp.retrbinary("RETR " + filename , 
                        open("/root/zbxapi/tmpfiles/" + filename, 'wb')
                                .write)

            if(Backup.upload(self.swaddr, SW_FTP_ADDRESS, SW_FTP_USERNAME, 
                                SW_FTP_PASSWORD, self.swname, filename)):
                print("(SW){}: Feito backup e enviado ao FTP". 
                                format(self.swaddr))
        except:
            print("(SW){}- Erro ao enviar backup!". format(self.swaddr))
            return 0

        return 1

    def logout(self):
        self.ftp.close()
        pass

if __name__ == "__main__":

    backup = Backup()

    #
    # - Backup de OLT Huawei
    #
    gHosts = backup.gethosts(backup.getgroupidbyname("fiberhome"))['result']
    
    x = 0
    while(x <= backup.getmaxhosts(backup.getgroupidbyname("fiberhome"))):
        
        olt = OLT(gHosts[x]['interfaces'][0]['ip'], gHosts[x]['name'])
        olt.login()
        olt.backupolt()
        olt.logout()

        x = (x + 1)


    #
    # - Backup de Switch Huawei
    #
    gHosts = backup.gethosts(backup.getgroupidbyname("Huawei"))['result']

    
    x = 0
    while(x <= backup.getmaxhosts(backup.getgroupidbyname("Huawei"))):

        sw = SW(gHosts[x]['interfaces'][0]['ip'], gHosts[x]['name'])
        sw.login()
        sw.backup(gHosts[x]['description'])
        sw.logout()
        
        x = (x + 1)

    del(backup)
