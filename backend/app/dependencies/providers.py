from app.api import WebWunder, ByteMe, PingPerfect
from app.schemas import ProviderEnum, BaseProvider
from typing import Dict
from collections.abc import Callable
import logging

providers: Dict[ProviderEnum, BaseProvider] = {
    ProviderEnum.WEBWUNDER: WebWunder(logger=logging.getLogger(ProviderEnum.WEBWUNDER.value)),
    ProviderEnum.BYTEME: ByteMe(logger=logging.getLogger(ProviderEnum.BYTEME.value)),
    ProviderEnum.PINGPERFECT: PingPerfect(logger=logging.getLogger(ProviderEnum.PINGPERFECT.value))
    # Add other providers here
}

def get_provider(provider_name: ProviderEnum) -> BaseProvider:
    """
    Get the provider instance by name.
    """
    return providers.get(provider_name, None)

def make_provider_getter(provider_name: ProviderEnum) -> Callable[[], BaseProvider]:
    """
    Create a provider getter function.
    """
    def provider_getter() -> BaseProvider:
        return get_provider(provider_name)
    return provider_getter

def get_all_providers() -> Dict[ProviderEnum, BaseProvider]:
    """
    Get all provider instances.
    """
    return providers