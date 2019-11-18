import string
from collections import Counter

import nltk

nltk.download('stopwords')
nltk.download('punkt')
useless_words = nltk.corpus.stopwords.words(
    "english") + list(string.punctuation)


def build_bag_of_words_features_filtered(words):
    return {word: 1 for word in words if word not in useless_words}


def filtered_tokenize(words):
    tokenized = nltk.word_tokenize(words)
    word_list = list(set([word.upper()
                          for word in tokenized if word.lower() not in useless_words and len(word) > 3]))
    return word_list


def get_most_common(word_list):
    word_counter = Counter(word_list)
    most_common = word_counter.most_common()
    return [{'text': x[0], 'value': x[1]} for x in most_common][:100]


def tokenized_lyrics(lyrics):
    lyrics = lyrics.replace('/n', ' ')
    lyrics = lyrics.replace('Verse', '')
    lyrics = lyrics.replace('Chorus', '')
    lyrics = lyrics.replace('Outro', '')
    lyrics = lyrics.replace('Intro', '')
    return filtered_tokenize(lyrics)
