# Helper scripts

## Create gpx-tracks from MarktStammdatenRegister Downloads

### Install

~~~
$ git clone git@github.com:fritzthekid/mastr-utils.git
$ cd engine_utils
$ python -m venv .venv
$ . .venv/bin/activate
(.venv) $ pip install -e .
~~~

### Usage

~~~
$ mastr-to-gpx.py -h
usage: mastrtogpx [-h] [-q QUERY] [-o OUTPUT] [-c COLOR] [-m MIN_WEIGHT] [-r RADIUS]
                  [-a] [-s] [-h_query]
                  mastr_file

Convert MaStR file to GPX file

positional arguments:
  mastr_file            Path to the MaStR CSV file

options:
  -h, --help            show this help message and exit
  -q QUERY, --query QUERY
                        Query to filter the data [default=None]
  -o OUTPUT, --output OUTPUT
                        Path to the output GPX file [default=None]
  -c COLOR, --color COLOR
                        Color of Waypoints [default='Amber']
  -m MIN_WEIGHT, --min_weight MIN_WEIGHT
                        Minimum weight of the cluster [default=0]
  -r RADIUS, --radius RADIUS
                        Radius [default=2000]
  -a, --analyse_datastruct
                        Value Ranges in Bundesland, Bruttoleistung
  -s, --show-columns    Show the columns of the MaStR file [default=False]
  -h_query, --help_query
                        Show Examples for Query [default=False]

~~~

Examples:

Show columns, to form a query
~~~
$ mastrtogpx '~/Downloads/Stromerzeuger(17).csv' -s
Columns in the MaStR file:
    MaStRNrDerEinheit
    AnzeigeNameDerEinheit
    BetriebsStatus
    Energieträger
    ....
~~~

Examples for querys:
~~~
Query to filter the data
Example: -q 'is_active & is_pv'
Example: -q 'BetriebsStatus != "In Betrieb" & is_pv & is_10mw'
Example: -q 'is_pv & Ort == "Berlin"'
Example: -q 'EnergieTräger == "Erdgas"'
~~~

Typical commands
~~~
$ mastrtogpx '~/Downloads/Stromerzeuger(17).csv' -q '(BruttoleistungDerEinheit > 20000)' -o tmp/ge10mw.gpx 
§
~~~

~~~
$ mastrtogpx '~/Downloads/Stromerzeuger(17).csv' -q 'is_pv & BetriebsStatus != "Endgültig stillgelegt"' -o tmp/x.gpx
$
~~~
