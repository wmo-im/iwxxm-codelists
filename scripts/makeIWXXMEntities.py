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
DCT.issued
DCT.relation
REG = Namespace("http://purl.org/linked-data/registry#")
REG.Register
REG.status
LDP = Namespace("http://www.w3.org/ns/ldp#")
LDP.Container
LDP.hasMemberRelation

dictionary = {'notation':SKOS.notation,
              'label':RDFS.label,
              'description':DCT.description,
              'altLabel':SKOS.altLabel,
              'source':DC.source,
              'publishDate':DCT.issued,
              'seeAlso':RDFS.seeAlso,
              'note':SKOS.note,
              'related':DCT.relation,
              'iwxxmVersionInfo':OWL.versionInfo,
              'status':REG.status}

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

        root_ttl = os.path.join(root_path, 'TTL', root_csv[len(os.path.join(root_path, 'CSV')) + 1:])
        root_rdf = os.path.join(root_path, 'RDF')
        
        # Create container TTL

        # If {root_path}/CSV/{table}/{table}_container.csv exist and under purview of TT-AvData
        relative_path=os.path.relpath(root_csv, os.path.join(root_path, 'CSV'))
        if os.path.exists(os.path.join(root_csv, '{}_container.csv'.format(os.path.basename(root_csv)))) and (relative_path != 'common' and relative_path != 'bufr4/codeflag'):

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
                    with open(os.path.join(root_ttl, '{}.ttl'.format(record.iloc[i]['notation'])), 'w', encoding = 'utf-8') as ttlf:
                        print('Creating {}'.format(os.path.join(root_ttl, '{}.ttl'.format(record.iloc[i]['notation']))))
                        g = Graph()
                        g.bind("dct", DCT)
                        g.bind("reg", REG)
                        g.bind("ldp", LDP)
                        ref = URIRef(record.iloc[i]['URI'])
                        g.add((ref, RDF.type, SKOS.Collection))
                        g.add((ref, RDF.type, REG.Register))
                        g.add((ref, RDF.type, LDP.Container))
                        for j in list(record):
                            # Skipping some columns in the CSV file to make a minimal TTL file
                            if j != 'URI' and j != 'notation' and j != 'description' and j != 'label' and j != 'altLabel' and j != 'source' and j != 'seeAlso' and j != 'note' and j != 'iwxxmVersionInfo':
                                continue
                            if j != 'URI':
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

        # Create entity TTL

        # if {root_path}/CSV/{table}/{table}_entity.csv exist and under purview of TT-AvData
        relative_path=os.path.relpath(root_csv, os.path.join(root_path, 'CSV'))
        if os.path.exists(os.path.join(root_csv, '{}_entity.csv'.format(os.path.basename(root_csv)))) and (relative_path != 'common/nil' and relative_path != 'bufr4/codeflag/0-11-030' and relative_path != 'bufr4/codeflag/0-20-008' and relative_path != 'bufr4/codeflag/0-20-012' and relative_path != 'bufr4/codeflag/0-20-041' and relative_path != 'bufr4/codeflag/0-22-061'):

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
                        ref = URIRef(record.iloc[i]['URI'])
                        g.add((ref, RDF.type, SKOS.Concept))
                        for j in list(record):
                            # Skipping some columns in the CSV file to make a minimal TTL file
                            if j != 'URI' and j != 'notation' and j != 'description' and j != 'label' and j != 'altLabel' and j != 'source' and j != 'seeAlso' and j != 'note' and j != 'iwxxmVersionInfo':
                                continue
                            if j != 'URI':
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
                    record_entity = pandas.read_csv(os.path.join(root_csv, '{0}/{1}_entity.csv'.format(record.iloc[i]['notation'], record.iloc[i]['notation'])), encoding = 'utf-8')
                    with open(os.path.join(root_rdf, 'codes.wmo.int-{0}-{1}.rdf'.format(os.path.relpath(root_csv, os.path.join(root_path, 'CSV')).replace(os.path.sep, '-'), record.iloc[i]['notation'])), 'w', encoding = 'utf-8') as rdff:
                        print('Creating {}'.format(os.path.join(root_rdf, 'codes.wmo.int-{0}-{1}.rdf'.format(os.path.basename(root_csv), record.iloc[i]['notation']))))
                        g = Graph()
                        g.bind("dct", DCT)
                        g.bind("reg", REG)
                        g.bind("ldp", LDP)
                        for k in range(record_entity.shape[0]):
                            #print(os.path.join(root_csv, '{0}/{1}_entity.csv'.format(record.iloc[i]['notation'], record.iloc[i]['notation'])))
                            if record_entity.iloc[k]['notation'] != '' and not pandas.isna(record_entity.iloc[k]['notation']):
                                n_concept = URIRef(record_entity.iloc[k]['URI'])
                                g.add((n_concept, RDF.type, SKOS.Concept))
                                for l in list(record_entity):
                                    # Skipping some columns in the CSV file to make a minimal RDF file
                                    if l != 'URI' and l != 'notation' and l != 'description' and l != 'label' and l != 'altLabel' and l != 'note' and l != 'iwxxmVersionInfo':
                                        continue
                                    if l != 'URI':
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
                                    n_register = URIRef(os.path.dirname(record_entity.iloc[k]['URI']))
                                    g.add((n_register, SKOS.member, n_concept))
                                    g.add((n_register, RDF.type, REG.Register))
                                    for j in list(record):
                                        # Skipping some columns in the CSV file to make a minimal RDF file
                                        if j != 'URI' and j != 'notation' and j != 'description' and j != 'label' and j != 'altLabel' and j != 'note' and j != 'iwxxmVersionInfo':
                                            continue
                                        if j != 'URI':
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
