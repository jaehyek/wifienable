# -*- coding: utf-8 -*-

from __future__ import print_function
from datetime import datetime, timedelta
import time

__author__ = 'jaehyek.choi'

"""
purpose :

"""

"""
from __future__ import division
"""

import os

class DateStrformat():
    '''
    입력 format은  20150912 처럼 string으로 표현되고, 내부에서는 날짜 개산을 하고,
    같은 format으로 출력한다.
    '''
    def __init__(self, datestr):
        year = datestr[:4]
        mon = datestr[4:6]
        day = datestr[6:8]

        # 계산은 낮 12시를 기준으로 한다.
        self.Refseconds  = self.ConvertDateTimeToMiliSeconds(int(year), int(mon), int(day), 12)

    def ConvertDateTimeToMiliSeconds(self, y, m, d, h = 0 , minute = 0 , s = 0 ):
        daydiff = datetime(y, m, d, h, minute, s) - datetime(1970, 1, 1, 9, 0, 0)
        return int(daydiff.total_seconds())

    def ConvertTimeStampToString ( self, inputsecond ):
        if inputsecond == None:
            return ""
        strfmt = "%Y%m%d"
        outdatetime = datetime(1970, 1, 1) + timedelta(hours= 9, seconds=inputsecond)
        return outdatetime.strftime(strfmt)

    def getDateStr_nDay(self, nDays):
        return self.ConvertTimeStampToString( self.Refseconds + 24 * 3600 * nDays)

    def getDateStr_Today(self):
        strfmt = "%Y%m%d"
        return datetime.now().strftime(strfmt)



def ordtohex(name) :
    strhex = ""
    for a in name :
        strhex += hex(ord(a))[2:]

    return strhex

def execwificmd(clsvar, strcmd ) :

    strcmd = clsvar.adb + strcmd

    liststr =  os.popen(strcmd).readlines()
    listret = []
    for line in liststr :
        line2 = line.strip()
        if len( line2) > 0 :
            listret.append(line2)

    return listret



def wifienable(clsvar):

    strhexwifiname = ordtohex(clsvar.wifiname)

    # enable root
    os.system("adb root")
    print("adb rooting")
    time.sleep(3)


    #enable wifi
    os.system("adb shell svc wifi enable")
    print("enabling wifi ")
    time.sleep(3)

    # make scan
    # os.system("adb shell wpa_cli IFNAME=wlan0 scan")
    # print("wifi scanning")
    # time.sleep(6)
    #
    # liststr = execwificmd(clsvar, "wpa_cli IFNAME=wlan0 scan_results")
    # found = 0
    # for line in liststr :
    #     if len(line) > 0 and clsvar.wifiname in line :
    #         found = 1
    #
    # if found ==  1 :
    #     print("%s was found" % clsvar.wifiname )
    # else :
    #     print("%s was not found " % clsvar.wifiname  )
    #     return


    # add the network profile
    liststr = execwificmd(clsvar, "wpa_cli IFNAME=wlan0 ADD_NETWORK")
    id = liststr[-1].strip()
    print("network ID : %s "%id)

    # assign AP name
    print("assign AP name")
    liststr = execwificmd(clsvar, "wpa_cli IFNAME=wlan0 SET_NETWORK %s ssid %s"%(id, strhexwifiname))
    if not "ok"  in liststr[-1].strip().lower() :
        return

    # assign the security method
    print("assign the security method")
    liststr = execwificmd(clsvar, "wpa_cli IFNAME=wlan0 SET_NETWORK %s key_mgmt WPA-PSK"%(id))
    if not "ok"  in liststr[-1].strip().lower() :
        return

    if clsvar.hidden == True :
        print("hidden wifi enabling")
        liststr = execwificmd(clsvar, "wpa_cli IFNAME=wlan0 SET_NETWORK %s scan_ssid 1"%(id))
        time.sleep(3)

        if not "ok"  in liststr[-1].strip().lower() :
            return

    # assign the password
    print("assign the password")
    strpassword = '\\"' + clsvar.password + '\\"'
    liststr = execwificmd(clsvar, "wpa_cli IFNAME=wlan0 SET_NETWORK %s psk %s "%(id, strpassword))
    time.sleep(3)
    if not "ok"  in liststr[-1].strip().lower() :
        return

    # enable the network
    print("enable the network")
    liststr = execwificmd(clsvar, "wpa_cli IFNAME=wlan0 ENABLE_NETWORK  %s "%(id))
    if not "ok"  in liststr[-1].strip().lower() :
        return

    # save the network
    print("save the network")
    liststr = execwificmd(clsvar, "wpa_cli IFNAME=wlan0 SAVE_CONFIG")
    if not "ok"  in liststr[-1].strip().lower() :
        return

    # select the network
    print("select the network")
    liststr = execwificmd(clsvar, "wpa_cli IFNAME=wlan0 select_network %s "%(id))
    if not "ok"  in liststr[-1].strip().lower() :
        return

    # reassociate
    print("reassociate")
    liststr = execwificmd(clsvar, "wpa_cli IFNAME=wlan0 reassociate")
    if not "ok"  in liststr[-1].strip().lower() :
        return

    print("=============== status ================================================")
    # print status
    liststr = execwificmd(clsvar, "wpa_cli IFNAME=wlan0 status")
    for line in liststr :
        print (line)



if __name__ == "__main__":

    datestr = DateStrformat("20150101")
    print(datestr.getDateStr_nDay(-1))
    print(datestr.getDateStr_Today())
    exit()


    import argparse

    cmdlineopt = argparse.ArgumentParser(description='enable and set-up the wifi with name and password')
    cmdlineopt.add_argument('-n', action="store", dest="wifiname", default='', help='wifi name')
    cmdlineopt.add_argument('-p', action="store", dest="password", default='', help='wifi password' )
    cmdlineopt.add_argument('-hi', action="store_true", dest="hidden", default=False, help='in case of hidden wifi' )

    clsvar = cmdlineopt.parse_args()

    clsvar.adb = "adb shell "

    if len(clsvar.wifiname) == 0  or len(clsvar.password) == 0 :
       print (" Must have the value of wifiname and password as parameter")
       exit()

    wifienable(clsvar)



