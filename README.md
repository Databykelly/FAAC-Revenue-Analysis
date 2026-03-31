# FAAC Federal Revenue Analysis

**Status: SQL Complete — Power BI In Progress**

A 5-year analysis of Nigeria's federal revenue distribution (January 2020 – December 2024) built for investors and financial analysts tracking Nigeria's fiscal health and state-level economic exposure.

---

## The Dataset

59 government Excel files downloaded manually from the National Bureau of Statistics Nigeria. No clean version of this dataset existed anywhere online before this project.

The files were inconsistent — sheet names changed 5 times across 5 years, column names varied across years, and some months split state data across multiple sheets. Power Query could not handle the inconsistency so a custom Python script was written to process each file individually.

**Final dataset:** 2,183 rows · 37 states · 59 files · Zero errors

---

## Business Questions

1. How stable is Nigeria's federal revenue between 2020 and 2024?
2. How dependent is Nigeria on oil revenue?
3. Is Nigeria's revenue mix shifting over time?
4. Which states consistently receive the most and least allocation?
5. Which states are growing or declining in allocation share?
6. How did external shocks affect allocations?

---

## Key Findings

- Nigeria's total allocation grew from ₦1.5T in 2020 to ₦3.4T in 2024 — but most of the post-2023 growth is currency-driven, not economic growth
- Oil dependency appears to have fallen from 63% to 12% — the drop is largely an illusion created by Exchange Gain inflating Total Allocation after the June 2023 Naira devaluation
- VAT grew from 30% to 56% of total allocation — a combination of genuine tax collection improvements and inflation effects
- Lagos received ₦898B over 5 years (rank 1). Bayelsa received ₦132B (rank 37) despite sitting on Nigeria's richest oil deposits
- Almost every state grew at the same rate — proving growth is systemic and macro-driven, not individual state performance
- COVID caused a 38% collapse in oil revenue in 4 months with 5-month recovery. Exchange Gain went from zero to ₦59B in a single month after June 2023 devaluation

---

## Repository Structure
```
FAAC-Revenue-Analysis/
│
├── data/
│   ├── faac_clean.py              # Python cleaning script
│   └── FAAC_Clean_Combined.csv    # Clean combined dataset
│
├── sql/
│   └── faac_analysis.sql          # 8 queries answering 6 business questions
│
├── screenshots/                   # Query result screenshots
│
└── README.md
```

---

## Tools

Python · Pandas · MySQL 8.0 · Power BI · GitHub

---

## Data Source

National Bureau of Statistics Nigeria — [nigerianstat.gov.ng](https://nigerianstat.gov.ng)

---

## Data Limitations

- Exchange Gain column has null values for several months in 2022 due to inconsistent reporting in source files
- July 2024 file was structurally corrupted and excluded from analysis
- Gross Statutory Allocation used as oil revenue proxy — other oil-linked components may exist within bundled figures
```

---
