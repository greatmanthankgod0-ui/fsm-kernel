TRANSITIONS = {
    "SELLER": {

        ("TC_PENDING", "AGREE"): {
            "guard": "agree_guard",
            "action": "SET_FULL_NAME",
            "next": "ASK_FULL_NAME"
        },

        ("ASK_FULL_NAME", "VALID_NAME"): {
            "guard": "name_guard",
            "action": "SAVE_FULL_NAME",
            "next": "ASK_SHOP_NAME"
        }

    }
}
