from __future__ import annotations

from app.providers.base import SourceProvider
from app.providers.ceec_gsat.provider import CeecGsatProvider
from app.providers.cpc_recruit.provider import CpcRecruitProvider
from app.providers.gept_cert.provider import GeptCertProvider
from app.providers.ipas_cert.provider import IpasCertProvider
from app.providers.moea_recruit.provider import MoeaRecruitProvider
from app.providers.moex.provider import MoexProvider
from app.providers.rcpet_cap.provider import RcpetCapProvider
from app.providers.sfi_cert.provider import SfiCertProvider
from app.providers.tabf_cert.provider import TabfCertProvider
from app.providers.taisugar_recruit.provider import TaisugarRecruitProvider
from app.providers.taipower_recruit.provider import TaipowerRecruitProvider
from app.providers.teacher_qual.provider import TeacherQualProvider
from app.providers.teacher_recruit_central_alliance.provider import CentralAllianceRecruitProvider
from app.providers.teacher_recruit_kaohsiung.provider import KaohsiungTeacherRecruitProvider
from app.providers.teacher_recruit_newtaipei.provider import NewTaipeiTeacherRecruitProvider
from app.providers.teacher_recruit_taipei_junior.provider import TaipeiJuniorRecruitProvider
from app.providers.teacher_recruit_tainan.provider import TainanTeacherRecruitProvider
from app.providers.teacher_recruit_taoyuan_elementary.provider import TaoyuanElementaryRecruitProvider
from app.providers.tii_cert.provider import TiiCertProvider
from app.providers.tocfl_cert.provider import TocflCertProvider
from app.providers.tqc_cert.provider import TqcCertProvider
from app.providers.twc_recruit.provider import TwcRecruitProvider
from app.providers.wdasec_skill.provider import WdasecSkillProvider

_PROVIDER_FACTORIES = {
    "ceec_gsat": CeecGsatProvider,
    "cpc_recruit": CpcRecruitProvider,
    "gept_cert": GeptCertProvider,
    "ipas_cert": IpasCertProvider,
    "moea_recruit": MoeaRecruitProvider,
    "moex": MoexProvider,
    "rcpet_cap": RcpetCapProvider,
    "sfi_cert": SfiCertProvider,
    "tabf_cert": TabfCertProvider,
    "taisugar_recruit": TaisugarRecruitProvider,
    "taipower_recruit": TaipowerRecruitProvider,
    "teacher_qual": TeacherQualProvider,
    "teacher_recruit_central_alliance": CentralAllianceRecruitProvider,
    "teacher_recruit_kaohsiung": KaohsiungTeacherRecruitProvider,
    "teacher_recruit_newtaipei": NewTaipeiTeacherRecruitProvider,
    "teacher_recruit_taipei_junior": TaipeiJuniorRecruitProvider,
    "teacher_recruit_tainan": TainanTeacherRecruitProvider,
    "teacher_recruit_taoyuan_elementary": TaoyuanElementaryRecruitProvider,
    "tii_cert": TiiCertProvider,
    "tocfl_cert": TocflCertProvider,
    "tqc_cert": TqcCertProvider,
    "twc_recruit": TwcRecruitProvider,
    "wdasec_skill": WdasecSkillProvider,
}


def get_provider(provider_id: str) -> SourceProvider:
    try:
        factory = _PROVIDER_FACTORIES[provider_id]
    except KeyError as exc:
        raise ValueError(f"Unknown provider_id: {provider_id}") from exc
    return factory()
