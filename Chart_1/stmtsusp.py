#!/usr/bin/python2.7

import argparse
import csv

def classname_to_filename(classname):
  if '$' in classname:
    classname = classname[:classname.find('$')]
  return classname.replace('.', '/') + '.java'
def stmt_to_line(stmt):
  classname, lineno = stmt.rsplit('#', 1)
  return '{}#{}'.format(classname_to_filename(classname), lineno)

assert classname_to_filename('org.apache.MyClass$Inner') == 'org/apache/MyClass.java'
assert stmt_to_line('org.apache.MyClass$Inner#123') == 'org/apache/MyClass.java#123'

parser = argparse.ArgumentParser()
parser.add_argument('--stmt-susps', required=True)
parser.add_argument('--source-code-lines', required=True)
parser.add_argument('--output', required=True)

args = parser.parse_args()

source_code = dict()
with open(args.source_code_lines) as f:
  for line in f:
    line = line.strip()
    entry = line.split(':')
    key = entry[0]
    if key in source_code:
      source_code[key].append(entry[1])
    else:
      source_code[key] = []
      source_code[key].append(entry[1])
f.close()

lines_susps = dict()

#
# Collect and convert all statements into lines
#
with open(args.stmt_susps) as fin:
  reader = csv.DictReader(fin)
  for row in reader:
    line = stmt_to_line(row['Statement'])
    susps = row['Suspiciousness']
    if line not in lines_susps: # TODO can the stmts file have repetitions?
      lines_susps[line] = susps
fin.close()

#
# Expand lines that have sub-lines
#
for line, susps in lines_susps.items():
  if line in source_code:
    for additional_line in source_code[line]:
      if additional_line not in lines_susps:
        lines_susps[additional_line] = susps

#
# Write the dictionary to the output file
#
with open(args.output, 'w') as f:
  writer = csv.DictWriter(f, ['Line','Suspiciousness'])
  writer.writeheader()
  for line, susps in lines_susps.items():
    writer.writerow({'Line': line, 'Suspiciousness': susps})
f.close()

# EOF

