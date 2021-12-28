"""Módulo de web scraping do site https://www.movidazerokm.com.br/assinatura/busca."""
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



class Movida:
    """Classe de web scraping do site https://www.movidazerokm.com.br/assinatura/busca.

    Realiza a coleta de dados de nome, url, Km, periodo de contrato, descrição de pagamento, preço e data de coleta dos dados, 
    de todos os carros presentes no link, com esses dados é gerados arquivos .csv.

    Durante a execução não minimizar ou fechar a janela do navegador que será aberta.
    
    O movidazerokm.com.br é um site problematico para fazer web scraping, ele gera diversas falhas durante a execução
    e mesmo tentando contornar essas falhas, varias vezes haverá erros.
    """

    def __init__(self):
        """Inicializador da classe Unidas."""
        self.url = 'https://www.movidazerokm.com.br/assinatura/busca'

        # Definindo quais opções serão usadas pelo navegador.
        options = Options()
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        self.dataframe = pd.DataFrame(columns=['Nome', 'Km', 'URL', '12 Meses', '18 Meses', '24 Meses', '30 Meses', '36 Meses', 'Desc 12 Meses', 'Desc 18 Meses', 'Desc 24 Meses', 'Desc 30 Meses', 'Desc 36 Meses'])
        self.navegador = selenium.webdriver.Chrome(service=Service('chromedriver.exe'), options=options)
        self.navegador.maximize_window()  # Maximizando a janela do navegador, para evitar probemas de visualização.

        print('Iniciando coleta em Movida')
        self.get_data()

    def pagina_inicial(self):
        """Acessa a página que contem todos os carros."""
        self.navegador.get(self.url)
        sleep(4)


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
        opcoes_meses = self.navegador.find_element(By.XPATH, '//mat-select[@id="mat-select-0"]')
        try:
            opcoes_meses.click()
        except:
            self.navegador.find_element(By.XPATH, '//button[contains(text(), "OK")]').click()
            opcoes_meses.click()
        meses = self.navegador.find_elements(By.XPATH, '//*[@role="option"]')
        return meses


    def load_kms(self):
        """Abre a lista que contem as opções de Km.

        Returns:
            list: Lista com todas as opções de Km.
        """
        opcoes_km = self.navegador.find_element(By.XPATH, '//mat-select[@id="mat-select-1"]')
        try:
            opcoes_km.click()
        except:
            self.navegador.find_element(By.XPATH, '//button[contains(text(), "OK")]').click()
            opcoes_km.click()
        kms = self.navegador.find_elements(By.XPATH, '//*[@role="option"]')
        return kms

    def fechar_chat(self):
        """Fecha o chat do site se estiver aberto."""
        try:
            self.navegador.switch_to.frame('chat-widget')  # Acessando frame em que o chat está.
            chat = self.navegador.find_element(By.XPATH, '//button[@aria-label="Minimizar janela"]')
            chat.click()
            self.navegador.switch_to.default_content()  # Voltando para o frame principal.
        except:
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
        for i in range(len(carros)):
            dados_carro = {'Nome':np.nan, 'Km':np.nan, 'URL':np.nan, 'Data':np.nan}
            self.fechar_chat()
            try:
                # Descendo na página principal para acessar o proximo carro.
                self.navegador.execute_script(f'window.scrollBy(0, {125*i})')
                sleep(2)
                car = self.navegador.find_element(By.ID, f'vehicleCard{i}')
            except:  # Exceção para quando a pagina não carregar completamente.
                self.navegador.refresh()
                sleep(10)
                self.navegador.execute_script(f'window.scrollBy(0, {125*i})')
                sleep(2)
                car = self.navegador.find_element(By.ID, f'vehicleCard{i}')

            ActionChains(self.navegador).move_to_element(car).perform()  # Movendo mouse para o carro.
            sleep(1)
            car.click()
            sleep(8)

            dados_carro['Nome'] = self.navegador.find_element(By.XPATH, '//h1[@class="title-car-detail"]').text
            dados_carro['URL'] = self.navegador.current_url

            # Descendo na página para evitar problemas de não conseguir acessar o objetivo por estar fora da tela ou com algo na frente.
            self.navegador.execute_script('window.scrollBy(0, 1000)')
            sleep(2)

            meses = self.load_meses()  # Abrindo lista de opções de Km.

            for mes in meses:
                dados_carro['Mes'] = mes.text.split(' ')[0]+' Meses'
                mes.click()    # Selecionando opção de km.
                sleep(1)
                kms = self.load_kms()  # Abrindo lista de opções de Km e salvandoa-as.
                kms[0].click()

                for km in kms:
                    self.load_kms()  # Abrindo lista de opções de Km.
                    dados_carro['Km'] = km.text.replace(' Km', '')
                    km.click()  # Selecionando opção de km.
                    sleep(2)

                    # Tentando coletar os dados.
                    try:
                        # Formatando preço para se tornar um numero to tipo float.
                        valor = self.navegador.find_element(By.XPATH, '//h1[@class="price-label"]').text
                        numeros = float(valor.replace('R$ ', '').replace('.', '').replace(',', '.'))
                    except:
                        # Segunda tentativa de coletar o preço caso a primeira falhe.
                        sleep(5)
                        valor = self.navegador.find_element(By.XPATH, '//h1[@class="price-label"]').text
                        numeros = float(valor.replace('R$ ', '').replace('.', '').replace(',', '.'))
                    try:
                        # Coletando descrição de pagamento se ela existir.
                        desc = self.navegador.find_element(By.XPATH, '//h5[@class="price-observation"]').text
                    except:
                        # Caso não consiga coletar, o valor será NaN.
                        desc = np.nan

                    # Salvando data da coleta e todos os outros dados.
                    dados_carro['Data'] = datetime.now().strftime('%d/%m/%Y %H:%M')
                    # Caso o carro ja esteja no dataframe, somente será salvo os dados que não foram coletados.
                    if not self.dataframe.loc[(self.dataframe['Nome'] == dados_carro['Nome']) & (self.dataframe['Km'] == dados_carro['Km'])].empty:
                        self.dataframe.loc[(self.dataframe['Nome'] == dados_carro['Nome']) & (self.dataframe['Km'] == dados_carro['Km']), dados_carro['Mes']] = numeros
                        self.dataframe.loc[(self.dataframe['Nome'] == dados_carro['Nome']) & (self.dataframe['Km'] == dados_carro['Km']), 'Desc '+dados_carro['Mes']] = desc
                    else:
                        self.dataframe.loc[len(self.dataframe)] = {'Nome':dados_carro['Nome'], 'URL':dados_carro['URL'], 'Data':dados_carro['Data'],'Km':dados_carro['Km'], dados_carro['Mes']:numeros, 'Desc '+dados_carro['Mes']:desc}

                self.load_meses()  # Abrindo lista de opções de períodos.

            # Voltando para a página inicial.
            self.pagina_inicial()
            sleep(5)

        print(f'Coleta do site {self.url} finalizada')
        self.navegador.close()
        self.export_data()


    def export_data(self):
        """Exportando dados em um arquivo csv."""
        print('Exportando dados')
        self.dataframe.to_csv('dados_movida.csv', index=False)


if __name__ == '__main__':
    movida = Movida()