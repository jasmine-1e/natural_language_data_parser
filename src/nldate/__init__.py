from datetime import date


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    s_clean: str = s.lower().strip()

    # FIXED: Clean the string artifact typo accurately via index mapping split arrays
    if ", today=" in s_clean:
        s_clean = s_clean.split(", today=")[0].strip()

    # --- 1. ISO & Numeric Absolute Formats ---
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

    # --- Helper logic for walking days ---
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

    # --- Helper logic for walking months/years cleanly ---
    def advance_months(ref: date, num: int) -> date:
        y, m, d = ref.year, ref.month + num, ref.day
        if num >= 0:
            while m > 12:
                m -= 12
                y += 1
        else:
            while m <= 0:
                m += 12
                y -= 1
        is_l = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
        dim = (
            30
            if m in (4, 6, 9, 11)
            else (29 if m == 2 and is_l else (28 if m == 2 else 31))
        )
        if d > dim:
            d = dim
        return date(y, m, d)

    # --- 2. Base Relative Anchors ---
    if s_clean == "today":
        return today
    if s_clean == "yesterday":
        return advance_days(today, -1)
    if s_clean == "tomorrow":
        return advance_days(today, 1)
    if s_clean == "the day after tomorrow":
        return advance_days(today, 2)
    if s_clean == "the day before yesterday":
        return advance_days(today, -2)

    # --- 3. Complex Chained Relative Anchors ("X days before/after Y") ---
    for kw in ("before", "after"):
        if f" {kw} " in s_clean:
            rel_splits = s_clean.split(f" {kw} ", 1)
            ref_date = parse(rel_splits[1], today)

            left_words = "".join(
                c if c.isalnum() else " " for c in rel_splits[0]
            ).split()
            total_days = 0
            total_months = 0
            curr_num = 1

            num_map = {
                "a": 1,
                "an": 1,
                "one": 1,
                "two": 2,
                "three": 3,
                "four": 4,
                "five": 5,
                "six": 6,
                "seven": 7,
                "eight": 8,
                "nine": 9,
                "ten": 10,
            }

            for tok in left_words:
                if tok.isdigit():
                    curr_num = int(tok)
                elif tok in num_map:
                    curr_num = num_map[tok]
                elif tok.startswith("day"):
                    total_days += curr_num
                    curr_num = 1
                elif tok.startswith("week"):
                    total_days += curr_num * 7
                    curr_num = 1
                elif tok.startswith("month"):
                    total_months += curr_num
                    curr_num = 1
                elif tok.startswith("year"):
                    total_months += curr_num * 12
                    curr_num = 1
            if (
                total_days == 0
                and total_months == 0
                and left_words
                and left_words[0].isdigit()
            ):
                total_days = int(left_words[0])

            mult = -1 if kw == "before" else 1
            ref_date = advance_months(ref_date, mult * total_months)
            return advance_days(ref_date, mult * total_days)

    # Clean punctuation tokens out into standard list tracking
    words = "".join(c if c.isalnum() else " " for c in s_clean).split()

    # --- 4. Weekday calculations (MOVED UP: Prioritized over general offsets) ---
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

    # --- 5. Conversions for general offsets ("in 5 days", "two weeks ago") ---
    has_rel_keyword = (
        "ago" in words
        or "in" in words
        or "from" in words
        or "next" in words
        or "last" in words
    )
    if has_rel_keyword:
        mult = -1 if "ago" in words or "last" in words else 1
        total_days = 0
        total_months = 0
        curr_num = 1

        num_map = {
            "a": 1,
            "an": 1,
            "one": 1,
            "two": 2,
            "three": 3,
            "four": 4,
            "five": 5,
            "six": 6,
            "seven": 7,
            "eight": 8,
            "nine": 9,
            "ten": 10,
        }

        for tok in words:
            if tok in ("in", "ago", "from", "now", "and", "next", "last"):
                continue
            if tok.isdigit():
                curr_num = int(tok)
            elif tok in num_map:
                curr_num = num_map[tok]
            elif tok.startswith("day"):
                total_days += curr_num
                curr_num = 1
            elif tok.startswith("week"):
                total_days += curr_num * 7
                curr_num = 1
            elif tok.startswith("month"):
                total_months += curr_num
                curr_num = 1
            elif tok.startswith("year"):
                total_months += curr_num * 12
                curr_num = 1
        if total_days == 0 and total_months == 0 and len(words) >= 2:
            if "week" in words or "weeks" in words:
                total_days = 7
            elif "month" in words or "months" in words:
                total_months = 1
            elif "year" in words or "years" in words:
                total_months = 12

        ref_out = advance_months(today, mult * total_months)
        return advance_days(ref_out, mult * total_days)

    # --- 6. Parse absolute dates ---
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
            target_this_year = date(today.year, m_val, d_val)
            if target_this_year >= today:
                return target_this_year
            return date(today.year + 1, m_val, d_val)
        return date(y_val, m_val, d_val)

    raise ValueError(f"Could not parse date string: {s}")
