import pandas as pd
#https://drive.google.com/file/d/15eFh_MUibA3PABir0p7p4Elz3xC40biJ/view?usp=sharing # for file.csv
df = pd.read_csv('file.csv')
df_filtered = df[(df['lat'] % 1 == 0) & (df['lon'] % 1 == 0)]
print(df_filtered)
# Save the filtered DataFrame to a CSV file
df_filtered.to_csv('data/filtered_big_data.csv', index=False)
