from typing import List
from abc import abstractmethod
from typing import List, Set,Mapping
from index.index.structure import TermOccurrence
import math
from enum import Enum

class IndexPreComputedVals():
    def __init__(self,index, skipPreCompute=False):
        self.index = index
        if not skipPreCompute:
            self.precompute_vals()

    def precompute_vals(self):
        """
        Inicializa os atributos por meio do indice (idx):
            doc_count: o numero de documentos que o indice possui
            document_norm: A norma por documento (cada termo é presentado pelo seu peso (tfxidf))
        """
        self.document_norm = {}
        self.doc_count = self.index.document_count
        self.term_freq = []

        dictionary = self.index.dic_index
        doc_count = len(self.index.set_documents)

        for term, lst_occurrences in dictionary.items():
            occurrence_list = self.index.get_occurrence_list(term)
            num_docs_with_term = len(occurrence_list)
            term_count = 0
            for occurrence in occurrence_list:
                doc_id = occurrence.doc_id
                if doc_id not in self.document_norm.keys():
                    self.document_norm[doc_id] = 0
                self.document_norm[doc_id] += math.pow(VectorRankingModel.tf_idf(doc_count, occurrence.term_freq, num_docs_with_term), 2)
                term_count += occurrence.term_freq
            self.term_freq.append((term_count, term))
        
        self.term_freq.sort(reverse=True)

        for doc_id, norm in self.document_norm.items():
            self.document_norm[doc_id] = math.sqrt(norm)
        
class RankingModel():
    @abstractmethod
    def get_ordered_docs(self,query:Mapping[str,TermOccurrence],
                              docs_occur_per_term:Mapping[str,List[TermOccurrence]]) -> (List[int], Mapping[int,float]):
        raise NotImplementedError("Voce deve criar uma subclasse e a mesma deve sobrepor este método")

    def rank_document_ids(self,documents_weight):
        doc_ids = list(documents_weight.keys())
        doc_ids.sort(key= lambda x:-documents_weight[x])
        return doc_ids

class OPERATOR(Enum):
  AND = 1
  OR = 2
    
#Atividade 1
class BooleanRankingModel(RankingModel):
    def __init__(self,operator:OPERATOR):
        self.operator = operator

    def intersection_all(self, map_lst_occurrences:Mapping[str,List[TermOccurrence]]) -> List[int]:
        set_ids = set()

        for term, lst_occurrences in map_lst_occurrences.items():
            term_occurrences_map = map(lambda occurrence: occurrence.doc_id, lst_occurrences)
            if len(set_ids) > 0:
                set_ids = set_ids.intersection(term_occurrences_map)
            else:
                set_ids.update(term_occurrences_map)

        return set_ids
    
    def union_all(self,map_lst_occurrences:Mapping[str,List[TermOccurrence]]) -> List[int]:
        set_ids = set()

        for term, lst_occurrences in map_lst_occurrences.items():
            term_occurrences_map = map(lambda occurrence: occurrence.doc_id, lst_occurrences)
            set_ids.update(term_occurrences_map)

        return set_ids

    def get_ordered_docs(self,query:Mapping[str,TermOccurrence],
                              map_lst_occurrences:Mapping[str,List[TermOccurrence]]) -> (List[int], Mapping[int,float]):
        """Considere que map_lst_occurrences possui as ocorrencias apenas dos termos que existem na consulta"""
        if self.operator == OPERATOR.AND:
            return self.intersection_all(map_lst_occurrences),None
        else:
            return self.union_all(map_lst_occurrences),None

#Atividade 2
class VectorRankingModel(RankingModel):

    def __init__(self,idx_pre_comp_vals:IndexPreComputedVals):
        self.idx_pre_comp_vals = idx_pre_comp_vals

    @staticmethod
    def tf(freq_term:int) -> float:
        if freq_term < 1:
            return 0
        result = 1 + math.log(freq_term, 2)
        return result

    @staticmethod
    def idf(doc_count:int, num_docs_with_term:int )->float:
        result = math.log(doc_count / num_docs_with_term, 2)
        return result

    @staticmethod
    def tf_idf(doc_count:int, freq_term:int, num_docs_with_term) -> float:
        tf = VectorRankingModel.tf(freq_term)
        idf = VectorRankingModel.idf(doc_count, num_docs_with_term)
        #print(f"TF:{tf} IDF:{idf} n_i: {num_docs_with_term} N: {doc_count}")
        return tf*idf

    def get_ordered_docs(self,query:Mapping[str,TermOccurrence], docs_occur_per_term:Mapping[str,List[TermOccurrence]]) -> (List[int], Mapping[int,float]):
        documents_weight = {}
        documents_norm = self.idx_pre_comp_vals.document_norm

        for term, query_occurrence in query.items():
            if term not in docs_occur_per_term.keys():
                continue
            
            docs_occurrence = docs_occur_per_term[term]
            num_docs_with_term = len(docs_occurrence)
            Wiq = VectorRankingModel.tf_idf(self.idx_pre_comp_vals.doc_count, query_occurrence.term_freq, num_docs_with_term)

            for occur in docs_occurrence:
                doc_id = occur.doc_id
                if doc_id not in documents_weight.keys():
                    documents_weight[doc_id] = 0
                documents_weight[doc_id] += Wiq * VectorRankingModel.tf_idf(self.idx_pre_comp_vals.doc_count, occur.term_freq, num_docs_with_term)

        for doc in documents_weight.keys():
            documents_weight[doc] = documents_weight[doc] / documents_norm[doc]

        #retona a lista de doc ids ordenados de acordo com o TF IDF
        return self.rank_document_ids(documents_weight), documents_weight

