from IPython.display import clear_output
from typing import List, Set, Union
from abc import abstractmethod
from functools import total_ordering
from os import path
import os
import pickle
import gc


class Index:
    def __init__(self):
        self.dic_index = {}
        self.set_documents = set()

    def index(self, term: str, doc_id: int, term_freq: int):
        if term not in self.dic_index:
            int_term_id = len(self.dic_index)
            self.dic_index[term] = self.create_index_entry(int_term_id)
        else:
            int_term_id = self.get_term_id(term)

        self.set_documents.add(doc_id)
        self.add_index_occur(
            self.dic_index[term], doc_id, int_term_id, term_freq)

    @property
    def vocabulary(self) -> List[str]:
        return list(self.dic_index)

    @property
    def document_count(self) -> int:
        return len(self.set_documents)

    @abstractmethod
    def get_term_id(self, term: str):
        raise NotImplementedError(
            "Voce deve criar uma subclasse e a mesma deve sobrepor este método")

    @abstractmethod
    def create_index_entry(self, termo_id: int):
        raise NotImplementedError(
            "Voce deve criar uma subclasse e a mesma deve sobrepor este método")

    @abstractmethod
    def add_index_occur(self, entry_dic_index, doc_id: int, term_id: int, freq_termo: int):
        raise NotImplementedError(
            "Voce deve criar uma subclasse e a mesma deve sobrepor este método")

    @abstractmethod
    def get_occurrence_list(self, term: str) -> List:
        raise NotImplementedError(
            "Voce deve criar uma subclasse e a mesma deve sobrepor este método")

    @abstractmethod
    def document_count_with_term(self, term: str) -> int:
        raise NotImplementedError(
            "Voce deve criar uma subclasse e a mesma deve sobrepor este método")

    def finish_indexing(self):
        print("~ Indexação finalizada! ~")

    def write(self, arq_index: str):
        file = open(arq_index, "wb")
        pickle.dump(self, file)
        file.close()

    @staticmethod
    def read(arq_index: str):
        file = open(arq_index, "rb")
        obj = pickle.load(file)
        file.close()
        return obj

    def __str__(self):
        arr_index = []
        for str_term in self.vocabulary:
            arr_index.append(
                f"{str_term} -> {self.get_occurrence_list(str_term)}")

        return "\n".join(arr_index)

    def __repr__(self):
        return str(self)


@total_ordering
class TermOccurrence:
    def __init__(self, doc_id: int, term_id: int, term_freq: int):
        self.doc_id = doc_id
        self.term_id = term_id
        self.term_freq = term_freq

    def write(self, idx_file):
        # return pickle.dump(self, idx_file)
        try:
            idx_file.write(self.doc_id.to_bytes(4, byteorder="big"))
            idx_file.write(self.term_id.to_bytes(4, byteorder="big"))
            idx_file.write(self.term_freq.to_bytes(4, byteorder="big"))
            return True
        except Exception as e:
            return None

    def __hash__(self):
        return hash((self.doc_id, self.term_id))

    def __eq__(self, other_occurrence: "TermOccurrence"):
        if other_occurrence is None:
            return False
        return self.term_id == other_occurrence.term_id and self.doc_id == other_occurrence.doc_id

    def __lt__(self, other_occurrence: "TermOccurrence"):
        if other_occurrence is None:
            return False
        return self.term_id < other_occurrence.term_id if self.term_id != other_occurrence.term_id else self.doc_id < other_occurrence.doc_id

    def __gt__(self, other_occurrence: "TermOccurrence"):
        if other_occurrence is None:
            return False
        return self.term_id > other_occurrence.term_id if self.term_id != other_occurrence.term_id else self.doc_id > other_occurrence.doc_id

    def __str__(self):
        return f"( doc: {self.doc_id} term_id:{self.term_id} freq: {self.term_freq})"

    def __repr__(self):
        return str(self)


# HashIndex é subclasse de Index
class HashIndex(Index):
    def get_term_id(self, term: str):
        return self.dic_index[term][0].term_id

    def create_index_entry(self, termo_id: int) -> List:
        return []

    def add_index_occur(self, entry_dic_index: List[TermOccurrence], doc_id: int, term_id: int, term_freq: int):
        entry_dic_index.append(TermOccurrence(doc_id, term_id, term_freq))

    def get_occurrence_list(self, term: str) -> List:
        return self.dic_index[term] if term in self.dic_index else []

    def document_count_with_term(self, term: str) -> int:
        return len(self.get_occurrence_list(term)) if term in self.dic_index else 0


class TermFilePosition:
    def __init__(self, term_id: int, term_file_start_pos: int = None, doc_count_with_term: int = None):
        self.term_id = term_id

        # a serem definidos após a indexação
        self.term_file_start_pos = term_file_start_pos
        self.doc_count_with_term = doc_count_with_term

    def __str__(self):
        return f"term_id: {self.term_id}, doc_count_with_term: {self.doc_count_with_term}, term_file_start_pos: {self.term_file_start_pos}"

    def __repr__(self):
        return str(self)


class FileIndex(Index):
    TMP_OCCURRENCES_LIMIT = 1000000

    def __init__(self, idx_dir: str = ""):
        super().__init__()

        self.lst_occurrences_tmp = [None]*FileIndex.TMP_OCCURRENCES_LIMIT
        self.idx_file_counter = 0
        self.str_idx_file_name = "occur_idx_file"
        self.str_idx_dir = idx_dir

        # metodos auxiliares para verifica o tamanho da lst_occurrences_tmp
        self.idx_tmp_occur_last_element = -1
        self.idx_tmp_occur_first_element = 0

    def get_tmp_occur_size(self):
        """Retorna o tamanho da lista temporária de ocorrências"""
        return self.idx_tmp_occur_last_element - self.idx_tmp_occur_first_element + 1 if self.idx_tmp_occur_last_element >= 0 else 0

    def get_term_id(self, term: str):
        return self.dic_index[term].term_id

    def create_index_entry(self, term_id: int) -> TermFilePosition:
        return TermFilePosition(term_id)

    def add_index_occur(self, entry_dic_index: TermFilePosition, doc_id: int, term_id: int, term_freq: int):
        # complete aqui adicionando um novo TermOccurrence na lista lst_occurrences_tmp
        # não esqueça de atualizar a(s) variável(is) auxiliares apropriadamente
        new_occurrence = TermOccurrence(doc_id, term_id, term_freq)

        self.idx_tmp_occur_last_element += 1
        self.lst_occurrences_tmp[self.idx_tmp_occur_last_element] = new_occurrence
        if self.get_tmp_occur_size() >= FileIndex.TMP_OCCURRENCES_LIMIT:
            self.save_tmp_occurrences()

    def next_from_list(self) -> TermOccurrence:
        if self.get_tmp_occur_size() > 0:
            # obtenha o proximo da lista e armazene em nex_occur
            # não esqueça de atualizar a(s) variável(is) auxiliares apropriadamente
            next_occur = self.lst_occurrences_tmp[self.idx_tmp_occur_first_element]
            self.idx_tmp_occur_first_element += 1
            return next_occur
        else:
            return None

    def next_from_file(self, file_pointer) -> TermOccurrence:
        # try:
        #     next_from_file = pickle.load(file_pointer)
        # except:
        #     return None
        # else:
        #     if not next_from_file:
        #         return None
        # doc_id = next_from_file.doc_id
        # term_id = next_from_file.term_id
        # term_freq = next_from_file.term_freq

        if file_pointer is None:
            return None

        bytes_doc_id = file_pointer.read(4)
        if not bytes_doc_id:
            return None
        doc_id = int.from_bytes(bytes_doc_id, byteorder='big')

        bytes_term_id = file_pointer.read(4)
        if not bytes_term_id:
            return None
        term_id = int.from_bytes(bytes_term_id, byteorder='big')

        bytes_term_freq = file_pointer.read(4)
        if not bytes_term_freq:
            return None
        term_freq = int.from_bytes(bytes_term_freq, byteorder='big')

        return TermOccurrence(doc_id, term_id, term_freq)

    def save_tmp_occurrences(self):

        # Para eficiência, todo o código deve ser feito com o garbage collector desabilitado gc.disable()
        gc.disable()

        # Ordena pelo term_id, doc_id
        occurrences = sorted(self.lst_occurrences_tmp[:self.get_tmp_occur_size(
        )], key=lambda x: (x.term_id, x.doc_id))
        self.lst_occurrences_tmp = occurrences

        # Cria o arquivo de índice e abre o arquivo antigo
        old_file = None if self.idx_file_counter == 0 else open(
            self.str_idx_file_name, 'rb')
        self.idx_file_counter += 1
        self.str_idx_file_name = f"occur_idx_file_{self.idx_file_counter}.idx"
        if self.str_idx_dir:
            if not os.path.exists(self.str_idx_dir):
                os.makedirs(self.str_idx_dir)
            self.str_idx_file_name = self.str_idx_dir + self.str_idx_file_name
        new_file = open(self.str_idx_file_name, 'wb')

        """
            Comparar sempre a primeira posição da lista com a primeira posição do arquivo usando 
            os métodos next_from_list e next_from_filee use o método write do TermOccurrence para 
            armazenar cada ocorrencia do novo índice ordenado
        """
        next_list = self.next_from_list()
        next_file = self.next_from_file(old_file)

        # Enquanto houverem elementos na lista e no arquivo, compara e escreve no novo arquivo
        while next_file and next_list:
            if next_list > next_file:
                next_file.write(new_file)
                next_file = self.next_from_file(old_file)
            else:
                next_list.write(new_file)
                next_list = self.next_from_list()

        # Se o arquivo acabou, escreve o restante da lista no arquivo novo
        while next_list:
            next_list.write(new_file)
            next_list = self.next_from_list()

        # Se a lista acabou, escreve o restante do arquivo no arquivo novo
        while next_file:
            next_file.write(new_file)
            next_file = self.next_from_file(old_file)

        # limpa a lista de ocorrências temporárias e reseta os índices
        self.idx_tmp_occur_first_element = 0
        self.idx_tmp_occur_last_element = -1

        # fecha os arquivos
        if old_file is not None:
            old_file.close()
        new_file.close()

        gc.enable()

    def finish_indexing(self):
        if len(self.lst_occurrences_tmp) > 0:
            self.save_tmp_occurrences()

        # Sugestão: faça a navegação e obetenha um mapeamento
        # id_termo -> obj_termo armazene-o em dic_ids_por_termo
        # obj_termo é a instancia TermFilePosition correspondente ao id_termo
        dic_ids_por_termo = {}
        for str_term, obj_term in self.dic_index.items():
            dic_ids_por_termo[obj_term.term_id] = str_term

        with open(self.str_idx_file_name, 'rb') as idx_file:
            # navega nas ocorrencias para atualizar cada termo em dic_ids_por_termo
            # apropriadamente

            # Lê o primeiro termo do arquivo
            term = self.next_from_file(idx_file)
            position = 0

            while term:
                position = idx_file.tell()

                # Pega o termo do dicionário
                str_term = dic_ids_por_termo[term.term_id]
                obj_term = self.dic_index[str_term]

                # Procura quantas vezes o termo ja apareceu no documento
                doc_term_freq = obj_term.doc_count_with_term
                if doc_term_freq is None:
                    doc_term_freq = 0

                # Atualiza o termo no dicionário
                self.dic_index[str_term].doc_count_with_term = doc_term_freq + 1

                # Caso o termo nao tenha sido encontrado ainda, atualiza o diciionário com a primeira posição encontrada
                if self.dic_index[str_term].term_file_start_pos is None:
                    self.dic_index[str_term].term_file_start_pos = position - 12

                # Busca o próximo termo
                term = self.next_from_file(idx_file)

    def get_occurrence_list(self, term: str) -> List:
        occurrence_list = []
        # existe no dicionario?
        if term in self.dic_index.keys():
            # entao o termo existe e ele tem um id
            term_id = self.dic_index[term].term_id

            # Abrir o arquivo e ir para a posicao de inicio do termo
            idx_file = open(self.str_idx_file_name, 'rb')
            idx_file.seek(self.dic_index[term].term_file_start_pos)

            # Consumir a primeira ocorrencia
            next = self.next_from_file(idx_file)

            # Enquanto o next tiver o mesmo term_id do passado na busca vai add
            while (next != None and next.term_id == term_id):
                occurrence_list.append(next)
                next = self.next_from_file(idx_file)

            idx_file.close()
        return occurrence_list

    def document_count_with_term(self, term: str) -> int:
        if term in self.dic_index:
            return self.dic_index[term].doc_count_with_term
        return 0
