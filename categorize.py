import sys
import pandas as pd


def main(input_file,output_file):
    
    df = pd.read_json(input_file)

    gothics_found = df[df['genres'].str.contains('Gothic')]
    gothics_found['label'] = 1

    gothics_found.to_json(f'{output_file}.json', orient='records', indent=4)

    no_gothics = df[~df['genres'].str.contains('Gothic')]

    no_gothics['new_book_num'] = no_gothics.groupby('book_num').ngroup() + 1

    no_gothics['book_num'] = no_gothics['new_book_num']

    no_gothics = no_gothics.drop(columns=['new_book_num'])

    no_gothics = no_gothics.sort_values(by='book_num',ascending=True)

    no_gothics.to_json('fantasy_2024_uncategorized.json', orient='records', indent=4)


if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file,output_file)