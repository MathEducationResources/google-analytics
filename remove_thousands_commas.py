# Remove thousandscommas in csv files
# see http://stackoverflow.com/questions/1864422/re-format-items-inside-list-read-from-csv-file-in-python
# call with
# python remove_thousands_commas infile.csv outfile.csv
import csv
import re
import sys

p = re.compile('["]([^"]*)["]')
fin = open(sys.argv[1],'r')
fout = open(sys.argv[2],'w')
for line in fin:
    line = p.sub(lambda m: m.groups()[0].replace(',',''), line)
    fout.write(line)
fin.close()
fout.close()


