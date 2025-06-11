#!/usr/bin/env python3

import re
import os
import shutil
import pandas
import urllib.parse
from rdflib import Graph, Literal, RDF, URIRef, Namespace, BNode
from rdflib.namespace import OWL, SKOS, RDFS, RDF, DC, XSD

# Define namespaces and attributes to be used
DCT = Namespace("http://purl.org/dc/terms/")
DCT.description
DCT.modified
DCT.publisher
REG = Namespace("http://purl.org/linked-data/registry#")
REG.manager
REG.owner
REG.Register
REG.status
REG.subregister
LDP = Namespace("http://www.w3.org/ns/ldp#")
LDP.Container
LDP.hasMemberRelation

dictionary = {'description':DCT.description,
              'label':RDFS.label,
              'notation':SKOS.notation,
              'status':REG.status,
              'altLabel':SKOS.altLabel,
              'modified':DCT.modified,
              'versionInfo':OWL.versionInfo,
              'seeAlso':RDFS.seeAlso,
              'manager':REG.manager,
              'owner':REG.owner,
              'source':DC.source,
              'note':SKOS.note,
              'publisher':DCT.publisher,
              'subregister':REG.subregister,
              'iwxxmVersionInfo':OWL.versionInfo}

IWXXMNameSpace= 'http://icao.int/iwxxm/'

def clean(astr):
    if '"' in astr:
        astr = astr.replace('"', "'")
    astr = astr.strip()
    return astr

def main():
    print('Converting IWXXM Codelists from CSV to TTL and RDF formats')

    root_path = os.path.dirname(os.path.dirname(__file__))
    if os.path.exists(os.path.join(root_path, 'TTL')):
        shutil.rmtree(os.path.join(root_path, 'TTL'))
    os.mkdir(os.path.join(root_path, 'TTL'))
    if os.path.exists(os.path.join(root_path, 'RDF')):
        shutil.rmtree(os.path.join(root_path, 'RDF'))
    os.mkdir(os.path.join(root_path, 'RDF'))

    for (root_csv, dummy1, dummy2) in os.walk(os.path.join(root_path, 'CSV')):

        # Skip obsoleted tables 'observable-property' and 'observation-type'
        if os.path.basename(root_csv) == 'observable-property' or os.path.basename(root_csv) == 'observation-type':
            continue
        
        root_ttl = os.path.join(root_path, 'TTL', root_csv[len(os.path.join(root_path, 'CSV')) + 1:])
        #root_rdf = os.path.join(root_path, 'RDF', root_csv[len(os.path.join(root_path, 'CSV')) + 1:])
        root_rdf = os.path.join(root_path, 'RDF')
        
        # Create container TTL

        # If {root_path}/CSV/{table}/{table}_container.csv exist
        if os.path.exists(os.path.join(root_csv, '{}_container.csv'.format(os.path.basename(root_csv)))):

            # Create {root_path}/TTL/{table}
            if not os.path.exists(root_ttl):
                os.makedirs(root_ttl)
            
            # Read {root_path}/CSV/{table}/{table}_container.csv.
            # For each row/record with non-empty identity column:
            #     1. Create {root_path}/TTL/{table}/{identity}
            #     2. Create {root_path}/TTL/{table}/{indentity}.ttl
            record = pandas.read_csv(os.path.join(root_csv, '{}_container.csv'.format(os.path.basename(root_csv))), encoding = 'utf-8')
            for i in range(record.shape[0]):
                if record.iloc[i]['notation'] != '' and not pandas.isna(record.iloc[i]['notation']):

                    # Skip obsoleted tables 'observable-property' and 'observation-type'
                    if record.iloc[i]['notation'] == 'observable-property' or record.iloc[i]['notation'] == 'observation-type':
                        continue

                    with open(os.path.join(root_ttl, '{}.ttl'.format(record.iloc[i]['notation'])), 'w', encoding = 'utf-8') as ttlf:
                        print('Creating {}'.format(os.path.join(root_ttl, '{}.ttl'.format(record.iloc[i]['notation']))))
                        g = Graph()
                        g.bind("dct", DCT)
                        g.bind("reg", REG)
                        g.bind("ldp", LDP)
                        ref = URIRef(record.iloc[i]['id'])
                        g.add((ref, RDF.type, SKOS.Collection))
                        g.add((ref, RDF.type, REG.Register))
                        g.add((ref, RDF.type, LDP.Container))
                        for j in list(record):
                            # Skipping some columns in the CSV file to make a minimal TTL file
                            if j != 'id' and j != 'notation' and j != 'status' and j != 'description' and j != 'label' and j != 'altLabel' and j != 'modified' and j != 'source' and j != 'seeAlso' and j != 'publisher' and j != 'manager' and j != 'owner' and j != 'note' and j != 'iwxxmVersionInfo':
                                continue
                            if j != 'id':
                                if record.iloc[i][j] != '' and not pandas.isna(record.iloc[i][j]):
                                    if j == 'notation' or j == 'status':
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j])))
                                    elif j == 'iwxxmVersionInfo':
                                        for m in record.iloc[i][j].split(';'):
                                            g.add((ref, dictionary[j], URIRef(urllib.parse.urljoin(IWXXMNameSpace, Literal(m.strip())))))
                                    elif re.match(r'^http://', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], URIRef(record.iloc[i][j])))
                                    elif re.match(r'^[0-9]+$', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j], datatype=XSD.integer)))
                                    elif re.match(r'^(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d\.\d+([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))$', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j], datatype=XSD.dateTime)))
                                    else:
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j], lang="en")))
                        ttlf.write(g.serialize(format='ttl'))
                        ttlf.close()

        # Create Entity TTL

        # if {root_path}/CSV/{table}/{table}_entity.csv exist
        if os.path.exists(os.path.join(root_csv, '{}_entity.csv'.format(os.path.basename(root_csv)))):

            # Create {root_path}/TTL/{table}
            if not os.path.exists(root_ttl):
                os.makedirs(root_ttl)
            
            # Read {root_path}/CSV/{table}/{table}_entity.csv.
            # For each row/record with non-empty identity column:
            #     1. Create {root_path}/TTL/{table}/{identity}.ttl
            record = pandas.read_csv(os.path.join(root_csv, '{}_entity.csv'.format(os.path.basename(root_csv))), encoding = 'utf-8')
            for i in range(record.shape[0]):
                if record.iloc[i]['notation'] != '' and not pandas.isna(record.iloc[i]['notation']):
                    with open(os.path.join(root_ttl, '{}.ttl'.format(record.iloc[i]['notation'])), 'w', encoding = 'utf-8') as ttlf:
                        print('Creating {}'.format(os.path.join(root_ttl, '{}.ttl'.format(record.iloc[i]['notation']))))
                        g = Graph()
                        g.bind("dct", DCT)
                        g.bind("reg", REG)
                        g.bind("ldp", LDP)
                        ref = URIRef(record.iloc[i]['id'])
                        g.add((ref, RDF.type, SKOS.Concept))
                        for j in list(record):
                            # Skipping some columns in the CSV file to make a minimal TTL file
                            if j != 'id' and j != 'notation' and j != 'status' and j != 'description' and j != 'label' and j != 'altLabel' and j != 'source' and j != 'seeAlso' and j != 'note' and j != 'iwxxmVersionInfo':
                                continue
                            if j != 'id':
                                if record.iloc[i][j] != '' and not pandas.isna(record.iloc[i][j]):
                                    if j == 'notation' or j == 'status':
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j])))
                                    elif j == 'iwxxmVersionInfo':
                                        for m in record.iloc[i][j].split(';'):
                                            g.add((ref, dictionary[j], URIRef(urllib.parse.urljoin(IWXXMNameSpace, Literal(m.strip())))))
                                    elif re.match(r'^http://', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], URIRef(record.iloc[i][j])))
                                    elif re.match(r'^[0-9]+$', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j], datatype=XSD.integer)))
                                    elif re.match(r'^(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d\.\d+([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))$', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j], datatype=XSD.dateTime)))
                                    else:
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j], lang="en")))
                        ttlf.write(g.serialize(format='ttl'))
                        ttlf.close()

        # Create entity RDF

        # If {root_path}/CSV/{table}/{table}_container.csv exist
        if os.path.exists(os.path.join(root_csv, '{}_container.csv'.format(os.path.basename(root_csv)))):

            # Create {root_path}/RDF/{table}
            if not os.path.exists(root_rdf):
                os.makedirs(root_rdf)

            # Read {root_path}/CSV/{table}/{table}_container.csv.
            # For each row/record with non-empty identity column:
            #     1. Create {root_path}/RDF/codes.wmo.int-{table}-{identity}.rdf
            record = pandas.read_csv(os.path.join(root_csv, '{}_container.csv'.format(os.path.basename(root_csv))), encoding = 'utf-8')
            for i in range(record.shape[0]):
                if record.iloc[i]['notation'] != '' and not pandas.isna(record.iloc[i]['notation']):

                    # Skip obsoleted tables 'observable-property' and 'observation-type'
                    if record.iloc[i]['notation'] == 'observable-property' or record.iloc[i]['notation'] == 'observation-type':
                        continue

                    record_entity = pandas.read_csv(os.path.join(root_csv, '{0}/{1}_entity.csv'.format(record.iloc[i]['notation'], record.iloc[i]['notation'])), encoding = 'utf-8')
                    with open(os.path.join(root_rdf, 'codes.wmo.int-{0}-{1}.rdf'.format(os.path.basename(root_csv), record.iloc[i]['notation'])), 'w', encoding = 'utf-8') as rdff:
                        print('Creating {}'.format(os.path.join(root_rdf, 'codes.wmo.int-{0}-{1}.rdf'.format(os.path.basename(root_csv), record.iloc[i]['notation']))))
                        g = Graph()
                        g.bind("dct", DCT)
                        g.bind("reg", REG)
                        g.bind("ldp", LDP)
                        for k in range(record_entity.shape[0]):
                            #print(os.path.join(root_csv, '{0}/{1}_entity.csv'.format(record.iloc[i]['notation'], record.iloc[i]['notation'])))
                            if record_entity.iloc[k]['notation'] != '' and not pandas.isna(record_entity.iloc[k]['notation']):
                                n_concept = URIRef(record_entity.iloc[k]['id'])
                                g.add((n_concept, RDF.type, SKOS.Concept))
                                for l in list(record_entity):
                                    # Skipping some columns in the CSV file to make a minimal RDF file
                                    if l != 'id' and l != 'notation' and l != 'description' and l != 'label' and l != 'altLabel' and l != 'note' and l != 'iwxxmVersionInfo':
                                        continue
                                    if l != 'id':
                                        if record_entity.iloc[k][l] != '' and not pandas.isna(record_entity.iloc[k][l]):
                                            if l == 'notation' or l == 'status':
                                                g.add((n_concept, dictionary[l], Literal(record_entity.iloc[k][l])))
                                            elif l == 'iwxxmVersionInfo':
                                                for m in record_entity.iloc[k][l].split(';'):
                                                    g.add((n_concept, dictionary[l], URIRef(urllib.parse.urljoin(IWXXMNameSpace, Literal(m.strip())))))
                                            elif re.match(r'^http://', record_entity.astype(str).iloc[k][l]):
                                                g.add((n_concept, dictionary[l], URIRef(record_entity.iloc[k][l])))
                                            elif re.match(r'^[0-9]+$', record_entity.astype(str).iloc[k][l]):
                                                g.add((n_concept, dictionary[l], Literal(record_entity.iloc[k][l], datatype=XSD.integer)))
                                            elif re.match(r'^(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d\.\d+([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))$', record_entity.astype(str).iloc[k][l]):
                                                g.add((n_concept, dictionary[l], Literal(record_entity.iloc[k][l], datatype=XSD.dateTime)))
                                            else:
                                                g.add((n_concept, dictionary[l], Literal(record_entity.iloc[k][l], lang="en")))
                                    n_register = URIRef(os.path.dirname(record_entity.iloc[k]['id']))
                                    g.add((n_register, SKOS.member, n_concept))
                                    g.add((n_register, RDF.type, REG.Register))
                                    for j in list(record):
                                        # Skipping some columns in the CSV file to make a minimal RDF file
                                        if j != 'id' and j != 'notation' and j != 'description' and j != 'label' and j != 'altLabel' and j != 'modified' and j != 'note' and j != 'iwxxmVersionInfo':
                                            continue
                                        if j != 'id':
                                            if record.iloc[i][j] != '' and not pandas.isna(record.iloc[i][j]):
                                                if j == 'notation' or j == 'status':
                                                    g.add((n_register, dictionary[j], Literal(record.iloc[i][j])))
                                                elif j == 'iwxxmVersionInfo':
                                                    for m in record.iloc[i][j].split(';'):
                                                        g.add((n_register, dictionary[j], URIRef(urllib.parse.urljoin(IWXXMNameSpace, Literal(m.strip())))))
                                                elif re.match(r'^http://', record.astype(str).iloc[i][j]):
                                                    g.add((n_register, dictionary[j], URIRef(record.iloc[i][j])))
                                                elif re.match(r'^[0-9]+$', record.astype(str).iloc[i][j]):
                                                    g.add((n_register, dictionary[j], Literal(record.iloc[i][j], datatype=XSD.integer)))
                                                elif re.match(r'^(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d\.\d+([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))|(\d{4}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d([+-][0-2]\d:[0-5]\d|Z))$', record.astype(str).iloc[i][j]):
                                                    g.add((n_register, dictionary[j], Literal(record.iloc[i][j], datatype=XSD.dateTime)))
                                                else:
                                                    g.add((n_register, dictionary[j], Literal(record.iloc[i][j], lang="en")))
                                    g.add((n_register, RDF.type, LDP.Container))
                                    g.add((n_register, RDF.type, SKOS.Collection))
                                    g.add((n_register, LDP.hasMemberRelation, SKOS.member))
                        rdff.write(g.serialize(format='pretty-xml'))
                        rdff.close()

if __name__ == '__main__':
    main()
