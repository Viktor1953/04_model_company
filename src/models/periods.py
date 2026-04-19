# src/models/periods.py
from datetime import date, timedelta
from enum import Enum
from typing import Tuple


class PeriodType(Enum):
    PAST_3M = "past_3m"           # Новый уровень: прошлые 3 месяца
    PAST = "past"                 # Прошлый (можно расширять)
    OPERATIONAL = "operational"   # 3 месяца вперёд
    TACTICAL = "tactical"         # 6 месяцев вперёд
    STRATEGIC = "strategic"       # 12 месяцев вперёд


class Period:
    def __init__(self, period_type: PeriodType, reference_date: date = None):
        self.period_type = period_type
        self.reference_date = reference_date or date.today()
        self.start_date, self.end_date = self._calculate_range()

    def _calculate_range(self) -> Tuple[date, date]:
        today = self.reference_date

        if self.period_type == PeriodType.STRATEGIC:
            return today, today + timedelta(days=365)
        elif self.period_type == PeriodType.TACTICAL:
            return today, today + timedelta(days=180)
        elif self.period_type == PeriodType.OPERATIONAL:
            return today, today + timedelta(days=90)
        elif self.period_type == PeriodType.PAST_3M:
            return today - timedelta(days=90), today
        else:  # PAST (общий прошлый)
            return today - timedelta(days=365), today

    def get_date_range(self) -> Tuple[date, date]:
        return self.start_date, self.end_date

    def get_level_name(self) -> str:
        names = {
            PeriodType.STRATEGIC: "Стратегический (12 мес)",
            PeriodType.TACTICAL: "Тактический (6 мес)",
            PeriodType.OPERATIONAL: "Оперативный (3 мес)",
            PeriodType.PAST_3M: "Прошлый период (3 мес)",
            PeriodType.PAST: "Прошлый (общий)"
        }
        return names.get(self.period_type, self.period_type.value)

    def __str__(self):
        return f"{self.get_level_name()}: {self.start_date.strftime('%Y-%m-%d')} — {self.end_date.strftime('%Y-%m-%d')}"


def create_period(period_type: str, reference_date: date = None) -> Period:
    mapping = {
        "strategic": PeriodType.STRATEGIC,
        "tactical": PeriodType.TACTICAL,
        "operational": PeriodType.OPERATIONAL,
        "past_3m": PeriodType.PAST_3M,
        "past": PeriodType.PAST
    }
    return Period(mapping[period_type.lower()], reference_date)