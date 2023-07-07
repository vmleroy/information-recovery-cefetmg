import tkinter as tk
import tkinter.scrolledtext as tkst

from util.time import CheckTime
from query.processing import QueryRunner
from query.ranking_models import RankingModel, VectorRankingModel, IndexPreComputedVals, BooleanRankingModel, OPERATOR
from index.index.structure import Index
from index.index.indexer import Cleaner

class ProcessamentoComInterface:
  dict_title_docs = {}
  index = None
  cleaner = None
  indexPreCom = None
  map_relevance = None

  result = ""
  arr_precisao = []
  arr_revocacao = []
  top_10 = []
  bottom_10 = []

  def pre_processamento(self):
    self.dict_title_docs = {}
    with open("titlePerDoc.dat", encoding="utf8") as arq:
      for line in arq:
        line = line.split(";")
        self.dict_title_docs[int(line[0])] = line[1].strip()

    #leia o indice (base da dados fornecida)
    self.index = Index().read("wiki.idx")
    print("Indice lido com sucesso")

    #Checagem se existe um documento (apenas para teste, deveria existir)
    # print(f"Existe o doc? {index.get_(105047)}")
    #Instancie o IndicePreCompModelo para pr ecomputar os valores necessarios para a query
    print("Precomputando valores atraves do indice...")
    check_time = CheckTime()

    self.indexPreCom = IndexPreComputedVals(self.index)
    # if os.path.exists('pre_compute.idx'):
    # 	with open('pre_compute.idx', 'rb') as f: indexPreCom = pickle.load(f)
    # else:
    # 	indexPreCom = IndexPreComputedVals(index)
    # 	with open('pre_compute.idx', 'wb') as f: pickle.dump(indexPreCom, f)

    check_time.print_delta("Precomputou valores")

    #Instanciando o cleaner
    self.cleaner = Cleaner(stop_words_file="stopwords2.txt",language="portuguese",
                      perform_stop_words_removal=True,perform_accents_removal=True,
                      perform_stemming=False)
    print("Cleaner instanciado com sucesso")
    #encontra os docs relevantes
    self.map_relevance = QueryRunner.get_relevance_per_query()


  def consulta (self, modelo=1):
    print(self.query)
    """
			Para um daterminada consulta `query` é extraído do indice `index` os documentos mais relevantes, considerando 
			um modelo informado pelo usuário. O `indice_pre_computado` possui valores précalculados que auxiliarão na tarefa. 
			Além disso, para algumas consultas, é impresso a precisão e revocaçãoVectorRankingModel nos top 5, 10, 20 e 50. Essas consultas estão
			Especificadas em `map_relevantes` em que a chave é a consulta e o valor é o conjunto de ids de documentos relevantes
			para esta consulta.
		"""
    time_checker = CheckTime()

		#PEça para usuario selecionar entre Booleano ou modelo vetorial para intanciar o QueryRunner
		#apropriadamente. NO caso do booleano, vc deve pedir ao usuario se será um "and" ou "or" entre os termos.
		#abaixo, existem exemplos fixos.
    qr = None
    if modelo == 1:
      print("Modelo Booleano AND escolhido")
      qr = QueryRunner(BooleanRankingModel(OPERATOR.AND), self.index, self.cleaner)
    elif modelo == 2:
      print("Modelo Booleano OR escolhido")
      qr = QueryRunner(BooleanRankingModel(OPERATOR.OR), self.index, self.cleaner)
    else:
      print("Modelo Vetorial escolhido")
      qr = QueryRunner(VectorRankingModel(self.indexPreCom), self.index, self.cleaner)
    time_checker.print_delta("\nQuery Creation")

    self.query = self.cleaner.preprocess_text(self.query)
    joined_query = self.query.replace(" ", "_")

		#Utilize o método get_docs_term para obter a lista de documentos que responde esta consulta
    self.result = qr.get_docs_term(self.query)
    self.result = list(self.result[0])
    # print(f"Resposta: {result}")
    time_checker.print_delta(f"anwered with {len(self.result)} docs\n")

		#nesse if, vc irá verificar se o termo possui documentos relevantes associados a ele
		#se possuir, vc deverá calcular a Precisao e revocação nos top 5, 10, 20, 50.
		#O for que fiz abaixo é só uma sugestao e o metododo countTopNRelevants podera auxiliar no calculo da revocacao e precisao
    self.arr_precisao = []
    self.arr_revocacao = []
    # arr_precisao_revocao = []
    if(True and joined_query in self.map_relevance.keys()):
      doc_relervantes = self.map_relevance[joined_query]
      arr_top = [5,10,20,50]
      precisao = 0
      revocacao = 0
      for n in arr_top:
        precisao, revocacao = qr.compute_precision_recall(n, self.result, doc_relervantes)
        self.arr_precisao.append([n, precisao])
        self.arr_revocacao.append([n, revocacao])
        # arr_precisao_revocao.append({"precisao": precisao, "revocacao": revocacao})
        # print(f"Precisao @{n}: {precisao}")
        # print(f"Recall @{n}: {revocacao}")
    # else:
      # print("Consulta sem documentos no mapeamento de relevantes")

    #imprima aas top 10 respostas
    top_10 = self.result[:10]

		# as 10 piores respostas
    bottom_10 = self.result[-10:]
    bottom_10.reverse()

    # print(f"\nTop 10:")
    for doc in top_10:
      self.top_10.append(f"{doc}: {self.dict_title_docs[doc]}")
    # print(f"\nBottom 10:")
    for doc in bottom_10:
      self.bottom_10.append(f"{doc}: {self.dict_title_docs[doc]}")


class Interface:
  @staticmethod
  def main():
    print("Iniciando interface...")
    print("Preprocessando dados...\n")
    processamento = ProcessamentoComInterface()
    processamento.pre_processamento()

    window = tk.Tk()
    window.title("Processador de consultas")
    window.config(padx=10, pady=10, width=500, height=300)

    # Labels
    website_label = tk.Label(text="Query:")
    website_label.grid(row=1, column=1)

    # Entries
    query_entry = tk.Entry(width=100)
    query_entry.grid(row=2, column=1, columnspan=4)
    query_entry.focus()

    # RadioButtons
    model_label = tk.Label(text="Escollha o modelo:")
    model_label.grid(row=3, column=1)
    model_choice = tk.IntVar()
    model_boolean_and = tk.Radiobutton(text="AND", value=1, variable=model_choice)
    model_boolean_and.grid(row=4, column=1)
    model_boolean_or = tk.Radiobutton(text="OR", value=2, variable=model_choice)
    model_boolean_or.grid(row=4, column=2)    
    model_vetorial = tk.Radiobutton(text="Modelo Vetorial", value=3, variable=model_choice)
    model_vetorial.grid(row=4, column=3)

    # ScrolledText
    result_label = tk.Label(text="Resultado da consulta:")
    result_label.grid(row=6, column=1)
    scrolledtext = tkst.ScrolledText(window)
    scrolledtext.grid(row=7, column=1, columnspan=4)
    
    def consulta():
      processamento.query = query_entry.get()
      print(processamento.query)
      processamento.consulta()
      scrolledtext.delete(1.0, tk.END)
      scrolledtext.insert(tk.INSERT, "Top 10:\n")
      for doc in processamento.top_10:
        scrolledtext.insert(tk.INSERT, doc)
        scrolledtext.insert(tk.INSERT, "\n")
      scrolledtext.insert(tk.INSERT, "\nBottom 10:\n")
      for doc in processamento.bottom_10:
        scrolledtext.insert(tk.INSERT, doc)
        scrolledtext.insert(tk.INSERT, "\n")
      if processamento.arr_precisao:
        scrolledtext.insert(tk.INSERT, "\n\n")
        for n, precisao in processamento.arr_precisao:
          scrolledtext.insert(tk.INSERT, f"Precisão @{n}: {precisao}\n")
        scrolledtext.insert(tk.INSERT, "\n")
        for n, revocacao in processamento.arr_revocacao:
          scrolledtext.insert(tk.INSERT, f"Revocação @{n}: {revocacao}\n")
      else:
        scrolledtext.insert(tk.INSERT, "Consulta sem documentos no mapeamento de relevantes")

    # Buttons
    add_button = tk.Button(text="Pesquisar", width=36, command=consulta)
    add_button.grid(row=5, column=1, columnspan=4)

    window.mainloop()
