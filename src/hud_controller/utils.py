"""Utility functions for the OI evaluation framework."""

import importlib
import logging
import pkgutil

logger = logging.getLogger(__name__)


def import_submodules(module):
    """Import all submodules of a module, recursively.
    
    This is used to ensure all problem definitions are registered
    when the app starts up.
    """
    for _loader, module_name, _is_pkg in pkgutil.walk_packages(
        module.__path__, module.__name__ + "."
    ):
        importlib.import_module(module_name)
