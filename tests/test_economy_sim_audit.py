from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import economy_sim_audit as audit


def test_settlement_audit_flags_route_and_market_gaps():
    report = audit.build_report()
    settlement_fields = report["settlements"]["detailed_only_fields"]

    assert "trade_routes" in settlement_fields
    assert "market" in settlement_fields
    assert "imports" in settlement_fields


def test_union_and_wolfshead_audit_flags_expected_economic_gaps():
    report = audit.build_report()

    assert "whisper_agents" in report["unions"]["missing_union_fields"]
    assert "tribute_livestock_monthly" in report["unions"]["missing_member_fields"]
    assert "survival_strategy" in report["wolfsheads"]["missing_fields"]


def test_markdown_report_mentions_top_level_gap_categories():
    rendered = audit.render_markdown(audit.build_report())

    assert "Settlement Economy Gaps" in rendered
    assert "Wolfshead Band Gaps" in rendered
    assert "Contract-Market Gaps" in rendered
