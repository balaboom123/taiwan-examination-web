from __future__ import annotations

from app.providers.base import SourceProvider
from app.providers.ceec_gsat.provider import CeecGsatProvider
from app.providers.moex.provider import MoexProvider
from app.providers.wdasec_skill.provider import WdasecSkillProvider

_PROVIDER_FACTORIES = {
    "ceec_gsat": CeecGsatProvider,
    "moex": MoexProvider,
    "wdasec_skill": WdasecSkillProvider,
}


def get_provider(provider_id: str) -> SourceProvider:
    try:
        factory = _PROVIDER_FACTORIES[provider_id]
    except KeyError as exc:
        raise ValueError(f"Unknown provider_id: {provider_id}") from exc
    return factory()
