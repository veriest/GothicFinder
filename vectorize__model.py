from sklearn.feature_extraction.text import TfidfVectorizer
import sys
import pandas as pd
import os
import json
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score

def main(input_dir):

    df = pd.DataFrame()

    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                df2 = pd.read_json(filepath, lines=True)
            df = pd.concat([df,df2], ignore_index=True)

    train_df, val_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)

    tf_vec = TfidfVectorizer(max_features=5000)

    X_train = tf_vec.fit_transform(train_df['review_text'])
    #print(tf_vec.vocabulary_)
    X_val = tf_vec.transform(val_df['review_text'])
    model = MultinomialNB()
    model.fit(X_train, train_df['label'])

    predictions = model.predict(X_val)

    accuracy = accuracy_score(val_df['label'], predictions)
    print(f'Validation Accuracy: {accuracy}')


if __name__ == '__main__':
    input_dir = sys.argv[1]
    main(input_dir)