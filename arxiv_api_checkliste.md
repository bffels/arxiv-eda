# arXiv API: Zu berücksichtigende Punkte für unabhängige Forschungsnutzung

Stand: 02.08.2026

Diese Zusammenfassung basiert auf den folgenden arXiv-Dokumenten:

- [Terms of Use for arXiv APIs](https://info.arxiv.org/help/api/tou.html)
- [arXiv API Basics](https://info.arxiv.org/help/api/basics.html)
- [arXiv API User Manual](https://info.arxiv.org/help/api/user-manual.html)

## 1. Rechtliche und organisatorische Anforderungen

### 1.1 Nutzung für Forschung und Bildung

- Die öffentlichen arXiv APIs dürfen für unabhängige, nicht-kommerzielle Forschungs- und Bildungszwecke genutzt werden.
- Für solche Projekte ist keine offizielle arXivLabs-Kollaboration erforderlich.
- Das Projekt sollte klar als unabhängig von arXiv erkennbar sein.

### 1.2 Anerkennung der arXiv-Nutzung

arXiv bittet darum, die Nutzung der arXiv-Daten mit folgendem Hinweis kenntlich zu machen:

> "Thank you to arXiv for use of its open access interoperability."

Dieser Hinweis sollte z. B. in der Dokumentation, im Repository, in einem Dashboard oder in einer Anwendung aufgenommen werden.

### 1.3 Keine irreführende Marken- oder Namensnutzung

Nicht verwenden, wenn dadurch eine offizielle Unterstützung durch arXiv suggeriert wird:

- „arXiv“
- „arXiv.org“
- „arXiv Labs“
- „arXivLabs“
- Logos, Farben, Webadressen oder sonstige Branding-Elemente von arXiv

Das eigene Projekt sollte nicht so wirken, als sei es ein offizielles Produkt oder ein offiziell unterstützter Dienst von arXiv.

### 1.4 Urheberrecht bei Paper-Inhalten beachten

- arXiv ist in der Regel nicht Rechteinhaber der eingereichten Paper.
- PDFs, LaTeX-Quellen und sonstige Volltexte unterliegen weiterhin dem jeweiligen Urheberrecht.
- Die Weiterverteilung von Paper-Inhalten ist nur zulässig, wenn die jeweilige Lizenz dies erlaubt oder die Rechteinhaber zugestimmt haben.

Erlaubt bzw. typischerweise unkritisch für eigene Forschung:

- Paper für die eigene Forschung herunterladen
- Paper lokal lesen und analysieren
- Paper lokal mit LLMs oder RAG-Systemen auswerten

Nicht automatisch erlaubt:

- PDFs selbst hosten
- große Paper-Sammlungen öffentlich bereitstellen
- arXiv-Inhalte über einen eigenen Dienst weiterverteilen

### 1.5 Metadaten dürfen frei genutzt werden

Beschreibende Metadaten dürfen unter CC0 genutzt werden. Dazu zählen insbesondere:

- Titel
- Abstracts
- Autoren
- arXiv-IDs
- Kategorien
- Klassifikationen
- DOI-Informationen
- Journal References

Für KI- und Research-Workflows ist es daher sinnvoll, bevorzugt mit Metadaten zu arbeiten und Volltexte nur selektiv und lokal zu verwenden.

---

## 2. Technische API-Anforderungen

### 2.1 Rate Limits einhalten

Für die Legacy APIs, einschließlich arXiv API, OAI-PMH und RSS, gelten:

- maximal ein Request alle 3 Sekunden
- nur eine aktive Verbindung gleichzeitig
- die Limits gelten für alle Maschinen unter eigener Kontrolle zusammen
- keine Umgehung durch Parallelisierung, mehrere Rechner oder mehrere Prozesse

Praktische Umsetzung in Python:

```python
import time

time.sleep(3)
```

### 2.2 Caching verwenden

- Identische Queries sollten nicht unnötig oft wiederholt werden.
- Suchergebnisse ändern sich typischerweise erst, wenn neue Artikel verarbeitet wurden.
- arXiv empfiehlt, Ergebnisse zu cachen.
- Für wiederkehrende Agenten oder Workflows sollte daher ein lokaler Cache oder eine Datenbank verwendet werden.

Empfohlene Praxis:

- einmal täglich neue Paper abrufen
- bereits verarbeitete arXiv-IDs speichern
- nur Deltas verarbeiten
- Ergebnisse lokal persistieren

### 2.3 API nicht für Massendownloads verwenden

Die normale arXiv API ist für Such- und Metadatenabfragen gedacht, nicht für großflächige Harvesting-Prozesse.

Für größere Datenmengen sollten stattdessen geprüft werden:

- OAI-PMH
- Bulk Metadata Dumps
- Full Text via S3
- sonstige Bulk-Access-Angebote von arXiv

### 2.4 Große Ergebnislisten vermeiden

- Große Resultsets erzeugen hohe Last.
- arXiv empfiehlt, Suchanfragen zu verfeinern, insbesondere bei mehr als 1.000 Treffern.
- Ergebnisse sollten in kleineren Seiten abgerufen werden.

Technische Grenzen aus dem User Manual:

- maximal 2.000 Ergebnisse pro Request-Slice
- maximal 30.000 Ergebnisse pro vollständiger Suchabfrage
- größere Requests können zu Fehlern führen

---

## 3. API-Nutzung und Query-Design

### 3.1 Basis-Endpunkt

Der zentrale API-Endpunkt lautet:

```text
https://export.arxiv.org/api/query
```

Parameter werden per HTTP GET oder POST übergeben.

### 3.2 Wichtige Query-Parameter

| Parameter | Bedeutung |
|---|---|
| `search_query` | Suchausdruck |
| `id_list` | Kommagetrennte Liste von arXiv-IDs |
| `start` | Startindex für Paging, 0-basiert |
| `max_results` | Anzahl der Ergebnisse |
| `sortBy` | Sortierfeld |
| `sortOrder` | Sortierreihenfolge |

### 3.3 Paging korrekt umsetzen

Beispiel:

```text
https://export.arxiv.org/api/query?search_query=cat:cs.AI&start=0&max_results=100
https://export.arxiv.org/api/query?search_query=cat:cs.AI&start=100&max_results=100
https://export.arxiv.org/api/query?search_query=cat:cs.AI&start=200&max_results=100
```

Zwischen mehreren Requests sollte jeweils eine Pause von mindestens 3 Sekunden eingehalten werden.

### 3.4 Nach aktuellen Papers suchen

Für aktuelle Paper empfiehlt sich:

```text
sortBy=submittedDate
sortOrder=descending
```

Beispiel:

```text
https://export.arxiv.org/api/query?search_query=cat:cs.AI&sortBy=submittedDate&sortOrder=descending&max_results=100
```

### 3.5 Datumsfilter für Delta-Abfragen nutzen

Für wiederkehrende Research-Agenten sollte der Zeitraum eingeschränkt werden:

```text
submittedDate:[YYYYMMDDTTTT+TO+YYYYMMDDTTTT]
```

Beispiel:

```text
submittedDate:[202608010000+TO+202608020000]
```

Das reduziert API-Last und verhindert doppelte Verarbeitung.

### 3.6 Suchfelder gezielt verwenden

| Feld | Präfix |
|---|---|
| Titel | `ti:` |
| Autor | `au:` |
| Abstract | `abs:` |
| Kommentar | `co:` |
| Journal Reference | `jr:` |
| Kategorie | `cat:` |
| ID | `id:` |
| Alle Felder | `all:` |

Für IDs sollte bevorzugt `id_list` statt `search_query=id:...` verwendet werden.

### 3.7 Boolesche Operatoren verwenden

Unterstützte Operatoren:

```text
AND
OR
ANDNOT
```

Beispiel:

```text
cat:cs.AI AND abs:"large language model"
```

Für komplexere Abfragen können Klammern und Phrasensuche genutzt werden. In URLs müssen Sonderzeichen korrekt encoded werden.

### 3.8 Artikelversionen berücksichtigen

- Ohne Versionsangabe wird die aktuelle Version eines Artikels abgerufen.
- Mit Versionssuffix kann eine konkrete Version abgefragt werden.

Beispiele:

```text
id_list=2508.12345
id_list=2508.12345v1
```

---

## 4. Umgang mit API-Antworten

### 4.1 Antwortformat

Die arXiv API gibt Ergebnisse im Atom-XML-Format zurück.

Typische Felder pro Paper:

- `id`
- `title`
- `published`
- `updated`
- `summary`
- `author`
- `category`
- `arxiv:primary_category`
- `arxiv:comment`
- `arxiv:journal_ref`
- `arxiv:doi`
- Links zur Abstract-Seite und zum PDF

### 4.2 Fehlerbehandlung

Fehler werden ebenfalls als Atom Feed zurückgegeben, häufig mit einem `summary`-Feld, das die Ursache beschreibt.

Typische Fehlerquellen:

- ungültiger `start`-Wert
- ungültiger `max_results`-Wert
- falsch formatierte arXiv-ID
- zu große Ergebnisabfragen
- fehlerhaft encodete Query

### 4.3 Robustheit in eigenen Workflows

Ein produktiver Workflow sollte berücksichtigen:

- HTTP-Fehler behandeln
- XML-Parsing-Fehler behandeln
- leere Ergebnislisten sauber verarbeiten
- Duplikate anhand der arXiv-ID erkennen
- Versionen berücksichtigen
- Wiederholungen und Retries begrenzen
- die 3-Sekunden-Regel auch bei Retries einhalten

---

## 5. Empfohlene Architektur für einen AI-Research-Agenten

Für einen persönlichen oder unabhängigen Forschungsworkflow empfiehlt sich:

1. Relevante Kategorien und Suchbegriffe definieren, z. B. `cs.AI`, `cs.CL`, `cs.LG`.
2. Tägliche oder wöchentliche Delta-Abfrage über `submittedDate` ausführen.
3. API-Rate-Limit strikt einhalten.
4. Ergebnisse lokal speichern, z. B. in SQLite, PostgreSQL, JSONL oder Parquet.
5. Bereits verarbeitete arXiv-IDs überspringen.
6. Metadaten für Suche, Ranking und Trendanalysen verwenden.
7. PDFs nur selektiv herunterladen, wenn sie für die eigene Analyse benötigt werden.
8. Volltexte nicht öffentlich rehosten oder weiterverteilen.
9. Zusammenfassungen, Klassifikationen oder Embeddings lokal erzeugen.
10. Quellenhinweis und arXiv-Acknowledgement in der Anwendung oder Dokumentation aufnehmen.

---

## 6. Checkliste vor Umsetzung

- [ ] Nutzung ist unabhängig, nicht irreführend und forschungsbezogen.
- [ ] arXiv Terms of Use wurden berücksichtigt.
- [ ] arXiv API Basics und User Manual wurden berücksichtigt.
- [ ] 1 Request pro 3 Sekunden wird eingehalten.
- [ ] Es wird nur eine Verbindung gleichzeitig genutzt.
- [ ] Keine Umgehung der Rate Limits durch Parallelisierung.
- [ ] Ergebnisse werden lokal gecacht.
- [ ] Identische Queries werden nicht unnötig oft wiederholt.
- [ ] Große Resultsets werden vermieden oder eingegrenzt.
- [ ] Für große Datenmengen werden Bulk-Zugänge geprüft.
- [ ] Metadaten werden bevorzugt genutzt, da sie unter CC0 stehen.
- [ ] PDFs und Volltexte werden nicht ungeprüft weiterverteilt.
- [ ] arXiv-Branding wird nicht irreführend verwendet.
- [ ] Das empfohlene arXiv-Acknowledgement wird aufgenommen.
- [ ] `submittedDate` wird für Delta-Abfragen genutzt.
- [ ] `sortBy=submittedDate` und `sortOrder=descending` werden für aktuelle Paper genutzt.
- [ ] Paging über `start` und `max_results` ist korrekt implementiert.
- [ ] Fehlerbehandlung für Atom-Fehlerantworten ist vorgesehen.
- [ ] Artikelversionen werden berücksichtigt.
- [ ] Die verarbeiteten arXiv-IDs werden gespeichert, um Duplikate zu vermeiden.

---

## 7. Kurzempfehlung

Für deinen geplanten Research-Agenten ist die sauberste Variante:

- arXiv API für Metadaten und gezielte Suchabfragen nutzen
- tägliches oder wöchentliches Delta-Crawling über `submittedDate`
- striktes Rate-Limiting mit mindestens 3 Sekunden Pause
- lokale Speicherung und Deduplizierung
- PDFs nur selektiv für eigene Forschung herunterladen
- keine öffentliche Weiterverteilung von Volltexten
- arXiv transparent als Datenquelle nennen

Damit bleibt der Workflow technisch effizient, API-schonend und im Rahmen der arXiv-Vorgaben.
