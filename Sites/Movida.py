"""Módulo de web scraping do site https://www.movidazerokm.com.br/assinatura/busca."""
import selenium
import numpy as np
import pandas as pd
from time import sleep
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class Movida:
    """Classe de web scraping do site https://www.movidazerokm.com.br/assinatura/busca.

    Realiza a coleta de dados de nome, url, Km, periodo de contrato, descrição de pagamento, preço e data de coleta dos dados, 
    de todos os carros presentes no link, com esses dados é gerados arquivos .csv.

    Durante a execução não minimizar ou fechar a janela do navegador que será aberta.
    
    O movidazerokm.com.br é um site problematico para fazer web scraping, ele gera diversas falhas durante a execução
    e mesmo tentando contornar essas falhas haverá erros.
    """

    def __init__(self):
        """Inicializador da classe Unidas."""
        self.url = 'https://www.movidazerokm.com.br/assinatura/busca'

        # Definindo quais opções serão usadas pelo navegador.
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.dataframe = pd.DataFrame(columns=['Nome', 'Data', 'Locadora', 'Km', 'Meses', 'Valor', 'Descricao'])
        self.navegador = selenium.webdriver.Chrome(service=Service('chromedriver.exe'), options=options)
        self.navegador.maximize_window()  # Maximizando a janela do navegador, para evitar probemas de visualização.

        print('Iniciando coleta em Movida')
        self.get_data()

    def pagina_inicial(self):
        """Acessa a página que contem todos os carros."""
        self.navegador.get(self.url)
        sleep(5)


    def get_carros(self):
        """Pegando o link de todos os carros disponíveis na página.

        Returns:
            list: Lista com o link de todos os carros.
        """
        carros =  self.navegador.find_elements(By.XPATH, '/html/body/app-root/div/div/app-search-results/div/div/div[2]/div/div')
        print(f'Foram encontrados {len(carros)} em {self.url}')
        return carros


    def load_meses(self):
        """Abre a lista que contem as opções de período.

        Returns:
            list: Lista com todas as opções de períodos.
        """
        try:
            opcoes_meses = self.navegador.find_element(By.XPATH, '//mat-select[@id="mat-select-0"]')
            ActionChains(self.navegador).move_to_element(opcoes_meses).perform()
            opcoes_meses.click()
        except:
            sleep(2)
            ActionChains(self.navegador).send_keys(Keys.ESCAPE).perform()
            opcoes_meses = self.navegador.find_element(By.XPATH, '//mat-select[@id="mat-select-4"]')
            ActionChains(self.navegador).move_to_element(opcoes_meses).perform()
            opcoes_meses.click()
        meses = self.navegador.find_elements(By.XPATH, '//*[@role="option"]')
        sleep(.5)
        return meses


    def load_kms(self):
        """Abre a lista que contem as opções de Km.

        Returns:
            list: Lista com todas as opções de Km.
        """
        try:
            opcoes_km = self.navegador.find_element(By.XPATH, '//mat-select[@id="mat-select-1"]')
            ActionChains(self.navegador).move_to_element(opcoes_km).perform()
            opcoes_km.click()
        except:
            sleep(2)
            ActionChains(self.navegador).send_keys(Keys.ESCAPE).perform()
            opcoes_km = self.navegador.find_element(By.XPATH, '//mat-select[@id="mat-select-5"]')
            ActionChains(self.navegador).move_to_element(opcoes_km).perform()
            opcoes_km.click()
        kms = self.navegador.find_elements(By.XPATH, '//*[@role="option"]')
        sleep(.5)
        return kms

    def fechar_chat(self):
        """Fecha o chat do site se estiver aberto."""
        try:
            self.navegador.switch_to.frame('chat-widget')  # Acessando frame em que o chat está.
            chat = self.navegador.find_element(By.XPATH, '//button[@aria-label="Minimizar janela"]')
            chat.click()
            self.navegador.switch_to.default_content()  # Voltando para o frame principal.
        except:
            self.navegador.switch_to.default_content()  # Voltando para o frame principal.
            pass


    def get_data(self):
        """Realiza a coleta dos dados nas paginas dos carros."""
        self.pagina_inicial()
        sleep(10)

        self.fechar_chat()

        # Fechando mensagem de cookies.
        self.navegador.find_element(By.XPATH, '//a[@aria-label="allow cookies"]').click()

        carros = self.get_carros()

        print('Coletando dados')
        i = 0
        while i < len(carros):
            try:
                dados_carro = {'Nome':np.nan, 'Data':np.nan, 'Locadora':'Movida Zero Km', 'Km':np.nan, 'Meses':np.nan, 'Valor':np.nan, 'Descricao':np.nan}
                self.fechar_chat()
                try:
                    # Descendo na página principal para acessar o proximo carro.
                    self.navegador.execute_script(f'window.scrollBy(0, {125*i})')
                    sleep(2)
                    car = self.navegador.find_element(By.ID, f'vehicleCard{i}')
                except:  # Exceção para quando a pagina não carregar completamente.
                    self.navegador.refresh()
                    sleep(15)
                    self.navegador.execute_script(f'window.scrollBy(0, {130*i})')
                    sleep(2)
                    car = self.navegador.find_element(By.ID, f'vehicleCard{i}')

                ActionChains(self.navegador).move_to_element(car).perform()  # Movendo mouse para o carro.
                sleep(1)
                car.click()
                sleep(8)

                dados_carro['Nome'] = self.navegador.find_element(By.XPATH, '//h1[@class="subtitle-car-detail"]').text

                # Descendo na página para evitar problemas de não conseguir acessar o objetivo por estar fora da tela ou com algo na frente.
                self.navegador.execute_script('window.scrollBy(0, 200)')
                sleep(1)

                meses = self.load_meses()  # Abrindo lista de opções de meses.

                for mes in meses:
                    dados_carro['Meses'] = int(mes.text.replace('meses', ''))
                    mes.click()    # Selecionando opção de km.
                    sleep(1)
                    try:
                        kms = self.load_kms()  # Abrindo lista de opções de Km e salvandoa-as.
                    except:
                        self.navegador.refresh()
                        sleep(8)
                        kms = self.load_kms()

                    for km in kms:
                        dados_carro['Km'] = int(km.text.replace(' Km', '').replace('.', ''))
                        km.click()  # Selecionando opção de km.
                        sleep(2)

                        # Tentando coletar os dados.
                        try:
                            # Formatando preço para se tornar um numero to tipo float.
                            valor = self.navegador.find_element(By.XPATH, '//h1[@class="price-label"]').text
                            numeros = float(valor.replace('R$ ', '').replace('.', '').replace(',', '.'))
                        except:
                            # Segunda tentativa de coletar o preço caso a primeira falhe.
                            sleep(6)
                            valor = self.navegador.find_element(By.XPATH, '//h1[@class="price-label"]').text
                            numeros = float(valor.replace('R$ ', '').replace('.', '').replace(',', '.'))
                        try:
                            # Coletando descrição de pagamento se ela existir.
                            desc = self.navegador.find_element(By.XPATH, '//h5[@class="price-observation"]').text
                        except:
                            # Caso não consiga coletar, o valor será NaN.
                            desc = np.nan

                        # Salvando dados que ainda não foram salvos.
                        dados_carro['Valor'] = numeros
                        dados_carro['Descricao'] = desc
                        dados_carro['Data'] = datetime.now().strftime('%d/%m/%Y %H:%M')

                        # Guardando no dataframe.
                        self.dataframe.loc[len(self.dataframe)] = dados_carro
                        self.load_kms()  # Abrindo lista de opções de Km.

                    kms[0].click()
                    try:
                        self.load_meses()  # Abrindo lista de opções de períodos.
                    except:
                        self.navegador.refresh()
                        sleep(8)
                        self.load_meses()
            except:
                self.navegador.refresh()
                sleep(8)
                i -= 1
            # Voltando para a página inicial.
            self.pagina_inicial()
            i += 1

        print(f'Coleta do site {self.url} finalizada')
        self.navegador.close()
        self.export_data()


    def export_data(self):
        """Exportando dados em um arquivo csv."""
        print('Exportando dados')
        self.dataframe.to_csv('dados_movida.csv', index=False)
