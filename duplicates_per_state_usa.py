#!/usr/bin/python

import sys
import io
import codecs

sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

TRANSFERRED = {}
MAX_FILE_SIZE = {}
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

STATE_ABBR_STR = """
Alabama	AL
Alaska	AK
Arizona	AZ
Arkansas	AR
California	CA
Colorado	CO
Connecticut	CT
Delaware	DE
Florida	FL
Georgia	GA
Hawaii	HI
Idaho	ID
Illinois	IL
Indiana	IN
Iowa	IA
Kansas	KS
Kentucky	KY
Louisiana	LA
Maine	ME
Maryland	MD
Massachusetts	MA
Michigan	MI
Minnesota	MN
Mississippi	MS
Missouri	MO
Montana	MT
Nebraska	NE
Nevada	NV
New Hampshire	NH
New Jersey	NJ
New Mexico	NM
New York	NY
North Carolina	NC
North Dakota	ND
Ohio	OH
Oklahoma	OK
Oregon	OR
Pennsylvania	PA
Rhode Island	RI
South Carolina	SC
South Dakota	SD
Tennessee	TN
Texas	TX
Utah	UT
Vermont	VT
Virginia	VA
Washington	WA
West Virginia	WV
Wisconsin	WI
Wyoming	WY
American Samoa	AS
District of Columbia	DC
Federated States of Micronesia	FM
Guam	GU
Marshall Islands	MH
Northern Mariana Islands	MP
Palau	PW
Puerto Rico	PR
Virgin Islands	VI
Armed Forces Africa	AE
Armed Forces Americas	AA
Armed Forces Canada	AE
Armed Forces Europe	AE
Armed Forces Middle East	AE
Armed Forces Pacific	AP
"""

STATE_ABBR_MAP = {}
abbrs = STATE_ABBR_STR.split("\n")
for abbr_line in abbrs:
    line = abbr_line.strip()
    if len(line) > 0:
        fields = line.split("\t")
        full = fields[0].strip()
        abbr = fields[1].strip()
        STATE_ABBR_MAP[abbr] = full

def get_full_state_name(abbr):
    return STATE_ABBR_MAP[abbr]

def filter_line(line):
    fields = line.split("\t")
    direction = fields[6]
    if direction == "INCOMING":
        return True

    bytes_transferred = int(fields[4])
    if bytes_transferred <= 0:
        return True

    country = fields[11]
    region_code = fields[9]
    if country == "United States" and region_code != "None":
        return False

    # filter all others
    return True

def analyze_line(line):
    fields = line.split("\t")
    region_code = fields[9]
    filename = fields[3]

    key = region_code + "\t" + filename
    bytes_transferred = int(fields[4])

    if key in TRANSFERRED:
        TRANSFERRED[key] = TRANSFERRED[key] + bytes_transferred
    else:
        TRANSFERRED[key] = bytes_transferred

    if key in MAX_FILE_SIZE:
        if MAX_FILE_SIZE[key] < bytes_transferred:
            MAX_FILE_SIZE[key] = bytes_transferred
    else:
        MAX_FILE_SIZE[key] = bytes_transferred

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

    for key in TRANSFERRED.keys():
        dupbytes = TRANSFERRED[key] - MAX_FILE_SIZE[key]
        if dupbytes != 0:
            fields = key.split("\t")

            if fields[0] in SUMMARY:
                SUMMARY[fields[0]] = SUMMARY[fields[0]] + dupbytes
            else:
                SUMMARY[fields[0]] = dupbytes

    for key in SUMMARY.keys():
        region_code = get_full_state_name(key)
        print "%s\t%d" % (region_code, SUMMARY[key])

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
