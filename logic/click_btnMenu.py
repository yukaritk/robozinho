import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os
from utils.store_mapper import StoreMapper
from logic.open_driver import OpenDriver
from utils.helper_methods import HelperMethods
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import logging


class ClickBtnMenu:
    def __init__(self, driver):
        self.driver = driver

    def salvar_htmls(self):
        # Captura HTML antes
        html_inicio = self.driver.page_source
        time.sleep(5)
        # Captura HTML depois
        html_fim = self.driver.page_source

        # Deixa bonito com BeautifulSoup
        inicio = BeautifulSoup(html_inicio, "html.parser").prettify()
        fim = BeautifulSoup(html_fim, "html.parser").prettify()

        # Salva os arquivos na pasta atual
        with open("inicio.html", "w", encoding="utf-8") as f:
            f.write(inicio)

        with open("fim.html", "w", encoding="utf-8") as f:
            f.write(fim)

    def select_btnMenu(self, op, parent=None):
        scope = self.driver
        if parent:
            scope = self.driver.find_element(By.XPATH, f"//*[contains(@id, '{parent}')]")
        
        botoes = scope.find_elements(By.XPATH, ".//*[contains(@class, 'btn') or @type='button']")
        
        for i, botao in enumerate(botoes):
            try:
                visivel = botao.is_displayed()
                valor = botao.get_attribute("value")
                texto = botao.text

                # 🔍 Print de depuração
                print(f"[{i}] Botão - visível: {visivel}, value: '{valor}', texto: '{texto}'")

                if not visivel:
                    continue

                match = (valor and valor.strip() == op.strip()) or (texto and texto.strip() == op.strip())

                if match:
                    print(f"🔘 Cliquei no botão [{i}] com match: '{op}'")
                    botao.click()
                    time.sleep(1)
                    return
            except Exception as e:
                print(f"⚠️ Erro ao processar botão [{i}]: {e}")
                continue
        
        raise Exception(f"Nenhum botão com valor ou texto igual a '{op}' foi encontrado ou clicável.")
    