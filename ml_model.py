import pandas
import glob
# import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfTransformer

# Open training data from news.txt file
with open('data/news.txt', 'r') as f:
    text = f.read()
    news = text.split("\n\n")
    count = {'sport': 0, 'world': 0, "us": 0, "business": 0, "health": 0, "entertainment": 0, "sci_tech": 0}
    for news_item in news:
        try:
            lines = news_item.split("\n")
            # print(len(lines))
            with open('data/' + lines[6] + '/' + str(count[lines[6]]) + '.txt', 'w+') as file_to_write:
                count[lines[6]] = count[lines[6]] + 1
                file_to_write.write(news_item)
        except Exception as e:
            pass

category_list = ["sport", "world", "us", "business", "health", "entertainment", "sci_tech"]
directory_list = ["data/sport/*.txt", "data/world/*.txt", "data/us/*.txt", "data/business/*.txt", "data/health/*.txt", "data/entertainment/*.txt", "data/sci_tech/*.txt", ]

text_files = list(map(lambda x: glob.glob(x), directory_list))
text_files = [item for sublist in text_files for item in sublist]

training_data = []

for t in text_files:
    f = open(t, 'r')
    f = f.read()
    t = f.split('\n')
    training_data.append({'data': t[0] + ' ' + t[1], 'flag': category_list.index(t[6])})

training_data = pandas.DataFrame(training_data, columns=['data', 'flag'])
training_data.to_csv("data/train_data.csv", sep=',', encoding='utf-8')

# GET VECTOR COUNT
count_vect = CountVectorizer()
X_train_counts = count_vect.fit_transform(training_data.data)

# TRANSFORM WORD VECTOR TO TF IDF
tfidf_transformer = TfidfTransformer()
X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)

# clf = MultinomialNB().fit(X_train_tfidf, training_data.flag)
X_train, X_test, y_train, y_test = train_test_split(X_train_tfidf, training_data.flag, test_size=0.25, random_state=42)
clf = MultinomialNB().fit(X_train, y_train)


# # SAVE WORD VECTOR
# pickle.dump(count_vect.vocabulary_, open("count_vector.pkl", "wb"))
#
# # SAVE TF-IDF
# pickle.dump(tfidf_transformer, open("tfidf.pkl", "wb"))
#
# # SAVE MODEL
# pickle.dump(clf, open("nb_model.pkl", "wb"))
#
# # LOAD MODEL
# loaded_vec = CountVectorizer(vocabulary=pickle.load(open("count_vector.pkl", "rb")))
# loaded_tfidf = pickle.load(open("tfidf.pkl", "rb"))
# loaded_model = pickle.load(open("nb_model.pkl", "rb"))


def predict(news_text):
    docs_new = [news_text]
    X_new_counts = count_vect.transform(docs_new)
    X_new_tfidf = tfidf_transformer.transform(X_new_counts)
    predicted = clf.predict(X_new_tfidf)
    result = category_list[predicted[0]]
    if result == 'us':
        result = 'india'
    return result
