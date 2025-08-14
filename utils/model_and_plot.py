from sklearn.feature_extraction.text import TfidfVectorizer
import sys
import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import seaborn as sns

def main(input_dir):
    df = pd.DataFrame()
    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(input_dir, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                df2 = pd.read_json(filepath, lines=True)
            df = pd.concat([df, df2], ignore_index=True)

    train_df, val_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)
    tf_vec = TfidfVectorizer(max_features=25000)
    X_train = tf_vec.fit_transform(train_df['review_text'])
    X_val = tf_vec.transform(val_df['review_text'])

    model = MultinomialNB()
    model.fit(X_train, train_df['label'])
    predictions = model.predict(X_val)
    accuracy = accuracy_score(val_df['label'], predictions)
    print(f'Validation Accuracy: {accuracy}')

    dir2 = input_dir + '/2025/'

    df3 = pd.DataFrame()

    for filename in os.listdir(dir2):
        if filename.endswith('.json'):
            filepath = os.path.join(dir2, filename)
            with open(filepath, 'r', encoding='utf-8') as file:
                df4 = pd.read_json(filepath, lines=True)
            df3 = pd.concat([df3, df4], ignore_index=True)

    X_new = tf_vec.transform(df3['review_text'])
    predicted_labels = model.predict(X_new)
    df3['predicted_label'] = predicted_labels

    book_predictions = (
        df3.groupby('book_num')['predicted_label']
        .agg(lambda x: int(x.mean() > 0.2))  
        .reset_index()
    )

    book_metadata = df3[['book_num','label','title']].drop_duplicates(subset='book_num')
    book_results = book_predictions.merge(book_metadata, on='book_num', how='left')

    book_results.to_json('2025_labeled_data_per_book.json', orient='records', lines=True)

    if 'label' in df3.columns:
        true_book_labels = (
            df3.groupby('book_num')['label']
            .agg(lambda x: int(x.mean() > 0.5))
            .reset_index()
        )

        true_vs_pred = true_book_labels.merge(book_predictions, on='book_num')
        accuracy_new = accuracy_score(true_vs_pred['label'], true_vs_pred['predicted_label'])
        print(f'Accuracy on tokenized_fantasy_2025 (per book): {accuracy_new:.4f}')

        mismatches = true_vs_pred[true_vs_pred['label'] != true_vs_pred['predicted_label']]
        print(f'Number of mismatched books: {len(mismatches)}')
    else:
        print("No truth labels in tokenized_fantasy_2025.json")

    print("Train label distribution:\n", train_df['label'].value_counts(normalize=True))
    print("Unseen data label distribution:\n", df3['label'].value_counts(normalize=True))
    print("Book-level predicted label distribution:\n", book_predictions['predicted_label'].value_counts(normalize=True))


if __name__ == '__main__':
    input_dir = sys.argv[1]
    main(input_dir)