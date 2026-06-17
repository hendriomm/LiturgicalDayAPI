from fastapi import FastAPI, Query, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import date as date_type, datetime
from typing import Optional
import os

from liturgical_engine import LiturgicalEngine, LocalizationManager

app = FastAPI(
    title="Liturgical Day API",
    description="API for the 1962 Roman Catholic Liturgical Calendar",
    version="1.0.0"
)

# Enable CORS so web apps can easily call it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engine and localization manager
engine = LiturgicalEngine()
localization = LocalizationManager()

@app.get("/")
def get_root():
    return {
        "message": "Welcome to the Liturgical Day API",
        "docs_url": "/docs",
        "endpoints": {
            "liturgical_day": "/liturgical-day"
        }
    }

@app.get("/liturgical-day")
def get_liturgical_day(
    date: Optional[str] = Query(
        None,
        description="The date to check in YYYY-MM-DD format. Defaults to today's local date."
    ),
    lang: Optional[str] = Query(
        None,
        description="Language code: pt, en, es, fr, de, pt-br. If not specified, uses Accept-Language header or falls back to 'en'."
    ),
    include_brazilian: bool = Query(
        True,
        description="Whether to include feasts specific to Brazil."
    ),
    accept_language: Optional[str] = Header(None)
):
    # Resolve date
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Expected YYYY-MM-DD.")
    else:
        target_date = datetime.now().date()

    # Resolve language
    # If lang is not provided, try to parse Accept-Language header
    selected_lang = "en"
    if lang:
        selected_lang = lang
    elif accept_language:
        parts = accept_language.split(",")
        if parts:
            first = parts[0].split(";")[0].strip()
            selected_lang = first

    try:
        result = engine.resolve(target_date, include_brazilian=include_brazilian)
        translations = localization.get_translations(selected_lang)
        
        actual_lang = selected_lang
        if not translations:
            translations = localization.get_translations("en")
            actual_lang = "en"
            
        response_dict = result.to_dict(translations)
        response_dict["date"] = target_date.isoformat()
        response_dict["requested_lang"] = selected_lang
        response_dict["resolved_lang"] = actual_lang
        response_dict["include_brazilian"] = include_brazilian
        
        return response_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal engine error: {str(e)}")
