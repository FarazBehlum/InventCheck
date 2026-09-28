# ZIP coordinate attribution

`us_zips.csv` is derived from the [GeoNames US postal-code archive](https://download.geonames.org/export/zip/US.zip), downloaded 2026-09-27. GeoNames postal data is licensed under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). Attribution: GeoNames, https://www.geonames.org/.

Changes: retain ZIP, city, state, latitude, longitude; restrict to all 50 states and DC; collapse duplicate ZIP rows by first occurrence; sort by ZIP. Coordinates approximate postal locations, not street addresses or driving distance. This snapshot is not a guarantee of all current USPS ZIPs; unknown ZIPs return a validation error. Territories and military ZIPs are outside this MVP dataset.

Refresh from the repository root:

```sh
curl -fL https://download.geonames.org/export/zip/US.zip -o /tmp/inventcheck-us.zip
python3 scripts/import_zips.py /tmp/inventcheck-us.zip
```

Review the data diff, rerun tests, and update the download date before committing a refreshed snapshot. App startup performs no download.
