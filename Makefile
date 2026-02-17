

get-dharmae: # NEEDS TESTING
	uv run python omeka_classic_to_rocrate.py -d ~/working/dharmae/dharmae/  -u https://dharmae.research.uts.edu.au/api   -m ./examples/dharmae/dharmae-ro-crate-metadata-template.json   ~/working/dharmae/temp/ro-crate-metadata_raw.json
	uv run python doctor_rocrate.py -m examples/dharmae/dharmae_mapping.json  ~/working/dharmae/temp/ro-crate-metadata_raw.json  ~/working/dharmae/dharmae/ro-crate-metadata.json
	
get-f2f: 
	mkdir -p f2f-out
	uv run python omeka_classic_to_rocrate.py   -d f2f-out  -u  http://omeka.uws.edu.au/farmstofreeways/api  -r ./examples/f2f/template/ro-crate-metadata.json -m  ./examples/f2f/farms_to_freeways_mapping.json   f2f-out/ro-crate-metadata.json
	rocxl f2f-out
	mkdir -p f2f-out/provenance
	cp f2f-out/ro-crate-metadata.*  f2f-out/provenance/





