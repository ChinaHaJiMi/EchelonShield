"""
组件注册表 - 将所有组件挂载到引擎
"""

from core.engine import engine
from components.clamav_component import ClamAVComponent
from components.falco_component import FalcoComponent
from components.wazuh_component import WazuhComponent
from components.tetragon_component import TetragonComponent
from components.rkhunter_component import RkhunterComponent
from components.osquery_component import OsqueryComponent
from components.fail2ban_component import Fail2banComponent
from components.suricata_component import SuricataComponent
from components.ufw_component import UFWComponent
from components.crowdsec_component import CrowdSecComponent
from components.lynis_component import LynisComponent
from components.trivy_component import TrivyComponent
from components.kubearmor_component import KubeArmorComponent
from components.safety_component import SafetyComponent
from components.loki_component import LokiComponent


def register_all():
    """注册所有安全组件到引擎"""
    components = [
        ClamAVComponent(),
        FalcoComponent(),
        WazuhComponent(),
        TetragonComponent(),
        RkhunterComponent(),
        OsqueryComponent(),
        Fail2banComponent(),
        SuricataComponent(),
        UFWComponent(),
        CrowdSecComponent(),
        LynisComponent(),
        TrivyComponent(),
        KubeArmorComponent(),
        SafetyComponent(),
        LokiComponent(),
    ]
    for comp in components:
        engine.register(comp)
    return engine


def init_engine():
    """初始化引擎并注册所有组件"""
    register_all()
    engine.start()
    return engine