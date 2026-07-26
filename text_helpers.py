from spellchecker import SpellChecker

_spell = SpellChecker()
_spell.word_frequency.load_words([
    "barbering", "catering", "tailoring", "laundry", "hairdressing",
    "photography", "carpentry", "plumbing", "electrical", "welding",
    "mechanic", "cleaning", "makeup", "nailtech", "cobbler", "vulcanizing",
    "bricklaying", "painting", "tiling", "upholstery", "graphics",
    "videography", "dj", "decoration", "catering", "babysitting",
    "tutoring", "computer", "repairs", "phonerepairs", "generatorrepair",
])

COMMON_SERVICES = [
    "Barbering", "Hairdressing", "Catering", "Tailoring", "Laundry",
    "Photography", "Videography", "Carpentry", "Plumbing", "Electrical Work",
    "Welding", "Mechanic", "Cleaning", "Makeup Artist", "Nail Tech",
    "Cobbler / Shoe Repair", "Vulcanizing", "Bricklaying", "Painting",
    "Tiling", "Upholstery", "Graphic Design", "DJ Services", "Decoration",
    "Babysitting", "Tutoring", "Phone Repairs", "Generator Repair",
]


def suggest_service_correction(text):
    """
    Checks a typed service/skill against the known common services list.
    Returns a suggested match string, or None if it's a reasonably close
    match already or doesn't look like a typo of anything common.
    """
    cleaned = text.strip().lower()
    if not cleaned:
        return None

    for service in COMMON_SERVICES:
        if cleaned == service.lower():
            return None  # exact match, no correction needed

    best_match = None
    best_distance = 3  # max edit distance we'll consider a "typo"

    for service in COMMON_SERVICES:
        dist = _levenshtein(cleaned, service.lower())
        if dist < best_distance:
            best_distance = dist
            best_match = service

    return best_match


def _levenshtein(a, b):
    if len(a) < len(b):
        return _levenshtein(b, a)
    if len(b) == 0:
        return len(a)
    previous_row = range(len(b) + 1)
    for i, c1 in enumerate(a):
        current_row = [i + 1]
        for j, c2 in enumerate(b):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]


def suggest_state_correction(text):
    from kernel.data.nigeria_states import NIGERIA_STATES_LGAS
    cleaned = text.strip().lower()
    if not cleaned:
        return None
    for state in NIGERIA_STATES_LGAS:
        if cleaned == state.lower():
            return None  # exact match
    best_match = None
    best_distance = 4
    for state in NIGERIA_STATES_LGAS:
        dist = _levenshtein(cleaned, state.lower())
        if dist < best_distance:
            best_distance = dist
            best_match = state
    return best_match


def suggest_lga_correction(text, state):
    from kernel.data.nigeria_states import NIGERIA_STATES_LGAS
    cleaned = text.strip().lower()
    lgas = NIGERIA_STATES_LGAS.get(state, [])
    if not lgas:
        return None
    for lga in lgas:
        if cleaned == lga.lower():
            return None  # exact match
    best_match = None
    best_distance = 4
    for lga in lgas:
        dist = _levenshtein(cleaned, lga.lower())
        if dist < best_distance:
            best_distance = dist
            best_match = lga
    return best_match


def get_state_lgas(state):
    from kernel.data.nigeria_states import NIGERIA_STATES_LGAS
    return NIGERIA_STATES_LGAS.get(state, [])


def send_city_confirm(bot, user_id, typed, suggestion):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(f"✅ {suggestion}", callback_data=f"city_use_{suggestion}"),
        InlineKeyboardButton(f"Keep \"{typed}\"", callback_data="city_keep")
    )
    bot.send_message(user_id,
        f"Did you mean *{suggestion}*?",
        reply_markup=kb,
        parse_mode="Markdown"
    )


def send_lga_confirm(bot, user_id, typed, suggestion):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton(f"✅ {suggestion}", callback_data=f"lga_use_{suggestion}"),
        InlineKeyboardButton(f"Keep \"{typed}\"", callback_data="lga_keep")
    )
    bot.send_message(user_id,
        f"Did you mean *{suggestion}*?",
        reply_markup=kb,
        parse_mode="Markdown"
    )


def send_location_confirm(bot, user_id, city, lga):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Yes, that's it", callback_data="location_confirm"),
        InlineKeyboardButton("❌ Change it", callback_data="location_change")
    )
    bot.send_message(user_id,
        f"Just to confirm — you're in *{lga}, {city}*?",
        reply_markup=kb,
        parse_mode="Markdown"
    )
