from tkinter import *

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

  def consulta (self):
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
		modelo = int(input("Digite o número do modelo escolhido -> 1: Booleano, 2: Vetorial\nResposta: "))
		if modelo == 1:
			tipo_operacao = int(input("Digite o número do tipo de operação escolhido -> 1: AND, 2: OR\nResposta: "))
			if tipo_operacao == 1:
				print("Modelo Booleano AND escolhido")
				qr = QueryRunner(BooleanRankingModel(OPERATOR.AND), self.index, self.cleaner)
			else:
				print("Modelo Booleano OR escolhido")
				qr = QueryRunner(BooleanRankingModel(OPERATOR.OR), self.index, self.cleaner)
		else:
			print("Modelo Vetorial escolhido")
			qr = QueryRunner(VectorRankingModel(self.indexPreCom), self.index, self.cleaner)
		time_checker.print_delta("\nQuery Creation")

		query = self.cleaner.preprocess_text(query)
		joined_query = query.replace(" ", "_")

		#Utilize o método get_docs_term para obter a lista de documentos que responde esta consulta
		resposta = qr.get_docs_term(query)
		resposta = list(resposta[0])
		# print(f"Resposta: {resposta}")
		time_checker.print_delta(f"anwered with {len(resposta)} docs\n")

		#nesse if, vc irá verificar se o termo possui documentos relevantes associados a ele
		#se possuir, vc deverá calcular a Precisao e revocação nos top 5, 10, 20, 50.
		#O for que fiz abaixo é só uma sugestao e o metododo countTopNRelevants podera auxiliar no calculo da revocacao e precisao
		arr_precisao = []
		arr_revocacao = []
		# arr_precisao_revocao = []
		if(True and joined_query in self.map_relevantes.keys()):
			doc_relervantes = self.map_relevantes[joined_query]
			arr_top = [5,10,20,50]
			precisao = 0
			revocacao = 0
			for n in arr_top:
				precisao, revocacao = qr.compute_precision_recall(n, resposta, doc_relervantes)
				arr_precisao.append(precisao)
				arr_revocacao.append(revocacao)
				# arr_precisao_revocao.append({"precisao": precisao, "revocacao": revocacao})
				print(f"Precisao @{n}: {precisao}")
				print(f"Recall @{n}: {revocacao}")
		else:
			print("Consulta sem documentos no mapeamento de relevantes")


  @staticmethod
  def main():
    processamento = ProcessamentoComInterface()
    processamento.pre_processamento()

    window = Tk()
    window.title("Processador de consultas")
    window.config(padx=10, pady=100, width=500, height=300)

    # Labels
    website_label = Label(text="Query:")
    website_label.grid(row=2, column=0)

    # Entries
    processamento.query = Entry(width=35)
    processamento.query.grid(row=2, column=1, columnspan=2)
    processamento.query.focus()

    # Buttons
    add_button = Button(text="Pesquisar", width=36, command=processamento.consulta)
    add_button.grid(row=4, column=1, columnspan=2)

    window.mainloop()
