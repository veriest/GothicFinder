import os
import sys
import pandas as pd

def main(input_dir):
    df = pd.DataFrame()
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                df2 = pd.read_json(filepath)
            df = pd.concat([df, df2], ignore_index=True)

    num_groups = df.groupby('book_num').ngroups
    print(f"Number of unique book_num groups: {num_groups}")

    filepath2 = os.path.join(input_dir, input_file2)
    with open(filepath2, 'r', encoding='utf-8') as file:
                df3 = pd.read_json(filepath2)

    num_groups2 = df3.groupby('book_num').ngroups
    print(f"Number of unique book_num groups2: {num_groups2}")    


if __name__ == '__main__':
    input_dir = sys.argv[1]
    input_file2 = sys.argv[2]
    main(input_dir)