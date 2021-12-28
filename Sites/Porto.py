"""Módulo de web scraping do site https://www.portosegurocarrofacil.com.br/veiculos."""
import selenium
import numpy as np
import pandas as pd
from time import sleep
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class Porto:
    """Classe de web scraping do site https://www.portosegurocarrofacil.com.br/veiculos.

    Realiza a coleta de dados de nome, url, Km, periodo de contrato, preço e data de coleta dos dados, 
    de todos os carros presentes no link, com esses dados é gerados arquivos .csv.

    Durante a execução não minimizar ou fechar a janela do navegador que será aberta.
    """

    def __init__(self):
        """Inicializador da classe Porto."""
        self.url = 'https://www.portosegurocarrofacil.com.br/veiculos'

        # Definindo quais opções serão usadas pelo navegador.
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Opção para ignorar erros de conexão com dispositivos.

        self.dataframe = pd.DataFrame(columns=['Nome', 'Km', 'URL', 'Data'])
        self.navegador = selenium.webdriver.Chrome(service=Service('chromedriver.exe'), options=options)

        print('Iniciando coleta em Porto Seguro')
        self.navegador.get(self.url)
        sleep(10)
        self.get_data()


    def load_all(self):
        """Carrega todos os carros disponíveis na página, neste site apenas descer até o fim já é suficiente."""
        self.navegador.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        sleep(5)


    def get_links(self):
        """Pegando o link de todos os carros disponíveis na página.

        Returns:
            list: Lista com o link de todos os carros.
        """
        self.load_all()

        # Procurando todos os links.
        enderecos = self.navegador.find_elements(By.XPATH, '//*[@href]')

        carros = []
        for end in enderecos:
            link = end.get_attribute('href')  # Pegando o link dos objetos encontrados.

            # Separando somente os que são links de carros.
            if '/veiculos/' in link and link not in carros and link is not None:
                carros.append(link)

        print(f'Foram encontrados {len(carros)} carros em {self.url}')
        return carros

    def get_data(self):
        """Realiza a coleta dos dados nas paginas dos carros."""
        carros = self.get_links()

        print('Coletando dados...')
        for carro in carros:
            dados_carro = {'Nome':np.nan, 'Km':np.nan, 'URL':np.nan,'Mes':[], 'Valor':[], 'Data':np.nan}
            self.navegador.get(carro)  # Acessando carro.
            sleep(2)

            # Lendo opções de periodo, elas são do tipo lista de seleção 
            # então já estão sendo salvas nesse formato, pois o Selenium da suporte para isso.
            meses = Select(self.navegador.find_element(By.XPATH, f'//*[@name="periods"]'))

            dados_carro['Nome'] = self.navegador.find_element(By.XPATH, '//h1[@class="styles__Model-sc-42cvqa-8 bgjONp"]').text
            dados_carro['URL'] = carro

            for km in range(1,5):
                for mes in meses.options[1:]:
                    meses.select_by_visible_text(mes.text)  # Selecioando opção da lista de periodos.
                    sleep(.5)

                    kms = Select(self.navegador.find_element(By.XPATH, f'//*[@name="bundles"]'))
                    kms.select_by_visible_text(kms.options[km].text)  # Selecioando opção da lista de Km.
                    sleep(.5)

                    # Formatando preço para se tornar um numero to tipo float.
                    preco = self.navegador.find_element(By.XPATH, '//p[@class="styles__Price-sc-42cvqa-6 bNzvrM"]').text
                    numeros = preco.split(' ')[-1]
                    valor = float(numeros.replace('.', '').replace(',', '.'))

                    # Salvando data da coleta e todos os outros dados.
                    dados_carro['Km'] = kms.options[km].text
                    dados_carro['Mes'].append(mes.text.replace('m', 'M'))
                    dados_carro['Valor'].append(valor)
                    dados_carro['Data'] = datetime.now().strftime('%d/%m/%Y %H:%M')

                self.dataframe.loc[len(self.dataframe)] = dados_carro
                for m, v in zip(dados_carro['Mes'], dados_carro['Valor']):
                    self.dataframe[m] = v

        print(f'Coleta do site {self.url} finalizada')
        self.navegador.close()
        self.export_data()


    def export_data(self):
        """Exportando dados em um arquivo csv."""
        print('Exportando dados')
        self.dataframe.to_csv('dados_porto.csv', index=False)
