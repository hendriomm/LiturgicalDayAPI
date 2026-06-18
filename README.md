# liturgical_engine

A Python library that resolves the liturgical feast of any date according to the **Roman Catholic Missal of 1962** (Extraordinary Form of the Roman Rite). Ported from the calendar engine of [LiturgyCalendarApp](https://github.com/hendriomm/LiturgyCalendarApp).

## Features

- **Date Resolution** — Given any `datetime.date`, resolves the principal liturgical feast and any commemorations.
- **Precedence Logic** — Full implementation of the 1962 Rubrics class hierarchy (I–IV), including tie-breaker rules for Sundays and Lord's feasts.
- **Easter Calculation** — Computes Easter Sunday and all movable feasts using the Meeus/Jones/Butcher algorithm.
- **Leap Year Shifts** — Moves St. Matthias to February 25th in leap years per standard 1962 rubrics.
- **Brazilian Proper** — Optionally includes feasts specific to the liturgical calendar of Brazil (e.g., Our Lady of Aparecida, October 12th).
- **Internationalization** — Localization support for **English, Portuguese, Spanish, French, and German**, parsed from Android-style `values-*/strings.xml` files.

## Installation

Requires Python 3.9+.

```bash
# Install directly from the repository
pip install -e .

# Or install dev dependencies for testing
pip install -e ".[dev]"
```

## Quick Start

```python
import datetime
from liturgical_engine import LiturgicalEngine, LocalizationManager

engine = LiturgicalEngine()
localization = LocalizationManager()

# Resolve today's feast
result = engine.resolve(datetime.date.today())

# Translate to English
translations = localization.get_translations("en")
print(result.to_dict(translations))
```

**Example output** for `2024-05-19` (Pentecost Sunday):
```json
{
  "main_day": {
    "name": "Pentecost Sunday",
    "class_code": "I",
    "class_name": "I Class",
    "color": "RED",
    "is_lord_feast": true
  },
  "commemorations": []
}
```

## API Reference

### `LiturgicalEngine`

```python
LiturgicalEngine(data_dir: str = None)
```

The main calendar resolution engine. By default, loads XML data bundled with the package.

| Method | Signature | Description |
|---|---|---|
| `resolve` | `(date: datetime.date, include_brazilian: bool = True) → LiturgicalResult` | Resolves the liturgical day for the given date. |
| `get_season_color` | `(date: datetime.date) → LiturgicalColor` | Returns the liturgical season color for a date. |

---

### `LocalizationManager`

```python
LocalizationManager(data_dir: str = None)
```

Loads and caches translations from Android-style `strings.xml` files.

| Method | Signature | Description |
|---|---|---|
| `get_translations` | `(lang: str) → dict` | Returns a translation dict for the given language code. Falls back to `"en"` if the language is unavailable. |

**Supported language codes:** `en`, `pt`, `pt-br`, `es`, `fr`, `de`

---

### `LiturgicalResult`

Returned by `LiturgicalEngine.resolve()`.

| Attribute | Type | Description |
|---|---|---|
| `main_day` | `LiturgicalDay` | The principal feast of the day. |
| `commemorations` | `list[LiturgicalDay]` | Any commemorations observed alongside the principal feast. |
| `to_dict(translations)` | `dict` | Serializes the result with translated names. |

---

### `LiturgicalDay`

Represents a single liturgical observance.

| Attribute | Type | Description |
|---|---|---|
| `name` | `str` | Fallback feast name (English). |
| `liturgical_class` | `LiturgicalClass` | Class I–IV (I being highest). |
| `color` | `LiturgicalColor` | Vestment color for the day. |
| `is_lord_feast` | `bool` | `True` if the feast celebrates Our Lord. |
| `to_dict(translations)` | `dict` | Serializes the day with a translated name. |

---

### `LiturgicalClass` (Enum)

| Value | Meaning |
|---|---|
| `LiturgicalClass.I` | First Class (highest precedence) |
| `LiturgicalClass.II` | Second Class |
| `LiturgicalClass.III` | Third Class |
| `LiturgicalClass.IV` | Fourth Class (lowest precedence) |

---

### `LiturgicalColor` (Enum)

`WHITE`, `RED`, `GREEN`, `VIOLET`, `BLACK`, `ROSE`

---

### `calculate_easter`

```python
from liturgical_engine import calculate_easter

easter: datetime.date = calculate_easter(year: int)
```

Returns the date of Easter Sunday for the given year using the Meeus/Jones/Butcher algorithm.

## Usage Examples

### Resolve with Brazilian Proper

```python
result = engine.resolve(datetime.date(2024, 10, 12), include_brazilian=True)
translations = localization.get_translations("pt-br")
print(result.to_dict(translations))
# main_day.name → "Nossa Senhora da Conceição Aparecida, Padroeira do Brasil"
```

### Resolve without Brazilian Proper

```python
result = engine.resolve(datetime.date(2024, 10, 12), include_brazilian=False)
translations = localization.get_translations("en")
print(result.to_dict(translations))
# main_day.name → "Our Lady of the Pillar" (universal feast)
```

### Easter calculation

```python
from liturgical_engine import calculate_easter

print(calculate_easter(2025))  # 2025-04-20
print(calculate_easter(2026))  # 2026-04-05
```

## Project Structure

```
LiturgicalDayAPI/
├── liturgical_engine/
│   ├── __init__.py          # Public API surface
│   ├── easter.py            # Easter date calculator
│   ├── engine.py            # Calendar resolution engine
│   ├── localization.py      # Android-style strings.xml parser
│   ├── models.py            # Enums & data classes
│   ├── sanctorale.py        # Fixed feasts parser (universal & Brazilian)
│   ├── temporal.py          # Movable feasts & temporal cycle parser
│   └── data/
│       ├── universal_sanctoral.xml
│       ├── brazilian_sanctoral.xml
│       ├── temporal_cycle.xml
│       ├── values/          # Default strings (Portuguese)
│       ├── values-en/
│       ├── values-es/
│       ├── values-fr/
│       ├── values-de/
│       └── values-pt-rBR/
├── tests/
│   └── test_engine.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Running Tests

```bash
python -m pytest tests/
```

## License

MIT License — see [LICENSE](LICENSE).
