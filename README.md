# lte_cell_locate

>This is a script used to return an approximate location based on a hex string input containing cell tower information.
>It makes use of Google Geolocation and Maps APIs.

- Hex string input is parsed
- Geolocation request is formed
- Geolocation response is parsed
- Maps URL is formed with parsed Geoloc response (lat, lng) & opened

- *If input is left empty, a known test string is used instead* 

## Usage
You will need need a Google Geolocation API key(GEO_API_KEY) and the API usage and billing information (you need to enable billing on your project).

- Data piped to stdin must contain cell tower information.

```bash
$ export GEO_API_KEY=value
$ echo "data_to_parse" | python3 cell_geolocate.py
```

- Script will exit with status 0 if successful
- exit 1: input parse error
- exit 2: cell info not found
- exit 3 | 4: geolocation request failed
