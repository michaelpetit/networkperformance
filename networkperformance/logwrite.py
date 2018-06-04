# Author: Michael Petit
# Date: May 2018
# michael.p.petit@gmail.com
# Copywrite: MIT Commons
########################################################################################################################
# Usage:
#
# from logwrite import logwrite
# ...
# LOGFILE = "speedtest_results.txt"
# ...
# with logwrite(LOGFILE) as log:
#     log.write(self.tostring()+"\n")
#
########################################################################################################################


class logwrite(object):
    DEBUG = False

    def __init__(self, name, writetype=0):
        self.filename = "empty.txt"
        self.writetype = "a+"
        self.doc = 0

        if writetype != 0:
            self.writetype = writetype
        self.filename = name
        if self.DEBUG is True:
            print("Log Write Filename: "+self.filename)
        self.doc = open(self.filename, str(self.writetype))

    def __enter__(self):
        if self.DEBUG is True:
            print("Log Write: Enter")
        return self.doc

    def close(self):
        if self.DEBUG is True:
            print("Closing "+self.filename)
        self.doc.close()

    def __exit__(self, ctx_type, ctx_value, ctx_traceback):
        if self.DEBUG is True:
            print("Auto closing: "+self.filename)
        self.close()

