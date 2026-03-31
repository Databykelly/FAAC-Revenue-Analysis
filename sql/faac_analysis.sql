-- ================================================================
-- FAAC FEDERAL REVENUE ANALYSIS — SQL LAYER
-- Author: Otito Emekekwue
-- Tool: MySQL 8.0
-- Dataset: FAAC_Clean_Combined.csv (2,183 rows | 2020-2024)
-- Description: 6 investor-grade business questions answered in SQL
-- ================================================================


-- ================================================================
-- Q1: HOW STABLE IS NIGERIA'S FEDERAL REVENUE (2020-2024)?
-- Measures total allocation per year to identify growth trends
-- and the impact of external shocks on overall revenue stability
-- ================================================================

SELECT
    Year,
    ROUND(SUM(Total_Allocation) / 1000000000, 2) AS Total_Allocation_Billions
FROM faac_disbursements
GROUP BY Year
ORDER BY Year;


-- ================================================================
-- Q2: HOW DEPENDENT IS NIGERIA ON OIL REVENUE?
-- Measures Gross Statutory Allocation as a percentage of total
-- allocation to track oil dependency across 5 years
-- ================================================================

SELECT
    Year,
    ROUND(SUM(Gross_Statutory) / 1000000000, 2) AS Gross_Statutory_Billions,
    ROUND(SUM(Total_Allocation) / 1000000000, 2) AS Total_Allocation_Billions,
    ROUND(SUM(Gross_Statutory) / SUM(Total_Allocation) * 100, 2) AS Oil_Dependency_Pct
FROM faac_disbursements
GROUP BY Year
ORDER BY Year;


-- ================================================================
-- Q2B: REAL OIL DEPENDENCY (STRIPPING EXCHANGE GAIN EFFECT)
-- Removes Exchange Gain from Total Allocation to reveal the true
-- oil dependency percentage beneath the Naira devaluation effect
-- ================================================================

SELECT
    Year,
    ROUND(SUM(Gross_Statutory) / 1000000000, 2) AS Gross_Statutory_Billions,
    ROUND((SUM(Total_Allocation) - SUM(Exchange_Gain)) / 1000000000, 2) AS Real_Total_Allocation_Billions,
    ROUND(SUM(Gross_Statutory) / (SUM(Total_Allocation) - SUM(Exchange_Gain)) * 100, 2) AS Real_Oil_Dependency_Pct
FROM faac_disbursements
GROUP BY Year
ORDER BY Year;


-- ================================================================
-- Q3: IS NIGERIA'S REVENUE MIX SHIFTING?
-- Measures VAT as a percentage of total allocation to track
-- whether non-oil revenue is growing as a share of the total pie
-- ================================================================

SELECT
    Year,
    ROUND(SUM(VAT) / 1000000000, 2) AS VAT_Billions,
    ROUND(SUM(Total_Allocation) / 1000000000, 2) AS Total_Allocation_Billions,
    ROUND(SUM(VAT) / SUM(Total_Allocation) * 100, 2) AS VAT_Share_Pct
FROM faac_disbursements
GROUP BY Year
ORDER BY Year;


-- ================================================================
-- Q4: WHICH STATES CONSISTENTLY RECEIVE THE MOST AND LEAST?
-- Ranks all 37 states by 5-year total allocation using RANK()
-- window function to identify fiscal concentration patterns
-- ================================================================

SELECT
    State,
    ROUND(SUM(Total_Allocation) / 1000000000, 2) AS Total_5Year_Allocation_Billions,
    RANK() OVER (ORDER BY SUM(Total_Allocation) DESC) AS Allocation_Rank
FROM faac_disbursements
GROUP BY State
ORDER BY Allocation_Rank;


-- ================================================================
-- Q5: WHICH STATES ARE GROWING OR DECLINING IN ALLOCATION SHARE?
-- Uses LAG() window function to calculate year-on-year percentage
-- change per state — identifying momentum and trajectory
-- ================================================================

SELECT
    State,
    Year,
    SUM(Total_Allocation) AS Annual_Allocation,
    LAG(SUM(Total_Allocation)) OVER (PARTITION BY State ORDER BY Year) AS Previous_Year,
    SUM(Total_Allocation) - LAG(SUM(Total_Allocation)) OVER (PARTITION BY State ORDER BY Year) AS Difference,
    ROUND(
        (SUM(Total_Allocation) - LAG(SUM(Total_Allocation)) OVER (PARTITION BY State ORDER BY Year))
        / LAG(SUM(Total_Allocation)) OVER (PARTITION BY State ORDER BY Year) * 100
    , 2) AS YoY_Change_Pct
FROM faac_disbursements
GROUP BY State, Year
ORDER BY State, Year;


-- ================================================================
-- Q6: HOW DID EXTERNAL SHOCKS AFFECT ALLOCATIONS?
-- Monthly breakdown of all revenue components to pinpoint
-- exact timing and magnitude of three major shocks:
-- (1) COVID-19 crash March 2020
-- (2) Russia-Ukraine oil surge February 2022
-- (3) Naira devaluation June 2023
-- ================================================================

SELECT
    Year,
    Month,
    ROUND(SUM(Total_Allocation) / 1000000000, 2) AS Monthly_Total_Billions,
    ROUND(SUM(VAT) / 1000000000, 2) AS Monthly_VAT_Billions,
    ROUND(SUM(Gross_Statutory) / 1000000000, 2) AS Monthly_Statutory_Billions,
    ROUND(SUM(Exchange_Gain) / 1000000000, 2) AS Monthly_Exchange_Gain_Billions
FROM faac_disbursements
GROUP BY Year, Month
ORDER BY Year, Month;


-- ================================================================
-- Q6B: NAIRA DEVALUATION SHOCK — JUNE 2023 DETAIL
-- Isolates 2023 monthly Exchange Gain to show the exact month
-- the devaluation effect hit allocation figures
-- ================================================================

SELECT
    Year,
    Month,
    ROUND(SUM(Exchange_Gain) / 1000000000, 2) AS Exchange_Gain_Billions,
    ROUND(SUM(Total_Allocation) / 1000000000, 2) AS Total_Allocation_Billions
FROM faac_disbursements
WHERE Year = 2023
GROUP BY Year, Month
ORDER BY Year, Month;