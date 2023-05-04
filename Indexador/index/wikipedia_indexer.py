try:
    from index.indexer import *
    from index.structure import *
except:
    from indexer import *
    from structure import *

if __name__ == "__main__":
    obj_index = FileIndex(idx_dir="./data/occurrences/")
    html_indexer = HTMLIndexer(obj_index)
    html_indexer.cleaner = Cleaner(stop_words_file="stopwords2.txt",
                        language="portuguese",
                        perform_stop_words_removal=True,
                        perform_accents_removal=True,
                        perform_stemming=False)
    
    html_indexer.index_text_dir("./data/wiki-pages")
    html_indexer.index.write("wiki.idx")