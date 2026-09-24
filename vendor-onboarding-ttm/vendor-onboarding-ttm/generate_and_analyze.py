"""
Vendor Onboarding & TTM Optimization - simulated case study.
All data is SYNTHETIC. Generates 1,500 merchant onboarding records, loads them into
SQLite, runs the SQL analysis, and builds the dashboard chart + scorecard.
Run: python generate_and_analyze.py
"""
import sqlite3
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

rng = np.random.default_rng(42)
N = 1500
CATEGORIES = ["Fashion", "Electronics", "Home & Kitchen", "Beauty", "Grocery", "Toys"]
CAT_W = [0.28, 0.22, 0.18, 0.14, 0.10, 0.08]
CAT_COMPLIANCE_LOAD = {"Fashion": 1.0, "Electronics": 1.35, "Home & Kitchen": 1.0,
                       "Beauty": 1.3, "Grocery": 1.25, "Toys": 1.1}  # regulated categories take longer


def simulate(n, reject_p, handoff_scale, seed, verify_scale=1.0, review_scale=1.0):
    r = np.random.default_rng(seed)
    cat = r.choice(CATEGORIES, n, p=CAT_W)
    load = np.array([CAT_COMPLIANCE_LOAD[c] for c in cat])
    start = pd.Timestamp("2025-01-01") + pd.to_timedelta(r.integers(0, 330, n), unit="D")
    d_category = r.gamma(3, 0.5, n) * review_scale                              # category review ~1.5d
    d_handoff = r.gamma(2.5, 1.9, n) * load * handoff_scale     # wait for Central Compliance queue
    d_verify = r.gamma(3, 0.5, n) * load * verify_scale                        # doc verification work
    rejections = np.where(r.random(n) < reject_p, r.integers(1, 4, n), 0)
    d_rework = rejections * r.gamma(2, 0.9, n)                  # each rejection loops back to merchant
    d_approval = r.gamma(3, 0.55, n)
    d_catalog = r.gamma(3, 0.8, n)                              # catalog setup + go-live
    total = d_category + d_handoff + d_verify + d_rework + d_approval + d_catalog
    df = pd.DataFrame({
        "merchant_id": [f"M{100000 + i}" for i in range(n)],
        "category": cat, "application_date": start.date,
        "category_review_days": d_category.round(1), "handoff_wait_days": d_handoff.round(1),
        "doc_verification_days": d_verify.round(1), "doc_rework_days": d_rework.round(1),
        "compliance_approval_days": d_approval.round(1), "catalog_setup_days": d_catalog.round(1),
        "doc_rejections": rejections, "total_ttm_days": total.round(1),
    })
    df["sla_breach"] = (df.total_ttm_days > 14).astype(int)      # SLA = 14 days
    df["status"] = np.where(df.total_ttm_days > 25, "Stuck", "Live")
    return df


baseline = simulate(N, reject_p=0.45, handoff_scale=1.0, seed=1)
# Simulated "to-be" what-if scenario (ASSUMPTIONS, not measured results): a standardized checklist cuts
# rejections and verification effort; a single intake form + parallel Category/Compliance review cuts handoff wait
to_be = simulate(N, reject_p=0.10, handoff_scale=0.30, seed=2, verify_scale=0.7, review_scale=0.8)
baseline.to_csv("data/merchant_onboarding.csv", index=False)

con = sqlite3.connect(":memory:")
baseline.to_sql("onboarding", con, index=False)
queries = open("sql/analysis.sql").read().split(";")
print("=== SQL RESULTS ===")
for q in [q.strip() for q in queries if q.strip()]:
    title = q.splitlines()[0].lstrip("- ").strip()
    print(f"\n{title}")
    print(pd.read_sql(q, con).to_string(index=False))

stages = ["category_review_days", "handoff_wait_days", "doc_verification_days",
          "doc_rework_days", "compliance_approval_days", "catalog_setup_days"]
labels = ["Category review", "Handoff wait\n(Category→Compliance)", "Doc verification",
          "Doc rework", "Compliance approval", "Catalog setup"]
b_mean, t_mean = baseline[stages].mean(), to_be[stages].mean()

print(f"\nAs-is avg TTM: {baseline.total_ttm_days.mean():.1f} days | SLA breach: {baseline.sla_breach.mean():.0%}")
print(f"Simulated to-be avg TTM: {to_be.total_ttm_days.mean():.1f} days | SLA breach: {to_be.sla_breach.mean():.0%}")

fig, ax = plt.subplots(1, 3, figsize=(17, 5))
ax[0].barh(labels, b_mean.values, color="#c0392b")
ax[0].set_title("As-is: avg days per stage"); ax[0].invert_yaxis()
x = np.arange(len(labels)); w = 0.4
ax[1].bar(x - w/2, b_mean.values, w, label="As-is", color="#c0392b")
ax[1].bar(x + w/2, t_mean.values, w, label="Simulated to-be", color="#27ae60")
ax[1].set_xticks(x); ax[1].set_xticklabels([l.split("\n")[0] for l in labels], rotation=35, ha="right")
ax[1].set_title("Stage time: as-is vs simulated to-be"); ax[1].legend()
cat = baseline.groupby("category").sla_breach.mean().sort_values() * 100
ax[2].barh(cat.index, cat.values, color="#2980b9"); ax[2].set_title("SLA breach % by category (>14 days)")
fig.suptitle("Vendor Onboarding Dashboard (simulated data)", fontsize=14)
plt.tight_layout(); plt.savefig("dashboard/dashboard_preview.png", dpi=130)

# Weekly scorecard (import this CSV into Power BI)
baseline["week"] = pd.to_datetime(baseline.application_date).dt.to_period("W").astype(str)
score = baseline.groupby(["week"]).agg(applications=("merchant_id", "count"),
        avg_ttm_days=("total_ttm_days", "mean"), sla_breach_pct=("sla_breach", "mean"),
        stuck_accounts=("status", lambda s: (s == "Stuck").sum())).round(2).reset_index()
score.to_csv("data/weekly_scorecard.csv", index=False)
to_be.to_csv("data/simulated_to_be.csv", index=False)
