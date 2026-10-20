# sebastianschnoerr.github.io

## News bearbeiten

Die Meldungen im News-Bereich stehen in `news.json`. Ein Eintrag enthält `date`, `category`, `title` und `description`. Einträge können bearbeitet, entfernt oder im Array `news` ergänzt werden. Nach dem Speichern und Neuladen der Website werden die Inhalte aus der JSON-Datei angezeigt.

Die Website muss über einen Webserver geöffnet werden, damit der Browser `news.json` laden kann. Beim direkten Öffnen von `index.html` als `file://`-Datei blockieren Browser diesen Abruf häufig.

## Karten erzeugen

Führe `python Leaflet.py` aus. Das Skript erzeugt beziehungsweise überschreibt:

- `kepler.html`: interaktive Kepler.gl-Karte mit animiertem Trip-Layer und Stationspunkten.
- `threejs.html`: interaktiver Three.js-Globus mit einer automatisch animierten Route und Stationen.

Die GeoJSON- und CSV-Daten werden in die HTML-Dateien eingebettet. Die Visualisierungen laden ihre JavaScript-Bibliotheken, Basiskarte beziehungsweise Erdtextur von externen Servern und benötigen daher eine Internetverbindung. Öffne die Seiten über einen lokalen Webserver, zum Beispiel mit `python -m http.server`.