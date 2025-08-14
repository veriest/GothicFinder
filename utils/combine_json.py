import sys
import pandas as pd
import os

def main(input_dir):
    df = pd.DataFrame()
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                df2 = pd.read_json(filepath)
            df = pd.concat([df, df2], ignore_index=True)

    print(df.columns)

    df = df.drop(columns=['review_id'])
    if df['book_num'].apply(lambda x: isinstance(x, list)).any():
        df['book_num'] = df['book_num'].apply(lambda x: x[0] if isinstance(x, list) else x)

    combined_df = (
    df.groupby('title')
      .agg({
          'review_text': ' '.join,  # join all review texts into one string
          'book_num': 'first',
          'title': 'first',         # keep first title per book
          'author': 'first',        # keep first author per book
          'genres': 'first',        # keep first genres entry
          'label': 'first',         # keep first label
          'new_label': 'first'      # keep first new_label
      })
    )   

    combined_df.to_json('combined_2024.json', orient='records', indent=4)

if __name__ == '__main__':
    input_dir = sys.argv[1]
    main(input_dir)