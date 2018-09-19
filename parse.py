#!/usr/bin/python

import sys
import io
import time
import datetime
import pygeoip
import codecs

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)


gi = pygeoip.GeoIP("GeoLiteCity.dat")

class vsftpd_log(object):
    def __init__(self, line):
        fields = line.split()
        if len(fields) != 18:
            raise Exception("There are only %d fields - %s" % (len(fields), line))

        #access time - Thu Mar 4 08:12:30 2004
        accesstimestr = " ".join(fields[0:5])
        self.access_time = time.strptime(accesstimestr)

        #transfer time (time taken in sec) - 1
        self.transfertime = int(fields[5].strip())
        #remotehost
        self.remotehost = fields[6].strip()
        #byte transferred
        self.bytecount = int(fields[7].strip())
        #filename
        self.filename = fields[8].strip()
        #transfertype
        self.transfertype = fields[9].strip()
        #action
        self.actionflag = fields[10].strip()
        #direction
        self.direction = fields[11].strip()
        #accessmode
        self.accessmode = fields[12].strip()
        #username
        self.username = fields[13].strip()
        #service-name
        self.servicename = fields[14].strip()
        #authentication-method
        self.authentication_method = fields[15].strip()
        #authentication-userid
        self.authentication_userid = fields[16].strip()
        #complettion status
        self.completion_status = fields[17].strip()

    def getTransferType(self):
        if self.transfertype in ["a", "A"]:
            return "ASCII"
        elif self.transfertype in ["b", "B"]:
            return "BINARY"
        else:
            raise Exception("Unknown transfer type : %s" % self.transfertype)

    def getActionType(self):
        if self.actionflag in ["_"]:
            return "NO ACTION"
        elif self.actionflag in ["c", "C"]:
            return "COMPRESSED"
        elif self.actionflag in ["u", "U"]:
            return "UNCOMPRESSED"
        elif self.actionflag in ["t", "T"]:
            return "TARED"
        else:
            raise Exception("Unknown action type : %s" % self.actionflag)

    def getDirection(self):
        if self.direction in ["o", "O"]:
            return "OUTGOING"
        elif self.direction in ["i", "I"]:
            return "INCOMING"
        else:
            raise Exception("Unknown direction type : %s" % self.direction)

    def getAccessMode(self):
        if self.accessmode in ["a", "A"]:
            return "ANONYMOUS"
        elif self.accessmode in ["g", "G"]:
            return "GUEST" #chrooted user
        elif self.accessmode in ["r", "R"]:
            return "REAL"
        else:
            raise Exception("Unknown access mode : %s" % self.accessmode)

    def getCompletionStatus(self):
        if self.completion_status in ["c", "C"]:
            return "COMPLETE"
        elif self.completion_status in ["i", "I"]:
            return "INCOMPLETE"
        else:
            raise Exception("Unknown completion status : %s" % self.completion_status)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __repr__(self):
        return "<vsftpd_log %s %d %s %s %d %s %s %s>" % \
            (time.strftime("%Y/%m/%d %H:%M:%S", self.access_time), self.transfertime, self.remotehost, self.filename, self.bytecount, self.getTransferType(), self.getDirection(), self.getCompletionStatus())

def parse_gps(log):
    record = gi.record_by_addr(log.remotehost)
    return record

def parse_line(line):
    l = vsftpd_log(line)
    loc = parse_gps(l)
    if loc:
        # public ip
        print u"%s\t%d\t%s\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%.8f\t%.8f" % \
            (time.strftime("%Y/%m/%d %H:%M:%S", l.access_time), l.transfertime, l.remotehost, l.filename, l.bytecount, l.getTransferType(), l.getDirection(), l.getCompletionStatus(), loc["city"], loc["region_code"], loc["metro_code"], loc["country_name"], loc["latitude"], loc["longitude"])
    else:
        # private ip
        print u"%s\t%d\t%s\t%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%.8f\t%.8f" % \
            (time.strftime("%Y/%m/%d %H:%M:%S", l.access_time), l.transfertime, l.remotehost, l.filename, l.bytecount, l.getTransferType(), l.getDirection(), l.getCompletionStatus(), "Tucson", "AZ", "Tucson, AZ", "United States", 32.23380000, -110.95000000)

def parse(path, max_lines):
    processed_lines = 0;

    with io.open(path, "r") as f:
        for line in f:
            parse_line(line)
            processed_lines += 1
            if max_lines > 0 and processed_lines >= max_lines:
                break

def main(argv):
    if len(argv) < 1:
        print "command : ./parse.py input_path"
    elif len(argv) >= 1:
        input_path = argv[0]
        max_lines = 0 # no limit

        if len(argv) == 2:
            max_lines = int(argv[1])
        parse(input_path, max_lines)

if __name__ == "__main__":
    main(sys.argv[1:])
