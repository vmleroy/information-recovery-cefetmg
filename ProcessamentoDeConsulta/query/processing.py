import datetime
import pickle
import os

from typing import List, Set,Mapping
from nltk.tokenize import word_tokenize
from util.time import CheckTime

from index.index.structure import Index, TermOccurrence
from index.index.indexer import Cleaner
from query.ranking_models import RankingModel, VectorRankingModel, IndexPreComputedVals, BooleanRankingModel, OPERATOR
from query.relatorio import plot_precision_recall

class QueryRunner:
	def __init__(self,ranking_model:RankingModel, index:Index, cleaner:Cleaner):
		self.ranking_model = ranking_model
		self.index = index
		self.cleaner = cleaner


	@staticmethod
	def get_relevance_per_query() -> Mapping[str,Set[int]]:
		"""
		Adiciona a lista de documentos relevantes para um determinada query (os documentos relevantes foram
		fornecidos no ".dat" correspondente. Por ex, belo_horizonte.dat possui os documentos relevantes da consulta "Belo Horizonte"

		"""
		dic_relevance_docs = {}
		for arquiv in os.listdir("relevant_docs"):
			if (arquiv.endswith(".dat")):
				with open(f"relevant_docs/{arquiv}") as arq:
					arr = [int(s) for s in arq.readline().split(",")]
					dic_relevance_docs[arquiv.replace(".dat", "")] = set(arr)
		return dic_relevance_docs

	def count_topn_relevant(self,n:int,respostas:List[int],doc_relevantes:Set[int]) -> int:
		"""
		Calcula a quantidade de documentos relevantes na top n posições da lista lstResposta que é a resposta a uma consulta
		Considere que respostas já é a lista de respostas ordenadas por um método de processamento de consulta (BM25, Modelo vetorial).
		Os documentos relevantes estão no parametro docRelevantes
		"""
		relevance_count = 0
		for doc in doc_relevantes:
			if doc in respostas[:n]:
				relevance_count += 1
		return relevance_count

	def compute_precision_recall(self, n:int, lst_docs:List[int], relevant_docs:Set[int]) -> (float,float):
		
		count_relevant = self.count_topn_relevant(n,lst_docs,relevant_docs)

		precision = float(count_relevant/n)
		recall = float(count_relevant/len(relevant_docs))

		return precision, recall
    
	def get_query_term_occurence(self, query:str) -> Mapping[str,TermOccurrence]:
		"""
			Preprocesse a consulta da mesma forma que foi preprocessado o texto do documento (use a classe Cleaner para isso).
			E transforme a consulta em um dicionario em que a chave é o termo que ocorreu
			e o valor é uma instancia da classe TermOccurrence (feita no trabalho prático passado).
			Coloque o docId como None.
			Caso o termo nao exista no indic, ele será desconsiderado.
		"""
		#print(self.index)
		map_term_occur = {}
		dic_count = {}

		text = self.cleaner.preprocess_text(query)
		text = word_tokenize(text, language="portuguese")

		# Consulta da frequencia de cada termo na consulta
		for token in text: 	
			term = self.cleaner.preprocess_word(token)
			if term is not None:
				if term not in dic_count:
					dic_count[term] = 0
				dic_count[term] += 1

		# Criação do dicionario de ocorrencia de cada termo presente na consulta
		for term, count in dic_count.items():
			occurrence_list = self.index.get_occurrence_list(term)
			if occurrence_list:
				map_term_occur[term] = TermOccurrence(None, self.index.get_term_id(term), count)
				
		return map_term_occur

	def get_occurrence_list_per_term(self, terms:List) -> Mapping[str, List[TermOccurrence]]:
		"""
			Retorna dicionario a lista de ocorrencia no indice de cada termo passado como parametro.
			Caso o termo nao exista, este termo possuirá uma lista vazia
		"""
		dic_terms = {}
		for term in terms:
			occurrence_list = self.index.get_occurrence_list(term)
			if occurrence_list:
				dic_terms[term] = occurrence_list
			else:
				dic_terms[term] = []
		return dic_terms

	def get_docs_term(self, query:str) -> List[int]:
		"""
			A partir do indice, retorna a lista de ids de documentos desta consulta
			usando o modelo especificado pelo atributo ranking_model
		"""
		# print(f"query: {query}")

		#Obtenha, para cada termo da consulta, sua ocorrencia por meio do método get_query_term_occurence
		dic_query_occur = self.get_query_term_occurence(query)
		# print(f"dic_query_occur: {dic_query_occur}")

		#obtenha a lista de ocorrencia dos termos da consulta
		dic_occur_per_term_query = self.get_occurrence_list_per_term(dic_query_occur.keys())
		# print(f"dic_occur_per_term_query: {dic_occur_per_term_query}")

		#utilize o ranking_model para retornar o documentos ordenados considrando dic_query_occur e dic_occur_per_term_query
		return self.ranking_model.get_ordered_docs(dic_query_occur, dic_occur_per_term_query)

	@staticmethod
	def runQuery(query:str, indice_pre_computado:IndexPreComputedVals, indice:Index, cleaner: Cleaner, map_relevantes:Mapping[str,Set[int]], plotPrecisionRecall=False):
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
				qr = QueryRunner(BooleanRankingModel(OPERATOR.AND), indice, cleaner)
			else:
				print("Modelo Booleano OR escolhido")
				qr = QueryRunner(BooleanRankingModel(OPERATOR.OR), indice, cleaner)
		else:
			print("Modelo Vetorial escolhido")
			qr = QueryRunner(VectorRankingModel(indice_pre_computado), indice, cleaner)
		time_checker.print_delta("\nQuery Creation")

		query = cleaner.preprocess_text(query)
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
		if(True and joined_query in map_relevantes.keys()):
			doc_relervantes = map_relevantes[joined_query]
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

		if (plotPrecisionRecall):
			plot_precision_recall(query, arr_top, arr_precisao, arr_revocacao)

		#imprima aas top 10 respostas
		top_10 = resposta[:10]

		# as 10 piores respostas
		bottom_10 = resposta[-10:]
		bottom_10.reverse()

		return top_10, bottom_10, (arr_precisao, arr_revocacao)


	@staticmethod
	def main(returnValue=False, plotPrecisionRecall=False):

		dict_title_docs = {}
		with open("titlePerDoc.dat", encoding="utf8") as arq:
			for line in arq:
				line = line.split(";")
				dict_title_docs[int(line[0])] = line[1].strip()

		#leia o indice (base da dados fornecida)
		index = Index().read("wiki.idx")
		print("Indice lido com sucesso")

		#Checagem se existe um documento (apenas para teste, deveria existir)
		# print(f"Existe o doc? {index.get_(105047)}")

		#Instancie o IndicePreCompModelo para pr ecomputar os valores necessarios para a query
		print("Precomputando valores atraves do indice...")
		check_time = CheckTime()
      
		indexPreCom = IndexPreComputedVals(index)

		# if os.path.exists('pre_compute.idx'):
		# 	with open('pre_compute.idx', 'rb') as f: indexPreCom = pickle.load(f)
		# else:
		# 	indexPreCom = IndexPreComputedVals(index)
		# 	with open('pre_compute.idx', 'wb') as f: pickle.dump(indexPreCom, f)
		
		check_time.print_delta("Precomputou valores")
		
		#Instanciando o cleaner
		cleaner = Cleaner(stop_words_file="stopwords2.txt",language="portuguese",
                      perform_stop_words_removal=True,perform_accents_removal=True,
                      perform_stemming=False)
		print("Cleaner instanciado com sucesso")

		#encontra os docs relevantes
		map_relevance = QueryRunner.get_relevance_per_query()
		
		#aquui, peça para o usuário uma query (voce pode deixar isso num while ou fazer um interface grafica se estiver bastante animado ;)
		# print("Fazendo query...")
		# query = "São Paulo"
		while True:
			print("\n===========================================")
			opcao = int(input('Voce deseja fazer uma consulta? -> 1: SIM, 2: NAO\nResposta: '))
			if(opcao == 1):
				query = input('Digite a query: ')
				print(f"Fazendo query de '{query}'...")
				result = QueryRunner.runQuery(query, indexPreCom, index, cleaner, map_relevance, plotPrecisionRecall)
				print(f"\nTop 10:")
				for doc in result[0]:
					print(f"{doc}: {dict_title_docs[doc]}")
				print(f"\nBottom 10:")
				for doc in result[1]:
					print(f"{doc}: {dict_title_docs[doc]}")
				# print(f"Precision and Recall: {result[2]}")
			else:
				print("  Saindo...")
				break
		
		if (returnValue):
			return index, indexPreCom, cleaner, map_relevance
			
			
