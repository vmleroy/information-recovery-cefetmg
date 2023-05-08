from nltk.stem.snowball import SnowballStemmer
from bs4 import BeautifulSoup as bs
import string
from nltk.tokenize import word_tokenize
import os
from tqdm import tqdm


class Cleaner:
    def __init__(self, stop_words_file: str, language: str,
                 perform_stop_words_removal: bool, perform_accents_removal: bool,
                 perform_stemming: bool):
        self.set_stop_words = self.read_stop_words(stop_words_file)

        self.stemmer = SnowballStemmer(language)
        in_table = "áéíóúâêôçãẽõü"
        out_table = "aeiouaeocaeou"
        # altere a linha abaixo para remoção de acentos (Atividade 11)
        self.accents_translation_table = str.maketrans(in_table, out_table)
        self.set_punctuation = set(string.punctuation)

        # flags
        self.perform_stop_words_removal = perform_stop_words_removal
        self.perform_accents_removal = perform_accents_removal
        self.perform_stemming = perform_stemming

    def html_to_plain_text(self, html_doc: str) -> str:
        return bs(html_doc, 'html.parser').get_text()

    @staticmethod
    def read_stop_words(str_file) -> set:
        set_stop_words = set()
        with open(str_file, encoding='utf-8') as stop_words_file:
            for line in stop_words_file:
                arr_words = line.split(",")
                [set_stop_words.add(word.strip().replace("\n", "")) for word in arr_words]
        return set_stop_words

    def is_stop_word(self, term: str):
        return term in self.set_stop_words

    def word_stem(self, term: str):
        return self.stemmer.stem(term)

    def remove_accents(self, term: str) -> str:
        return term.translate(self.accents_translation_table)

    def preprocess_word(self, term: str) -> str or None:
        if self.perform_stop_words_removal and self.is_stop_word(term):
            return None
        if term in self.set_punctuation:
            return None
        if self.perform_stemming:
            term = self.word_stem(term)
        return term

    def preprocess_text(self, text: str) -> str or None:
        text = text.lower()
        if self.perform_accents_removal:
            text = self.remove_accents(text)
        return text


class HTMLIndexer:
    cleaner = Cleaner(stop_words_file="stopwords.txt",
                      language="portuguese",
                      perform_stop_words_removal=True,
                      perform_accents_removal=True,
                      perform_stemming=True)

    def __init__(self, index):
        self.index = index

    def text_word_count(self, plain_text: str):
        dic_word_count = {}

        tokens = word_tokenize(plain_text, language="portuguese")

        for word in tokens:
            word = self.cleaner.preprocess_word(word)
            if word is not None:
                if word in dic_word_count:
                    dic_word_count[word] += 1
                else:
                    dic_word_count[word] = 1

        # return dict(sorted(dic_word_count.items()))
        return dic_word_count

    def index_text(self, doc_id: int, text_html: str):
        plain_text = self.cleaner.html_to_plain_text(text_html)
        plain_text = self.cleaner.preprocess_text(plain_text)

        dic_word_count = self.text_word_count(plain_text)
        for word, count in dic_word_count.items():
            self.index.index(word, doc_id, count)
        self.index.finish_indexing()

    def index_text_dir(self, path: str, sub_dir: bool = True):
        # for str_sub_dir in tqdm(os.listdir(path),desc='Main loop', leave=True):
        for str_sub_dir in os.listdir(path):
            if sub_dir:
                path_sub_dir = f"{path}/{str_sub_dir}"
            else:
                path_sub_dir = path
            # for str_file in tqdm(os.listdir(path_sub_dir), leave=False):
            for str_file in os.listdir(path_sub_dir):
                path_file = f"{path_sub_dir}/{str_file}"
                with open(path_file, encoding='utf-8') as file:
                    self.index_text(int(str_file.split('.')[0]), file.read())
                file.close()
