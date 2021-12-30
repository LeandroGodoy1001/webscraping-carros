"""Módulo de web scraping dos sites https://www.meuflua.com.br/jeep e https://www.meuflua.com.br/fiat."""
import selenium
import numpy as np
import pandas as pd
from time import sleep
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains



class Flua:
    """Classe de web scraping do site https://www.meuflua.com.br/jeep e https://www.meuflua.com.br/fiat.

    Realiza a coleta de dados de nome, url, Km, periodo de contrato, preço e data de coleta dos dados, 
    de todos os carros presentes no link, com esses dados é gerados arquivos .csv.

    Durante a execução não minimizar ou fechar a janela do navegador que será aberta.
    """

    def __init__(self):
        """Inicializador da classe Unidas."""
        self.url = ['https://www.meuflua.com.br/jeep', 'https://www.meuflua.com.br/fiat']

        # Definindo quais opções serão usadas pelo navegador.
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.dataframe = pd.DataFrame(columns=['Nome', 'Data', 'Locadora', 'Km', 'Meses', 'Valor', 'Descricao'])
        self.navegador = selenium.webdriver.Chrome(service=Service('chromedriver.exe'), options=options)

        print('Iniciando coleta em Flua')
        self.get_data()

    def load_all(self):
        """Carrega todos os carros disponíveis na página."""

        # Tendando fechar aviso de cookies.
        try:
            bnt = self.navegador.find_elements(By.XPATH, '//*[contains(text(), "Fechar")]')[-1]
            bnt.click()
        except:
            pass

        # Procurando botão de ver mais
        bnt = self.navegador.find_elements(By.XPATH, '//*[contains(text(), "VER MAIS")]')[-1]
        # Descendo até ele
        self.navegador.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        bnt.click()
        sleep(1)
        # Descendo até o fim da pagina para carregá-la
        self.navegador.execute_script('window.scrollTo(0,document.body.scrollHeight)')
        sleep(1)


    def get_data(self):
        """Realiza a coleta dos dados nas paginas dos carros."""
        for end in self.url:
            self.navegador.get(end)  # Acessando os sites da lista.
            sleep(10)

            self.load_all()

            # Procurando botões para acessar os carros.
            carros =  self.navegador.find_elements(By.XPATH, '//*[contains(text(), "EU QUERO ESTE")]')
            print(f'Foram encontrados {len(carros)} carros em {end}')

            print('Coletando dados')
            for car in carros:
                ActionChains(self.navegador).move_to_element(car).perform()  # Move o mouse para o carro.
                sleep(.5)
                car.click()
                sleep(1)
                # Procurando botão para voltar para a página anterior.
                bnt_voltar =  self.navegador.find_element(By.XPATH, '//*[contains(text(), "Voltar")]')

                dados_carro = {'Nome':np.nan, 'Data':np.nan, 'Locadora':'Flua', 'Km':np.nan, 'Meses':np.nan, 'Valor':np.nan, 'Descricao':np.nan}

                dados_carro['Nome'] = self.navegador.find_element(By.XPATH, '//div[@class="offer-header no-label"]/h3').text

                # Pegando opçoes de periodo
                meses = self.navegador.find_elements(By.CLASS_NAME, 'monthly-plans__item')
                for mes in meses:
                    mes.click()
                    sleep(1)
                    dados_carro['Meses'] = int(mes.text.split('\n')[0])

                    # Pegando slider de seleção de Km
                    slider = self.navegador.find_element(By.XPATH, '//input[@type="range"]')
                    kms = self.navegador.find_element(By.CLASS_NAME, 'hub-input-range')

                    # Colocando slider na primeira posição.
                    for i in range(5):
                        slider.send_keys(Keys.LEFT)

                    for km in kms.text.split('\n'):
                        dados_carro['Km'] = int(km.replace(' Km', ''))

                        # Formatando preço para se tornar um numero to tipo float.
                        preco = self.navegador.find_element(By.XPATH, '//div[@class="offer-info__price"]/h3').text
                        numeros = float(preco.replace('R$', '').replace('.', '').replace(',', '.'))
                        dados_carro['Valor'] = numeros

                        # Salvando data da coleta e todos os outros dados.
                        dados_carro['Data'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                        self.dataframe.loc[len(self.dataframe)] = dados_carro

                        # Deslizando slider para a proxima posição.
                        slider.send_keys(Keys.RIGHT)
                        sleep(1)

                # Voltando para a pagina dos carros.
                bnt_voltar.click()
                sleep(1)

            print(f'Coleta do site {end} finalizada')
        self.navegador.close()
        self.export_data()


    def export_data(self):
        """Exportando dados em um arquivo csv."""
        print('Exportando dados')
        self.dataframe.to_csv('dados_flua.csv', index=False)
