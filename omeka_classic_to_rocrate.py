"""

Quick and dirty script to create a DataCrate from an Omeka Classic repository

At this stage it just handles working datacrates, not bagged data crates

TODO:
 - Create the index.html file
 - Handle bagging

"""


from sys import stdout, stdin
import argparse
import json
import urllib.parse
import os
import json
import csv
import shelve
import copy
import requests
import pickle
import sys
from pathlib import Path
from tinycrate.tinycrate import TinyCrate, minimal_crate


def deal_with_files(crate, item_json, item, data_dir):
    """Handle any dowloads, cache as files locally, then add files to crate"""

    url = item["files"]["url"]
    print("Files url", url)
    r = requests.get(url)

    for file in r.json():
        download_this = True
        file_url = file["file_urls"]["original"]
        filename = file["original_filename"]
        print("file_url", file_url)
        if file_url:

            new_path = os.path.join(data_dir, str(item["id"]))
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            file_path = os.path.join(new_path, filename)
            print("Local filename: %s", file_path)

            # Check if we have one the same size already
            if os.path.exists(file_path):
                r = requests.head(file_url)
                if "content-length" in r.headers:
                    download_size = r.headers["content-length"]
                else:
                    download_size = -1

                file_size = os.path.getsize(file_path)
                # print("Download size", download_size, "Local file size", file_size)
                if download_size == str(file_size):
                    print(
                        "Already have a download of the same size: %s" % file_size
                    )
                    download_this = False

            if download_this:
                # try:
                # print("Downloading")
                r = requests.get(file_url)
                open(file_path, "wb").write(r.content)

                # except:
                # print ("Some kind of download error happened fetching %s - pressing on" % file_url)
            file_rel_path = os.path.join(

                os.path.basename(data_dir), os.path.relpath(
                    file_path, data_dir)
            )
            # Add file entity to crate
            crate.add("File", file_rel_path, {"path": file_rel_path})

            if "hasFile" not in item_json:
                item_json["hasFile"] = []
            item_json["hasFile"].append({"@id": file_rel_path})


class Elements:
    def __init__(self):
        self.element_names = {}

    def get_element_name(self, id):
        if id not in self.element_names:

            r = requests.get(endpoint + "/elements/" + str(id))
            element = json.loads(r.content)
            self.element_names[id] = element["name"]
        return self.element_names[id]


class Relations:
    def __init__(self):
        self.relation_names = {}

    def get_relation_name(self, id):
        if id not in self.relation_names:
            r = requests.get(
                endpoint + "/item_relations_properties/" + str(id)
            )
            print(endpoint + "/item_relations_properties/" + str(id))
            element = json.loads(r.content)
            print(element)
            self.relation_names[id] = element["local_part"]
        return self.relation_names[id]


class ItemTypes:

    def __init__(self):
        self.item_types = {}

    def get_item_type_name(self, item_json, id):
        """Legacy method for compatibility - appends to @type list"""
        type_name = self.get_item_type_name_str(id)
        if type_name:
            item_json["@type"].append(type_name)

    def get_item_type_name_str(self, id):
        """Get item type name as string"""
        if id not in self.item_types:
            r = requests.get(endpoint + "/item_types/" + str(id))
            element = json.loads(r.content)
            self.item_types[id] = element["name"]
        return self.item_types[id]


relation_stash = Relations()
item_type_stash = ItemTypes()
collection_ids = {}
names = {} #Look up ID by name


def get_relations(item_json, id):
    """ Find all inter-related items. Note that this will fail for more than 50 relations"""

    r = requests.get(
        endpoint + "/item_relations?subject_item_id=%s" % (str(id)))
    relations = json.loads(r.content)
    print(endpoint + "/item_relations?subject_item_id=%s" % (str(id)))
    for rel in relations:
        # relation_name = relation_stash.get_relation_name(rel["property_id"])
        print("rel:", rel)
        if ("property_local_part" in rel):
            relation_name = rel["property_local_part"]
            item_json[relation_name] = {
                "@id": "#" + str(rel["object_item_id"])}

    # {'id': 165, 'subject_item_id': 149,
    # 'property_id': 39, 'object_item_id': 167, 'property_vocabulary_id': 1, 'pro


def load_collections(endpoint, api_key, data_dir, crate, mapper, try_linking):
    page = 1
    while True:
        r = requests.get(endpoint + "/collections?page=" + str(page))
        page += 1
        items = json.loads(r.content)
        if items == []:
            break

        print("Got a set of %s collections" % len(items))
        for item in items:
            id = str(item["url"])
            collection_ids[str(item["id"])] = id
            item_props = {"pcdm:memberOf": {"@id": "./"}}
            for val in item["element_texts"]:
                text = val["text"]
                # uri = val["uri"]
                el_id = val["element"]["id"]
                el_name = els.get_element_name(el_id)
                el_name = el_name.replace(" ", "")
                el_name = el_name[0].lower() + el_name[1:]
                if el_name in mapper:
                    el_name = mapper[el_name]
                if not el_name in item_props:
                    item_props[el_name] = []
                item_props[el_name].append(text)
                if el_name == "name" and try_linking:
                    names[text] = id
            crate.add("RepositoryCollection", id, item_props)
    return crate


def load_items(endpoint, api_key, data_dir, metadata_file, mapper, try_linking):

    if metadata_file:
        # Load existing crate from metadata file
        print("Loading crate from metadata file:", metadata_file)
        crate_data = json.load(open(metadata_file))
        crate = TinyCrate(crate_data)
    else:
        # Create a new crate
        crate = minimal_crate()
       
    crate = load_collections(endpoint, api_key, data_dir, crate, mapper, try_linking)
    # TODO: Get root data entity ID from crate and use that for collection membership instead of "./"
    rootID = crate.root()["@id"]
    print("ROOT ID", rootID)   
    page = 1

    while True:
        r = requests.get(endpoint + "/items?page=" + str(page))
        page += 1
        items = json.loads(r.content)
        if items == []:
            break

        print("Got a set of %s items" % len(items))
        for item in items:
            in_collection = str(item["collection"]["id"])
            id = str(item["id"])
            item_id = item["url"]
            item_types = ["RepositoryObject"]
            #
            item_props = {"pcdm:memberOf": {
                "@id": collection_ids[in_collection]}}

            if "item_type" in item and item["item_type"] and "id" in item["item_type"]:
                item_type = item["item_type"]["id"]
                # Get item type name and add to types list
                item_type_name = item_type_stash.get_item_type_name_str(
                    item_type)
                if item_type_name:
                    item_types.append(item_type_name)

            for val in item["element_texts"]:
                text = val["text"]
                # uri = val["uri"]
                el_id = val["element"]["id"]
                el_name = els.get_element_name(el_id)

                el_name = el_name.replace(" ", "")
                el_name = el_name[0].lower() + el_name[1:]
                # Update property name if it's in the mapping file
                if el_name in mapper:
                    el_name = mapper[el_name]
                if not el_name in item_props:
                    item_props[el_name] = []
                if el_name == "name" and try_linking:
                    names[text] = item_id
                item_props[el_name].append(text)

            # Geolocations
            if "geolocations" in item["extended_resources"]:
                place_url = item["extended_resources"]["geolocations"]["url"]
                # TODO - Up to 50...
                r = requests.get(place_url)
                place = r.json()
                place_props = {}
                if "address" in place:
                    place_props["address"] = place["address"]
                    place_props["@label"] = place["address"]
                if "latitude" in place and "longitude" in place:
                    geo_props = {
                        "latitude": str(place["latitude"]),
                        "longitude": str(place["longitude"]),
                        "@label": "Lat: %s Long: %s "
                        % (str(place["latitude"]), str(place["longitude"])),
                    }
                    crate.add("GeoCoordinates", place_url + "#GEO", geo_props)
                    place_props["geo"] = {"@id": place_url + "#GEO"}
                crate.add("Place", place_url, place_props)
                item_props["contentLocation"] = {"@id": place_url}

            deal_with_files(crate, item_props, item, data_dir)
            if not args["no_relations"]:
                get_relations(item_props, id)
            # Add item to crate with proper type
            crate.add(item_types[0] if len(item_types) ==
                      1 else "RepositoryObject", item_id, item_props)
            # If there are multiple types, update the entity
            if len(item_types) > 1:
                entity = crate.get(item_id)
                if entity:
                    entity["@type"] = item_types

    if try_linking:
        # Try to link any unlinked items based on name matching
        for item in crate.all():
            for prop, value in item.items():
                if prop != "name": #Don't try to link on name properties
                    if isinstance(value, list):
                        for v in value:
                            if isinstance(v, str) and v in names:
                                item[prop] = {"@id": names[v]}
                elif isinstance(value, str) and value in names:
                    item[prop] = {"@id": names[value]}  

    # Set the crate directory for proper file resolution
    crate.set_directory(Path(data_dir).parent if data_dir else Path.cwd())

    # Write output using TinyCrate's write_json or json() method
    if args["outfile"].name == '<stdout>':
        args["outfile"].write(crate.json())
    else:
        # Write to file using TinyCrate's write_json
        output_path = Path(args["outfile"].name)
        print("Output path:", output_path)
        if output_path.suffix == '.json':
            # Write just the JSON file
            args["outfile"].write(crate.json())
        else:
            # Write the full crate to a directory
            crate.write_json(output_path.parent)


# Define and parse command-line arguments


if __name__ == "__main__":
    els = Elements()
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--key", default=None, help="Omeka API Key")
    parser.add_argument(
        "-u",
        "--api_url",
        default=None,
        help="Omeka API Endpoint URL (hint, ends in /api)",
    )
    parser.add_argument(
        "-d",
        "--download_cache",
        default="./content",
        help="Path to a directory in which to cache dowloads (defaults to ./data)",
    )
    parser.add_argument(
        "-r",
        "--rocrate",
        default=None,
        help="RO-Crate metadata document to use as a template (will be updated with items from Omeka)",
    )

    parser.add_argument(
        "-n",
        "--no_relations",
        action='store_true',

        help="Don't try to fetch item relations",
    )

    parser.add_argument(
        "-m", "--mapping", type=argparse.FileType("r"), help="JSON mapping file")
    parser.add_argument("-l", "--link", default=False, action='store_true',
                    help="Try to link items using name values instead of just IDs")

    parser.add_argument(
        "outfile", nargs="?", type=argparse.FileType("w"), default=sys.stdout
    )
    

    args = vars(parser.parse_args())
    endpoint = args["api_url"]
    api_key = args["key"]
    data_dir = args["download_cache"]
    metadata_file = args["rocrate"]
    if api_key:
        auth = {"key": api_key}
    else:
        auth = {}

    if args["mapping"]:
        mapper = json.loads(args["mapping"].read())
    else:
        mapper = {}

    load_items(endpoint, api_key, data_dir, metadata_file, mapper, args["link"])
