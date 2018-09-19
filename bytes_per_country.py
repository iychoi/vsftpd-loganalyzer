#!/usr/bin/python

import sys
import io
import codecs

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

SUMMARY = {}

#(time.strftime("%Y/%m/%d %H:%M:%S", l.access_time), - 0
#l.transfertime, - 1
#l.remotehost, - 2
#l.filename, - 3
#l.bytecount, - 4
#l.getTransferType(), - 5
#l.getDirection(), - 6
#l.getCompletionStatus(), - 7
#loc["city"], - 8
#loc["region_code"], - 9
#loc["metro_code"], - 10
#loc["country_name"], - 11
#loc["latitude"], - 12
#loc["longitude"]) - 13

def filter_line(line):
    fields = line.split("\t")
    direction = fields[6]
    if direction == "INCOMING":
        return True

    bytes_transferred = int(fields[4])
    if bytes_transferred <= 0:
        return True

    return False

def analyze_line(line):
    fields = line.split("\t")
    country = fields[11]

    key = country

    bytes_transferred = int(fields[4])
    if key in SUMMARY:
        SUMMARY[key] = SUMMARY[key] + bytes_transferred
    else:
        SUMMARY[key] = bytes_transferred

    #print line

def analyze(path, max_lines):
    processed_lines = 0;

    with io.open(path, "r") as f:
        for line in f:
            if not filter_line(line):
                analyze_line(line)
            processed_lines += 1
            if max_lines > 0 and processed_lines >= max_lines:
                break

    for key in SUMMARY.keys():
        if SUMMARY[key] != 0:
            print "%s\t%d" % (key, SUMMARY[key])

def main(argv):
    if len(argv) < 1:
        print "command : ./bytes_per_city.py input_path"
    elif len(argv) >= 1:
        input_path = argv[0]
        max_lines = 0 # no limit

        if len(argv) == 2:
            max_lines = int(argv[1])
        analyze(input_path, max_lines)

if __name__ == "__main__":
    main(sys.argv[1:])
