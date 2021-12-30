"""Módulo de web scraping do site https://livre.unidas.com.br/carros."""
import selenium
import numpy as np
import pandas as pd
from time import sleep
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains


class Unidas:
    """Classe de web scraping do site https://livre.unidas.com.br/carros.

    Realiza a coleta de dados de nome, url, Km, periodo de contrato, descrição de pagamento, preço e data de coleta dos dados, 
    de todos os carros presentes no link, com esses dados é gerados arquivos .csv.

    Durante a execução não minimizar ou fechar a janela do navegador que será aberta.
    """

    def __init__(self):
        """Inicializador da classe Unidas."""
        self.url = 'https://livre.unidas.com.br/carros'

        # Definindo quais opções serão usadas pelo navegador.
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Opção para ignorar erros de conexão com dispositivos.

        self.dataframe = pd.DataFrame(columns=['Nome', 'Data', 'Locadora', 'Km', 'Meses', 'Valor', 'Descricao'])
        self.navegador = selenium.webdriver.Chrome(service=Service('chromedriver.exe'), options=options)

        print('Iniciando coleta em Unidas')
        self.navegador.get(self.url)
        sleep(10)
        self.get_data()


    def load_all(self):
        """Carrega todos os carros disponíveis na página."""
        for i in range(2):
            # Procurando botão de ver mais.
            bnt = self.navegador.find_elements(By.XPATH, '//*[contains(text(), "Ver mais")]')[-1]
            # Descendo até ele.
            ActionChains(self.navegador).move_to_element(bnt).perform()
            # Descendo um pouco mais para a mensagem de cookies não ficar na frente.
            self.navegador.execute_script('window.scrollBy(0, 200)')
            sleep(1)
            # Clicando no botão.
            bnt.click()
            sleep(2)


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
            if '/carros/' in link and link not in carros and link is not None:
                carros.append(link)

        print(f'Foram encontrados {len(carros)} carros em {self.url}')
        return carros


    def get_data(self):
        """Realiza a coleta dos dados nas paginas dos carros."""
        carros = self.get_links()

        print('Coletando dados...')
        for carro in carros:
            dados_carro = {'Nome':np.nan, 'Data':np.nan, 'Locadora':'Unidas', 'Km':np.nan, 'Meses':np.nan, 'Valor':np.nan, 'Descricao':np.nan}
            self.navegador.get(carro)  # Acessando carro.
            sleep(3)

            dados_carro['Nome'] = self.navegador.find_element(By.CLASS_NAME, 'page-title').text

            # Lendo opções de Km e periodo, elas são do tipo lista de seleção 
            # então já estão sendo salvas nesse formato, pois o Selenium da suporte para isso.
            kms = Select(self.navegador.find_element(By.XPATH, f'//*[@id="franchise"]'))
            meses = Select(self.navegador.find_element(By.XPATH, f'//*[@id="period"]'))

            for km in kms.options:
                dados_carro['Km'] = int(km.text.replace(' Km', ''))
                kms.select_by_visible_text(km.text)  # Selecioando opção da lista de Km.
                sleep(2)

                for mes in meses.options:
                    meses.select_by_visible_text(mes.text)  # Selecioando opção da lista de periodos.
                    sleep(2)
                    dados_carro['Meses'] = int(mes.text.replace('Meses', ''))

                    preco = self.navegador.find_elements(By.XPATH, '//p[@class="overview-purchase__card-p price"]/span')[-1]

                    # Formatando preço para se tornar um numero to tipo float.
                    texto_separado = preco.text.split(' ')
                    numero = texto_separado[-1].split('/')[0]
                    dados_carro['Valor'] = float(numero.replace('.', '').replace(',', '.'))

                    descricao = self.navegador.find_element(By.XPATH, '//p[@class="font-size-0dot875 text-success mt-3 mb-5 ng-star-inserted"]')
                    dados_carro['Descricao'] = descricao.text

                    # Salvando data da coleta.
                    dados_carro['Data'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                    self.dataframe.loc[len(self.dataframe)] = dados_carro

        print(f'Coleta do site {self.url} finalizada')
        self.navegador.close()
        self.export_data()


    def export_data(self):
        """Exportando dados em um arquivo csv."""
        print('Exportando dados')
        self.dataframe.to_csv('dados_unidas.csv', index=False)
