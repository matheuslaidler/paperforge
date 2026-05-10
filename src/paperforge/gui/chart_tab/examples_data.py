"""Built-in example data loaded the first time each template is selected.

Removes the "fill data to render" friction: as soon as the user opens the
Chart tab, every template has a meaningful preview. The user can edit any
cell to override or click *Clear* to start from scratch.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from paperforge.charts.data_loader import Series
from paperforge.gui.chart_tab.state import Band, EnvelopeSpec, VLine


@dataclass
class TemplateExample:
    title: str = ""
    xlabel: str = ""
    ylabel: str = ""
    source: str = ""
    log_x: bool = False
    log_y: bool = False
    legend_loc: str = "best"
    series: list[Series] = field(default_factory=list)
    bar_categories: list[str] = field(default_factory=list)
    bar_series: list[dict] = field(default_factory=list)
    vlines: list[VLine] = field(default_factory=list)
    bands: list[Band] = field(default_factory=list)
    envelopes: list[EnvelopeSpec] = field(default_factory=list)


# ---------- LINE ---------------------------------------------------------- #
def _line_example() -> TemplateExample:
    return TemplateExample(
        title="Sample line chart",
        xlabel="Time (h)",
        ylabel="Concentration (g/L)",
        source="PaperForge demo",
        legend_loc="lower right",
        series=[
            Series(
                label="Treatment A",
                x=[0, 6, 12, 18, 24, 36, 48],
                y=[0, 8, 22, 38, 50, 58, 62],
                marker="o", linestyle="-", color="#2E86AB",
            ),
            Series(
                label="Treatment B",
                x=[0, 6, 12, 18, 24, 36, 48],
                y=[0, 5, 14, 24, 34, 42, 46],
                marker="s", linestyle="-", color="#06A77D",
            ),
        ],
    )


# ---------- BAR ----------------------------------------------------------- #
def _bar_example() -> TemplateExample:
    return TemplateExample(
        title="Yield comparison ± treatment",
        xlabel="",
        ylabel="Ethanol yield (g/L)",
        source="Burphan et al. 2018 — adapted",
        legend_loc="upper left",
        bar_categories=[
            "BY4742\n30 °C", "BY4742\n40 °C",
            "TISTR5606\n30 °C", "TISTR5606\n40 °C",
        ],
        bar_series=[
            {"label": "Control", "color": "#D62246",
             "values": [60.3, 35.2, 66.1, 45.4]},
            {"label": "+ NAC 30 mM", "color": "#06A77D",
             "values": [69.3, 44.0, 73.6, 55.3]},
        ],
    )


# ---------- LOG-SCALE (yeast biomass × ethanol fermentation) -------------- #
def _log_scale_example() -> TemplateExample:
    """Real fermentation case study: biomass-vs-ethanol log chart out of the box."""
    F = 0.30  # OD600 -> g/L dry weight conversion factor

    def od_to_g(od: list[float]) -> list[float]:
        return [round(v * F, 3) for v in od]

    return TemplateExample(
        title=("Biomass of S. cerevisiae vs accumulated ethanol "
               "(VHG fermentation)"),
        xlabel="Accumulated ethanol, P (g/L)",
        ylabel="Biomass, X (g/L dry weight, log scale)",
        source=("BURPHAN et al. Sci Rep 8:13069, 2018  ·  "
                "GHOSE & TYAGI Biotechnol Bioeng 21:1401, 1979  ·  "
                "OD600 → g/L factor 0.30"),
        log_y=True,
        legend_loc="lower left",
        series=[
            Series(
                label="TISTR5606 — 30 °C — no NAC",
                x=[0.5, 10, 25, 40, 55, 63, 66.1],
                y=od_to_g([0.5, 3.0, 7.0, 11.0, 14.0, 14.0, 14.0]),
                marker="s", linestyle="-", color="#06A77D",
            ),
            Series(
                label="TISTR5606 — 30 °C + NAC 30 mM",
                x=[0.5, 12, 28, 45, 60, 70, 73.6],
                y=od_to_g([0.5, 3.5, 8.0, 13.0, 16.0, 17.0, 17.0]),
                marker="s", linestyle="-", color="#2E86AB",
            ),
            Series(
                label="TISTR5606 — 40 °C — no NAC",
                x=[0.3, 8, 18, 28, 36, 42, 45.4],
                y=od_to_g([0.4, 2.0, 4.0, 6.0, 8.0, 9.0, 9.5]),
                marker="^", linestyle="-", color="#F4A261",
            ),
            Series(
                label="TISTR5606 — 40 °C + NAC 30 mM",
                x=[0.3, 10, 22, 35, 45, 52, 55.3],
                y=od_to_g([0.4, 2.5, 5.0, 8.0, 10.0, 11.0, 11.5]),
                marker="^", linestyle="-", color="#D62246",
            ),
            Series(
                label="BY4742 lab — 40 °C — no NAC",
                x=[0.2, 5, 14, 22, 28, 33, 35.2],
                y=od_to_g([0.3, 1.5, 3.0, 4.0, 5.0, 6.0, 6.5]),
                marker="v", linestyle="--", color="#5C5C5C",
            ),
            Series(
                label="BY4742 lab — 40 °C + NAC 30 mM",
                x=[0.2, 8, 18, 28, 35, 41, 44.0],
                y=od_to_g([0.3, 2.0, 4.0, 6.0, 7.5, 8.5, 9.0]),
                marker="v", linestyle="--", color="#9D4EDD",
            ),
        ],
        vlines=[
            VLine(x=50, label="inhibition limit (Basso 2008)",
                  color="#888888", linestyle="--", alpha=0.5),
        ],
        bands=[
            Band(x_start=60, x_end=75, label="industrial VHG zone",
                 color="#06A77D", alpha=0.10),
        ],
        envelopes=[
            EnvelopeSpec(label="Ghose-Tyagi  P_crit=75 g/L",
                         expression="10 * (1 - x / 75) ** 1",
                         color="#999999", alpha=0.55),
            EnvelopeSpec(label="Ghose-Tyagi  P_crit=90 g/L",
                         expression="10 * (1 - x / 90) ** 1",
                         color="#666666", alpha=0.65),
            EnvelopeSpec(label="Ghose-Tyagi  P_crit=105 g/L",
                         expression="10 * (1 - x / 105) ** 1",
                         color="#333333", alpha=0.75),
        ],
    )


# ---------- SCATTER ------------------------------------------------------- #
def _scatter_example() -> TemplateExample:
    return TemplateExample(
        title="Correlation between dose and response",
        xlabel="Dose (mM)",
        ylabel="Response (a.u.)",
        source="PaperForge demo",
        series=[
            Series(
                label="Replicate 1",
                x=[1, 2, 3, 5, 7, 10, 14, 18, 22, 28, 35],
                y=[1.2, 2.4, 3.0, 5.1, 6.4, 9.8, 13.0, 17.5, 22.0, 27.4, 33.1],
                marker="o", color="#2E86AB",
            ),
            Series(
                label="Replicate 2",
                x=[1, 2, 3, 5, 7, 10, 14, 18, 22, 28, 35],
                y=[0.9, 2.0, 2.8, 5.5, 6.0, 10.2, 13.6, 16.7, 22.7, 26.8, 34.3],
                marker="^", color="#06A77D",
            ),
        ],
    )


# ---------- DOSE-RESPONSE ------------------------------------------------- #
def _dose_response_example() -> TemplateExample:
    return TemplateExample(
        title="Dose-response — ethanol tolerance",
        xlabel="Ethanol concentration (% v/v)",
        ylabel="Cell viability (%)",
        source=("SUNYER-FIGUERES et al. Antioxidants 10:1735, 2021  ·  "
                "YANG et al. Front Microbiol 13:976321, 2022"),
        series=[
            Series(
                label="BY4743 (laboratory)",
                x=[0, 4, 6, 8, 9, 10, 12, 14],
                y=[100, 98, 92, 78, 70, 61.1, 30, 8],
                marker="o", linestyle="-", color="#D62246",
            ),
            Series(
                label="QA23 (industrial wine yeast)",
                x=[0, 4, 6, 8, 9, 10, 12, 14],
                y=[100, 99, 97, 94, 92, 88.3, 65, 25],
                marker="s", linestyle="-", color="#06A77D",
            ),
            Series(
                label="YN81 (ALE-evolved mutant)",
                x=[0, 4, 6, 8, 9, 10, 12, 14],
                y=[100, 99.5, 98, 95, 90.7, 60.2, 18, 4],
                marker="^", linestyle="-", color="#2E86AB",
            ),
            Series(
                label="CS31 (parent strain)",
                x=[0, 4, 6, 8, 9, 10, 12, 14],
                y=[100, 97, 90, 80, 66.8, 24.7, 6, 1],
                marker="v", linestyle="-", color="#F4A261",
            ),
        ],
    )


REGISTRY: dict[str, callable] = {
    "line": _line_example,
    "bar": _bar_example,
    "log-scale": _log_scale_example,
    "scatter": _scatter_example,
    "dose-response": _dose_response_example,
}


def get_example(template: str) -> TemplateExample:
    """Return a fresh ``TemplateExample`` for the given template name."""
    factory = REGISTRY.get(template)
    return factory() if factory else TemplateExample()
