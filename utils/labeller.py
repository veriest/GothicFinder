import os
import sys
import pandas as pd

def main(input_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                df = pd.read_json(filepath)
                if 'new_label' in df.columns:
                    df['label'] = df['new_label']
                    df.to_json(filename, orient='records', lines=True)
                    new_df = df[['label','new_label']]
                    print(new_df.head())
                else:
                    pass


if __name__ == '__main__':
    input_dir = sys.argv[1]
    main(input_dir)