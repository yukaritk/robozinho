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
import logging


class ClickBtnMenu:
    def __init__(self, driver):
        self.driver = driver
        
    def select_btnMenu(self, op, parent=None):
        if parent:
            scope = self.driver.find_element(By.XPATH, f"//*[contains(@id, '{parent}')]")
            botoes = scope.find_elements(By.CLASS_NAME, "btnMenu")
        else:
            botoes = self.driver.find_elements(By.CLASS_NAME, "btnMenu")

        for botao in botoes:
            if botao.is_displayed():
                if botao.get_attribute("value") == op:
                    botao.click()
                    time.sleep(1)
                    return
        raise Exception
    