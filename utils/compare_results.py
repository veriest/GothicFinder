import sys
import pandas as pd
import os

def main(input_dir):
    df = pd.DataFrame()
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                df2 = pd.read_json(filepath, lines=True)
            df = pd.concat([df, df2], ignore_index=True)

    print(df.column)
    
if __name__ == '__main__':
    input_dir = sys.argv[1]
    main(input_dir)