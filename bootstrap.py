from .registration_flows.rules.seller import register_seller_flow
from .registration_flows.rules.buyer import register_buyer_flow
from .registration_flows.rules.driver import register_driver_flow
from .registration_flows.rules.service import register_service_flow
from kernel.kernel import dispatch, register_rule, register_action, register_guard


def init_kernel():
    register_seller_flow()
    register_buyer_flow()
    register_driver_flow()
    register_service_flow()
    print("🐙 FSM Kernel Initialized")
    return True


def load_modules():
    return init_kernel()
