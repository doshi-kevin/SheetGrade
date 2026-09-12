from sheetgrade.infer import ROUTING_TABLE, BackendTarget, CallSite, route


def test_every_call_site_has_a_routing_entry():
    for call_site in CallSite:
        assert call_site in ROUTING_TABLE


def test_high_volume_low_stakes_call_sites_route_local():
    assert route(CallSite.REGION_CLASSIFICATION) is BackendTarget.LOCAL
    assert route(CallSite.HEADER_EMBEDDING) is BackendTarget.LOCAL


def test_low_volume_quality_critical_call_site_routes_hosted():
    assert route(CallSite.FEEDBACK_GENERATION) is BackendTarget.HOSTED
