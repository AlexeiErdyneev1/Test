.PHONY: build validate package clean

build:
	python3 tools/build_assets.py

validate:
	python3 tools/validate_pack.py

package: validate
	python3 tools/package_pack.py

clean:
	rm -f release/Dark_Citadel_Phase_1.zip
