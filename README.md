# 🔥 Shawarma Falafel City — Website

Bestellwebseite für ein Kebab-/Falafel-Restaurant in der Schweiz.
Kunden können online bestellen (Abholung oder Lieferung). Der Besitzer verwaltet alles über das Admin-Panel.

---

## Stack (Technologien)

| Was | Womit |
|---|---|
| Backend (Server-Logik) | Python / Django 5 |
| Datenbank | PostgreSQL 16 (läuft in Docker) |
| Frontend (Aussehen) | HTML + CSS + JavaScript (kein Framework) |
| Admin-Panel | Django Admin (eingebaut) |
| Umgebungsvariablen | `.env` Datei (python-decouple) |
| Öffentlicher Tunnel (Test) | Cloudflare Tunnel (`cloudflared`) |

---

## Ordnerstruktur

```
shawarma_city/
│
├── shawarma_city/          ← Django-Projekteinstellungen
│   ├── settings.py         ← Konfiguration (DB, Sprache, Dateipfade...)
│   ├── urls.py             ← Haupt-URL-Routen
│   └── wsgi.py             ← Produktionsserver-Einstiegspunkt
│
├── shop/                   ← Die eigentliche App (Logik)
│   ├── models.py           ← Datenbank-Tabellen (Category, MenuItem, Order...)
│   ├── views.py            ← Was bei jedem URL passiert
│   ├── urls.py             ← URL-Routen der App
│   ├── forms.py            ← Bestellformular (Checkout)
│   └── admin.py            ← Admin-Panel Konfiguration
│
├── templates/              ← HTML-Seiten
│   ├── base.html           ← Grundgerüst (Navbar, Footer) — alle Seiten erben davon
│   ├── admin/
│   │   └── base_site.html  ← Admin-Panel angepasst (Kurdisch-Toggle)
│   └── shop/
│       ├── home.html       ← Startseite (Hero, Featured Items)
│       ├── menu.html       ← Speisekarte (Tabs: Essen / Getränke)
│       ├── cart.html       ← Warenkorb
│       ├── checkout.html   ← Bestellformular
│       ├── order_success.html ← Bestätigungsseite
│       └── dashboard.html  ← Besitzer-Dashboard (nur für Staff)
│
├── static/
│   ├── css/
│   │   └── main.css        ← Gesamtes Styling der Webseite
│   ├── js/
│   │   └── animations.js   ← Scroll-Animationen, Hover-Effekte
│   └── img/                ← Logo, Hintergrundbilder
│
├── media/                  ← Von Admin hochgeladene Bilder (Menü-Fotos)
│
├── .env                    ← Geheime Einstellungen (nicht in Git!)
├── app.py                  ← Server starten: `python app.py runserver`
└── requirements.txt        ← Python-Pakete
```

---

## Server starten

```bash
# 1. Conda-Umgebung aktivieren
conda activate website

# 2. Docker (PostgreSQL) starten — falls nicht läuft
docker start <container-name>

# 3. Django-Server starten
python app.py runserver

# Seite: http://127.0.0.1:8000
# Admin: http://127.0.0.1:8000/admin
```

### Öffentlich testen (Cloudflare Tunnel)
```bash
# Neues Terminal öffnen, dann:
cloudflared tunnel --url http://127.0.0.1:8000
# → Gibt eine öffentliche URL aus, z.B. https://xyz.trycloudflare.com
```

---

## Datenbank

Drei wichtige Tabellen:

| Tabelle | Was sie speichert |
|---|---|
| `Category` | Kategorien: "Essen", "Getränke" |
| `MenuItem` | Einzelne Artikel: Name, Preis, Bild, Kategorie |
| `Order` | Bestellungen: Kunde, Artikel, Status, Typ (Abholung/Lieferung) |
| `OrderItem` | Zeile in einer Bestellung: welcher Artikel, wie viele |

Migrations ausführen (wenn Modelle geändert wurden):
```bash
python app.py makemigrations
python app.py migrate
```

---

## Frontend verstehen

### Wie die Seiten aufgebaut sind

Alle Seiten basieren auf **`templates/base.html`**. Das ist das Grundgerüst:
- Topbar (Telefon, Öffnungszeiten)
- Navbar (Logo, Links, Warenkorb-Badge, Hamburger für Handy)
- `{% block content %}` — hier kommt der Inhalt jeder Seite rein
- Footer
- `animations.js` wird auf jeder Seite geladen

Jede andere HTML-Datei beginnt mit:
```html
{% extends 'base.html' %}
{% block content %}
  ... Inhalt der Seite ...
{% endblock %}
```

### CSS (`static/css/main.css`)

Die Datei ist in Abschnitte aufgeteilt (mit `/* === ... === */` Kommentaren):

| Abschnitt | Was er macht |
|---|---|
| CSS-Variablen | Farben (Feuer-Orange, Gelb, Dunkel) — zentral änderbar |
| Reset / Base | Schrift, Grundfarben, Body |
| Feuer-Ränder | `.fire-edge` — fixierte Feuerbilder links/rechts |
| Topbar | Schmale Info-Leiste ganz oben |
| Navbar | Navigation mit Hamburger-Menü für Handy |
| Hero | Grosses Bild auf der Startseite |
| Menükarten | `.menu-card` — Karte mit Bild, Name, Preis |
| Warenkorb | Tabelle mit Bestellpositionen |
| Checkout | Formular-Styling |
| Dashboard | Besitzer-Übersicht |
| Animationen | `.pop-ready` / `.pop-in` — Aufpopp-Effekte |
| Responsive | `@media` — Anpassungen für Tablet und Handy |

### JavaScript (`static/js/animations.js`)

Eine einzige Datei, die auf allen Seiten läuft. Sie macht:

1. **Scroll-Animationen** — Elemente (Karten, Überschriften) poppen auf, wenn sie ins Bild scrollen (`IntersectionObserver`)
2. **Hover-Effekt** — Menükarten leuchten orange beim Drüberfahren
3. **Button-Bounce** — "Hinzufügen"-Button springt kurz beim Klicken
4. **Aktiver Nav-Link** — aktueller Link in der Navbar wird markiert
5. **Scroll-Indikator** — Pfeil auf der Startseite verschwindet beim Scrollen
6. **Tab-Bounce** — Kategorie-Tabs springen beim Klicken

### Wie der Warenkorb funktioniert

Der Warenkorb wird **nicht in der Datenbank** gespeichert — er lebt in der **Django-Session** (serverseitig im Arbeitsspeicher):

```
session['cart'] = {
    "3": 2,   # MenuItem ID 3, Menge 2
    "7": 1,   # MenuItem ID 7, Menge 1
}
```

Erst wenn der Kunde auf "Bestellen" klickt, wird eine echte `Order` in der Datenbank gespeichert.

### Wie das Admin-Panel funktioniert

- URL: `/admin/`
- Login mit dem Django-Superuser-Account
- Sprache: Deutsch (Standard), Kurdisch per Knopfdruck (gespeichert im Browser)
- Der Kurdisch-Toggle ist in `templates/admin/base_site.html` implementiert (reines JavaScript, ersetzt DOM-Texte)
- Der Besitzer kann direkt in der Liste den Status einer Bestellung ändern

---

## Umgebungsvariablen (`.env`)

```
SECRET_KEY=...          ← Django-Sicherheitsschlüssel (geheim halten!)
DEBUG=True              ← False in Produktion!
ALLOWED_HOSTS=localhost,127.0.0.1,.trycloudflare.com
DB_NAME=shawarma_city
DB_USER=shawarma_user
DB_PASSWORD=...
DB_HOST=localhost
DB_PORT=5432
```

---

## URLs (Routen)

| URL | Seite |
|---|---|
| `/` | Startseite |
| `/menu/` | Speisekarte |
| `/cart/` | Warenkorb |
| `/checkout/` | Bestellformular |
| `/order/<id>/success/` | Bestellbestätigung |
| `/dashboard/` | Besitzer-Dashboard (nur Staff) |
| `/admin/` | Django Admin-Panel |
