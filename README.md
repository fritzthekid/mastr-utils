# Helper scripts

## Create gpx-tracks from MarktStammdatenRegister Downloads

~~~
$ python python/mastr-to-gpx.py -h
~~~

Example

~~~
python/mastrtogpx.py '~/Downloads/Stromerzeuger(17).csv' -q '(BruttoleistungDerEinheit > 10000)' -o tmp/ge10mw.gpx -c 'Blue'
~~~

