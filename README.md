# omeka-datacrate-tools

This repository contains some  python3 scripts to push  DataCrates/RO-Crates in and out of Omeka S and to move data out of Omeka Classic. As time permits we're updating these scripts to follow the [RO-Crate specification](https://researchobject.github.io/ro-crate/).

These scripts are packaged for use with uv via pyproject.toml.


## The scripts

There are two script for extracting data from Omeka repositories:

-  [`omeka_classic_to_rocrate.py`](./omeka_classic_to_rocratecrate.py) exports
   from Omeka Classic repositories into DataCrate format.


-  *NEEDS UPDATING* [`omeka_s_to_ro-crate.py`](./omeka_s_to_ro-crate.py) exports from Omeka S
   to DataCrate format, it puts metadata into both CATALOG.json and into a file
   containing raw Omeka S API data: API.json.

There are two ways to import DataCrate metadata into Omeka S.

-   *NEEDS UPDATING* [`datacrate_to_omeka_s.py`](./datacrate_to_omeka_s.py) will work with ANY
    DataCrate data, and uses the CATALOG.json file for metadata. To run this the target repository must have the schema.org vocabulary installed.
-   *NEEDS UPDATING* [`reconstitute_omeka_s.py`](./reconstitute_omeka_s.py) uses the API dump from an omeka site.



# Audience =

This is for experienced Python developers

# An example

This is a worked example of how to export data from an Omeka Classic repostiory to an RO-Crate, and optionally to re-upload it.

The example repository "Farms to Freeways" is here:
<http://omeka.scem.ws/farmstofreeways/exhibits/show/viewall>.

## Get this code and install with uv

-  Get the code:
    ```
   git s
    ```

-  Install dependencies (including TinyCrate from GitHub) with uv:

   ```
   uv sync
   ```

-  Run scripts with uv:

   ```
   uv run python omeka_classic_to_rocrate.py --help
   ```


# Download data from Omeka Classic

-  To see what the ```omeka_classic_to_rocrate.py``` script takes as arguments type:

```

python omeka_classic_to_rocrate.py --help

```

```
usage: omeka_classic_to_rocrate.py [-h] [-k KEY] [-u API_URL] [-d DOWNLOAD_CACHE] [-r ROCRATE] [-n] [-m MAPPING] [-l] [outfile]

positional arguments:
  outfile

options:
  -h, --help            show this help message and exit
  -k, --key KEY         Omeka API Key
  -u, --api_url API_URL
                        Omeka API Endpoint URL (hint, ends in /api)
  -d, --download_cache DOWNLOAD_CACHE
                        Path to a directory in which to cache dowloads (defaults to ./data)
  -r, --rocrate ROCRATE
                        RO-Crate metadata document to use as a template (will be updated with items from Omeka)
  -n, --no_relations    Don't try to fetch item relations
  -m, --mapping MAPPING
                        JSON mapping file
  -l, --link            Try to link items using name values instead of just IDs

```

-  For this example use this command:

```
make get-f2f

```


This creates an RO-Crate directory ./f2f2-out with the data from Omeka.




<!--
# Download data from Omeka S 

Use the script `omeka_s_to_ro-crate.py`.

Usage:
```
> python omeka_s_to_ro-crate.py -h
usage: omeka_s_to_ro-crate.py [-h] [-k KEY_IDENTITY] [-c KEY_CREDENTIAL]
                              [-u API_URL] [-d DOWNLOAD_CACHE] [-m METADATA]
                              [outfile]

positional arguments:
  outfile

optional arguments:
  -h, --help            show this help message and exit
  -k KEY_IDENTITY, --key-identity KEY_IDENTITY
                        Omeka S Key indetity
  -c KEY_CREDENTIAL, --key-credential KEY_CREDENTIAL
                        Omeka S Key credential
  -u API_URL, --api_url API_URL
                        Omeka API Endpoint URL (hint, ends in /api)
  -d DOWNLOAD_CACHE, --download_cache DOWNLOAD_CACHE
                        Path to a directory in which to cache dowloads
                        (defaults to ./data)
  -m METADATA, --metadata METADATA
                        Datacrate Metadata file (CATALOG.json) to use as a
                        base.
```

See the above section on downloading from Omeka Classic for how to fix the resulting file using `doctor_datacrate.py`


# Use Calcyte.js to bag the content and create a index.html

To generate HTML (-g), bag (-b) and zip (-z) ```~/working/f2f/farms_to_freeways/```:

-  use this command:

    ```
    calcyfy -z  -g  -b ~/working/f2f/bags/ ~/working/f2f/farms_to_freeways/
    ```



# Upload RO-Crate data into Omeka S



-  Install Omeka S - eg from here: https://git.research.uts.edu.au/eresearch/infra-aws-omeka-s/-/tree/master/docker

-  Load the Schema.org vocab into Omeka S
   - Go to https://schema.org/docs/developers.html
   -  Download the Vocabulary definition file for schema in Format: Triples
      <https://schema.org/version/latest/schemaorg-current-http.ttl>
   -  In Omeka S:
      -  click on Vocabularies and add Sechma.org using the file you downloaded above schemaorg-current-http.ttl
      -  Get an API key identity and crednetial (under Users)


-  Define environment variables like:
   ```
   export OMEKA_KEY_IDENTITY=bJCEy...j
   export OMEKA_KEY_CREDENTIAL=9Fzvqy...O

   ```


-  Run this:
    ```
    python datacrate_to_omeka_s.py   -u http://localhost/api/ -s ~/working/f2f/data_migration/saved_ids  ~/working/f2f/farms_to_freeways/CATALOG.json -f
    ```


TIPS / troubleshooting:

-  Files failing to upload? YOu need to set the upload limit in PHP (TODO: how???)

-  If you have errors then the local cache of IDs might get corrupted, delele it:
  ```
  rm ~/working/f2f/data_migration/saved_ids
  ```

-  To turn off file uploads remove the -f option - this will speed things up considerably for testing.
-->
