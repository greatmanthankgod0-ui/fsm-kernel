("ASK_FULL_NAME", "VALID_NAME"): {
    "guard": None,
    "action": "SET_FULL_NAME"
    "next": "ASK_SHOP_NAME"
},

("ASK_SHOP_NAME", "VALID_SHOP_NAME"): {
    "guard": None,
    "action": "SAVE_SHOP_NAME",
    "next": "ASK_PHONE"
}
