# processor.py
import os
import pandas as pd
from collections import defaultdict

def process_files(source_folder, dest_folder, name_folder):
    os.makedirs(dest_folder, exist_ok=True)
    os.makedirs(name_folder, exist_ok=True)

    files = [f for f in os.listdir(source_folder) if f.endswith('.xlsx')]
    grouped_files = defaultdict(list)

    for file in files:
        file_path = os.path.join(source_folder, file)
        df = pd.read_excel(file_path, engine='openpyxl')
        for idx, row in df.iterrows():
            if row.iloc[13] == "入账":
                group_key = (row.iloc[17], row.iloc[7])
                grouped_files[group_key].append(file_path)
                break

    for (group_key_18, group_key_8), file_list in grouped_files.items():
        combined_df = pd.DataFrame()
        for file_path in file_list:
            df = pd.read_excel(file_path, engine='openpyxl')
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        combined_df = combined_df.sort_values(by=combined_df.columns[11])

        new_filename = f"{group_key_18}.xlsx"
        for i in range(len(combined_df) - 1):
            if abs(combined_df.iloc[i, 5] - combined_df.iloc[i+1, 5]) in [500, 600, 1] and combined_df.iloc[i, 11] != combined_df.iloc[i+1, 11]:
                base, ext = os.path.splitext(new_filename)
                new_filename = base + "_my" + ext
                break

        combined_df['新列'] = combined_df.apply(
            lambda x: "疑似嫖客" if (x.iloc[5] in [499, 500, 501, 599, 600, 601, 1000, 1200, 1500, 1800, 2000] and x.iloc[13] == "入账") else "",
            axis=1
        )

        dest_path = os.path.join(dest_folder, new_filename)
        combined_df.to_excel(dest_path, index=False, engine='openpyxl')

    name_df = pd.DataFrame()
    for file in os.listdir(dest_folder):
        if file.endswith('.xlsx'):
            try:
                df = pd.read_excel(os.path.join(dest_folder, file), engine='openpyxl')
                if df.shape[1] >= 18:
                    name_data = df.iloc[:, [7, 17]]
                    name_df = pd.concat([name_df, name_data], ignore_index=True)
            except Exception as e:
                print(f"Error reading {file}: {e}")

    name_df = name_df.drop_duplicates()
    name_df.to_excel(os.path.join(name_folder, '姓名库.xlsx'), index=False, engine='openpyxl')

def build_transaction_circle(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    files = [f for f in os.listdir(input_folder) if f.endswith('.xlsx')]

    for file in files:
        df = pd.read_excel(os.path.join(input_folder, file))
        merged_column = pd.concat([df.iloc[:, 2], df.iloc[:, 7]], ignore_index=True)
        merged_column = merged_column.drop_duplicates()
        merged_df = pd.DataFrame(merged_column, columns=['Merged'])
        output_file = os.path.join(output_folder, file)
        merged_df.to_excel(output_file, index=False)

def merge_and_count_duplicates(input_folder, original_folder):
    files = [f for f in os.listdir(input_folder) if f.endswith('.xlsx')]
    merged_data = []

    for file in files:
        df = pd.read_excel(os.path.join(input_folder, file))
        merged_data.append(df.iloc[:, 0])

    merged_series = pd.concat(merged_data, ignore_index=True)
    merged_df = pd.DataFrame({'合并': merged_series})
    merged_df.to_excel(os.path.join(input_folder, 'merged_data.xlsx'), index=False)

    duplicates_df = merged_df[merged_df.duplicated()]
    duplicates_count = duplicates_df['合并'].value_counts().reset_index()
    duplicates_count.columns = ['合并', '重复次数']
    duplicates_count = duplicates_count.drop_duplicates()
    duplicates_count.to_excel(os.path.join(input_folder, 'duplicates_count.xlsx'), index=False)

    unique_df = duplicates_count.drop_duplicates()
    unique_df.to_excel(os.path.join(original_folder, 'unique_duplicates_count.xlsx'), index=False)

def match_r_column(input_folder):
    unique_file = os.path.join(input_folder, 'unique_duplicates_count.xlsx')
    unique_df = pd.read_excel(unique_file)
    unique_df['R列内容'] = None
    r_column_index = 17

    files = [f for f in os.listdir(input_folder) if f.endswith('.xlsx') and f != 'unique_duplicates_count.xlsx']

    for file in files:
        file_path = os.path.join(input_folder, file)
        df = pd.read_excel(file_path)
        for idx, row in unique_df.iterrows():
            if df.shape[1] > r_column_index:
                matching_rows = df[df.iloc[:, 7] == row['合并']]
                if not matching_rows.empty:
                    r_value = matching_rows.iloc[0, r_column_index]
                    unique_df.at[idx, 'R列内容'] = r_value

    output_file = os.path.join(input_folder, 'unique_duplicates_count_updated.xlsx')
    unique_df.to_excel(output_file, index=False)