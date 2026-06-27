import os
import datetime
from .models import LiturgicalDay, LiturgicalClass, LiturgicalColor, LiturgicalResult
from .easter import calculate_easter
from .temporal import TemporalCycle
from .sanctorale import Sanctorale, BrazilianSanctorale

class LiturgicalEngine:
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), "data")
        self.data_dir = data_dir
        
        temporal_path = os.path.join(data_dir, "temporal_cycle.xml")
        universal_path = os.path.join(data_dir, "universal_sanctoral.xml")
        brazilian_path = os.path.join(data_dir, "brazilian_sanctoral.xml")
        
        self.temporal_cycle = TemporalCycle(temporal_path)
        self.sanctorale = Sanctorale(universal_path)
        self.brazilian_sanctorale = BrazilianSanctorale(brazilian_path)

    def resolve(self, date: datetime.date, include_brazilian: bool = True) -> LiturgicalResult:
        temporal = self.temporal_cycle.get_day(date)
        universal_sanctoral = self.sanctorale.get_day(date)
        brazilian_sanctoral = self.brazilian_sanctorale.get_day(date) if include_brazilian else None
        
        sanctoral_comms = []
        if brazilian_sanctoral is not None:
            if universal_sanctoral is None:
                sanctoral = brazilian_sanctoral
            elif brazilian_sanctoral.liturgical_class.value <= universal_sanctoral.liturgical_class.value:
                sanctoral = brazilian_sanctoral
                sanctoral_comms.append(universal_sanctoral)
            else:
                sanctoral = universal_sanctoral
                sanctoral_comms.append(brazilian_sanctoral)
        else:
            sanctoral = universal_sanctoral

        def result_with_filtered_comms(main: LiturgicalDay, comms: list) -> LiturgicalResult:
            filtered = []
            seen = set()
            for c in comms:
                if c.liturgical_class == LiturgicalClass.IV:
                    continue
                if c.observance_key() == main.observance_key():
                    continue
                key = c.observance_key()
                if key not in seen:
                    seen.add(key)
                    filtered.append(c)
            return LiturgicalResult(main, filtered)

        # Special check for Our Lady on Saturday
        if date.isoweekday() == 6 and (temporal is None or temporal.name_res_id == "feria") and sanctoral is None:
            season_color = self.get_season_color(date)
            if season_color in (LiturgicalColor.GREEN, LiturgicalColor.WHITE):
                return LiturgicalResult(
                    LiturgicalDay(
                        "Our Lady on Saturday",
                        "our_lady_saturday",
                        None,
                        LiturgicalClass.IV,
                        LiturgicalColor.WHITE
                    )
                )

        if temporal is None and sanctoral is None:
            season_color = self.get_season_color(date)
            return LiturgicalResult(
                LiturgicalDay(
                    "Feria",
                    "feria",
                    None,
                    LiturgicalClass.IV,
                    season_color
                )
            )

        if temporal is not None and sanctoral is None:
            return LiturgicalResult(temporal)

        if temporal is None and sanctoral is not None:
            return result_with_filtered_comms(sanctoral, sanctoral_comms)

        t = temporal
        s = sanctoral
        comms = [s] + sanctoral_comms
        comms_if_s_wins = [t] + sanctoral_comms

        # Rule 1: Higher class wins
        if t.liturgical_class.value < s.liturgical_class.value:
            return result_with_filtered_comms(t, comms)
        elif s.liturgical_class.value < t.liturgical_class.value:
            return result_with_filtered_comms(s, comms_if_s_wins)

        # Rule 2: Same class
        if date.isoweekday() == 7: # Sunday
            if t.is_lord_feast:
                return result_with_filtered_comms(t, comms)
            if s.is_lord_feast:
                return result_with_filtered_comms(s, comms_if_s_wins)
            if t.liturgical_class == LiturgicalClass.I:
                return result_with_filtered_comms(t, comms)
            return result_with_filtered_comms(t, comms)

        return result_with_filtered_comms(t, comms)

    def get_season_color(self, date: datetime.date) -> LiturgicalColor:
        year = date.year
        easter = calculate_easter(year)
        diff_from_easter = (date - easter).days

        if 0 <= diff_from_easter <= 55:
            return LiturgicalColor.WHITE
        if -70 <= diff_from_easter <= -1:
            return LiturgicalColor.VIOLET

        christmas = datetime.date(year, 12, 25)
        christmas_dow = christmas.isoweekday()
        sunday_before_christmas = christmas - datetime.timedelta(days=christmas_dow)
        advent1 = sunday_before_christmas - datetime.timedelta(weeks=3)
        
        if advent1 <= date < christmas:
            return LiturgicalColor.VIOLET
        if date >= christmas or date <= datetime.date(year, 1, 13):
            return LiturgicalColor.WHITE

        return LiturgicalColor.GREEN
