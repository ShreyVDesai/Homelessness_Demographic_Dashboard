import os
import pandas as pd
import re

# Config
INPUT_FILE = '2007-2024-PIT-Counts-by-CoC.xlsb'
OUTPUT_DIR = 'output_data'
MERGERS_SHEET = 'CoC Mergers'

try:
    os.mkdir(OUTPUT_DIR)
except:
    print('Output directory already exists')

# Concat all years into 1 df
all_years = []
xls = pd.ExcelFile(INPUT_FILE, engine="pyxlsb")
year_sheets = [s for s in xls.sheet_names if s.isdigit()]
for sheet in sorted(year_sheets):
    df = pd.read_excel(INPUT_FILE, engine = 'pyxlsb', sheet_name=sheet)
    df['year'] = int(sheet)
    all_years.append(df)
wide = pd.concat(all_years, ignore_index=True)

# Melt the df
id_vars = ['year','CoC Number', 'CoC Name', 'Count Types']
value_vars = [c for c in wide.columns if c not in id_vars]

fact = wide.melt(
    id_vars = id_vars,
    value_vars = value_vars,
    var_name = 'subgroup',
    value_name = 'count'
).rename(columns = {
    "CoC Number":"coc_number",
    "CoC Name":'coc_name',
    'Count Types':"count_type"
})


fact = fact[fact['count'].notna() & (fact['count'] != 0)]

# We are not changing CoC codes based on mergers to accurately reflect the values recorded for a given CoC in a given year.

dim_coc = fact[['coc_number','coc_name']].drop_duplicates().reset_index(drop=True)
dim_ct = fact[['count_type']].drop_duplicates().dropna().reset_index(drop=True)

dim_ct['shelter_category'] = dim_ct['count_type'].apply(lambda x: ' '.join(x.split()[:-1]))
dim_ct['program_type'] = dim_ct['count_type'].str.extract(r"(ES|TH|SH|Total)")

dim_sg = fact[['subgroup']].drop_duplicates().reset_index(drop=True)

# def tag_dimension(s):
#     s_low = s.lower()
#     if any(k in s_low for k in ['under','over','age']):
#         return "Age"
#     if any(k in s_low for k in ['woman','man','transgender','non binary','gender questioning','culturally specific identity','different identity','more than one gender','']):
#         return "Gender"
#     return "Race/Ethnicity"
def tag_dimension(s):
    s_low = s.lower()
    
    if re.search(r'\bunder\b|\bover\b|\bage\b', s_low):
        return "Age"
    
    if re.search(r'\bwoman\b|\bman\b|\btransgender\b|\bnon binary\b|\bgender questioning\b|\bculturally specific identity\b|\bdifferent identity\b|\bmore than one gender\b', s_low):
        return "Gender"
    
    return "Race/Ethnicity"

dim_sg['demographic_dimension'] = dim_sg['subgroup'].apply(tag_dimension)

# Join keys back into fact
dim_coc['coc_key'] = dim_coc.index + 1
dim_ct['count_type_key'] = dim_ct.index + 1
dim_sg['subgroup_key'] = dim_sg.index + 1

# Merge keys
fact = fact.merge(dim_coc, on=['coc_number','coc_name'], how = 'left')
fact = fact.merge(dim_ct, on=['count_type'], how = 'left')
fact = fact.merge(dim_sg, on = ['subgroup'], how = 'left')

# Keep only the keys + measures in the fact
fact_final = fact[["year", "coc_key", "count_type_key", "subgroup_key", "count"]]


# Export CSVs
fact_final.to_csv(f'{OUTPUT_DIR}/fact_pit.csv', index=False)
dim_coc.to_excel(f'{OUTPUT_DIR}/dim_coc.xlsx', index=False)
dim_ct.to_excel(f'{OUTPUT_DIR}/dim_ct.xlsx', index = False)
dim_sg.to_excel(f'{OUTPUT_DIR}/dim_sg.xlsx', index=False)

print("ETL complete — CSVs written to", OUTPUT_DIR)

