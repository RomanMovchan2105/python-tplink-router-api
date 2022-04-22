from environment import initConfig, config
from bs4 import BeautifulSoup
from requests.exceptions import HTTPError
import json
import requests
from flask import Flask, redirect
app = Flask(__name__)

# TODO: remove hardcode, parse script wlanStatusStringArray
wlanStatusStringArray = [
    "STA-AUTH",
    "STA-ASSOC",
    "WPA",
    "WPA-Personal",
    "WPA2",
    "WPA2-Personal",
    "802_1X",
    "STA-JOINED",
    "AP-UP",
    "AP-DOWN",
    "Disconnected"
]

initConfig()

router_ip = config.get('router.ip', '')

headersDefault = {
    'accept': '*/*',
    "Accept-language": "en-XA,en;q=0.9",
    "Authorization": config.get('authorization.basic'),
    "Cache-control": "no-cache",
    "Pragma": "no-cache",
    # set dynamic referer
    "Referer": config.get('router.ip', '') + "/userRpm/WlanStationRpm.htm",
}


@app.route("/")
def hello():
    return json.dumps("Hello World!")


def login():

    try:
        r = requests.get(router_ip, headers=headersDefault)
    except HTTPError as e:
        print(e.response.text)
        return e.response.text
    r.raise_for_status()

    if r.status_code == 200:
        x = 1
        while x < 3:
            try:
                session_id = r.text[r.text.index(
                    router_ip)+len(router_ip)+1:r.text.index('userRpm')-1]
                return session_id

            except ValueError:
                return 'Login error'

            x += 1
    else:
        return 'r.status_code'


@app.route("/routercontrol")
def routercontrol():
    return redirect('/routercontrol/active')


@app.route("/routercontrol/<operation>")
def routercontrolSlug(operation='active', remote_ip='255.255.255.255'):

    # Авторизация

    # if login()=='IP unreachable' or login()=='Login error':
    #     return login()
    #     exit(0)

    # else:
    #     session=login()
    #     print ('Login OK: '+session)

    # if operation=='Enable ports':

    #     #Открыть Port Forwarding
    #     r = requests.get(router_ip+'/'+session+'/userRpm/VirtualServerRpm.htm?doAll=EnAll&Page=1',headers={'Referer':router_ip+'/'+session+'/userRpm/VirtualServerRpm.htm','Cookie': auth_token})
    #     status=str(r.status_code)
    #     print (logout(session))
    #     return 'Enable all ports: '+status+' http://31.207.73.10:8082'

    # elif operation=='Disable ports':

    #     #Закрыть Port Forwarding
    #     r = requests.get(router_ip+'/'+session+'/userRpm/VirtualServerRpm.htm?doAll=DisAll&Page=1',headers={'Referer':router_ip+'/'+session+'/userRpm/VirtualServerRpm.htm','Cookie': auth_token})
    #     status=str(r.status_code)
    #     print (logout(session))
    #     return 'Disable all ports: '+status

    # elif operation=='Reboot':

    #     #Перезагрузка
    #     r = requests.get(router_ip+'/'+session+'/userRpm/SysRebootRpm.htm?Reboot=%D0%9F%D0%B5%D1%80%D0%B5%D0%B7%D0%B0%D0%B3%D1%80%D1%83%D0%B7%D0%B8%D1%82%D1%8C',headers={'Referer':router_ip+'/'+session+'/userRpm/SysRebootRpm.htm','Cookie': auth_token})
    #     status=str(r.status_code)
    #     print (logout(session))
    #     return 'Reboot: '+status

    # elif operation=='Remote IP':

    #     #Задание IP адреса удаленного управления
    #     r = requests.get(router_ip+'/'+session+'/userRpm/ManageControlRpm.htm?port=5110&ip='+remote_ip+'&Save=%D0%A1%D0%BE%D1%85%D1%80%D0%B0%D0%BD%D0%B8%D1%82%D1%8C',headers={'Referer':router_ip+'/'+session+'/userRpm/SysRebootRpm.htm','Cookie': auth_token})
    #     status=str(r.status_code)
    #     print (logout(session))
    #     return 'Remote IP '+remote_ip+': '+status

    if operation == 'active':

        # Определение подключенных устройств
        r = requests.get(
            router_ip + '/userRpm/WlanStationRpm.htm', headers=headersDefault)
        # print(r)
        status = str(r.status_code)
        if (status != '200'):
            return 'error code: ' + status

        parsedResponce = BeautifulSoup(r.text, 'html.parser')
        scriptText = ''
        for script in parsedResponce.find_all('script'):
            if ('var hostList = new Array(' in script.text):
                scriptText = script.text
                break

        if(len(scriptText) == 0):
            return 'script not found'

        scriptTextSplit = scriptText.replace(
            'var hostList = new Array(', '').replace(' );', '').replace('\n', '').split(',')

        activeConnectionList = []
        for index, item in enumerate(scriptTextSplit):
            if (index % 4 == 0 and item.replace(' ', '') != '0'):
                activeConnectionList.append({
                    'macAdress': scriptTextSplit[index].replace(' ', '').replace('"', ''),
                    'wlanStatus': wlanStatusStringArray[int(scriptTextSplit[index + 1])],
                    'receivedPackets': scriptTextSplit[index + 2].replace(' ', ''),
                    'sentPackets': scriptTextSplit[index + 3].replace(' ', ''),
                })

        return json.dumps(activeConnectionList)
    else:
        return 'Wrong command'


if __name__ == '__main__':
    app.run(host="192.168.1.107", port=8000, debug=True)
