from datetime import date


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s_clean: str = s.lower().strip()
    if ", today=" in s_clean:
        s_clean = s_clean.split(", today=")[0].strip()

    # --- 1. ISO & Numeric Absolute Formats (e.g., '2025-12-04', '2025/12/04') ---
    for sep in ("-", "/"):
        if sep in s_clean:
            iso_parts = [p.strip() for p in s_clean.split(sep)]
            if len(iso_parts) == 3 and all(p.isdigit() for p in iso_parts):
                try:
                    if len(iso_parts[0]) == 4:
                        return date(
                            int(iso_parts[0]), int(iso_parts[1]), int(iso_parts[2])
                        )
                    if len(iso_parts[2]) == 4:
                        return date(
                            int(iso_parts[2]), int(iso_parts[0]), int(iso_parts[1])
                        )
                except ValueError:
                    pass

    # --- Helper logic for day walking without timedelta ---
    def advance_days(ref: date, num: int) -> date:
        y, m, d = ref.year, ref.month, ref.day + num
        if num >= 0:
            while True:
                is_l = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
                dim = (
                    30
                    if m in (4, 6, 9, 11)
                    else (29 if m == 2 and is_l else (28 if m == 2 else 31))
                )
                if d <= dim:
                    break
                d -= dim
                m += 1
                if m > 12:
                    m, y = 1, y + 1
        else:
            while d <= 0:
                m -= 1
                if m == 0:
                    m, y = 12, y - 1
                is_l = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
                dim = (
                    30
                    if m in (4, 6, 9, 11)
                    else (29 if m == 2 and is_l else (28 if m == 2 else 31))
                )
                d += dim
        return date(y, m, d)

    # --- 2. Base Relative Anchors ---
    if s_clean == "today":
        return today
    if s_clean == "yesterday":
        return advance_days(today, -1)
    if s_clean == "tomorrow":
        return advance_days(today, 1)

    # --- 3. Complex Chained Relative Anchors ("X days before/after Y") ---
    for kw in ("before", "after"):
        if f" {kw} " in s_clean:
            rel_splits = s_clean.split(f" {kw} ", 1)
            ref_date = parse(rel_splits[1], today)

            left_words = "".join(
                c if c.isalnum() else " " for c in rel_splits[0]
            ).split()
            total_days = 0
            curr_num = 1
            for tok in left_words:
                if tok.isdigit():
                    curr_num = int(tok)
                elif tok.startswith("day"):
                    total_days += curr_num
                elif tok.startswith("week"):
                    total_days += curr_num * 7
                elif tok.startswith("month"):
                    total_days += curr_num * 30
                elif tok.startswith("year"):
                    total_days += curr_num * 365
            if total_days == 0 and left_words and left_words[0].isdigit():
                total_days = int(left_words[0])

            return advance_days(ref_date, -total_days if kw == "before" else total_days)

    # Clean punctuation tokens out into standard list tracking
    words = "".join(c if c.isalnum() else " " for c in s_clean).split()

    # --- 4. Conversions for general offsets ("in 5 days", "2 weeks ago", "next week", "last month") ---
    if (
        "ago" in words
        or s_clean.startswith("in ")
        or (
            words
            and words[0] in ("next", "last")
            and words[-1] in ("week", "weeks", "month", "months", "year", "years")
        )
    ):
        mult = -1 if "ago" in words or (words and words[0] == "last") else 1
        total_days = 0
        curr_num = 1
        for tok in words:
            if tok in ("in", "ago", "and", "next", "last"):
                continue
            if tok.isdigit():
                curr_num = int(tok)
            elif tok.startswith("day"):
                total_days += curr_num
                curr_num = 1
            elif tok.startswith("week"):
                total_days += curr_num * 7
                curr_num = 1
            elif tok.startswith("month"):
                total_days += curr_num * 30
                curr_num = 1
            elif tok.startswith("year"):
                total_days += curr_num * 365
                curr_num = 1
        if total_days == 0 and len(words) == 2 and words[0] in ("next", "last"):
            # Fallback for bare expressions like "next week" where implicit digit is 1
            if words[1].startswith("week"):
                total_days = 7
            elif words[1].startswith("month"):
                total_days = 30
            elif words[1].startswith("year"):
                total_days = 365

        return advance_days(today, mult * total_days)

    # --- 5. Weekday calculations ("next Tuesday", "last Tuesday", "this Friday") ---
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
        if day_name in words:
            days_needed = 0
            if "next" in words:
                days_needed = (day_idx - today.weekday() + 7) % 7
                if days_needed == 0:
                    days_needed = 7
            elif "last" in words:
                days_needed = -((today.weekday() - day_idx + 7) % 7)
                if days_needed == 0:
                    days_needed = -7
            elif "this" in words:
                days_needed = day_idx - today.weekday()
            else:
                days_needed = (day_idx - today.weekday() + 7) % 7

            return advance_days(today, days_needed)

    # --- 6. Parse absolute dates (e.g., "January 5th, 2025", "June 10") ---
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

    m_val: int | None = None
    d_val: int | None = None
    y_val: int | None = None

    for w in words:
        if len(w) >= 3 and w[:3] in months:
            m_val = months[w[:3]]
        else:
            digits = "".join(c for c in w if c.isdigit())
            if digits:
                val = int(digits)
                if val > 31:
                    y_val = val
                else:
                    d_val = val

    if m_val is not None and d_val is not None:
        if y_val is None:
            # No-year handling: pick the nearest matching future date instance
            target_this_year = date(today.year, m_val, d_val)
            if target_this_year >= today:
                return target_this_year
            return date(today.year + 1, m_val, d_val)
        return date(y_val, m_val, d_val)

    raise ValueError(f"Could not parse date string: {s}")
