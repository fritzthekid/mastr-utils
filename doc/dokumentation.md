# Dokumentation

Die Tools in diesem Repository sollen bei der Auswertung der Daten des
Marktstammdatenregisters helfen.

Zurzeit gibt es nur ein Tool zum Lokalisieren der Anlagen.

## Tool zum Lokalisieren von Energieanlagen

Um die Anlagen zu lokalisieren, wird mit dem Tool eine GPX-Datei erzeugt, in der
die Anlagen als GPX-Waypoints (Wegpunkte) markiert sind. Informationen zur Energieanlage sind zusammen mit dem Punkt 
aufgeführt und können dann
mit den jeweiligen Tools direkt angezeigt werden.

Die Dateien können in einer Vielzahl von Handy-Apps, Laptop-Apps, aber auch direkt online
auf Karten visualisiert werden.

Bisher gibt es nur eine Kommandozeilenvariante - diese ist bisher nur mit Linux getestet, sollte aber auch plattformunabhängig funktionieren.

Typische Anwendungsfälle sind:

- Suchen großer Solaranlagen ( > 10 MW )
- Suchen großer Solarparks ( > 90 MW ). Hierbei wird die flächige Suche unterstützt, da
  die Anlagen in der Nähe mit berücksichtigt werden müssen. Das gilt, da große Solarparks
  häufig aus mehreren kleineren zusammengesetzt sind. Zwischen den Anlagen sind dann unter anderem Wildkorridore.
- Suchen von Batteriespeichern in der Nähe, auch große Speicher.
- Suchen von Windkraftanlagen und Windkraftanlagenparks.
- Alle Arten von Energieanlagen in unmittelbarer Nähe.

## Anwendung des Tools

Für jeden der obigen Fälle gibt es unterschiedliche Vorgehensweisen.
In jedem Fall muss vom Marktstammdatenregister [MaStR](https://www.marktstammdatenregister.de/MaStR/Einheit/Einheiten/ErweiterteOeffentlicheEinheitenuebersicht) eine gefilterte CSV-Datei heruntergeladen werden. Nennen wir es im folgenden Beispiel 
<code>~/Downloads/Stromerzeuger(17).csv</code>. Dieses Beispiel enthält nur die großen PV-Anlagen in ganz Deutschland.

Das Tool liefert mit <code>mastrtogpx -h</code> eine kleine Hilfe, in der die einstellbaren Parameter erläutert werden. Ein Aufruf hat immer die Gestalt:

~~~
usage: mastrtogpx [-h] [-q QUERY] [-o OUTPUT] [-c COLOR] [-m MIN_WEIGHT] [-r RADIUS]
                  [-a] [-s] [-h_query]
                  mastr_file
~~~

Das <code>mastr_file</code> ist die Datei, die vom MaStR-Server heruntergeladen wurde.
Dann können noch weitere Einschränkungen über eine Query spezifiziert werden.
So dass schließlich in einer Datei mit allen Anlagen (auch Öl und Gas) einer Stadt die jeweils 
interessanten untersucht werden können. Die Suchkriterien können mit der Option <code>-s</code> angezeigt werden. Typische Beispiele finden sich über die Option 
<code>-h_query</code>. Die Punkte können mit einer Farbe markiert sein (nicht alle Tools 
unterstützen die Anzeige). Für die Solarparks und Windparks gibt es zwei weitere 
Optionen: Mit <code>-r</code> wird ein Suchradius (um jeden Punkt) beschrieben (Standard 1 km), mit <code>-m</code> eine weitere Mindestschwelle für die Bruttoenergie-Leistung des Parks. Übersteigt der Park den Radius, können auch mehrere Aggregate nebeneinander angezeigt werden.

### Nur drei Beispiele:

**Kleinstes Beispiel**

Ein kleines Beispiel liefert ohne weitere Einschränkungen alle Anlagen, die als gefilterte Auswahl vom Server heruntergeladen wurden. Hier am Beispiel des Landkreises Ludwigsburg:

~~~
mastrtogpx '~/Downloads/Stromerzeuger(15).csv' -o tmp/alles.gpx
~~~

(Das File <code>~/Downloads/Stromerzeuger(15).csv</code> enthält alle größeren Anlagen im 
Landkreis Ludwigsburg.)

Diese Information ist geeignet, um schnell alle Anlagen in der Region zu finden und
die wichtigsten Faktoren zu ermitteln.

**Suche der Großspeicher in der Nähe**:

Dieses Beispiel hilft, den Stromspeicher in Marbach genauer zu lokalisieren. Geeignet für
die nächste Fahrradtour. Das Ergebnis wird unten mit Hilfe der Handy-App OSMAnd dargestellt.

~~~
mastrtogpx '~/Downloads/Stromerzeuger(15).csv' -q 'is_speicher & BruttoleistungDerEinheit > 10000 & (BetriebsStatus != "Endgültig stillgelegt")' -o tmp/speicher.gpx -c Red
~~~

**Suche großer Solarparks in Deutschland**:

Das Zurechtfinden der wirklich großen Solarparks hilft die folgende Suche und das Ergebnis.
(Siehe auch Online-Betrachter sowie Viking als PC-Tool)

~~~
mastrtogpx '~/Downloads/Stromerzeuger(17).csv' -q 'is_pv & BruttoleistungDerEinheit > 10000 & (BetriebsStatus != "Endgültig stillgelegt")' -m 90000 -r 1000 -o tmp/ge_90_1000.gpx -c Black
~~~

## Tools zur Visualisierung von GPX-Dateien

Hier sind Links zu einigen Online-Viewern:

- [j-berkemeier](https://www.j-berkemeier.de/ShowGPX.html)

![](img/online2_10_90_1000_bei_Leibzig-SILUX-Solarpark.png)

- [gpx.studio](https://gpx.studio/)

![](img/online1-ge_90_1000.png)

Mobile:

- [OSMAnd](https://osmand.net/)

Beispiel für die Suche eines Großspeichers in der Nähe für die nächste Fahrradtour:

![OSMAnd](img/OsmAnd_Marbach_Speicher_100mW.jpg)

PC:

- [Viking](https://wiki.openstreetmap.org/wiki/Viking)

![Viking](img/Viking_10_90_1000_bei_Leibzig-SILUX-Solarpark.png)



