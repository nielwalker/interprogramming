import nltk
from nltk.tokenize import sent_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from heapq import nlargest

nltk.download('stopwords')
nltk.download('punkt')


text = """
In the heart of the city, a new park has opened, 
providing a green oasis for residents. The park features walking trails, 
picnic areas, and a playground for children. Local officials are excited about the 
positive impact this park will have on the community, promoting outdoor activities 
and social interaction among neighbors. The grand opening ceremony is scheduled for 
next Saturday, and everyone is invited to join in the festivities.
"""

sentences = sent_tokenize(text)
stemmer = PorterStemmer()
stop_words = set(stopwords.words('english'))
words = []
for sentence in sentences:
    for word in nltk.word_tokenize(sentence):
        if word not in stop_words and word.isalpha():
            words.append(stemmer.stem(word))

freq_dist = nltk.FreqDist(words)
top_words =  [word [0] for word in freq_dist.most_common(10)]

summary = []
for sentence in sentences:
    sentence_words = nltk.word_tokenize(sentence.lower())
    sentence_score = 0
    for word in sentence_words:
        if stemmer.stem(word) in top_words:
            sentence_score += 1
    summary.append((sentence, sentence_score))

for sentence in nlargest(3, summary, key=lambda x: x[1]):
    print(sentence[0])