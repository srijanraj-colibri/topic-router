"""
core.registry
=============

Dynamic route discovery and registration.

This module is responsible for discovering all routing implementations
under the `routes` package, instantiating them, and exposing them to
the event listener.

Routes are discovered dynamically to allow:
- Plug-and-play extensions
- Independent deployment of routing logic
- Clean separation between core routing engine and business rules
"""
import importlib
import pkgutil
import logging

from core.base import BaseRoute

logger = logging.getLogger("router.registry")


def load_routes():
    """
    Discover and load all route implementations.

    This function scans the `routes` package, imports each module,
    and instantiates all classes that subclass `BaseRoute`.

    Returns
    -------
    list of BaseRoute
        Instantiated route objects.

    Notes
    -----
    - Route classes must have a no-argument constructor.
    - Routes are expected to be stateless.
    - Import errors will propagate to fail fast during startup.
    """
    route_instances = []

    import routes

    for _, module_name, _ in pkgutil.iter_modules(routes.__path__):
        module = importlib.import_module(f"routes.{module_name}")

        for obj in vars(module).values():
            if (
                isinstance(obj, type)
                and issubclass(obj, BaseRoute)
                and obj is not BaseRoute
            ):
                route_instances.append(obj())
                logger.info("Loaded route: %s", obj.__name__)

    return route_instances
