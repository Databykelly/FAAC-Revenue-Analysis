# Data Exploration Notes

## File Overview
This project uses 60 Excel files downloaded from the NBS e-library 
covering January 2020 to December 2024, with the exception of 
October 2024 which was unavailable on the NBS website at the time 
of download. The files contain FAAC allocation data for federal, 
state, and local governments.

## Sheet Selection
The sheet extracted from every file is the SumSum sheet. This sheet 
was selected because it provides a clean state-level summary of all 
revenue allocations without the complexity found in other sheets such 
as State Details. It contains one row per state and covers all the 
key revenue components needed to answer the 6 business questions.

## Sheet Name Changes Across Years
The SumSum sheet is not consistently named across files. The exact 
name per year is as follows:

| Year      | Sheet Name |
|-----------|------------|
| 2020      | sumsum     |
| 2021      | Sum Sum    |
| 2022      | Sumsum     |
| 2023      | SumSum     |
| 2024      | SumSum     |
| July 2024 | Sum        |

This inconsistency must be handled in Power Query before combining 
the files.

## Column Structure by Year
The following columns appear consistently across most or all years:
- State (labelled as Beneficiaries in 2020 and 2021)
- Gross Statutory Allocation
- Deduction
- Exchange Gain (labelled as FOREX-related columns in 2020 and 2021)
- Value Added Tax (VAT)
- Total Allocation

The following columns only appear from 2022 onwards:
- Total Ecology Fund
- Transfer of 50% Share of Ecology to NDDC/HYPPADEC
- Net Share of Ecology

The following column only appears from 2023 onwards:
- Electronic Money Transfer Levy (EMTL)

The 2021 file contains two additional FOREX Equalisation columns 
that do not appear in any other year. These will be mapped into the 
standard Exchange Gain column during cleaning.

## Key Decisions
The following decisions were made during exploration to balance data 
completeness with cleaning complexity:

1. **Gross Statutory Allocation** will be set to null for 2023 files. 
The data exists in the State Details sheet but pulling from two 
different sheets depending on the year adds unnecessary complexity 
to the Power Query process.

2. **EMTL** will be null for all files before 2023 as this revenue 
stream did not exist in earlier periods.

3. **Ecology-related columns** will be null for all files before 2022 
as this breakdown was not reported separately before that year.

4. **FOREX Equalisation columns** in the 2021 file will be combined 
and mapped into the Exchange Gain column to maintain a consistent 
structure across all years.

## Final Clean Table Structure
The combined clean dataset will contain the following 10 columns:

| Column                   | Notes                              |
|--------------------------|------------------------------------|
| Year                     | Extracted from filename            |
| Month                    | Extracted from filename            |
| State                    | Standardised name across all years |
| Gross Statutory Allocation | Null for 2023 SumSum files       |
| Deduction                | Null where missing                 |
| Exchange Gain            | Includes mapped 2021 FOREX data    |
| EMTL                     | Null for pre-2023 files            |
| Ecology Fund             | Null for pre-2022 files            |
| VAT                      | Consistent across all years        |
| Total Allocation         | Final total per state per month    |
