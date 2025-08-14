# GothicFinder

scrape.py code heavily adapted from https://www.reddit.com/r/learnpython/comments/1fknl27/so_close_to_getting_my_code_to_work_goodreads/ by u/BlueLagoon226 and https://github.com/maria-antoniak/goodreads-scraper/blob/master/get_reviews.py#L279 by by Maria Antoniak and Melanie Walsh.

A Goodreads webscraping and data analysis project to find 'hidden' fantasy/science-fiction Gothic novels

Required libraries: pandas, urllib.parse, collections, Beautiful Soup, selenium, NLTK, sklearn (TfidfVectorizer,train_test_split,MultinomialNB,accuracy_score)

scrape.y takes in the url to a list of goodreads books, and returns JSON formatted reviews of up to 300 reviews per book. It will not work on GoodReads shelves, as the 'Book' schema used in lists does not exist in shelves.

format.py takes an input directory of raw JSON book data, and returns an output file of all of the books in one JSON file with the books numbered by index of order in which they were scraped.

categorize.py takes in an input file, labels the books as either category 0 (not gothic), or 1 ('gothic' as found in 'genre'), and saves it to an output file. The files are then split to show only the book_num and title to produce convenient lists of what has been categorized as gothic, and non-gothic, and another file is generated of only the non-gothic books (for manual categorization).

manual_categorizer.py takes an input file, and asks on the command line if a book is to be manually categorized as gothic or not. It can save lists of categorized gothics, categorized not gothics, and uncategorized data to split the task of manual categorization.

tokenize_reviews.py takes an input directory, and an output directory, removes stop words and punctuation and formats text into lower case, and then uses the nltk library to tokenize the text which it saves to an output directory.

vectorize__model.py takes an input directory of tokenized files (as well as a hard-coded subdirectory of 'unseen' data to run the model on), vectorizes the text with tf-idf vectorization, and then applies a multinomial Naive Bayes model to predict gothic or non gothic labels. It prints some information on the frequency of labels and accuracy scores.

the utils folder contains some helper functions and the code which I used to make my plots.

book_1.json is an example of one book's worth of scraped reviews, before any formatting.