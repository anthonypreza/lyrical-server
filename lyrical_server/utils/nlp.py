import string
from collections import Counter
from typing import Any, Dict, List, Tuple

import nltk  # type: ignore

nltk.download('stopwords')
nltk.download('punkt')
useless_words: List[str] = nltk.corpus.stopwords.words("english") + list(
    string.punctuation)


def build_bag_of_words_features_filtered(words: List[str]) -> Dict[str, int]:
    bag: Dict[str,
              int] = {word: 1
                      for word in words if word not in useless_words}
    return bag


def filtered_tokenize(words: str) -> List[str]:
    tokenized: List[str] = nltk.word_tokenize(words)
    word_list: List[str] = list(
        set([
            word.upper() for word in tokenized
            if word.lower() not in useless_words and len(word) > 3
        ]))
    return word_list


def get_most_common(word_list: List[str]) -> List[Dict[str, Any]]:
    word_counter: Counter = Counter(word_list)
    most_common: List[Tuple[str, int]] = word_counter.most_common(100)
    res: List[Dict[str, Any]] = [{
        'text': x[0],
        'value': x[1]
    } for x in most_common]
    return res


def tokenized_lyrics(lyrics: str) -> List[str]:
    try:
        lyrics = lyrics.replace('/n', ' ').replace('Verse', '').replace(
            'Chorus', '').replace('Outro', '').replace('Intro', '')
        tokenized: List[str] = filtered_tokenize(lyrics)
        return tokenized
    except AttributeError as e:
        print(e)
        return list()
