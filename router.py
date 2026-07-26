# ontabs_v10/kernel/router.py

from kernel.kernel import dispatch

# -----------------------------
# FLOW REGISTRY (EEL MAP)
# -----------------------------
FLOW_MAP = {
    "registration": "registration_flow"
}
    # later:
    # "transaction": "transaction_flow",
    # "feed": "feed_flow",


# -----------------------------
# CORE ROUTER FUNCTION
# -----------------------------
def handle_event(flow_key, state, event, ctx):
    """
    Main routing entry for all flows
    """
    print("FLOW =", flow_key)
    print("STATE =", state)
    print("EVENT =", event)

    if flow_key not in FLOW_MAP:
        print("NO FLOW FOUND")
        return state, "NO_FLOW"

    return dispatch(state, event, ctx)
