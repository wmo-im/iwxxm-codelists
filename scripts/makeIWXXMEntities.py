#!/usr/bin/env python3

import csv
import os
import re
import warnings
import shutil

collectionHeader = ('@prefix skos: <http://www.w3.org/2004/02/skos/core#> . \n'
                    '@prefix dct:  <http://purl.org/dc/terms/> . \n'
                    '@prefix ldp:  <http://www.w3.org/ns/ldp#> .\n'
                    '@prefix reg:  <http://purl.org/linked-data/registry#> .\n'
                    '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n')

collectionTemplate = ('\n<{identity}>\n'
                      '\ta reg:Register , skos:Collection , ldp:Container  ;\n'
                      '\tldp:hasMemberRelation skos:member ;\n'
                      '\tdct:description "{description}" ;\n'
                      '\trdfs:label "{label}" ;\n'
                      '\tskos:notation "{notation}" ;\n'
                      '\treg:status "{status}" ;\n'
                      '\treg:altLabel "{altlabel}" ;\n'
		      '\tdct:modified "{modified}" ;\n'
		      '\towl:versionInfo "{versioninfo}" ;\n'
                      '\treg:seeAlso "{seealso}" ;\n'
                      '\treg:manager "{manager}" ;\n'
                      '\treg:owner "{owner}" .\n')

conceptHeader = ('@prefix skos: <http://www.w3.org/2004/02/skos/core#> . \n'
                 '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n'
                 '@prefix reg:  <http://purl.org/linked-data/registry#> .\n'
                 '@prefix dct:  <http://purl.org/dc/terms/> . \n')

conceptTemplate = ('\n<{identity}>\n'
                   '\ta skos:Concept ;\n'
                   '\tdct:description "{description}" ;\n'
                   '\trdfs:label "{label}" ;\n'
                   '\tskos:notation "{notation}" ;\n'
                   '\treg:status "{status}" ;\n'
                   '\treg:related "{related}" .\n')

def clean(astr):
    if '"' in astr:
        astr = astr.replace('"', "'")
    astr = astr.strip()
    return astr

def main():
    print('Make IWXXM Codelists TTL contents')
    root_path = os.path.split(os.path.dirname(__file__))[0]
    if os.path.exists(os.path.join(root_path, 'TTL')):
        shutil.rmtree(os.path.join(root_path, 'TTL'))
    os.mkdir(os.path.join(root_path, 'TTL'))

    dircontents = os.listdir(os.path.join(root_path, 'CSV'))
    for name in dircontents:
        if name.endswith(".csv"):
            with open(os.path.join(root_path, 'CSV', name), encoding = 'utf-8') as csvf:
                with open(os.path.join(root_path, 'TTL', '{}.ttl'.format(name[:-4])), 'w', encoding = 'utf-8') as ttlf:
                    ttlf.write(collectionHeader)
                    lines = csv.reader(csvf, delimiter = ',', quotechar='"')
                    next(lines)
                    for line in lines:
                        ttlf.write(collectionTemplate.format(identity = clean(line[0]),
                                                             description = clean(line[3]),
                                                             label = clean(line[4]),
                                                             notation = clean(line[1]),
                                                             status = clean(line[2]),
                                                             altlabel = clean(line[5]),
                                                             modified = clean(line[6]),
                                                             versioninfo = clean(line[7]),
                                                             seealso = clean(line[8]),
                                                             manager = clean(line[9]),
                                                             owner = clean(line[10])))

            if not os.path.exists(os.path.join(root_path, 'CSV', name[:-4])):
                raise ValueError('IWXXM code table entries directory {} missing from path'.format(name[:-4]))
            dir1contents = os.listdir(os.path.join(root_path, 'CSV', name[:-4]))
            for name1 in dir1contents:
                if name1.endswith(".csv"):
                    if not os.path.exists(os.path.join(root_path, 'TTL', name[:-4])):
                        os.mkdir(os.path.join(root_path, 'TTL', name[:-4]))
                    with open(os.path.join(root_path, 'CSV', name[:-4], name1), encoding = 'utf-8') as csvf1:
                        with open(os.path.join(root_path, 'TTL', name[:-4], '{}.ttl'.format(name1[:-4])), 'w', encoding = 'utf-8') as ttlf1:
                            ttlf1.write(conceptHeader)
                            lines1 = csv.reader(csvf1, delimiter = ',', quotechar='"')
                            next(lines1)
                            for line1 in lines1:
                                ttlf1.write(conceptTemplate.format(identity = clean(line1[0]),
                                                                   description = clean(line1[3]),
                                                                   label = clean(line1[4]),
                                                                   notation = clean(line1[1]),
                                                                   status = clean(line1[2]),
                                                                   related = clean(line1[5])))
                        
if __name__ == '__main__':
    main()
