#!/usr/bin/env python3
# Author: Michael Petit
# Date: May 2018
# michael.p.petit@gmail.com
# Copywrite: MIT Commons
########################################################################################################################

import datetime
import speedtest
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import socket
import subprocess
import connectivity
import sys
from sys import platform
from logwrite import logwrite

# TODO
# Refactor classes # http://docs.python-guide.org/en/latest/writing/structure/
# try/catch everything that makes sence
# Add node to node iperf3 to check LAN performance - use arg qulaifier

# Variables
LOGFILE = "speedtest_results.txt"
DEBUG = False

try:
    if platform == "linux" or platform == "linux2":
        osplatform = "linux"
        if DEBUG is True:
            print("Operating system: Linux")
    elif platform == "win32":
        osplatform = "win"
        if DEBUG is True:
            print("Operating system: Windows")
    else:
        print("Unsupported operating system - exiting...")
        exit()
except NameError as err:
    print("Error: NameError: Unable to set platform: {0}".format(err))
except OSError as err:
    print("Error: OSError: Unable to set platform: {0}".format(err))
except ReferenceError as err:
    print("Error: ReferenceError: Unable to set platform: {0}".format(err))
except RuntimeError as err:
    print("Error: RuntimeError: Unable to set platform: {0}".format(err))
except SyntaxError as err:
    print("Error: SyntaxError: Unable to set platform: {0}".format(err))
except TypeError as err:
    print("Error: TypeError: Unable to set platform: {0}".format(err))
except ValueError as err:
    print("Error: ValueError: Unable to set platform: {0}".format(err))
except ArithmeticError as err:
    print("Error: ArithmeticError: Unable to set platform: {0}".format(err))
except EOFError as err:
    print("Error: EOFError: Unable to set platform: {0}".format(err))
except ImportError as err:
    print("Error: ImportError: Unable to set platform: {0}".format(err))
except MemoryError as err:
    print("Error: MemoryError : Unable to set platform: {0}".format(err))
except StopIteration as err:
    print("Error: StopIteration : Unable to set platform: {0}".format(err))


def printdot():
    sys.stdout.write(".")
    sys.stdout.flush()


class NetworkPerformance(object):

    def __init__(self):
        self.date = datetime.datetime.now().strftime("%y-%m-%d")
        self.time = datetime.datetime.now().strftime("%H:%M:%S")
        self.datetime = self.date + " " + self.time
        self.isp = 0
        self.download = 0
        self.upload = 0
        self.ping = 0
        self.client = '?'
        self.client_latitude = 0
        self.client_longitude = 0
        self.server = '?'
        self.server_location = '?'
        self.server_latitude = 0
        self.server_longitude = 0
        self.hostname = socket.gethostname()
        self.hops = []
        self.highhopserver = 0
        self.highhop = 0

    def printout(self):
        print ("Date:         " + str(self.date))
        print ("Time:         " + str(self.time))
        print ("ISP:          " + str(self.isp))
        print ("Hostname:     " + str(self.hostname))
        print ("Client IP:    " + str(self.client))
        print ("Client lat:   " + str(self.client_latitude))
        print ("Client lon:   " + str(self.client_longitude))
        print ("Server:       " + str(self.server))
        print ("Server Loc:   " + str(self.server_location))
        print ("Server lat:   " + str(self.server_latitude))
        print ("Server lon:   " + str(self.server_longitude))
        print ("Download:     " + str(self.download))
        print ("Upload:       " + str(self.upload))
        print ("Ping:         " + str(self.ping))
        print ("Hop Count:    " + str(len(self.hops)))
        if self.hops:
            for h in self.hops:
                h.printout()
        print ("High Hop Ser: " + str(self.highhopserver))
        print ("High Hop:     " + str(self.highhop))

    def tostring(self):
        return str(self.date) + "," + \
            str(self.time) + "," + \
            str(self.datetime) + "," + \
            str(self.isp) + "," + \
            str(self.hostname) + "," + \
            str(self.client) + "," + \
            str(self.client_latitude) + "," + \
            str(self.client_longitude) + "," + \
            str(self.server) + "," + \
            str(self.server_location) + "," + \
            str(self.server_latitude) + "," + \
            str(self.server_longitude) + "," + \
            str(self.download) + "," + \
            str(self.upload) + "," + \
            str(self.ping) + "," + \
            str(self.highhopserver) + "," + \
            str(self.highhop)

    def toarray(self):
        arr = [
            str(self.date),
            str(self.time),
            str(self.datetime),
            str(self.isp),
            str(self.hostname),
            str(self.client),
            str(self.client_latitude),
            str(self.client_longitude),
            str(self.server),
            str(self.server_location),
            str(self.server_latitude),
            str(self.server_longitude),
            self.download,
            self.upload,
            self.ping,
            len(self.hops),
            str(self.highhopserver),
            self.highhop]
        return arr

    def sethighhop(self):
        if self.hops:
            for h in self.hops:
                if h.highms > self.highhop:
                    self.highhop = h.highms
                    self.highhopserver = h.ip + " / " + h.name

    def savedata(self):
        self.logdata()
        self.gdwrite()

    def gdwrite(self):
        if DEBUG is True:
            print("Write to GoogleDocs...")

        # set highhop and highhopserver if not set
        if self.highhop == 0:
            self.sethighhop()

        # Google Docs auth and open spreadsheet
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name("servicecredentials.json", scope)
        connection = gspread.authorize(credentials)
        spreadsheet = connection.open("NetworkMonitorData")

        # Write Speedtest data - Insert at the top of GD:Speedtest sheet
        sheet = spreadsheet.worksheet("Speedtest")
        arr = self.toarray()
        sheet.insert_row(arr, 2, 'RAW')

        # Write trace data - insert data at the top of GD:traceroute sheet
        sheet = spreadsheet.worksheet("TraceRoute")
        for h in reversed(self.hops):
            if DEBUG is True:
                h.printout()
            arr = h.toarray()
            arr.insert(0, str(self.server))
            arr.insert(0, str(self.client))
            arr.insert(0, str(self.time))
            arr.insert(0, str(self.date))
            sheet.insert_row(arr, 2, 'RAW')

    def logdata(self):
        if DEBUG is True:
            print("Log data...")
        with logwrite(LOGFILE) as log:
            log.write(self.tostring() + "\n")

    def wanspeedtest(self):
        if DEBUG is True:
            print("Speed test...")

        st = speedtest.Speedtest()
        printdot()
        st.get_best_server()
        printdot()
        self.download = round(st.download()/1000000, 2)
        self.upload = round(st.upload()/1000000, 2)
        self.ping = round(st.results.ping, 2)
        results = st.results
        printdot()

        if DEBUG is True:
            print(st.results)

        client = st.results.client
        self.client = client.get("ip", "?")
        self.client_latitude = client.get("lat", "?")
        self.client_longitude = client.get("lon", "?")
        self.isp = client.get("isp", "?")
        server = st.results.server
        self.server = server.get("host", "?")
        self.server_location = server.get("name", "?")
        self.server_latitude = server.get("lat", "?")
        self.server_longitude = server.get("lon", "?")

        if DEBUG is True:
            print(results.json())
            self.download = st.results.download
            self.ping = st.results.ping
            self.upload = st.results.upload
            # print(st._opener)
            # print(st._secure)
            # print(st._best)
            print(st.closest)
            print(st.config)
            print(st.servers)
            # print(st._source_address)
            # print(st._timeout)

    def traceroute(self):
        if DEBUG is True:
            print ("Traceroute...")
        values = self.server.split(":")
        if osplatform == "linux":
            strg = "paris-traceroute -n "+values[0]
        elif osplatform == "win":
            strg = "tracert -d -4 "+values[0]
        if DEBUG is True:
            print(strg)
        p = subprocess.Popen(strg, shell=True, stdout=subprocess.PIPE)
        while True:
            line = p.stdout.readline()
            if not line:
                break
            if DEBUG is True:
                print (line)

            h = NetworkHop(line)
            if h.hopnum != 0:
                if DEBUG is True:
                    print (">>>>>>> " + str(h))
                self.hops.append(h)


class NetworkHop(object):

    def __init__(self, line):
        self.hopnum = 0
        self.ip = 0
        self.name = "?"
        self.ms1 = 0
        self.ms2 = 0
        self.ms3 = 0
        self.highms = self.ms1  # highest out of 3 ms
        self.msavg = 0  # average

        line = line.replace("ms ", " ").strip().replace("  ", " ").replace("  ", " ")
        if DEBUG is True:
            print ("LINE: " + line)
        values = line.split(" ")
        if osplatform == "linux":
            if DEBUG is True:
                print("Platform is linux in NetworkHop")
            if len(values) == 4 and values[1] == "*":
                self.hopnum = values[0]
                self.ip = "?"
                self.name = "?"
                self.ms1 = 0
                self.ms2 = 0
                self.ms3 = 0
                self.msavg = 0
                self.highms = 0
            elif len(values) == 5:
                self.hopnum = values[0]
                self.ip = values[1]
                self.name = self._gethostbyaddress()
                self.ms1 = float(values[2])
                self.ms2 = float(values[3])
                self.ms3 = float(values[4])
                self.msaverage()
                self.sethighms()
        elif osplatform == "win":
            if DEBUG is True:
                print("Platform is win in NetworkHop")
            print("LINE: " + line)
            print("TODO: Windows tracert")
            print("LEN: " + str(len(line)))
            # if len(values) > 4 and values[1] == "*":

            # Tracing route to google.com [2607:f8b0:4009:80f::200e]
            # over a maximum of 30 hops:
            #
            # 1     *        *        *     Request timed out.
            # 2    52 ms    28 ms    38 ms  2600:1007:b027:d1bc:0:5c:4745:9940
            # 3     *        *        *     Request timed out.
            # 4    32 ms    30 ms    46 ms  2001:4888:35:2010:383:2a1:0:1
            # 5    24 ms    36 ms    47 ms  2001:4888:35:2079:383:2a1::
            # 6   295 ms    36 ms    20 ms  2001:4888:35:200e:383:25:0:1
            # 7   316 ms    30 ms    28 ms  2001:4888:35:2000:383:26:0:1
            # 8    63 ms    38 ms    38 ms  2001:4888:3f:4191:383:1::
            # 9   305 ms    39 ms    40 ms  2001:4888:3f:4191:383:1::
            # 10   309 ms    39 ms    32 ms  2001:4888:35:1001:383:24::
            # 11   326 ms    40 ms    40 ms  2600:805:71f::5
            # 12    65 ms    47 ms    55 ms  2600:805::85
            # 13    66 ms    60 ms    53 ms  2600:805:41f::26
            # 14    63 ms    59 ms    57 ms  2001:4860:0:100d::e
            # 15   327 ms    56 ms    45 ms  2001:4860:0:1::1579
            # 16   341 ms    42 ms    50 ms  ord30s26-in-x0e.1e100.net [2607:f8b0:4009:80f::200e]
            #
            # Trace complete.

        else:
            print("Unsupported OS - should have never got here - yikes!")

        if DEBUG is True:
            self.printout()

    def _gethostbyaddress(self):

        if DEBUG is True:
            print("IP: "+self.ip)

        octet = self.ip.split(".")
        if len(octet) == 4:
            try:
                name, alias, addressliet = socket.gethostbyaddr(self.ip)
                return name
            except:
                if DEBUG is True:
                    print("Socket error")

                return "?"
        else:
            if DEBUG is True:
                print("IP does not have 4 octets")
            return "?"

    def sethighms(self):
        if self.ms2 > self.highms:
            self.highms = self.ms2
        if self.ms2 > self.highms:
            self.highms = self.ms3

    def gethighms(self):
        return self.highms

    def toarray(self):
        arr = [
            str(self.hopnum),
            str(self.ip),
            str(self.name),
            str(self.ms1),
            str(self.ms2),
            str(self.ms2),
            str(self.msavg)]
        return arr

    def printout(self):
        print ("")
        print ("hopnum:   " + str(self.hopnum))
        print ("ip:    " + str(self.ip))
        print ("name:  " + str(self.name))
        print ("ms1:   " + str(self.ms1))
        print ("ms2:   " + str(self.ms2))
        print ("ms3:   " + str(self.ms3))
        print ("msavg:   " + str(self.msavg))

    def msaverage(self):
        self.msavg = float((self.ms1 + self.ms2 + self.ms3)/3)
        self.msavg = round(self.msavg, 2)
        return self.msavg


def main():

    netp = 0

    printdot()
    printdot()
    printdot()

    try:
        internet = connectivity.Connectivity()
        if internet.hasinternet() is False:
            return

        netp = NetworkPerformance()
        printdot()

        netp.wanspeedtest()
        printdot()

        netp.traceroute()
        printdot()

        netp.savedata()
        printdot()
    except Exception as error:
        print("Error: {0}".format(error))
        print(type(error))
        print(error.message)
        print(error.args)

    print("Execution complete: " + str(netp.datetime) + ": Download:" + str(netp.download) + "MBps Upload:" +
          str(netp.upload) + "MBps Latency:" + str(netp.ping) + "ms Hops:" + str(len(netp.hops)))


if __name__ == "__main__":
    main()
