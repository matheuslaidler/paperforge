"""Tests for ``charts.data_loader``."""

from paperforge.charts.data_loader import load_csv, series_from_config


def test_load_csv_two_columns(tmp_path):
    csv = tmp_path / "data.csv"
    csv.write_text("t,viability\n0,100\n1,90\n2,80\n", encoding="utf-8")
    data = load_csv(csv, x_col="t", y_col="viability")
    assert len(data.series) == 1
    assert data.series[0].x == [0.0, 1.0, 2.0]
    assert data.series[0].y == [100.0, 90.0, 80.0]


def test_load_csv_with_series_column(tmp_path):
    csv = tmp_path / "data.csv"
    csv.write_text(
        "strain,t,y\nA,0,100\nA,1,90\nB,0,100\nB,1,70\n",
        encoding="utf-8",
    )
    data = load_csv(csv, x_col="t", y_col="y", series_col="strain")
    labels = sorted(s.label for s in data.series)
    assert labels == ["A", "B"]


def test_series_from_config():
    items = [
        {"label": "X", "x": [0, 1, 2], "y": [10, 20, 30], "marker": "s"},
    ]
    series = series_from_config(items)
    assert len(series) == 1
    assert series[0].label == "X"
    assert series[0].marker == "s"
