import pandas as pd
import os
import re

folder = r"C:\Users\Lukeg\Documents\DATA ANALYST STUDY FILES\FAAC_Raw_Files"
output = r"C:\Users\Lukeg\Documents\DATA ANALYST STUDY FILES\FAAC_Clean_Combined.csv"

COLUMN_MAP = {
    'beneficiaries': 'State',
    'state': 'State',
    'gross statutory allocation': 'Gross_Statutory',
    'statutory allocation': 'Gross_Statutory',
    'net statutory allocation': 'Gross_Statutory',
    'statutory': 'Gross_Statutory',
    'value added tax': 'VAT',
    'net vat allocation': 'VAT',
    'vat': 'VAT',
    'total net amount': 'Total_Allocation',
    'total net allocation': 'Total_Allocation',
    'total allocation': 'Total_Allocation',
    'net allocation': 'Total_Allocation',
    'total': 'Total_Allocation',
    'exchange gain': 'Exchange_Gain',
    'exchange gain allocation': 'Exchange_Gain',
    'distribution from forex equalisation account': 'Exchange_Gain',
    'deduction': 'Deduction',
    'electronic money transfer levy (emtl)': 'EMTL',
    'electronic money transfer levy': 'EMTL',
}

MONTHS = {
    'january':1,'february':2,'march':3,'april':4,'may':5,'june':6,
    'july':7,'august':8,'september':9,'october':10,'november':11,'december':12
}

NIGERIAN_STATES = {
    'abia','adamawa','akwa ibom','anambra','bauchi','bayelsa','benue','borno',
    'cross river','delta','ebonyi','edo','ekiti','enugu','gombe','imo','jigawa',
    'kaduna','kano','katsina','kebbi','kogi','kwara','lagos','nasarawa','nassarawa',
    'niger','ogun','ondo','osun','oyo','plateau','rivers','sokoto','taraba',
    'yobe','zamfara','fct-abuja','fct'
}

SHEET_PRIORITY = [
    'sum sum', 'sumsum', 'sumlgcs', 'sum lgc', 'sum lgcs',
    'lgcs sum', 'summary', 'sum & fg'
]

SKIP_SHEETS = [
    'ecology to states', 'ecology to individuals', 'ecology to lgcs',
    'states ecology', 'monthentry', 'lg details', 'lg detail',
    'lgcs details', 'lgc details', 'state details', 'sg details',
    'ecology to lgcs', 'individual lgcs', 'ecology'
]

def extract_month_year(filename):
    name = filename.lower().replace('_',' ').replace('-',' ')
    year_match = re.search(r'20\d{2}', name)
    year = int(year_match.group()) if year_match else None
    month = None
    for m in MONTHS:
        if m in name:
            month = MONTHS[m]
            break
    return month, year

def clean_value(val):
    if pd.isna(val):
        return None
    val = str(val).replace(',','').replace('₦','').replace(' ','').strip()
    try:
        return float(val)
    except:
        return None

def normalize_state(val):
    val = str(val).strip()
    val = re.sub(r'\s+LGCS?$', '', val, flags=re.IGNORECASE)
    val = re.sub(r'\s+LGC$', '', val, flags=re.IGNORECASE)
    if re.match(r'^FCT[\s,\-]', val, re.IGNORECASE) or val.upper() in ['FCT', 'FCT-ABUJA', 'FCT, ABUJA']:
        val = 'FCT-ABUJA'
    return val.strip().upper()

def is_state_row(val):
    if pd.isna(val):
        return False
    val_clean = str(val).strip().lower()
    if 'total' in val_clean:
        return False
    if re.match(r'^\d+\.?\d*$', val_clean):
        return False
    normalized = normalize_state(val).lower()
    if normalized in NIGERIAN_STATES:
        return True
    for s in NIGERIAN_STATES:
        if s in normalized and len(normalized) < len(s) + 8:
            return True
    return False

def try_read_sheet(filepath, sheet_name):
    for i in range(11):
        try:
            temp = pd.read_excel(filepath, sheet_name=sheet_name, header=i, nrows=3)
            cols = [str(c).lower().strip() for c in temp.columns]
            if any('state' in c or 'beneficiar' in c for c in cols):
                df = pd.read_excel(filepath, sheet_name=sheet_name, header=i)
                return df
        except:
            continue
    return None

def count_state_rows(df):
    state_col = None
    for col in df.columns:
        if 'state' in str(col).lower() or 'beneficiar' in str(col).lower():
            state_col = col
            break
    if state_col is None:
        return 0, None
    count = df[state_col].apply(is_state_row).sum()
    return count, state_col

def get_all_candidate_sheets(filepath, xl):
    candidates = []
    sheet_names_lower = {s.lower().strip(): s for s in xl.sheet_names}

    for priority in SHEET_PRIORITY:
        if priority in sheet_names_lower:
            real_name = sheet_names_lower[priority]
            df = try_read_sheet(filepath, real_name)
            if df is None:
                continue
            count, _ = count_state_rows(df)
            if count > 0:
                candidates.append((real_name, df, count))

    for sheet in xl.sheet_names:
        sl = sheet.lower().strip()
        if sl in [p.lower() for p in SHEET_PRIORITY]:
            continue
        if any(skip in sl for skip in SKIP_SHEETS):
            continue
        df = try_read_sheet(filepath, sheet)
        if df is None:
            continue
        count, _ = count_state_rows(df)
        if count > 0:
            candidates.append((sheet, df, count))

    return candidates

def merge_split_sheets(candidates):
    if not candidates:
        return None, None

    candidates.sort(key=lambda x: x[2], reverse=True)
    top_sheet, top_df, top_count = candidates[0]

    if top_count >= 35:
        return top_sheet, top_df

    all_dfs = []
    seen_states = set()
    sheet_names_used = []

    for sheet, df, count in candidates:
        state_col = None
        for col in df.columns:
            if 'state' in str(col).lower() or 'beneficiar' in str(col).lower():
                state_col = col
                break
        if state_col is None:
            continue

        filtered = df[df[state_col].apply(is_state_row)].copy()
        filtered[state_col] = filtered[state_col].apply(normalize_state)
        new_rows = filtered[~filtered[state_col].isin(seen_states)]
        if len(new_rows) > 0:
            seen_states.update(new_rows[state_col].tolist())
            all_dfs.append(new_rows)
            sheet_names_used.append(sheet)

    if not all_dfs:
        return top_sheet, top_df

    merged = pd.concat(all_dfs, ignore_index=True)
    return '+'.join(sheet_names_used), merged

all_data = []
errors = []

files = [f for f in os.listdir(folder) if f.endswith('.xlsx') or f.endswith('.xls')]
print(f"Total Excel files found: {len(files)}\n")

for filename in sorted(files):
    month, year = extract_month_year(filename)
    if not month or not year:
        errors.append(f"DATE PARSE FAILED: {filename}")
        continue

    filepath = os.path.join(folder, filename)

    try:
        xl = pd.ExcelFile(filepath)
        candidates = get_all_candidate_sheets(filepath, xl)

        if not candidates:
            errors.append(f"NO USABLE SHEET: {filename}")
            continue

        sheet_name, df = merge_split_sheets(candidates)

        if df is None or df.empty:
            errors.append(f"EMPTY AFTER MERGE: {filename}")
            continue

        new_cols = {}
        for col in df.columns:
            col_clean = str(col).lower().strip()
            if col_clean in COLUMN_MAP:
                new_cols[col] = COLUMN_MAP[col_clean]
        df = df.rename(columns=new_cols)

        if 'State' not in df.columns:
            for col in df.columns:
                if df[col].dtype == object:
                    df = df.rename(columns={col: 'State'})
                    break

        if 'State' not in df.columns:
            errors.append(f"NO STATE COLUMN: {filename}")
            continue

        df = df[df['State'].apply(is_state_row)].copy()

        if df.empty:
            errors.append(f"NO STATE ROWS: {filename}")
            continue

        df['State'] = df['State'].apply(normalize_state)
        df = df.drop_duplicates(subset=['State'], keep='first')

        keep = ['State','Gross_Statutory','VAT','Total_Allocation',
                'Exchange_Gain','Deduction','EMTL']
        df = df[[c for c in keep if c in df.columns]]

        for col in ['Gross_Statutory','VAT','Total_Allocation',
                    'Exchange_Gain','Deduction','EMTL']:
            if col in df.columns:
                df[col] = df[col].apply(clean_value)

        df['Month'] = month
        df['Year'] = year

        all_data.append(df)
        print(f"OK [{sheet_name}]: {filename} — {len(df)} rows")

    except Exception as e:
        errors.append(f"ERROR {filename}: {str(e)}")

final = pd.concat(all_data, ignore_index=True)

for col in ['Gross_Statutory','VAT','Total_Allocation',
            'Exchange_Gain','Deduction','EMTL']:
    if col not in final.columns:
        final[col] = None

final = final[['State','Month','Year','Gross_Statutory','VAT','Total_Allocation',
               'Exchange_Gain','Deduction','EMTL']]

final.to_csv(output, index=False)

print(f"\n✅ DONE — {len(final)} total rows saved directly to MySQL Uploads folder")
print(f"Files processed successfully: {len(all_data)} of {len(files)}")

if errors:
    print(f"\n⚠️  PROBLEMS ({len(errors)} files):")
    for e in errors:
        print("  ", e)
else:
    print("\n✅ Zero errors — all files processed cleanly")