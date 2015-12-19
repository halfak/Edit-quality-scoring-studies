import sys

import mysqltsv

revs = mysqltsv.Reader(sys.stdin)

for rev in revs:
    print(rev.values())
