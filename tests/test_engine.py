import unittest
import datetime
import sys
import os

# Ensure the app folder is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../app")))

from liturgical_engine import LiturgicalEngine, calculate_easter, LiturgicalClass, LiturgicalColor

class TestLiturgicalEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = LiturgicalEngine()

    def test_easter_calculation(self):
        self.assertEqual(calculate_easter(2024), datetime.date(2024, 3, 31))
        self.assertEqual(calculate_easter(2025), datetime.date(2025, 4, 20))
        self.assertEqual(calculate_easter(2026), datetime.date(2026, 4, 5))

    def test_pentecost_2024(self):
        pentecost = datetime.date(2024, 5, 19)
        result = self.engine.resolve(pentecost)
        self.assertEqual(result.main_day.name, "Pentecost Sunday")
        self.assertEqual(result.main_day.liturgical_class, LiturgicalClass.I)
        self.assertEqual(result.main_day.color, LiturgicalColor.RED)

    def test_immaculate_conception(self):
        dec8 = datetime.date(2024, 12, 8)
        result = self.engine.resolve(dec8, include_brazilian=False)
        self.assertEqual(result.main_day.name, "2nd Sunday of Advent")
        self.assertEqual(len(result.commemorations), 1)
        self.assertEqual(result.commemorations[0].name, "Immaculate Conception of the B.V.M.")

    def test_christ_the_king(self):
        date = datetime.date(2024, 10, 27)
        result = self.engine.resolve(date)
        self.assertEqual(result.main_day.name, "Feast of Christ the King")
        self.assertEqual(result.main_day.liturgical_class, LiturgicalClass.I)
        self.assertEqual(result.main_day.color, LiturgicalColor.WHITE)

    def test_feria(self):
        date = datetime.date(2024, 7, 11)
        result = self.engine.resolve(date)
        self.assertEqual(result.main_day.name, "Feria")
        self.assertEqual(result.main_day.liturgical_class, LiturgicalClass.IV)
        self.assertEqual(result.main_day.color, LiturgicalColor.GREEN)

    def test_catherine_of_siena(self):
        date = datetime.date(2024, 4, 30)
        result = self.engine.resolve(date)
        self.assertEqual(result.main_day.name, "St. Catherine of Siena, Virgin")
        self.assertEqual(result.main_day.name_res_id, "st_catherine_siena")
        self.assertEqual(result.main_day.liturgical_class, LiturgicalClass.III)
        self.assertEqual(result.main_day.color, LiturgicalColor.WHITE)

    def test_trinity_sunday_and_next_sunday(self):
        trinity_sunday = datetime.date(2024, 5, 26)
        res_trinity = self.engine.resolve(trinity_sunday)
        self.assertEqual(res_trinity.main_day.name, "Trinity Sunday")
        self.assertEqual(res_trinity.main_day.name_res_id, "trinity_sunday")
        self.assertEqual(res_trinity.main_day.liturgical_class, LiturgicalClass.I)
        self.assertEqual(res_trinity.main_day.color, LiturgicalColor.WHITE)

        next_sunday = datetime.date(2024, 6, 2)
        res_next = self.engine.resolve(next_sunday)
        self.assertEqual(res_next.main_day.name, "2nd Sunday after Pentecost")
        self.assertEqual(res_next.main_day.name_res_id, "sunday_after_pentecost")
        self.assertEqual(res_next.main_day.liturgical_class, LiturgicalClass.II)
        self.assertEqual(res_next.main_day.color, LiturgicalColor.GREEN)

    def test_angela_merici(self):
        date = datetime.date(2024, 6, 1)
        result = self.engine.resolve(date)
        self.assertEqual(result.main_day.name, "St. Angela Merici, Virgin")
        self.assertEqual(result.main_day.name_res_id, "st_angela_merici")
        self.assertEqual(result.main_day.liturgical_class, LiturgicalClass.III)
        self.assertEqual(result.main_day.color, LiturgicalColor.WHITE)

    def test_brazilian_sanctorale_xml_loading(self):
        date = datetime.date(2024, 10, 12)
        result = self.engine.resolve(date)
        self.assertEqual(result.main_day.name, "Our Lady of Aparecida")
        self.assertEqual(result.main_day.name_res_id, "our_lady_aparecida")
        self.assertEqual(result.main_day.liturgical_class, LiturgicalClass.I)
        self.assertEqual(result.main_day.color, LiturgicalColor.WHITE)

    def test_holy_family_and_epiphany_sundays(self):
        holy_family_2024 = datetime.date(2024, 1, 7)
        res1 = self.engine.resolve(holy_family_2024)
        self.assertEqual(res1.main_day.name, "Feast of the Holy Family")
        self.assertEqual(res1.main_day.liturgical_class, LiturgicalClass.II)

        sunday2 = datetime.date(2024, 1, 14)
        res2 = self.engine.resolve(sunday2)
        self.assertEqual(res2.main_day.name, "2nd Sunday after Epiphany")
        self.assertEqual(res2.main_day.color, LiturgicalColor.GREEN)

        holy_family_2026 = datetime.date(2026, 1, 11)
        res3 = self.engine.resolve(holy_family_2026)
        self.assertEqual(res3.main_day.name, "Feast of the Holy Family")

    def test_christmas_octave(self):
        stephen = datetime.date(2024, 12, 26)
        self.assertEqual(self.engine.resolve(stephen).main_day.name, "St. Stephen, Protomartyr")
        
        sunday = datetime.date(2024, 12, 29)
        self.assertEqual(self.engine.resolve(sunday).main_day.name, "Sunday within the Octave of Christmas")
        
        jan1 = datetime.date(2025, 1, 1)
        self.assertEqual(self.engine.resolve(jan1).main_day.name, "Circumcision of Our Lord")

    def test_duplicate_observances_are_not_commemorated(self):
        epiphany = self.engine.resolve(datetime.date(2025, 1, 6), include_brazilian=False)
        self.assertEqual(epiphany.main_day.name, "The Epiphany of Our Lord")
        self.assertEqual(len(epiphany.commemorations), 0)

        baptism = self.engine.resolve(datetime.date(2025, 1, 13), include_brazilian=False)
        self.assertEqual(baptism.main_day.name, "Commemoration of the Baptism of Our Lord")
        self.assertEqual(len(baptism.commemorations), 0)

        stephen = self.engine.resolve(datetime.date(2024, 12, 26), include_brazilian=False)
        self.assertEqual(stephen.main_day.name, "St. Stephen, Protomartyr")
        self.assertEqual(len(stephen.commemorations), 0)

    def test_holy_name_of_jesus(self):
        jan5 = datetime.date(2025, 1, 5)
        self.assertEqual(self.engine.resolve(jan5).main_day.name, "Most Holy Name of Jesus")
        self.assertEqual(self.engine.resolve(datetime.date(2025, 1, 2), include_brazilian=False).main_day.name, "Feria")
        
        jan2 = datetime.date(2024, 1, 2)
        self.assertEqual(self.engine.resolve(jan2).main_day.name, "Most Holy Name of Jesus")

    def test_septuagesima_feria(self):
        monday = datetime.date(2024, 1, 22)
        res = self.engine.resolve(monday, include_brazilian=False)
        self.assertEqual(res.main_day.name, "SS. Vincent and Anastasius, Martyrs")
        
        tuesday = datetime.date(2024, 2, 13)
        res_tue = self.engine.resolve(tuesday, include_brazilian=False)
        self.assertEqual(res_tue.main_day.name, "Feria of Septuagesima")
        self.assertEqual(res_tue.main_day.color, LiturgicalColor.VIOLET)

    def test_lent_sundays(self):
        expected = [
            (datetime.date(2024, 2, 18), "1st Sunday of Lent"),
            (datetime.date(2024, 2, 25), "2nd Sunday of Lent"),
            (datetime.date(2024, 3, 3), "3rd Sunday of Lent"),
            (datetime.date(2024, 3, 10), "4th Sunday of Lent")
        ]

        for date, name in expected:
            result = self.engine.resolve(date, include_brazilian=False)
            self.assertEqual(result.main_day.name, name)
            self.assertEqual(result.main_day.name_res_id, "lent_sunday")
            self.assertEqual(result.main_day.liturgical_class, LiturgicalClass.I)
            self.assertEqual(result.main_day.color, LiturgicalColor.VIOLET)

    def test_our_lady_on_saturday(self):
        july6 = datetime.date(2024, 7, 6)
        res = self.engine.resolve(july6, include_brazilian=False)
        self.assertEqual(res.main_day.name, "Our Lady on Saturday")
        self.assertEqual(res.main_day.color, LiturgicalColor.WHITE)

        march16 = datetime.date(2024, 3, 16)
        res_lent = self.engine.resolve(march16, include_brazilian=False)
        self.assertEqual(res_lent.main_day.name, "Feria of Lent")
        self.assertEqual(res_lent.main_day.color, LiturgicalColor.VIOLET)
        self.assertEqual(res_lent.main_day.liturgical_class, LiturgicalClass.III)

    def test_no_iv_class_commemorations(self):
        date = datetime.date(2024, 1, 22)
        result = self.engine.resolve(date, include_brazilian=False)
        self.assertEqual(result.main_day.name, "SS. Vincent and Anastasius, Martyrs")
        self.assertEqual(len(result.commemorations), 0)

    def test_lenten_feria_precedence(self):
        march7 = datetime.date(2024, 3, 7)
        result = self.engine.resolve(march7, include_brazilian=False)
        self.assertEqual(result.main_day.name, "Feria of Lent")
        self.assertEqual(result.main_day.liturgical_class, LiturgicalClass.III)
        self.assertEqual(result.commemorations[0].name, "St. Thomas Aquinas, Confessor and Doctor")

    def test_holy_week_precedence(self):
        march25 = datetime.date(2024, 3, 25)
        result = self.engine.resolve(march25, include_brazilian=False)
        self.assertEqual(result.main_day.name, "Monday of Holy Week")
        self.assertEqual(result.main_day.liturgical_class, LiturgicalClass.I)
        self.assertEqual(result.commemorations[0].name, "Annunciation of the B.V.M.")

    def test_sundays_after_easter(self):
        april14 = datetime.date(2024, 4, 14)
        res2 = self.engine.resolve(april14, include_brazilian=False)
        self.assertEqual(res2.main_day.name, "2nd Sunday after Easter (Good Shepherd Sunday)")
        self.assertEqual(res2.main_day.name_res_id, "sunday_after_easter_good_shepherd")
        self.assertEqual(res2.main_day.liturgical_class, LiturgicalClass.II)
        self.assertEqual(res2.main_day.color, LiturgicalColor.WHITE)

        april21 = datetime.date(2024, 4, 21)
        res3 = self.engine.resolve(april21, include_brazilian=False)
        self.assertEqual(res3.main_day.name, "3rd Sunday after Easter")
        self.assertEqual(res3.main_day.name_res_id, "sunday_after_easter")
        self.assertEqual(res3.main_day.liturgical_class, LiturgicalClass.II)

        may5 = datetime.date(2024, 5, 5)
        res5 = self.engine.resolve(may5, include_brazilian=False)
        self.assertEqual(res5.main_day.name, "5th Sunday after Easter")
        self.assertEqual(res5.main_day.name_res_id, "sunday_after_easter")
        self.assertEqual(res5.main_day.liturgical_class, LiturgicalClass.II)

if __name__ == "__main__":
    unittest.main()
