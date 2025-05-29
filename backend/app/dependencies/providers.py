from app.api import WebWunder, ByteMe, PingPerfect, VerbynDich, ServusSpeed
from app.schemas import ProviderEnum, BaseProvider
from typing import Dict
from collections.abc import Callable
import logging

providers: list[BaseProvider] = [
    WebWunder(logger=logging.getLogger(ProviderEnum.WEBWUNDER.value)),
    ByteMe(logger=logging.getLogger(ProviderEnum.BYTEME.value)),
    PingPerfect(logger=logging.getLogger(ProviderEnum.PINGPERFECT.value)),
    VerbynDich(logger=logging.getLogger(ProviderEnum.VERBYNDICH.value)),
    ServusSpeed(logger=logging.getLogger(ProviderEnum.SERVUSSPEED.value)),
]

def _get_provider(provider_name: ProviderEnum) -> BaseProvider:
    """
    Get the provider instance by name.
    """
    return next((provider for provider in providers if provider.provider_name == provider_name), None)

def make_provider_getter(provider_name: ProviderEnum) -> Callable[[], BaseProvider]:
    """
    Create a provider getter function.
    """
    def provider_getter() -> BaseProvider:
        return _get_provider(provider_name)
    return provider_getter

def get_all_providers() -> list[BaseProvider]:
    """
    Get all provider instances.
    """
    return providers