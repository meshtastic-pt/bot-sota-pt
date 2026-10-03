
from config.regions_ct import REGIOES_CT, parse_sota_ref

def test_regions():
    assert len(REGIOES_CT) == 11
    assert REGIOES_CT["AL"] == "Algarve"
    assert REGIOES_CT["TM"] == "Trás-os-Montes e Alto Douro"

def test_refs():
    assert parse_sota_ref("CT/AL-001") == ("CT", "AL", "001")
    assert parse_sota_ref("CT-AL-001") == ("CT", "AL", "001")
    assert parse_sota_ref("AL-001") == ("CT", "AL", "001")
