import sys
import pandas as pd
from nltk.corpus import stopwords
from nltk import RegexpTokenizer
import os
import json

def tokenize_reviews(review_col):

    tokenizer = RegexpTokenizer(r"\w+")
    stop_words = stopwords.words("English")

    tokens = review_col.apply(lambda x: tokenizer.tokenize(x.lower()))
    tokens = tokens.apply(lambda x: [word for word in x if word not in stop_words])

    return tokens

def main(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            filepath = os.path.join(input_folder, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            df = pd.DataFrame(data)

            df['tokenized'] = tokenize_reviews(df['review_text'])

            output_filepath = os.path.join(output_folder, f'tokenized_{filename}')
            df.to_json(output_filepath, orient='records', lines=True)

if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    main(input_file, output_file)