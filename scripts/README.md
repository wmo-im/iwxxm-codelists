## Workflows

### Generate TTL and RDF
The `.github/workflows/build.yml` runs on push.  It creates all `ttl` and `rdf` files from the csv source.

## Testing and management
These scripts provides tools written in Python to check content consistency with the published test and prod registers and to upload changes.

* generate `ttl` and `rdf` files 
```
python3 -m scripts.makeIWXXMEntities
```
 
* check for existence and consistency against target registry
```
tmode=test python3 -m scripts.check_urls
```

* check for existence and consistency against target registry and send outputs for upload to a named local file 

```
tmode=test outfile=upload/<output_filename> python3 -m scripts.check_urls
```

* upload new (post) and updates (put) (using JSON encoded text input at the command line)

```
python -m scripts.uploadChanges.py <username> <password> test '{"PUT": [],"POST": []}'
```

* upload new (post) and updates (put) (using JSON encoded local file input)

```
python3 -m scripts.uploadChanges <username> <temporaryKey> test upload/<output_filename>
```
