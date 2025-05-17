# import pandas as pd

# # Load fact and dimension tables
# fact = pd.read_csv("output_data/fact_pit.csv")
# dim_subgroup = pd.read_excel("output_data/dim_sg.xlsx")

# # Filter out empty or invalid subgroup_key entries
# fact = fact[fact['subgroup_key'].notnull()]

# # Merge fact table with subgroup dimension to get demographic labels
# merged = pd.merge(fact, dim_subgroup, on='subgroup_key', how='left')

# merged['count'] = pd.to_numeric(merged['count'], errors='coerce')

# # Check for any missing joins
# if merged['subgroup'].isnull().any():
#     print("⚠️ Warning: Some subgroup_keys didn't match.")

# # Create Gender Aggregate
# agg_gender = (
#     merged[merged['demographic_dimension'] == 'Gender']
#     .groupby(['year', 'subgroup'], as_index=False)['count']
#     .sum()
#     .rename(columns={'subgroup': 'gender', 'count': 'total_count'})
# )

# age_filter = merged['subgroup'].str.contains('Under 18|Age 18 to 24|Over 24', case=False, na=False)

# # Create Age Aggregate
# agg_age = (
#     merged[(merged['demographic_dimension'] == 'Age') & age_filter]
#     .groupby(['year', 'subgroup'], as_index=False)['count']
#     .sum()
#     .rename(columns={'subgroup': 'age_group', 'count': 'total_count'})
# )

# # Create Race/Ethnicity Aggregate
# agg_race = (
#     merged[(merged['demographic_dimension'] == 'Race/Ethnicity') & age_filter]

#     .groupby(['year', 'subgroup'], as_index=False)['count']
#     .sum()
#     .rename(columns={'subgroup': 'race_ethnicity', 'count': 'total_count'})
# )

# # Save each to CSV (optional)
# agg_gender.to_csv("output_data/agg_gender.csv", index=False)
# agg_age.to_csv("output_data/agg_age.csv", index=False)
# agg_race.to_csv("output_data/agg_race.csv", index=False)

import pandas as pd

# Load fact and dimension tables
fact = pd.read_csv("output_data/fact_pit.csv")
dim_subgroup = pd.read_excel("output_data/dim_sg.xlsx")

# Filter out empty or invalid subgroup_key entries
fact = fact[fact['subgroup_key'].notnull()]

# Merge fact table with subgroup dimension to get demographic labels
merged = pd.merge(fact, dim_subgroup, on='subgroup_key', how='left')
merged['count'] = pd.to_numeric(merged['count'], errors='coerce')

# Check for any missing joins
if merged['subgroup'].isnull().any():
    print("⚠️ Warning: Some subgroup_keys didn't match.")

# ----------------------------
# Define Filters
# ----------------------------

# Age-related subgroups
age_filter = merged['subgroup'].str.contains(r'Under 18|Age 18 to 24|Over 24', case=False, na=False)

# Race/Ethnicity-related subgroups (adjust as per your data's actual values)
race_filter = merged['subgroup'].str.contains(
    r'American Indian|Alaska Native|Asian|Black|African American|Hispanic|Latino|Pacific Islander|White|Multiracial|Ethnicity|Race',
    case=False, na=False
)

# ----------------------------
# Aggregations
# ----------------------------

# Gender Aggregate
agg_gender = (
    merged[merged['demographic_dimension'] == 'Gender']
    .groupby(['year', 'subgroup'], as_index=False)['count']
    .sum()
    .rename(columns={'subgroup': 'gender', 'count': 'total_count'})
)

# Age Aggregate
agg_age = (
    merged[(merged['demographic_dimension'] == 'Age') & age_filter]
    .groupby(['year', 'subgroup'], as_index=False)['count']
    .sum()
    .rename(columns={'subgroup': 'age_group', 'count': 'total_count'})
)

# Race/Ethnicity Aggregate
agg_race = (
    merged[(merged['demographic_dimension'] == 'Race/Ethnicity') & race_filter]
    .groupby(['year', 'subgroup'], as_index=False)['count']
    .sum()
    .rename(columns={'subgroup': 'race_ethnicity', 'count': 'total_count'})
)

# ----------------------------
# Unmatched Subgroups
# ----------------------------

matched = pd.concat([
    merged[merged['demographic_dimension'] == 'Gender'],
    merged[(merged['demographic_dimension'] == 'Age') & age_filter],
    merged[(merged['demographic_dimension'] == 'Race/Ethnicity') & race_filter]
])

unmatched = merged.loc[~merged.index.isin(matched.index)]
unmatched = unmatched[['year', 'subgroup', 'demographic_dimension', 'count']]

# ----------------------------
# Save to CSV
# ----------------------------

agg_gender.to_csv("output_data/agg_gender.csv", index=False)
agg_age.to_csv("output_data/agg_age.csv", index=False)
agg_race.to_csv("output_data/agg_race.csv", index=False)
unmatched.to_csv("output_data/unmatched_subgroups.csv", index=False)
