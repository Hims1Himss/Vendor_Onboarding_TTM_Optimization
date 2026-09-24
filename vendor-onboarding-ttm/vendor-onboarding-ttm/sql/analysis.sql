-- 1. Overall onboarding lead-time summary
SELECT COUNT(*) AS merchants, ROUND(AVG(total_ttm_days),1) AS avg_ttm_days,
       ROUND(AVG(sla_breach)*100,1) AS sla_breach_pct
FROM onboarding;

-- 2. Average days per stage (where does time go?)
SELECT ROUND(AVG(category_review_days),1) AS category_review,
       ROUND(AVG(handoff_wait_days),1) AS handoff_wait,
       ROUND(AVG(doc_verification_days),1) AS doc_verification,
       ROUND(AVG(doc_rework_days),1) AS doc_rework,
       ROUND(AVG(compliance_approval_days),1) AS compliance_approval,
       ROUND(AVG(catalog_setup_days),1) AS catalog_setup
FROM onboarding;

-- 3. Share of total TTM spent in document handoff + verification + rework
SELECT ROUND(100.0*SUM(handoff_wait_days+doc_verification_days+doc_rework_days)/SUM(total_ttm_days),1) AS doc_stage_share_pct
FROM onboarding;

-- 4. Impact of document rejections on TTM
SELECT doc_rejections, COUNT(*) AS merchants, ROUND(AVG(total_ttm_days),1) AS avg_ttm_days
FROM onboarding GROUP BY doc_rejections ORDER BY doc_rejections;

-- 5. SLA breach and stuck accounts by category
SELECT category, COUNT(*) AS merchants, ROUND(AVG(total_ttm_days),1) AS avg_ttm_days,
       ROUND(AVG(sla_breach)*100,1) AS sla_breach_pct,
       SUM(CASE WHEN status='Stuck' THEN 1 ELSE 0 END) AS stuck_accounts
FROM onboarding GROUP BY category ORDER BY sla_breach_pct DESC
