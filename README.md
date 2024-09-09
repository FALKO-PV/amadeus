![image](docs/header.png)

# Unterrichtsevaluation mit AMADEUS – zuverlässig, datenschutzkonform und kostenlos

Mithilfe von AMADEUS (Anonym nutzbare Mobile App zur digitalen Evaluation des Unterrichts durch Schüler:innen) können Sie als Lehrkraft die Qualität Ihres Unterrichts einfach, schnell und zuverlässig durch Ihre Schüler:innen evaluieren lassen. Die Anwendung wird von der Forschungsgruppe FALKO-PV an der Universität Regensburg bereitgestellt und fortlaufend wissenschaftlich begleitet. Die Nutzung der Evaluationsapp ist datenschutzkonform und absolut kostenlos.

Mehr Informationen finden Sie unter [amadeus.falko-pv.de](https://amadeus.falko-pv.de/).

## Installation

Unabhängig davon, ob Sie die manuelle oder die Docker-Installationsanleitung verwenden, geben Sie die folgenden Umgebungsvariablen an

```shell
# Diesen 'SECRET_KEY' verwendet Django für Verschlüsselungen und kann erstellt werden mit $ openssl rand -base64 32
SECRET_KEY = "..."

# Add E-Mail Host
AMADEUS_EMAIL_HOST='smtp.hostingservice.de'
AMADEUS_EMAIL_HOST_USER='hostmail@mail.de'
AMADEUS_EMAIL_HOST_PASSWORD='hostpasswort'
WEBSITE_URL = 'http://deinewebsite.de/' # production url
```

### Docker

1. Erstelle ein Docker-Image

```shell
docker build -t amadeus_app .
```

2. Starte den Docker-Container

```shell
docker run -p 8000:8000 amadeus_app
```

### Manuelle Installation

1. Erstelle ein [Virtual Environment](https://docs.python.org/3/library/venv.html) oder ein [Conda Environment](https://conda.io/projects/conda/en/latest/user-guide/install/index.html)

2. Installiere alle Requirements

```shell
pip install -r requirements.txt
```

3. Starte die Anwendung

```shell
python manage.py runserver
```

## Weitere Empfehlungen

### Anwendung im Netzwerk laufen lassen

1. Fügen Sie zusätzliche IP-Adressen zu ALLOWED_HOSTS in settings.py hinzu.
2. `python manage.py runserver <IP-Adresse>:<PORT>` (Zum Beispiel: `python manage.py runserver 192.168.178.87:8080`)

### Datenbank Migrationen

Migrationen anwenden
`python manage.py makemigrations evaluation_tool`

Migrationen hinzufügen
`python manage.py migrate`
