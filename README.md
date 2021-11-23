# ispbackup
Desenvolvi este código para fazer backup de OLT Fiberhome e Switch Huawei em massa, consumindo informações do Zabbix via JSON


Parâmetros necessários para funcionamento.


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
