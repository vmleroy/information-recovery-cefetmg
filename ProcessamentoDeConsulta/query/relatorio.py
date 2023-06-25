from typing import List
import matplotlib.pyplot as plt

from index.index.structure import Index
from query.ranking_models import VectorRankingModel


def plot_precision_recall(query: str, arr_top: List[int], arr_precision: List[float], arr_recall: List[float]) -> None:
  plt.plot(arr_top, arr_precision, marker=".", label="Precision")
  plt.plot(arr_top, arr_recall, marker="x", label="Recall")
  plt.title(f"Precision and Recal of query: '{query}'")
  plt.xlabel("N docs")
  plt.ylabel("Metric")
  plt.legend()
  plt.show()
  plt.close()
  plt.plot(arr_recall, arr_precision, marker="*", color="red")
  plt.title(f"Precision X Recal of query: '{query}'")
  plt.xlabel("Recall")
  plt.ylabel("Precision")
  plt.show()


def plot_terms_freq(term_freq_list: List[int]):
  x = [i for i in range(len(term_freq_list))]
  y = [freq for freq, _ in term_freq_list]
  _, ax = plt.subplots()
  ax.scatter(x, y)
  ax.set_yscale('log')
  plt.show()


class IDF:
  def __init__(self):
    self.index = Index().read("wiki.idx")
    self.idf_list = []
    self.term_freq_list = []

  def print_mid_idf(self, n):
    x_median = self.idf_list[-1][0] / 2
    mid_idf = 0
    for i, item in enumerate(self.idf_list):
      if (item[0] >= x_median):
        mid_idf = i
        break
    print(f"Top {n} mid idf:")
    for i, item in enumerate(self.idf_list[mid_idf:mid_idf+n]):
      print(f"{i+1}: {item}")

  def print_top_idf(self, n):
    top_melhores_idf = self.idf_list[-10:]
    top_melhores_idf.reverse()
    top_piores_idf = self.idf_list[:10]

    print(f"Top {n} melhores idf:")
    for i, item in enumerate(top_melhores_idf):
      print(f"{i+1}: {item}")
    
    print(f"\nTop {n} piores idf:")
    for i, item in enumerate(top_piores_idf):
      print(f"{i+1}: {item}")

  def calculate_tops(self):
    vocab = self.index.dic_index
    doc_count = len(self.index.set_documents)
    term_freq_list = []
    for term in vocab:
      occur_list = self.index.get_occurrence_list(term)
      num_docs_with_term = len(occur_list)
      self.idf_list.append((VectorRankingModel.idf(doc_count, num_docs_with_term), term))
      term_occur_count = 0
      for occur in occur_list:
        term_occur_count += occur.term_freq
      term_freq_list.append((term_occur_count, term))
    self.idf_list.sort()
    term_freq_list.sort(reverse=True)
    self.term_freq_list = term_freq_list


class TF:
  def __init__(self):
    self.index = Index().read("wiki.idx")
    self.tf_list = []
    self.term_freq_list = []

  def print_mid_tf(self, n):
    x_median = self.tf_list[-1][0] / 2
    mid_tf = 0
    for i, item in enumerate(self.tf_list):
      if (item[0] >= x_median):
        mid_tf = i
        break
    print(f"Top {n} mid tf:")
    for i, item in enumerate(self.tf_list[mid_tf:mid_tf+n]):
      print(f"{i+1}: {item}")


  def print_top_tf(self, n):
    top_melhores_tf = self.tf_list[-10:]
    top_melhores_tf.reverse()
    top_piores_tf = self.tf_list[:10]

    print(f"Top {n} melhores idf:")
    for i, item in enumerate(top_melhores_tf):
      print(f"{i+1}: {item}")
    
    print(f"\nTop {n} piores idf:")
    for i, item in enumerate(top_piores_tf):
      print(f"{i+1}: {item}")

  def calculate_tops(self):
    vocab = self.index.dic_index
    doc_count = len(self.index.set_documents)
    term_freq_list = []
    for term in vocab:
      occur_list = self.index.get_occurrence_list(term)
      term_occur_count = 0
      for occur in occur_list:
        term_occur_count += occur.term_freq
      term_freq_list.append((term_occur_count, term))
      self.tf_list.append((VectorRankingModel.tf(term_occur_count), term))
    self.tf_list.sort()
    term_freq_list.sort(reverse=True)
    self.term_freq_list = term_freq_list

    
