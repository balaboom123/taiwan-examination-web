from __future__ import annotations

from app.providers.base import SourceProvider
from app.providers.ceec_gsat.provider import CeecGsatProvider
from app.providers.cpc_recruit.provider import CpcRecruitProvider
from app.providers.moea_recruit.provider import MoeaRecruitProvider
from app.providers.moex.provider import MoexProvider
from app.providers.rcpet_cap.provider import RcpetCapProvider
from app.providers.sfi_cert.provider import SfiCertProvider
from app.providers.tabf_cert.provider import TabfCertProvider
from app.providers.taisugar_recruit.provider import TaisugarRecruitProvider
from app.providers.taipower_recruit.provider import TaipowerRecruitProvider
from app.providers.tii_cert.provider import TiiCertProvider
from app.providers.twc_recruit.provider import TwcRecruitProvider
from app.providers.wdasec_skill.provider import WdasecSkillProvider

_PROVIDER_FACTORIES = {
    "ceec_gsat": CeecGsatProvider,
    "cpc_recruit": CpcRecruitProvider,
    "moea_recruit": MoeaRecruitProvider,
    "moex": MoexProvider,
    "rcpet_cap": RcpetCapProvider,
    "sfi_cert": SfiCertProvider,
    "tabf_cert": TabfCertProvider,
    "taisugar_recruit": TaisugarRecruitProvider,
    "taipower_recruit": TaipowerRecruitProvider,
    "tii_cert": TiiCertProvider,
    "twc_recruit": TwcRecruitProvider,
    "wdasec_skill": WdasecSkillProvider,
}


def get_provider(provider_id: str) -> SourceProvider:
    try:
        factory = _PROVIDER_FACTORIES[provider_id]
    except KeyError as exc:
        raise ValueError(f"Unknown provider_id: {provider_id}") from exc
    return factory()
