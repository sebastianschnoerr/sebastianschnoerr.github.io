# sebastianschnoerr.github.io

## News bearbeiten

Die Meldungen im News-Bereich stehen in `news.json`. Ein Eintrag enthält `date`, `category`, `title` und `description`. Einträge können bearbeitet, entfernt oder im Array `news` ergänzt werden. Nach dem Speichern und Neuladen der Website werden die Inhalte aus der JSON-Datei angezeigt.

Die Website muss über einen Webserver geöffnet werden, damit der Browser `news.json` laden kann. Beim direkten Öffnen von `index.html` als `file://`-Datei blockieren Browser diesen Abruf häufig.