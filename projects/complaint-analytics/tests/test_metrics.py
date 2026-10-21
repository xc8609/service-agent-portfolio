import pytest

from triage.metrics import accuracy, estimate_hours_saved, macro_f1, per_class_report, to_teams


def test_accuracy():
    assert accuracy(["a", "b", "c", "a"], ["a", "b", "a", "a"]) == 0.75
    assert accuracy([], []) == 0.0


def test_length_mismatch_raises():
    with pytest.raises(ValueError):
        accuracy(["a"], ["a", "b"])


def test_per_class_report():
    reports = {r.label: r for r in per_class_report(["a", "a", "b"], ["a", "b", "b"])}
    assert reports["a"].precision == 1.0
    assert reports["a"].recall == 0.5
    assert reports["b"].precision == 0.5
    assert reports["b"].recall == 1.0
    assert reports["a"].support == 2


def test_macro_f1_perfect():
    assert macro_f1(["x", "y"], ["x", "y"]) == 1.0


def test_estimate_hours_saved():
    result = estimate_hours_saved(
        monthly_volume=1000,
        minutes_per_manual_triage=6,
        auto_route_rate=0.5,
        accuracy_on_auto_routed=0.9,
        minutes_per_misroute=30,
    )
    assert result["auto_routed"] == 500
    assert result["misroutes"] == pytest.approx(50)
    assert result["gross_hours_saved"] == pytest.approx(50)
    assert result["rework_hours"] == pytest.approx(25)
    assert result["net_hours_saved"] == pytest.approx(25)


def test_estimate_rejects_bad_rate():
    with pytest.raises(ValueError):
        estimate_hours_saved(100, 5, 1.5, 0.9, 10)


def test_to_teams_ignores_within_team_confusion():
    mapping = {"Credit card": "Cards", "Prepaid card": "Cards", "Mortgage": "Home Lending"}
    y_true = ["Credit card", "Mortgage"]
    y_pred = ["Prepaid card", "Mortgage"]
    assert accuracy(y_true, y_pred) == 0.5
    assert accuracy(to_teams(y_true, mapping), to_teams(y_pred, mapping)) == 1.0


def test_to_teams_rejects_out_of_scope_label():
    with pytest.raises(ValueError, match="Debt collection"):
        to_teams(["Debt collection"], {"Mortgage": "Home Lending"})
