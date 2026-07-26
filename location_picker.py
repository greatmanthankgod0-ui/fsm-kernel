from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from kernel.data.nigeria_states import NIGERIA_STATES_LGAS

STATE_NAMES = sorted(NIGERIA_STATES_LGAS.keys())


def build_state_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(s, callback_data=f"state_{s}") for s in STATE_NAMES]
    for i in range(0, len(buttons), 2):
        kb.row(*buttons[i:i+2])
    return kb


def build_lga_keyboard(state):
    lgas = NIGERIA_STATES_LGAS.get(state, [])
    kb = InlineKeyboardMarkup(row_width=2)
    buttons = [InlineKeyboardButton(lga, callback_data=f"lga_{lga}") for lga in lgas]
    for i in range(0, len(buttons), 2):
        kb.row(*buttons[i:i+2])
    return kb


def is_valid_state(name):
    return name in NIGERIA_STATES_LGAS


def is_valid_lga(state, lga):
    return lga in NIGERIA_STATES_LGAS.get(state, [])
