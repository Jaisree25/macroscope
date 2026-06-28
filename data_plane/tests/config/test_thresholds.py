"""Threshold table loads and covers every watched series (design §7.3/§7.4)."""

from __future__ import annotations

from data_plane.config.thresholds import load_thresholds


def test_loads_all_base_indicators():
    cfg = load_thresholds()
    for sid in ["DFF", "CPIAUCSL", "PAYEMS", "UNRATE", "GDPC1", "DGS10", "UMCSENT", "SP500", "VIXCLS"]:
        assert cfg.for_series(sid) is not None, f"missing threshold for {sid}"


def test_loads_four_composites():
    cfg = load_thresholds()
    assert set(cfg.composites) == {"yield_curve", "sahm", "risk_off", "stagflation"}


def test_tiers_present_for_surprise_series():
    cfg = load_thresholds()
    cpi = cfg.for_series("CPIAUCSL")
    assert cpi.notable.z == 2 and cpi.significant.z == 3
    assert cpi.warmup == cpi.window == 12
