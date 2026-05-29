from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

CORPUS = [
    ("Buy cheap viagra now!!!", "spam"),
    ("Hello, how are you?", "ham"),
    ("Win a free iPhone click here", "spam"),
    ("Meeting at 3pm tomorrow", "ham"),
    ("Congratulations you won a prize", "spam"),
    ("Can you pick up milk on the way home", "ham"),
]

texts, labels = zip(*CORPUS)

pipeline = Pipeline([
    ("vect", CountVectorizer()),
    ("tfidf", TfidfTransformer()),
    ("clf", MultinomialNB()),
])

pipeline.fit(texts, labels)
preds = pipeline.predict(texts)

print("Accuracy:", accuracy_score(labels, preds))
print(classification_report(labels, preds))
