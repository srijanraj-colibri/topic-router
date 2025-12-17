import importlib
import pkgutil
import logging
from core.base import BaseRoute

logger = logging.getLogger("router.registry")


def load_routes():
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
