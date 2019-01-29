# Speedtestcli-db

Dieses Script verwendet das Python Programm *speedtest-cli* und schreibt die Resultate in eine SQLite Datenbank.


Dieses kleine Python Programm schickt die Speedtest-cli Resultate in eine SQLite Datenbank.
Danach kann man die DB mit z.b.: DB Browser for SQLite öffnen und auch darin ein Diagramm erstellen.


## Benötigte Pakete

* Python 3.4,3.5 oder 3.6
* PIP (für die weiteren installationen der benötigten Pakete)

## Installation

Mit pip install -r requirements.txt installiert man die restlichen Pakete.
<pre> user@NB:#$ pip install -r requirements.txt</pre>

## Verwendung

Mit 

Hilfe Ausgeben
<pre>
user@NB:#$ python speedtestcli-db.py --help
Usage: Speedtestcli-db v0.1.3 options

Options:
  -h, --help   show this help message and exit
  --run-test   run Speedtest and store result into DB
  --create-db  rename old database if exists and create new one 
</pre>

### Start einer Messung
Wenn man speedtestcli-db.py mit der option --run-test aufruft, erzeugt es falls nicht vorhanden eine SQLite Datenbank,
und startet mit der Messung.
Dabei wird das Resultat der Messung erst zum schluss gezeigt, somit kann es ein wenig dauern bis man das Resultat sieht (für die Anleitung 
dauerte es ca. 23 Sekunden).

<pre>
user@NB:#$ python speedtestcli-db.py --run-test
Speedtest Completed
=========================
        Results          
-------------------------
Ping =  45.08 ms
Download =  18.80 Mbit/s
Upload =  14.43 Mbit/s
=========================
</pre>

Wenn man jetzt nochmal den gleichen Befehl aufruft, wird das ergebnis in die bereits bestehende Datenbank geschrieben.
