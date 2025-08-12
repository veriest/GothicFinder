import os
import sys
import pandas as pd
import json
import re

def main(input_file):
    df = pd.read_json(input_file)
    #get starting length of current input dataframe
    print(f'length of inputs is {len(df)}')

    #group by book number
    books = df.groupby('book_num')
    #print(books.ngroups)
    
    labels = {}

    #iterate over grouped book numbers and label as either gothic ('1') or not gothic ('0')
    #code taken from: https://stackoverflow.com/questions/27405483/how-to-loop-over-grouped-pandas-dataframe
    for name, group in books:
        print(f"Enter 1 for Gothic 0 for not, currently categorizing book title {group['title']} (type 'exit' to quit): ")
        user_input = input()
        if user_input.lower() == 'exit':
            print("Exiting program.")
            break
        else:
            print(f"You entered: {user_input} for {group['title']}, book number {group['book_num']}")
            labels[name] = user_input
    
    #map new labels to the corresponding book numbers
    df['new_label'] = df['book_num'].map(labels)

    #save unfinished progress in new dataframe
    unfinished = df[df['new_label'].isna()]

    print(f'length of unfinished data is {len(unfinished)}')

    #drop the unlabelled books
    df = df.dropna(subset='new_label')

    gothics_found = df[df['new_label'].str.contains('1')]
    no_gothics = df[df['new_label'].str.contains('0')]
    
    print(f'length of gothics found is {len(gothics_found)}')
    print(f'length of no gothics is {len(no_gothics)}')

    #save uncategorized work for later
    unfinished.to_json('unfinished4.json', orient='records', indent=4)

    #save gothics found
    gothics_found.to_json('manually_categorized_gothics4.json', orient='records', indent=4)

    #save the not gothics found
    no_gothics.to_json('manually_categorized_fantasy.json', orient='records', indent=4)

if __name__ == '__main__':
    input_file = sys.argv[1]
    main(input_file)