###  Compare 2 .csv files which have the same "key" column (like network_id), identify rows with differences in other columns and print the differences for each row.
###  Before running: set the paths to the two files and the key column to identify unique rows. This might be a network_id or a user_id but must be in the labeled .csv files.
###############################################
file1_path = "/Users/mypath1.csv"
file2_path = "/Users/mypath2.csv"
key_column = "dim_network_key"
###############################################
### if two column index (like dim_network_key and dim_date_key), use this:
two_column_index = True
key_column1 = "dim_network_key"  # Replace with the actual column name
key_column2 = "dim_month_key"  # Replace with the actual column name
###############################################


import pandas as pd


def compare_csv(file1, file2, key_column):
    # Read CSV files into pandas DataFrames
    df1 = pd.read_csv(file1, index_col=key_column)
    df2 = pd.read_csv(file2, index_col=key_column)

    # Find common key values
    common_keys = df1.index.intersection(df2.index)

    # Identify columns with differences for each common key
    diff_columns = {}

    for key_value in common_keys:
        # Compare columns for differences
        row_diff_columns = []

        for col in df1.columns:
            if df1.at[key_value, col] != df2.at[key_value, col]:
                row_diff_columns.append(f"{col}: {df1.at[key_value, col]} vs {df2.at[key_value, col]}")

        if row_diff_columns:
            diff_columns[key_value] = row_diff_columns

    # Find rows missing in each file
    missing_file1 = [key_value for key_value in df2.index if key_value not in common_keys]
    missing_file2 = [key_value for key_value in df1.index if key_value not in common_keys]

    return diff_columns, missing_file1, missing_file2


def compare_2col_csv(file1, file2, key_column1, key_column2):
    # Read CSV files into pandas DataFrames with two columns as index
    df1 = pd.read_csv(file1, index_col=[key_column1, key_column2])
    df2 = pd.read_csv(file2, index_col=[key_column1, key_column2])

    # Find common key values
    common_keys = df1.index.intersection(df2.index)

    # Identify columns with differences for each common key
    diff_columns = {}

    for key_value in common_keys:
        # Compare columns for differences
        row_diff_columns = []

        for col in df1.columns:
            if df1.at[key_value, col] != df2.at[key_value, col]:
                row_diff_columns.append(f"{col}: {df1.at[key_value, col]} vs {df2.at[key_value, col]}")

        if row_diff_columns:
            diff_columns[key_value] = row_diff_columns

    # Find rows missing in each file
    missing_file1 = [key_value for key_value in df2.index if key_value not in common_keys]
    missing_file2 = [key_value for key_value in df1.index if key_value not in common_keys]

    return diff_columns, missing_file1, missing_file2

def output_to_file(diff_columns, missing_file1, missing_file2):
    with open('output.txt', 'w') as f:
        print(f"Columns with differences for each common {key_column}:", file=f)
        for key_value, columns in diff_columns.items():
            print(f"{key_column.capitalize()} {key_value}: {columns}", file=f)

        print(f"\nRows missing in {file1_path}:", file=f)
        print(missing_file1, file=f)

        print(f"\nRows missing in {file2_path}:", file=f)
        print(missing_file2, file=f)



if __name__ == "__main__":
    if two_column_index:
        diff_columns, missing_file1, missing_file2 = compare_2col_csv(file1_path, file2_path, key_column1, key_column2)
    else:
        diff_columns, missing_file1, missing_file2 = compare_csv(file1_path, file2_path, key_column)

    print(f"Columns with differences for each common {key_column}:")
    for key_value, columns in diff_columns.items():
        print(f"{key_column.capitalize()} {key_value}: {columns}")

    print(f"\nRows missing in {file1_path}:")
    print(missing_file1)

    print(f"\nRows missing in {file2_path}:")
    print(missing_file2)


    output_to_file(diff_columns, missing_file1, missing_file2)
