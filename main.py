"""
Módulo principal de WebScraping dos sites:

- https://livre.unidas.com.br/carros
- https://www.portosegurocarrofacil.com.br/veiculos
- https://www.movidazerokm.com.br/assinatura/busca
- https://www.meuflua.com.br/jeep
- https://www.meuflua.com.br/fiat
"""
import os
import pandas as pd
from Sites.Flua import Flua
from Sites.Porto import Porto
from Sites.Unidas import Unidas
from Sites.Movida import Movida
from multiprocessing import Process

class WebScraping:
    """Classe principal do Web Scraping.

    Utilizando, ou não, multiprocessamento, realiza a coleta de dados de nome, url, Km, periodo de contrato, descrição de pagamento,
    preço e data de coleta dos dados, de todos os carros presentes no link, com esses dados são gerados arquivos .csv de cada site 
    ou um .csv contendo todos eles.

    Durante a execução não minimizar ou fechar as janelas do navegador que serão abertas
    """

    def __init__(self, unidas, porto, movida, flua, juntar_dados=True, multi_process=True):
        """Inicializador da classe Web Scraping

        Args:
            unidas (bool): Condição para realizar web scraping no site https://livre.unidas.com.br/carros.
            porto (boll): Condição para realizar web scraping no site https://www.portosegurocarrofacil.com.br/veiculos.
            movida (bool): Condição para realizar web scraping no site https://www.movidazerokm.com.br/assinatura/busca.
            flua (bool): Condição para realizar web scraping nos sites https://www.meuflua.com.br/jeep e  https://www.meuflua.com.br/fiat.
            juntar_dados (bool, opcional): Condição para criação de um unico .csv que contenha todos os dados coletados. Padrão é True.
            multi_process (bool, opcional): Condição para utilizar multiprocessamento no web scraping. Padrão é True.
        """
        self.sites = []
        self.dados= []
        if unidas:
            self.sites.append(Unidas)
            self.dados.append('dados_unidas.csv')
        if porto:
            self.sites.append(Porto)
            self.dados.append('dados_porto.csv')
        if movida:
            self.sites.append(Movida)
            self.dados.append('dados_movida.csv')
        if flua:
            self.sites.append(Flua)
            self.dados.append('dados_flua.csv')

        self.mutli_process = multi_process
        self.juntar = juntar_dados


    def run(self):
        """Roda o web scraping para os sites selecionados."""
        if self.mutli_process:
            processos = []
            for site in self.sites:
                p = Process(target=site)  # Criando processo.
                p.start()  # Iniciando processo.
                processos.append(p)  # Salvando processo para realizar multiprocessamento.

            # Rodando todos os processos em conjunto.
            for p in processos:
                p.join()
        else:
            # Rodando web scraping de cada site sem multiprocessamento.
            for site in self.sites:
                site()

        if self.juntar:
            self.juntar_dados()


    def juntar_dados(self):
        print('Juntando dados...')

        dados = pd.DataFrame()
        for arquivo in self.dados:
            # Tentando ler arquivo com dados dos site e apagando ele após a leitura.
            try:
                csv = pd.read_csv(arquivo)
                os.remove(arquivo)
            except:  # Exceção para caso não seja possivel ler o arquivo, neste caso ele será apenas ignorado.
                continue
            dados = pd.concat([dados, csv])  # Juntando dados.

        # Exportando dados em um unico .csv.
        dados.to_csv('dados.csv', index=False)
        print('Dados juntados com sucesso!')



if __name__ == '__main__':
    ws = WebScraping(unidas=True, porto=True, movida=True, flua=True, juntar_dados=True, multi_process=True)
    ws.run()
