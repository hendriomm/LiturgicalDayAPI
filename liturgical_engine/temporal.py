import os
import xml.etree.ElementTree as ET
import datetime
from .models import LiturgicalDay, LiturgicalClass, LiturgicalColor
from .easter import calculate_easter

class TemporalCycle:
    def __init__(self, xml_path: str):
        self.easter_cycle = {}
        self.christmas_cycle = {}
        self.parse(xml_path)

    def parse(self, xml_path: str):
        if not os.path.exists(xml_path):
            return
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            easter_cycle_node = root.find("easter_cycle")
            if easter_cycle_node is not None:
                for day_elem in easter_cycle_node.findall("day"):
                    offset = int(day_elem.attrib.get("offset"))
                    self.easter_cycle[offset] = self.parse_day(day_elem)
                    
            christmas_cycle_node = root.find("christmas_cycle")
            if christmas_cycle_node is not None:
                for day_elem in christmas_cycle_node.findall("day"):
                    date = day_elem.attrib.get("date")
                    self.christmas_cycle[date] = self.parse_day(day_elem)
        except Exception as e:
            print(f"Error parsing temporal cycle {xml_path}: {e}")

    def parse_day(self, elem: ET.Element) -> LiturgicalDay:
        name = elem.attrib.get("name")
        name_res_id = elem.attrib.get("nameResId")
        class_str = elem.attrib.get("class")
        color_str = elem.attrib.get("color")
        is_lord_feast = elem.attrib.get("isLordFeast") == "true"
        name_arg = elem.attrib.get("nameArg")

        try:
            lit_class = LiturgicalClass[class_str]
        except KeyError:
            lit_class = LiturgicalClass.III

        try:
            lit_color = LiturgicalColor[color_str]
        except KeyError:
            lit_color = LiturgicalColor.WHITE

        name_args = None
        if name_arg:
            try:
                val = int(name_arg)
                if 1 <= val <= 5:
                    name_args = [f"ord_{val}"]
                else:
                    name_args = [val]
            except ValueError:
                name_args = [name_arg]

        return LiturgicalDay(
            name=name,
            name_res_id=name_res_id or None,
            name_args=name_args,
            liturgical_class=lit_class,
            color=lit_color,
            is_lord_feast=is_lord_feast
        )

    def get_day(self, date: datetime.date) -> LiturgicalDay:
        year = date.year
        easter = calculate_easter(year)
        diff_from_easter = (date - easter).days
        septuagesima = easter - datetime.timedelta(days=63)
        
        christmas = datetime.date(year, 12, 25)
        
        nov27 = datetime.date(year, 11, 27)
        nov27_dow = nov27.isoweekday()
        advent1 = nov27 if nov27_dow == 7 else nov27 + datetime.timedelta(days=7 - nov27_dow)

        # 5. Sundays after Epiphany
        epiphany = datetime.date(year, 1, 6)
        epiphany_dow = epiphany.isoweekday()
        sunday_after_epiphany_1 = epiphany + datetime.timedelta(days=7 if epiphany_dow == 7 else 7 - epiphany_dow)
        
        if date == sunday_after_epiphany_1 and date < septuagesima:
            return LiturgicalDay("Feast of the Holy Family", "holy_family", None, LiturgicalClass.II, LiturgicalColor.WHITE)

        # 1. Easter Cycle (from XML)
        from_easter = self.easter_cycle.get(diff_from_easter)
        if from_easter is not None:
            return from_easter

        # 2. Christmas Cycle (from XML fixed dates and Sunday within Octave)
        if date.month == 1 and date.day == 13:
            pass
        
        if date.month == 12 and 26 <= date.day <= 31:
            sunday_within_octave = next(
                (christmas + datetime.timedelta(days=i) for i in range(1, 7) 
                 if (christmas + datetime.timedelta(days=i)).isoweekday() == 7),
                None
            )
            if date == sunday_within_octave:
                return LiturgicalDay("Sunday within the Octave of Christmas", "sunday_octave_christmas", None, LiturgicalClass.II, LiturgicalColor.WHITE)
        
        christmas_key = f"{date.month:02d}-{date.day:02d}"
        from_christmas = self.christmas_cycle.get(christmas_key)
        if from_christmas is not None:
            if from_christmas.name_res_id == "day_octave_nativity":
                day_num = date.day - 24
                arg = f"ord_{day_num}" if 1 <= day_num <= 5 else day_num
                return LiturgicalDay(
                    name=from_christmas.name,
                    name_res_id=from_christmas.name_res_id,
                    name_args=[arg],
                    liturgical_class=from_christmas.liturgical_class,
                    color=from_christmas.color,
                    is_lord_feast=from_christmas.is_lord_feast
                )
            return from_christmas

        # 3. Septuagesima Time Logic
        if septuagesima <= date < easter - datetime.timedelta(days=46):
             if date.isoweekday() != 7:
                 return LiturgicalDay("Feria of Septuagesima", "feria", None, LiturgicalClass.IV, LiturgicalColor.VIOLET)

        # 4. Lenten Ferias (III Class)
        if diff_from_easter < 0 and diff_from_easter > -46 and date.isoweekday() != 7:
            return LiturgicalDay("Feria of Lent", "feria", None, LiturgicalClass.III, LiturgicalColor.VIOLET)

        for i in range(2, 7):
            sunday = sunday_after_epiphany_1 + datetime.timedelta(weeks=i - 1)
            if date == sunday and date < septuagesima:
                arg = f"ord_{i}" if 1 <= i <= 5 else i
                return LiturgicalDay(
                    name=f"{self.get_english_ordinal(i)} Sunday after Epiphany",
                    name_res_id="sunday_after_epiphany",
                    name_args=[arg],
                    liturgical_class=LiturgicalClass.II,
                    color=LiturgicalColor.GREEN
                )

        # 6. Sundays after Pentecost
        if diff_from_easter > 56 and date.isoweekday() == 7 and date < advent1:
            total_sundays_after_pentecost = ((advent1 - (easter + datetime.timedelta(days=56))).days - 1) // 7 + 1
            sunday_num = (diff_from_easter - 56) // 7 + 1
            
            if sunday_num == total_sundays_after_pentecost:
                arg = f"ord_24" if 1 <= 24 <= 5 else 24
                return LiturgicalDay("24th Sunday after Pentecost", "sunday_after_pentecost", [arg], LiturgicalClass.II, LiturgicalColor.GREEN)
            
            if total_sundays_after_pentecost > 24:
                num_extra = total_sundays_after_pentecost - 24
                if sunday_num > 23 and sunday_num <= 23 + num_extra:
                    last_epiphany_sunday = ((septuagesima - sunday_after_epiphany_1).days - 1) // 7 + 1
                    omitted_start = last_epiphany_sunday + 1
                    current_omitted = omitted_start + (sunday_num - 24)
                    if 3 <= current_omitted <= 6:
                        arg = f"ord_{current_omitted}" if 1 <= current_omitted <= 5 else current_omitted
                        return LiturgicalDay(
                            name=f"{self.get_english_ordinal(current_omitted)} Sunday after Epiphany (Resumed)",
                            name_res_id="sunday_after_epiphany",
                            name_args=[arg],
                            liturgical_class=LiturgicalClass.II,
                            color=LiturgicalColor.GREEN
                        )
                
                if sunday_num > 23 + num_extra:
                    arg = f"ord_24" if 1 <= 24 <= 5 else 24
                    return LiturgicalDay("24th Sunday after Pentecost", "sunday_after_pentecost", [arg], LiturgicalClass.II, LiturgicalColor.GREEN)

            if sunday_num <= 23:
                arg = f"ord_{sunday_num}" if 1 <= sunday_num <= 5 else sunday_num
                return LiturgicalDay(
                    name=f"{self.get_english_ordinal(sunday_num)} Sunday after Pentecost",
                    name_res_id="sunday_after_pentecost",
                    name_args=[arg],
                    liturgical_class=LiturgicalClass.II,
                    color=LiturgicalColor.GREEN
                )

        # 7. Ember Days
        sept1 = datetime.date(year, 9, 1)
        sept1_dow = sept1.isoweekday()
        sept_sunday1 = sept1 if sept1_dow == 7 else sept1 + datetime.timedelta(days=7 - sept1_dow)
        sept_sunday3 = sept_sunday1 + datetime.timedelta(days=14)
        
        if date == sept_sunday3 + datetime.timedelta(days=3):
            return LiturgicalDay("Ember Wednesday of September", "ember_wednesday", ["of_september"], LiturgicalClass.II, LiturgicalColor.VIOLET)
        if date == sept_sunday3 + datetime.timedelta(days=5):
            return LiturgicalDay("Ember Friday of September", "ember_friday", ["of_september"], LiturgicalClass.II, LiturgicalColor.VIOLET)
        if date == sept_sunday3 + datetime.timedelta(days=6):
            return LiturgicalDay("Ember Saturday of September", "ember_saturday", ["of_september"], LiturgicalClass.II, LiturgicalColor.VIOLET)

        # 8. Holy Name of Jesus (Special Logic)
        sunday_candidates = [datetime.date(year, 1, i) for i in range(2, 6)]
        sunday_match = next((d for d in sunday_candidates if d.isoweekday() == 7), None)
        holy_name_date = sunday_match or datetime.date(year, 1, 2)
        if date == holy_name_date:
            return LiturgicalDay("Most Holy Name of Jesus", "holy_name_jesus", None, LiturgicalClass.II, LiturgicalColor.WHITE, is_lord_feast=True)

        # 9. Advent Cycle Logic
        diff_from_advent1 = (date - advent1).days
        if date < christmas:
            if date == advent1:
                arg = f"ord_1" if 1 <= 1 <= 5 else 1
                return LiturgicalDay("1st Sunday of Advent", "sunday_of_advent", [arg], LiturgicalClass.I, LiturgicalColor.VIOLET)
            if diff_from_advent1 > 0:
                sunday_num = diff_from_advent1 // 7 + 1
                if date.isoweekday() == 7:
                    color = LiturgicalColor.ROSE if sunday_num == 3 else LiturgicalColor.VIOLET
                    arg = f"ord_{sunday_num}" if 1 <= sunday_num <= 5 else sunday_num
                    return LiturgicalDay(
                        name=f"{self.get_english_ordinal(sunday_num)} Sunday of Advent",
                        name_res_id="sunday_of_advent",
                        name_args=[arg],
                        liturgical_class=LiturgicalClass.I,
                        color=color
                    )
                
                if sunday_num == 3:
                    dow = date.isoweekday()
                    if dow == 3:
                        return LiturgicalDay("Ember Wednesday of Advent", "ember_wednesday", ["of_advent"], LiturgicalClass.II, LiturgicalColor.VIOLET)
                    elif dow == 5:
                        return LiturgicalDay("Ember Friday of Advent", "ember_friday", ["of_advent"], LiturgicalClass.II, LiturgicalColor.VIOLET)
                    elif dow == 6:
                        return LiturgicalDay("Ember Saturday of Advent", "ember_saturday", ["of_advent"], LiturgicalClass.II, LiturgicalColor.VIOLET)

        return None

    def get_english_ordinal(self, n: int) -> str:
        if n == 1: return "1st"
        if n == 2: return "2nd"
        if n == 3: return "3rd"
        if n == 4: return "4th"
        return f"{n}th"
