# Vendor Onboarding & Time-to-Market (TTM) Optimization: Case Study

> **Note: this is a self-initiated case study built on SYNTHETIC (simulated) data.** No real company data
> is used. The "to-be" result is a what-if scenario driven by stated assumptions, not a measured outcome.

## Problem
Marketplace merchants take ~2 weeks to go live. Which stage causes the delay, and how could the process be redesigned to cut it?

## What's in this repo
| Path | Contents |
|---|---|
| `generate_and_analyze.py` | Generates 1,500 synthetic merchant onboarding records, loads them to SQLite, runs the SQL, builds charts |
| `sql/analysis.sql` | 5 SQL queries: lead time by stage, doc-stage share, rejection impact, SLA breach by category |
| `data/` | `merchant_onboarding.csv` (1,500 rows), `weekly_scorecard.csv` (import into Power BI), `simulated_to_be.csv` |
| `dashboard/` | `dashboard_preview.png` + Power BI build steps below |
| `docs/SOP_compliance_checklist.md` | Standardized intake framework and compliance checklist |

## Key findings (simulated data)
- Average TTM: **14.2 days**; **~46%** of merchants breach a 14-day SLA.
- The **Category → Central Compliance handoff wait (5.3 days avg)** is the single largest stage.
- Handoff + verification + rework = **~61% of total TTM**.
- Each document rejection adds ~2 days (0 rejections: 12.5 days; 3 rejections: 18.2 days).
- Regulated categories (Electronics, Grocery, Beauty) breach SLA most.

## Proposed redesign
1. Single intake form + **completeness checklist before handoff** (see SOP) to cut first-pass rejections.
2. **1-day pickup SLA** for Compliance with same-day tracker updates.
3. Parallel Category/Compliance review instead of sequential.
4. Weekly scorecard: avg TTM, SLA breach %, stuck accounts.

**Simulated to-be scenario** (assumes rejections 45% → 10%, handoff wait -70%, verification effort -30%):
avg TTM ~**8.4 days**. These are assumptions to be validated with a pilot, not proven results.

## Interactive dashboard
Open `dashboard/dashboard.html` in a browser (works offline; category filter, KPI cards, stage/category/weekly charts). Enable GitHub Pages to get a live link.

## Power BI version (optional, build in ~15 min)
1. Get Data → Text/CSV → load `merchant_onboarding.csv` and `weekly_scorecard.csv`.
2. Cards: Avg TTM, SLA breach %, Stuck accounts. 3. Stacked bar: avg days per stage. 
4. Line: weekly avg TTM (from scorecard). 5. Bar: SLA breach % by category. 
6. Slicers: category, week. Save `.pbix` in `dashboard/` and add screenshots.

## Run it
```
pip install pandas numpy matplotlib
python generate_and_analyze.py
```
