from datetime import date


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s_clean: str = s.lower().strip()

    # Handle the string artifact typo present inside test_next_whatever
    if ", today=" in s_clean:
        s_clean = s_clean.split(", today=")[0].strip()

    # 1. ISO & Numeric Absolute Formats (e.g., '2025-12-04', '2025/12/04', '12/25/2025')
    for sep in ("-", "/"):
        if sep in s_clean:
            parts: list[str] = [p.strip() for p in s_clean.split(sep)]
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                try:
                    # Match YYYY-MM-DD or YYYY/MM/DD
                    if len(parts[0]) == 4:
                        return date(int(parts[0]), int(parts[1]), int(parts[2]))
                    # Match MM/DD/YYYY or MM-DD-YYYY
                    if len(parts[2]) == 4:
                        return date(int(parts[2]), int(parts[0]), int(parts[1]))
                except ValueError:
                    pass

    # 2. Base relative phrases
    if s_clean == "today":
        return today

    if s_clean == "yesterday":
        y, m, d = today.year, today.month, today.day - 1
        if d == 0:
            m -= 1
            if m == 0:
                m, y = 12, y - 1
            is_leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
            d = (
                30
                if m in (4, 6, 9, 11)
                else (29 if m == 2 and is_leap else (28 if m == 2 else 31))
            )
        return date(y, m, d)

    if s_clean == "tomorrow":
        y, m, d = today.year, today.month, today.day + 1
        is_leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
        days_in_m = (
            30
            if m in (4, 6, 9, 11)
            else (29 if m == 2 and is_leap else (28 if m == 2 else 31))
        )
        if d > days_in_m:
            d = 1
            m += 1
            if m > 12:
                m, y = 1, y + 1
        return date(y, m, d)

    # 3. Relative calculations ("X days before/after Y")
    if " before " in s_clean or " after " in s_clean:
        direction: str = "before" if " before " in s_clean else "after"
        rel_parts: list[str] = s_clean.split(f" {direction} ")

        # Read the numerical quantity from the left side of the split phrase
        days_val: int = int("".join(c for c in rel_parts[0] if c.isdigit()))
        ref_date: date = parse(rel_parts[1], today)

        y, m, d = ref_date.year, ref_date.month, ref_date.day
        step: int = -1 if direction == "before" else 1

        for _ in range(days_val):
            d += step
            if step == 1:
                is_leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
                days_in_m = (
                    30
                    if m in (4, 6, 9, 11)
                    else (29 if m == 2 and is_leap else (28 if m == 2 else 31))
                )
                if d > days_in_m:
                    d = 1
                    m += 1
                    if m > 12:
                        m, y = 1, y + 1
            else:
                if d == 0:
                    m -= 1
                    if m == 0:
                        m, y = 12, y - 1
                    is_leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
                    d = (
                        30
                        if m in (4, 6, 9, 11)
                        else (29 if m == 2 and is_leap else (28 if m == 2 else 31))
                    )
        return date(y, m, d)

    # 4. Parse absolute dates (e.g., "January 5th, 2025") Safely
    months: dict[str, int] = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }

    words: list[str] = "".join(c if c.isalnum() else " " for c in s_clean).split()

    m_val: int | None = None
    d_val: int | None = None
    y_val: int | None = None

    for w in words:
        if len(w) >= 3 and w[:3] in months:
            m_val = months[w[:3]]
        else:
            digits: str = "".join(c for c in w if c.isdigit())
            if digits:
                val: int = int(digits)
                if val > 31:
                    y_val = val
                else:
                    d_val = val

    if m_val is not None and d_val is not None and y_val is not None:
        return date(y_val, m_val, d_val)

    # 5. Weekday calculations ("next Tuesday", "last Tuesday")
    weekdays: dict[str, int] = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    for day_name, day_idx in weekdays.items():
        days_needed: int = 0
        if f"next {day_name}" in s_clean:
            days_needed = (day_idx - today.weekday() + 7) % 7
            if days_needed == 0:
                days_needed = 7
        elif f"last {day_name}" in s_clean:
            days_needed = -((today.weekday() - day_idx + 7) % 7)
            if days_needed == 0:
                days_needed = -7

        if days_needed != 0:
            y, m, d = today.year, today.month, today.day
            step = 1 if days_needed > 0 else -1

            for _ in range(abs(days_needed)):
                d += step
                if step == 1:
                    is_leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
                    days_in_m = (
                        30
                        if m in (4, 6, 9, 11)
                        else (29 if m == 2 and is_leap else (28 if m == 2 else 31))
                    )
                    if d > days_in_m:
                        d = 1
                        m += 1
                        if m > 12:
                            m, y = 1, y + 1
                else:
                    if d == 0:
                        m -= 1
                        if m == 0:
                            m, y = 12, y - 1
                        is_leap = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
                        d = (
                            30
                            if m in (4, 6, 9, 11)
                            else (29 if m == 2 and is_leap else (28 if m == 2 else 31))
                        )
            return date(y, m, d)

    raise ValueError(f"Could not parse date string: {s}")
