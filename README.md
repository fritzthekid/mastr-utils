# Helper Scripts to Analyze MarktStammdatenRegister

All tools provided require at least one download from the MarktStammdatenRegister.
Let's assume it's the file <code>'~/Downloads/Stromerzeuger(17).csv'</code>.
The file is already a filtered set of the register; otherwise, it cannot be retrieved.

**Marktstammdatenregister** [MaStR](https://www.marktstammdatenregister.de/MaStR/Einheit/Einheiten/ErweiterteOeffentlicheEinheitenuebersicht)

The extended overview is necessary because only here is information such as the geographical coordinates of the installations included.

Actually, there is only one tool so far: **<code>mastrtogpx</code>**.

## Create GPX Tracks from MarktStammdatenRegister Downloads

My interest is to find energy plants on a map. The energy plants have many features
that can be used to filter the results. To view the dots on a map, this tool extracts 
a GPX file, where each plant is a waypoint. The file can be visualized online, on a mobile phone
(any tracking app supports GPX), or with apps on a laptop.

### Install

~~~
$ git clone git@github.com:fritzthekid/mastr-utils.git
$ cd mastr-utils
$ python -m venv .venv
$ . .venv/bin/activate
(.venv) $ pip install -e .
~~~

### Usage

~~~
$ mastrtogpx -h
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
                        Color of waypoints [default='Amber']
  -m MIN_WEIGHT, --min_weight MIN_WEIGHT
                        Minimum weight of the cluster [default=0]
  -r RADIUS, --radius RADIUS
                        Radius [default=2000]
  -a, --analyse_datastruct
                        Value ranges in Bundesland, Bruttoleistung
  -s, --show-columns    Show the columns of the MaStR file [default=False]
  -h_query, --help_query
                        Show examples for query [default=False]

~~~

Examples:

Show columns to form a query
~~~
$ mastrtogpx '~/Downloads/Stromerzeuger(17).csv' -s
Columns in the MaStR file:
    MaStRNrDerEinheit
    AnzeigeNameDerEinheit
    BetriebsStatus
    Energieträger
    ....
~~~

Examples for queries:
~~~
Query to filter the data
Example: -q 'is_active & is_pv'
Example: -q 'BetriebsStatus != "In Betrieb" & is_pv & is_10mw'
Example: -q 'is_pv & Ort == "Berlin"'
Example: -q 'EnergieTräger == "Erdgas"'
~~~

Typical commands
~~~
mastrtogpx '~/Downloads/Stromerzeuger(17).csv' -q '(BruttoleistungDerEinheit > 20000)' -o tmp/ge10mw.gpx 
~~~

~~~
mastrtogpx '~/Downloads/Stromerzeuger(17).csv' -q 'is_pv & BetriebsStatus != "Endgültig stillgelegt"' -o tmp/x.gpx
~~~

### Tools to Visualize GPX Files

Here are links to some online viewers:

- [j-berkemeier](https://www.j-berkemeier.de/ShowGPX.html)
- [gpx.studio](https://gpx.studio/)

Mobile:

- [OSMAnd](https://osmand.net/)

PC:

- [Viking](https://wiki.openstreetmap.org/wiki/Viking)