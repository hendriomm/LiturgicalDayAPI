import os
import xml.etree.ElementTree as ET
import datetime
from .models import LiturgicalDay, LiturgicalClass, LiturgicalColor

class Sanctorale:
    def __init__(self, xml_path: str):
        self.feasts = self.parse(xml_path)

    def parse(self, xml_path: str) -> dict:
        feasts = {}
        if not os.path.exists(xml_path):
            return feasts
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for elem in root.findall("feast"):
                date = elem.attrib.get("date")
                name = elem.attrib.get("name")
                name_res_id = elem.attrib.get("nameResId")
                class_str = elem.attrib.get("class")
                color_str = elem.attrib.get("color")
                is_lord_feast = elem.attrib.get("isLordFeast") == "true"

                try:
                    lit_class = LiturgicalClass[class_str]
                except KeyError:
                    lit_class = LiturgicalClass.III

                try:
                    lit_color = LiturgicalColor[color_str]
                except KeyError:
                    lit_color = LiturgicalColor.WHITE

                feasts[date] = LiturgicalDay(
                    name=name,
                    name_res_id=name_res_id or None,
                    name_args=None,
                    liturgical_class=lit_class,
                    color=lit_color,
                    is_lord_feast=is_lord_feast
                )
        except Exception as e:
            print(f"Error parsing sanctoral {xml_path}: {e}")
        return feasts

    def get_day(self, date: datetime.date) -> LiturgicalDay:
        year = date.year
        oct31 = datetime.date(year, 10, 31)
        oct31_dow = oct31.isoweekday()
        christ_the_king = oct31 if oct31_dow == 7 else oct31 - datetime.timedelta(days=oct31_dow)
        if date == christ_the_king:
            return LiturgicalDay(
                "Feast of Christ the King",
                "christ_the_king",
                None,
                LiturgicalClass.I,
                LiturgicalColor.WHITE,
                is_lord_feast=True
            )

        month = date.month
        day = date.day
        
        is_leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        if is_leap and month == 2:
            if day == 24:
                key = "02-24-LEAP-NONE"
            elif day == 25:
                key = "02-24"
            else:
                key = f"{month:02d}-{day:02d}"
        else:
            key = f"{month:02d}-{day:02d}"
            
        return self.feasts.get(key)

class BrazilianSanctorale:
    def __init__(self, xml_path: str):
        self.feasts = self.parse(xml_path)

    def parse(self, xml_path: str) -> dict:
        feasts = {}
        if not os.path.exists(xml_path):
            return feasts
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            for elem in root.findall("feast"):
                date = elem.attrib.get("date")
                name = elem.attrib.get("name")
                name_res_id = elem.attrib.get("nameResId")
                class_str = elem.attrib.get("class")
                color_str = elem.attrib.get("color")
                is_lord_feast = elem.attrib.get("isLordFeast") == "true"

                try:
                    lit_class = LiturgicalClass[class_str]
                except KeyError:
                    lit_class = LiturgicalClass.III

                try:
                    lit_color = LiturgicalColor[color_str]
                except KeyError:
                    lit_color = LiturgicalColor.WHITE

                feasts[date] = LiturgicalDay(
                    name=name,
                    name_res_id=name_res_id or None,
                    name_args=None,
                    liturgical_class=lit_class,
                    color=lit_color,
                    is_lord_feast=is_lord_feast
                )
        except Exception as e:
            print(f"Error parsing Brazilian sanctoral {xml_path}: {e}")
        return feasts

    def get_day(self, date: datetime.date) -> LiturgicalDay:
        key = f"{date.month:02d}-{date.day:02d}"
        return self.feasts.get(key)
