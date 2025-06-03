# Dokumentation

**Das wichtigste**: Diese Tools und die Webanwendung werden angeboten wie in der LICENCE angegeben. Es gibt keine Gewähr, keinen Support oder ähnliches.

Dieses Repository enthält Tools zur Auswertung der Daten des Marktstammdatenregisters (MaStR). Derzeit sind folgende Anwendungen verfügbar:

1. **mastrtogpx**: Ein Kommandozeilen-Tool zur Konvertierung von MaStR-Daten in das GPX-Format.
2. **mastrtoplot**: Ein Kommandozeilen-Tool zur Erstellung von Plots aus MaStR-Dateien in als Vektorgraphik (SVG-Format).
3. **Webanwendung**: Eine Anwendung zur der obigen Tools also Lokalisierung von Anlagen und Anlagen-Parks, wobei benachbarte Anlagen zusammengefasst werden können, sowie das Erstellen von Plots.


## Ziel der Anwendung mastrtogpx

Mit der Anwendung sollten in erster Linie große Windparks oder Solaranlagen gefunden werden. Für diese Anlagen gilt in der Regel, dass diese Stromerzeugungseinheiten in der Regel aus vielen einzelen in einem Park zusammenstehen. Das heißt das reine Filtern auf Einheiten mit deutlich größeren Werten als 10 MW für Solaranlagen oder deutlich größer als 7MW nicht hilfreicht ist. Deshalb wird mit der Anwendung auch eine sogenannte flächige Clusterung angeboten. Dabei können auch große Eiheiten mit deutlich größer als 100 MW gesucht werden. So eine Suche ist weiter unten als Beispiel beschrieben.

## Ablaufe der Anlagensuche

### Abruf der Daten

1. Aufruf des [**MarktStammdatenregisters**](https://www.marktstammdatenregister.de/MaStR/Einheit/Einheiten/ErweiterteOeffentlicheEinheitenuebersicht)

2. **Filterung der Daten**: Erstellen Sie einen Filter, um die gewünschten Anlagen einzugrenzen. Achten Sie darauf, dass das Ergebnis **10.000 Anlagen nicht übersteigt**. Typische Filterkriterien könnten sein:
   - **Bundesland**: Auswahl des spezifischen Bundeslandes.
   - **Anlagentyp**: Auswahl des gewünschten Anlagentypen (auch mehrere).
   - **Mindestbruttoleistung**: Festlegung einer minimalen Bruttoleistung.

![MaStR Query](img/mastr_query.png)

*Hinweis*: Am 31.03.2025 lieferte eine solche Abfrage beispielsweise 844 Anlagen (sowohl in Betrieb als auch in Planung).

3. **Export der Daten**: Exportieren Sie die gefilterte Tabelle, beispielsweise als `Downloads/Stromerzeuger.csv`.

### Nutzung des Tools mastrtogpx

1. **Zugriff auf die Anwendung**: Öffne den Webbrowser und navigieren zur Webanwendung unter der Adresse 

  - [https://eduard.uber.space/mastrutils](https://eduard.uber.space/mastrutils). 
  - Bei lokaler Installation (siehe unten) würde der Zugriff über [localhost:5000](http://localhost:5000) erfolgen.

![Mastr to GPX Query und Map](img/mastr_gpx_konverter_form_map.png)

2. **Eingabe der Daten**:

In der Abfrage muss eingegeben werden:
- ein Passwort, ist beim Entwickler mit Begründung abzufragen.
- File von Marktstammdatenregister
- Query [kann auch leer sein]
- Min. Bruttoleistung der Fläche in kW:
  - für 0 werden alle Anlagen die die Query erfüllen angezeigt
  - für Werte größer 0 wird innerhalb des Radius um jede Anlage nach weiteren Anlagen gesucht und ein Zentrum
    identifiziert.
- Radius nur wesentlich bei flächiger Suche siehe Min Bruttoleistung der Fläche > 0
- Output File Name (optional)

Jetzt starten der App mit **Convert**

3. **Ergebnisanzeige**: Die Anwendung visualisiert die Anlagen auf einer Karte und fasst benachbarte Anlagen gemäß den angegebenen Kriterien zusammen.

![popup](img/popup_one_item.png)

Bei flächiger Suche werden die Anlagen zusammengefasst und die Eigenschaften einer dieser Anlagen ausgegeben 
(allerdings mit der Gesamtbruttoleistung aller Anlagen.)

![flaechige Suche](img/flaechige_suche.png)

**Hinweise**

- Stellen Sie sicher, dass die exportierte CSV-Datei die erwartete Struktur und Datenfelder enthält, um eine korrekte Verarbeitung in der Webanwendung zu gewährleisten.
- Bei Fragen oder Problemen konsultieren Sie bitte die bereitgestellten Dokumentationen.

### Download gpx

Anschließend kann das gewünschte gpx file runtergeladen und in z.b. eienr Handy-App verwendet werden. 

Hier endet die Beschreibung der Web Applikation

## Beispiel Suche nach Solarparks mit Leistungen größer als 100MW

Zunächst wird ein [**Marktstammdatenregister Auszug**](https://www.marktstammdatenregister.de/MaStR/Einheit/Einheiten/ErweiterteOeffentlicheEinheitenuebersicht) erstellt, dabei wird folgender Filer angewendet:
- "Energieträger" entspricht "Solare Strahlungsenergie"
- "Bruttoleistung der Einheit" größer als 10000
- "Betriebsstatus" entspricht nicht "Endgültig stillgelegt"

(Stand 04.04.2025: 698 Stromerzeugungseinheiten.)

Tabelle Exportieren (als .csv) 
- Datei "Stromerzeuger...csv" befindet sich jetzt in Downloads

Wechsel zu [**MaStR to GPX Konverter**](https://eduard.user.space/)

### Einfache Suche

Eingabe folgender Daten:
- Passwort: bekannt
- Filename: wie eben vom Marktstammdatenregister geholt
- Querey: leer
- Min. Bruttoleistung der Fläche in kW: 0
- Radius [m]: 2000
- Output File Name: leer

Drücke Convert

Es sollten jetzt auf der rechten Seite sämtlichen c.a. 700 Einheiten dargestellt sein.

![PV > 10MW in Deutschland](img/pv_10mw_deutschland.png)

### Flächige Suche nach Solarparks mit Gesamtleistung größer 150 MW

Einzige Unterschied zur obigen Eingabe ist die Eingabe einer Min. Bruttoleistung.

Dort kann dann 150000 [kW] stehen, erst jetzt wird der Radius relevant.
Die Karte wird jetzt deutlich übersichtlicher:

![PV > 150MW in Deutschland](img/pv_150mw_deutschland.png)

Werte über 200kW reduzieren sich die Anlagen auf die deutschlandweit größte Anlage bei Leibzig.

### Nutzung des Tools mastrtoplot

**Zugriff auf die Anwendung**: Öffne den Webbrowser und navigiere zur Webanwendung unter der Adresse

- `https://eduard.uber.space/mastrutils/`. 

- Bei lokaler Installation (siehe unten) würde der Zugriff über `http://localhost:5000` erfolgen.

Zunächst unterscheidet sich mastrtoplot von mastrtogpx gering, allerdings wird mit diesem
Tool eine Vektorgraphik mit akkumulierter Bruttoleistung abhänging von einer Zielgröße 
(z.B. Bundesland, Landkreis oder Postleitzahl) ausgegeben.

**Beispiel 1**

Als erstes Beispiel die Abfrage der Anteile von Leistungen durch Energieträger pro Landkreis.
(kurze Anmerkung: is_pv steht für Energieträger="Solare Strahlungsenergie", is_batterie ist eine Abkürzung für Batterien) 

![Akumulierte Leistung aufgeteilt in Energieträger](img/plot_energietraeger_typen.png)

Der Plot kann runtergeladen oder durch anklicken in eigenem Tab
geöffnet werden.

**Beispiel 2**

Es soll die pv Leistungen in Segmenten summiert werden. Also
im Interval zwischen 1MW und 10MV, 10MW und 100MW, sowie größer 100MW.
Für die 10er Potenzen bei den Bruttoleistungen gibt es Abkürzungen:
- Dabei steht ge_1mw für BruttoleistungDerEinheit >= 1000
- lt_100mw analog für BruttoleistungDerEinheit < 100000

![pv Leistungsaufteilung nach Bundesland](img/plot_pv_leistungs_segmente.png)

**Beispiel 3**

Es soll die pv Leistung vor oder nach einem bestimmten Datum ermittel werden, an dem die Einheit das erste Mal erwähnt wird  ermittelt wird. Dafür gibt es die Operatoren:

~~~
before_DD.MM.YYYY und
after_DD.MM.YYYY
~~~

Eine solche Abfrage könne dann aussehen:

![PV vor und nach](img/pv_nach_2023.png)

## Hinweis zu Querys

Hier gibt es auch bereits online Hilfen zu auf den Seiten.

Aus software technischen Gründen wird z.B. der Begriff
`Bruttoleistung der Einheit` zu `BruttoleistungDerEinheit`. Es können alle Begriffe in dieser Art, die im csv Header stehen verwendet werden.
Die Querys können Operatoren wie in den meisten Programmiersprächen
enthalten also (`&` für und `|` für oder u.s.w.)
Ein Ausdruck muss dabei aber immer die Form haben `Spaltenkopf == "Typ"`, anstelle von `"Typ"` und nicht `'Typ'`. Im Fall von können auch `>`, `<`, `<=` oder `>=` als Operatoren verwendet werden.

Das heißt die Abfrage:

`BruttoleistungDerEinheit > 1000` ist identisch zu `ge_1mw`.

Weiter gibt es noch Abkürzungen für:

~~~
is_active: Betriebsstatus == "in Betrieb"
~~~



----

# Mastr-Utils (lokale Version)

## Installation

1. **Repository klonen**:
   ```bash
   git clone https://github.com/fritzthekid/mastr-utils.git
   ```
2. **In das Projektverzeichnis wechseln**:
   ```bash
   cd mastr-utils
   ```
3. **Virtuelle Umgebung erstellen und aktivieren**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Für Unix-/Linux-Systeme
   venv\Scripts\activate     # Für Windows-Systeme
   ```
4. **Abhängigkeiten installieren**:
   ```bash
   pip install -e .
   ```

## Nutzung des Kommandozeilen Tool zum Lokalisieren von Energieanlagen

Die Nutzung des Tools **mastrtogpx** wird wie oben beschrieben durchgeführt.

Die kleine Hilfe liefert die Argumente:

```
mastrtogpx -h
```
Ergebnis ist eine gpx-Datei. Diese kann dann z.B. auf einer Handy-App genutzt werden.

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
mastrtogpx '~/Downloads/Stromerzeuger(15).csv' -q 'is_battery & BruttoleistungDerEinheit > 10000 & (BetriebsStatus != "Endgültig stillgelegt")' -o tmp/speicher.gpx -c Red
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

# Lizenz

Dieses Projekt steht unter der [BSD-Lizenz](LICENSE).

Für das Logo gilt die CC BY-SA 4.0 Lizenz
```
https://commons.wikimedia.org/wiki/File:Eyes-blitz.svg
```
