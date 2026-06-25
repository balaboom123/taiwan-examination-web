from __future__ import annotations

from app.providers.base import SourceProvider
from app.providers.ceec_gsat.provider import CeecGsatProvider
from app.providers.cpc_recruit.provider import CpcRecruitProvider
from app.providers.moea_recruit.provider import MoeaRecruitProvider
from app.providers.moex.provider import MoexProvider
from app.providers.taipower_recruit.provider import TaipowerRecruitProvider

_PROVIDER_FACTORIES = {
    "ceec_gsat": CeecGsatProvider,
    "cpc_recruit": CpcRecruitProvider,
    "moea_recruit": MoeaRecruitProvider,
    "moex": MoexProvider,
    "taipower_recruit": TaipowerRecruitProvider,
}


def get_provider(provider_id: str) -> SourceProvider:
    try:
        factory = _PROVIDER_FACTORIES[provider_id]
    except KeyError as exc:
        raise ValueError(f"Unknown provider_id: {provider_id}") from exc
    return factory()
