# Sample academic report

> A minimal demo for `paperforge pdf`. Replace this content with your work.

## Sumário

1. [Introduction](#1-introduction)
2. [Methods](#2-methods)
3. [Results](#3-results)
4. [References](#4-references)

---

## 1. Introduction

PaperForge converts Markdown into a styled PDF using a headless browser. This
file demonstrates the supported features: tables, code blocks, math formulas,
blockquotes, and an ABNT-style references section.

The thermodynamic equilibrium relation is given by

$$ \Delta G = \Delta H - T \Delta S $$

inline math also works: $E = mc^2$.

## 2. Methods

| Sample | Mass (g) | Volume (mL) |
|--------|----------|-------------|
| A      | **1.20** | 5.0         |
| B      | 0.85     | 4.2         |
| C      | 1.05     | 4.8         |

```python
def normalize(values):
    total = sum(values)
    return [v / total for v in values]
```

## 3. Results

> A blockquote stands out the way a sidebar would.

The viability data showed a **35% improvement** in the treated condition.

## 4. References

ALDIGUIER, A. S. et al. Synergistic temperature and ethanol effect on
*Saccharomyces cerevisiae* dynamic behaviour. **Bioprocess and Biosystems
Engineering**, v. 26, p. 217–222, 2004.

GHOSE, T. K.; TYAGI, R. D. Rapid ethanol fermentation of cellulose hydrolysate.
**Biotechnology and Bioengineering**, v. 21, p. 1401–1420, 1979.
