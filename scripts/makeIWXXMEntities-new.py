#!/usr/bin/env python3

import re
import os
import shutil
import pandas
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import OWL, SKOS, RDFS, RDF, DC

# Define namespaces and attributesto be used
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
              'publisher':DCT.publisher,
              'subregister':REG.subregister}

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
        root_rdf = os.path.join(root_path, 'RDF', root_csv[len(os.path.join(root_path, 'CSV')) + 1:])
        
        # Create container TTL

        # If {root_path}/CSV/{table}/{table}_container.csv exist
        if os.path.exists(os.path.join(root_csv, '{}_container.csv'.format(os.path.basename(root_csv)))):

            # Create {root_path}/TTL/{table}
            if not os.path.exists(root_ttl):
                os.mkdir(root_ttl)
            
            # Read {root_path}/CSV/{table}/{table}_container.csv.
            # For each row/record with non-empty identity column:
            #     1. Create {root_path}/TTL/{table}/{identity}
            #     2. Create {root_path}/TTL/{table}/{indentity}.ttl
            record = pandas.read_csv(os.path.join(root_csv, '{}_container.csv'.format(os.path.basename(root_csv))), encoding = 'utf-8')
            for i in range(record.shape[0]):
                if record.iloc[i]['notation'] != '' and not pandas.isna(record.iloc[i]['notation']):
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
                            if j != 'id' and j != 'notation' and j != 'status' and j != 'description' and j != 'label' and j != 'manager' and j != 'owner':
                                continue
                            if j != 'id' and j != 'related':
                                if record.iloc[i][j] != '' and not pandas.isna(record.iloc[i][j]):
                                    if j == 'notation' or j == 'status' or j == 'modified':
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j])))
                                    elif re.match('^http://', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], URIRef(record.iloc[i][j])))
                                    elif re.match('^[0-9]+$', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j])))
                                    else:
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j], lang="en")))
                        ttlf.write(g.serialize(format='ttl'))
                        ttlf.close()

        # Create Entity TTL

        # if {root_path}/CSV/{table}/{table}_entity.csv exist
        if os.path.exists(os.path.join(root_csv, '{}_entity.csv'.format(os.path.basename(root_csv)))):

            # Create {root_path}/TTL/{table}
            if not os.path.exists(root_ttl):
                os.mkdir(root_ttl)
            
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
                        g.add((ref, RDF.type, SKOS.Collection))
                        g.add((ref, RDF.type, REG.Register))
                        g.add((ref, RDF.type, LDP.Container))
                        for j in list(record):
                            # Skipping some columns in the CSV file to make a minimal TTL file
                            if j != 'id' and j != 'notation' and j != 'status' and j != 'description' and j != 'label' and j != 'manager' and j != 'owner':
                                continue
                            if j != 'id' and j != 'related':
                                if record.iloc[i][j] != '' and not pandas.isna(record.iloc[i][j]):
                                    if j == 'notation' or j == 'status' or j == 'modified':
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j])))
                                    elif re.match('^http://', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], URIRef(record.iloc[i][j])))
                                    elif re.match('^[0-9]+$', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j])))
                                    else:
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j], lang="en")))
                        ttlf.write(g.serialize(format='ttl'))
                        ttlf.close()

        # Create container RDF

        # If {root_path}/CSV/{table}/{table}_container.csv exist
        if os.path.exists(os.path.join(root_csv, '{}_container.csv'.format(os.path.basename(root_csv)))):

            # Create {root_path}/RDF/{table}
            if not os.path.exists(root_rdf):
                os.mkdir(root_rdf)

            # Read {root_path}/CSV/{table}/{table}_container.csv.
            # For each row/record with non-empty identity column:
            #     1. Create {root_path}/RDF/{table}/{identity}
            #     2. Create {root_path}/RDF/{table}/{indentity}.rdf
            record = pandas.read_csv(os.path.join(root_csv, '{}_container.csv'.format(os.path.basename(root_csv))), encoding = 'utf-8')
            for i in range(record.shape[0]):
                if record.iloc[i]['notation'] != '' and not pandas.isna(record.iloc[i]['notation']):
                    with open(os.path.join(root_rdf, '{}.rdf'.format(record.iloc[i]['notation'])), 'w', encoding = 'utf-8') as rdff:
                        print('Creating {}'.format(os.path.join(root_rdf, '{}.rdf'.format(record.iloc[i]['notation']))))
                        g = Graph()
                        g.bind("dct", DCT)
                        g.bind("reg", REG)
                        g.bind("ldp", LDP)
                        ref = URIRef(record.iloc[i]['id'])
                        g.add((ref, RDF.type, SKOS.Collection))
                        g.add((ref, RDF.type, REG.Register))
                        g.add((ref, RDF.type, LDP.Container))
                        for j in list(record):
                            # Skipping some columns in the CSV file to make a minimal RDF file
                            if j != 'id' and j != 'notation' and j != 'status' and j != 'description' and j != 'label' and j != 'manager' and j != 'owner':
                                continue
                            if j != 'id' and j != 'related':
                                if record.iloc[i][j] != '' and not pandas.isna(record.iloc[i][j]):
                                    if j == 'notation' or j == 'status' or j == 'modified':
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j])))
                                    elif re.match('^http://', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], URIRef(record.iloc[i][j])))
                                    elif re.match('^[0-9]+$', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j])))
                                    else:
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j], lang="en")))
                        rdff.write(g.serialize(format='xml'))
                        rdff.close()

        # Create Entity RDF

        # if {root_path}/CSV/{table}/{table}_entity.csv exist
        if os.path.exists(os.path.join(root_csv, '{}_entity.csv'.format(os.path.basename(root_csv)))):

            # Create {root_path}/RDF/{table}
            if not os.path.exists(root_rdf):
                os.mkdir(root_rdf)

            # Read {root_path}/CSV/{table}/{table}_entity.csv.
            # For each CSV file:
            #     1. Create {root_path}/RDF/{table}/{identity}.rdf
            #     2. For each row/record with non-empty identity column insert an entity into the RDF file
            record = pandas.read_csv(os.path.join(root_csv, '{}_entity.csv'.format(os.path.basename(root_csv))), encoding = 'utf-8')
            with open(os.path.join(root_rdf, '{}.rdf'.format(record.iloc[i]['notation'])), 'w', encoding = 'utf-8') as rdff:
                print('Creating {}'.format(os.path.join(root_rdf, '{}.rdf'.format(record.iloc[i]['notation']))))
                g = Graph()
                g.bind("dct", DCT)
                g.bind("reg", REG)
                g.bind("ldp", LDP)
                ref = URIRef(record.iloc[i]['id'])
                g.add((ref, RDF.type, SKOS.Collection))
                g.add((ref, RDF.type, REG.Register))
                g.add((ref, RDF.type, LDP.Container))
                for i in range(record.shape[0]):
                    if record.iloc[i]['notation'] != '' and not pandas.isna(record.iloc[i]['notation']):
                        for j in list(record):
                            # Skipping some columns in the CSV file to make a minimal RDF file
                            if j != 'id' and j != 'notation' and j != 'status' and j != 'description' and j != 'label' and j != 'manager' and j != 'owner':
                                continue
                            if j != 'id' and j != 'related':
                                if record.iloc[i][j] != '' and not pandas.isna(record.iloc[i][j]):
                                    if j == 'notation' or j == 'status' or j == 'modified':
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j])))
                                    elif re.match('^http://', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], URIRef(record.iloc[i][j])))
                                    elif re.match('^[0-9]+$', record.astype(str).iloc[i][j]):
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j])))
                                    else:
                                        g.add((ref, dictionary[j], Literal(record.iloc[i][j], lang="en")))
                rdff.write(g.serialize(format='xml'))
                rdff.close()
                        
if __name__ == '__main__':
    main()
