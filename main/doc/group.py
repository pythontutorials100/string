import pandas as pd

# Replace 'input.xlsx' with the path to your input Excel file
input_file = 'input.xlsx'

# Read the Excel file into a DataFrame
df = pd.read_excel(input_file)

# Factorize the 'rdfs_subClassOf' column to get unique codes based on first occurrence
codes, uniques = pd.factorize(df['rdfs_subClassOf'], sort=False)

# Assign the codes to a new column 'GroupNumber' for sorting
df['GroupNumber'] = codes

# Sort the DataFrame by 'GroupNumber' to group terms based on first occurrence
df_sorted = df.sort_values('GroupNumber')

# Optionally, drop the 'GroupNumber' column if you don't need it in the output
df_sorted = df_sorted.drop(columns=['GroupNumber'])

# Reset the index if desired
df_sorted = df_sorted.reset_index(drop=True)

# Save the sorted DataFrame to an Excel file
output_excel_file = 'output.xlsx'
df_sorted.to_excel(output_excel_file, index=False)

# Or save to a CSV file
output_csv_file = 'output.csv'
df_sorted.to_csv(output_csv_file, index=False)
