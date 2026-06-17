# LiturgicalDayAPI
LiturgicalDayAPI is a Python-based REST API that determines the liturgical feast of a given date according to the Roman Catholic Missal of 1962 (extraordinary form of the Roman Rite). It is built using FastAPI and ports the calendar precedence and calculation engine from LiturgyCalendarApp.

## Features

- **Date Resolution**: Given any ISO date (YYYY-MM-DD), resolves the corresponding liturgical feast and its precedence.
- **Precedence Logic**: Implements the complex priority rules of the 1962 Rubrics (class hierarchies, tie-breakers for Sundays, variable feasts, and Lenten/Easter cycles).
- **Easter Cycle Calculations**: Computes Easter Sunday and all movable feasts dynamically using the Meeus/Jones/Butcher algorithm.
- **Leap Year Shifts**: Moves St. Matthias to February 25th in leap years, matching standard 1962 rubrics.
- **Brazilian Proper**: Optionally includes feasts specific to the liturgical calendar of Brazil (e.g., Our Lady of Aparecida on October 12th).
- **Internationalization**: Full localization support (English, Portuguese, Spanish, French, German) parsed dynamically from Android string resources on startup.
- **CORS Enabled**: Cross-Origin Resource Sharing (CORS) is enabled by default to allow easy integration into frontend applications.

## Project Structure

```
LiturgicalDayAPI/
├── app/
│   ├── main.py                  # FastAPI Application Entrypoint
│   └── liturgical_engine/
│       ├── __init__.py          # Package Init exposing main classes
│       ├── easter.py            # Easter date calculator
│       ├── engine.py            # Main calendar resolution engine
│       ├── localization.py      # Android-style string formatting & values-xml parsing
│       ├── models.py            # Enum & Data class definitions
│       ├── sanctorale.py        # Fixed feasts (Universal & Brazilian) parser
│       ├── temporal.py          # Temporal cycle (movable feasts/ferias) parser
│       └── data/                # Copied source XML configurations & string files
│           ├── universal_sanctoral.xml
│           ├── brazilian_sanctoral.xml
│           ├── temporal_cycle.xml
│           ├── values/
│           ├── values-en/
│           ├── values-es/
│           ├── values-fr/
│           ├── values-de/
│           └── values-pt-rBR/
├── tests/
│   ├── test_engine.py           # Unit tests validating engine against original test cases
│   └── test_api.py              # Unit tests for FastAPI HTTP endpoints
├── requirements.txt
└── README.md
```

## Setup and Installation

Make sure Python 3.10+ is installed.

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Unit Tests**:
   ```bash
   python3 -m pytest
   ```

3. **Start the API Server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

   Once running, the API interactive documentation will be available at:
   - Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

### 1. Root Information

- **URL**: `GET /`
- **Description**: Returns welcome message and links to documentation.
- **Response**:
  ```json
  {
    "message": "Welcome to the Liturgical Day API",
    "docs_url": "/docs",
    "endpoints": {
      "liturgical_day": "/liturgical-day"
    }
  }
  ```

### 2. Get Liturgical Day

- **URL**: `GET /liturgical-day`
- **Description**: Returns the resolved liturgical day and any commemorations for the date.
- **Query Parameters**:
  - `date` (string, optional): ISO formatted date `YYYY-MM-DD`. Defaults to local current date.
  - `lang` (string, optional): Language code (e.g. `en`, `pt`, `pt-br`, `es`, `fr`, `de`). If omitted, negotiates using the `Accept-Language` HTTP header, defaulting to `en`.
  - `include_brazilian` (boolean, optional): Whether to include Brazilian proper feasts. Defaults to `true`.
- **Sample Request**:
  ```bash
  curl "http://localhost:8000/liturgical-day?date=2024-05-19&lang=en"
  ```
- **Sample Response**:
  ```json
  {
    "main_day": {
      "name": "Pentecost Sunday",
      "class_code": "I",
      "class_name": "I Class",
      "color": "RED",
      "is_lord_feast": true
    },
    "commemorations": [],
    "date": "2024-05-19",
    "requested_lang": "en",
    "resolved_lang": "en",
    "include_brazilian": true
  }
  ```

- **Sample Request (Portuguese / Brazilian Proper)**:
  ```bash
  curl "http://localhost:8000/liturgical-day?date=2024-10-12&lang=pt-br"
  ```
- **Sample Response**:
  ```json
  {
    "main_day": {
      "name": "Nossa Senhora da Conceição Aparecida, Padroeira do Brasil",
      "class_code": "I",
      "class_name": "I Classe",
      "color": "WHITE",
      "is_lord_feast": false
    },
    "commemorations": [],
    "date": "2024-10-12",
    "requested_lang": "pt-br",
    "resolved_lang": "pt-br",
    "include_brazilian": true
  }
  ```
