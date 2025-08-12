import os
import sys
import pandas as pd
import json
import re

def main(in_directory,output_name):
    json_files = [f for f in os.listdir(in_directory) if f.endswith('.json')]


    data = []
    for file_name in json_files:
        file_path = os.path.join(in_directory, file_name)

        with open(file_path) as f:
            book = json.load(f)['book']
            book_num = re.findall(r'\d+', file_path)[1]
        for review in book['reviews']:
            row = [
                review['review_id'],
                review['review_text'],
                book_num,
                book['title'],
                book['author'],
                book['genres']
            ]
            data.append(row)

    df = pd.DataFrame(data, columns=['review_id','review_text','book_num','title','author','genres'])
    df['label'] = 0

    df.to_json(f'{output_name}.json', orient='records', indent=4)

if __name__ == '__main__':
    in_directory = sys.argv[1]
    output_name = sys.argv[2]
    main(in_directory,output_name)