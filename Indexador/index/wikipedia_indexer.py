try:
    from index.indexer import *
    from index.structure import *
except:
    from indexer import *
    from structure import *

def make_wkipedia_index():
    # obj_index = FileIndex(idx_dir="./data/occurrences/")
    obj_index = HashIndex()
    html_indexer = HTMLIndexer(obj_index)
    html_indexer.cleaner = Cleaner(stop_words_file="stopwords2.txt",
                        language="portuguese",
                        perform_stop_words_removal=True,
                        perform_accents_removal=True,
                        perform_stemming=False)
    
    html_indexer.index_text_dir("./data/wiki-pages")
    html_indexer.index.write("wiki.idx")

def search_words_at_wikipedia_index():
    print("Loading index...")
    wiki_idx = Index.read("wiki.idx")
    while True:
        word = input("Enter a word to search: ")
        print("Searching...")
        lst_occur = wiki_idx.get_occurrence_list(word)
        print("Found", len(lst_occur), "occurrences")
        lst_aux = {}
        for occur in lst_occur:
            lst_aux[occur.doc_id] = occur.term_freq
            # print("DocID:", occur.doc_id, "TF:", occur.term_freq)
        print(lst_aux)
        print("Done!")
        lst_occur = None
        lst_aux = None


if __name__ == "__main__":
    print("Choose what you want to do:", "\n", "1. Make Wikipedia Index", "\n", "2. Search words in Wikipedia Index")
    choice = input("Enter your choice: ")
    if choice == "1":
        make_wkipedia_index()
    elif choice == "2":
        search_words_at_wikipedia_index()
