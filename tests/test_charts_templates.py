"""Smoke tests: every chart template produces a non-empty PNG."""

from pathlib import Path

import pytest

from paperforge.charts.builder import ChartBuildRequest, build_chart


@pytest.fixture
def csv_two_columns(tmp_path: Path) -> Path:
    p = tmp_path / "two.csv"
    p.write_text("x,y\n0,1\n1,2\n2,4\n3,8\n", encoding="utf-8")
    return p


@pytest.fixture
def csv_dose_response(tmp_path: Path) -> Path:
    p = tmp_path / "dr.csv"
    p.write_text(
        "strain,dose,viability\n"
        "A,0,100\nA,5,90\nA,10,60\nA,12,30\n"
        "B,0,100\nB,5,98\nB,10,90\nB,12,70\n",
        encoding="utf-8",
    )
    return p


def _build(req: ChartBuildRequest) -> Path:
    res = build_chart(req)
    assert res.path.is_file()
    assert res.path.stat().st_size > 1024, "PNG suspiciously small"
    return res.path


def test_line_template(csv_two_columns: Path, tmp_path: Path) -> None:
    out = tmp_path / "line.png"
    _build(ChartBuildRequest(template="line", csv=csv_two_columns,
                             x_col="x", y_col="y", output=out,
                             title="Line", xlabel="x", ylabel="y"))


def test_log_scale_template(csv_two_columns: Path, tmp_path: Path) -> None:
    out = tmp_path / "log.png"
    _build(ChartBuildRequest(template="log-scale", csv=csv_two_columns,
                             x_col="x", y_col="y", output=out,
                             log_y=True, title="Log"))


def test_scatter_template(csv_two_columns: Path, tmp_path: Path) -> None:
    out = tmp_path / "scatter.png"
    _build(ChartBuildRequest(template="scatter", csv=csv_two_columns,
                             x_col="x", y_col="y", output=out))


def test_dose_response_template(csv_dose_response: Path, tmp_path: Path) -> None:
    out = tmp_path / "dr.png"
    _build(ChartBuildRequest(template="dose-response",
                             csv=csv_dose_response,
                             x_col="dose", y_col="viability",
                             series_col="strain", output=out))


def test_bar_template_from_yaml(tmp_path: Path) -> None:
    import yaml
    yaml_path = tmp_path / "bar.yaml"
    yaml_path.write_text(yaml.safe_dump({
        "template": "bar",
        "title": "Test bars",
        "categories": ["A", "B", "C"],
        "series": [
            {"label": "S1", "values": [1, 2, 3]},
            {"label": "S2", "values": [2, 4, 6]},
        ],
    }), encoding="utf-8")
    out = tmp_path / "bar.png"
    _build(ChartBuildRequest(template="bar", config_file=yaml_path, output=out))
