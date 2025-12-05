# lab_cli/actions/__init__.py
from typing import Callable, Dict, Any, List
import inspect

# Type definition for an Action: Function that takes context (dict) and returns bool
ActionFunc = Callable[[Dict[str, Any]], bool]

class ActionDefinition:
    def __init__(self, func: ActionFunc, name: str, params: List[str], help_text: str):
        self.func = func
        self.name = name
        self.params = params
        self.help_text = help_text

# Global registry
ACTION_REGISTRY: Dict[str, ActionDefinition] = {}

def register_action(name: str):
    """Decorator to register a function as a usable experiment step."""
    def decorator(func):
        # Inspect function arguments to know what to ask the user
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())

        # 'context' is an internal argument, don't ask user for it
        if "context" in params:
            params.remove("context")

        ACTION_REGISTRY[name] = ActionDefinition(
            func=func,
            name=name,
            params=params,
            help_text=func.__doc__ or "No description."
        )
        return func
    return decorator

def get_all_actions():
    return ACTION_REGISTRY

def get_action(name: str):
    return ACTION_REGISTRY.get(name)

# --- Import modules here to ensure they register themselves ---
from . import general_actions
from . import cryo_actions
from . import laser_actions
# Future: from . import oscilloscope_actions
