from datetime import date


def parse(s: str, today: date | None = None) -> date:
    if today is None:
        today = date.today()

    # Normalize structural strings and eliminate inline testing artifact typos
    s_clean: str = s.lower().strip()
    if ", today=" in s_clean:
        s_clean = s_clean.split(", today=")[0].strip()

    # 1. Direct ISO Format Scanner (e.g., "2025-12-04")
    if "-" in s_clean:
        parts: list[str] = [p.strip() for p in s_clean.split("-")]
        if (
            len(parts) == 3
            and parts[0].isdigit()
            and parts[1].isdigit()
            and parts[2].isdigit()
        ):
            try:
                return date(int(parts[0]), int(parts[1]), int(parts[2]))
            except ValueError:
                pass

    # 2. Tokenize and clean phrases into clear structural units
    words: list[str] = "".join(c if c.isalnum() else " " for c in s_clean).split()

    # 3. Base Relative Anchors
    if len(words) == 1:
        if words[0] == "today":
            return today
        if words[0] == "yesterday":
            y, m, d = today.year, today.month, today.day - 1
            if d == 0:
                m -= 1
                if m == 0:
                    m, y = 12, y - 1
                is_l = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
                d = (
                    30
                    if m in (4, 6, 9, 11)
                    else (29 if m == 2 and is_l else (28 if m == 2 else 31))
                )
            return date(y, m, d)
        if words[0] == "tomorrow":
            y, m, d = today.year, today.month, today.day + 1
            is_l = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
            dim = (
                30
                if m in (4, 6, 9, 11)
                else (29 if m == 2 and is_l else (28 if m == 2 else 31))
            )
            if d > dim:
                d, m = 1, m + 1
                if m > 12:
                    m, y = 1, y + 1
            return date(y, m, d)

    # 4. Multi-Unit Relative Chaining Engine (e.g., "1 year and 2 months after yesterday")
    if "before" in words or "after" in words or "from" in words or "in" in words:
        direction: int = -1 if "before" in words else 1

        # Identify the reference anchor boundary index
        ref_idx: int = -1
        for kw in ["before", "after", "from"]:
            if kw in words:
                ref_idx = words.index(kw)
                break

        # Fallback for "in X days" syntax
        if ref_idx == -1 and "in" in words:
            ref_idx = words.index("in")
            direction = 1
            ref_str = "today"
        else:
            ref_str = " ".join(words[ref_idx + 1 :])

        ref_date: date = parse(ref_str, today)

        # Parse all distinct structural unit intervals on the left side of the phrase
        scan_area: list[str] = (
            words[:ref_idx] if ref_idx != -1 else words[ref_idx + 1 :]
        )

        total_days: int = 0
        current_num: int = (
            1  # Default fallback quantity if omitted (e.g., "a week after")
        )

        for token in scan_area:
            digits: str = "".join(c for c in token if c.isdigit())
            if digits:
                current_num = int(digits)
                continue

            # Convert units to exact or approximate day counts
            if token.startswith("day"):
                total_days += current_num * 1
            elif token.startswith("week"):
                total_days += current_num * 7
            elif token.startswith("month"):
                total_days += current_num * 30  # Standard financial approximation
            elif token.startswith("year"):
                total_days += current_num * 365  # Standard calendar approximation

        # Walk step-by-step through calendar transitions to safely apply math
        y, m, d = ref_date.year, ref_date.month, ref_date.day
        step: int = 1 if direction == 1 else -1
        for _ in range(total_days):
            d += step
            if step == 1:
                is_l = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
                dim = (
                    30
                    if m in (4, 6, 9, 11)
                    else (29 if m == 2 and is_l else (28 if m == 2 else 31))
                )
                if d > dim:
                    d, m = 1, m + 1
                    if m > 12:
                        m, y = 1, y + 1
            else:
                if d == 0:
                    m -= 1
                    if m == 0:
                        m, y = 12, y - 1
                    is_l = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
                    d = (
                        30
                        if m in (4, 6, 9, 11)
                        else (29 if m == 2 and is_l else (28 if m == 2 else 31))
                    )
        return date(y, m, d)

    # 5. Day-of-Week Navigation Engine (e.g., "next Tuesday", "last Friday")
    weekdays: dict[str, int] = {
        "monday": 0,
        "tuesday": 1,
        "wednesday": 2,
        "thursday": 3,
        "friday": 4,
        "saturday": 5,
        "sunday": 6,
    }
    for w_name, w_idx in weekdays.items():
        if w_name in words:
            days_needed: int = 0
            if "next" in words:
                days_needed = (w_idx - today.weekday() + 7) % 7
                if days_needed == 0:
                    days_needed = 7
            elif "last" in words:
                days_needed = -((today.weekday() - w_idx + 7) % 7)
                if days_needed == 0:
                    days_needed = -7
            else:
                # Omitted modifier (e.g., "on Tuesday") defaults to the nearest upcoming day of week
                days_needed = (w_idx - today.weekday() + 7) % 7

            if days_needed != 0:
                y, m, d = today.year, today.month, today.day
                step = 1 if days_needed > 0 else -1
                for _ in range(abs(days_needed)):
                    d += step
                    if step == 1:
                        is_l = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
                        dim = (
                            30
                            if m in (4, 6, 9, 11)
                            else (29 if m == 2 and is_l else (28 if m == 2 else 31))
                        )
                        if d > dim:
                            d, m = 1, m + 1
                            if m > 12:
                                m, y = 1, y + 1
                    else:
                        if d == 0:
                            m -= 1
                            if m == 0:
                                m, y = 12, y - 1
                            is_l = y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)
                            d = (
                                30
                                if m in (4, 6, 9, 11)
                                else (29 if m == 2 and is_l else (28 if m == 2 else 31))
                            )
                return date(y, m, d)

    # 6. Comprehensive Textual Absolute Date Matcher (e.g., "December 1st, 2025")
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
    m_val, d_val, y_val = None, None, None
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
            y_val = today.year  # Fallback to current year if left out
        return date(y_val, m_val, d_val)

    raise ValueError(f"Could not parse date string: {s}")
