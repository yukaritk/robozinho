from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import logging
from utils.store_mapper import StoreMapper
from logic.open_driver import OpenDriver
from utils.helper_methods import HelperMethods
from logic.click_btnMenu import ClickBtnMenu
import time



class ReleaseAndListOrder:
    def __init__(self, driver):
        self.driver = driver
        self.sm = StoreMapper()
        self.hm = HelperMethods(self.driver)
        self.cb = ClickBtnMenu(self.driver)

    def select_pd(self, pd_number, id_parcial, dif_col):
        rows_tr = self.driver.find_elements(By.XPATH, f"//tbody[contains(@id, '{id_parcial}')]/tr")
        for tr in rows_tr:
            tds = tr.find_elements(By.TAG_NAME, "td")
            for index, td in enumerate(tds):
                if td.text.strip() == str(pd_number):
                    pd_select = tds[index + dif_col]
                    input_click = pd_select.find_element(By.TAG_NAME, "input")
                    input_click.click()
                    return
        raise Exception

    def liberar_faturamento(self):
        self.hm.carregando('Liberar para Faturamento')
        self.cb.select_btnMenu('Liberar para Faturamento','incCentral:incCentralVenda:formConteudo:btnPedLiberar')


    def accept_confirm(self):
        WebDriverWait(self.driver, 5).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert.accept()  # Clica em OK
        WebDriverWait(self.driver, 5).until_not(EC.alert_is_present())



    def select_operation(self, operation_number):
        self.hm.is_display_on(By.XPATH, "//*[@id='incCentral:incCentralVenda:frmmodalOperacao:selOpeCoOperacao']")
        
        select_element = self.driver.find_element(By.ID, "incCentral:incCentralVenda:frmmodalOperacao:selOpeCoOperacao")
        options = select_element.find_elements(By.TAG_NAME, "option")

        index = next((i for i, o in enumerate(options) if o.get_attribute("value") == str(operation_number)),None)

        if index is None:
            raise Exception(f"Operação {operation_number} não encontrada.")

        select_element.click()
        for _ in range(index):
            select_element.send_keys(Keys.ARROW_DOWN)
            time.sleep(0.1)
        select_element.send_keys(Keys.TAB)
        self.cb.select_btnMenu('Selecionar Operação', 'incCentralVenda:frmmodalOperacao')


    def _liberar (self, origem, pd_number):
        logging.info(f"Vendas>Pedido")
        self.cb.select_btnMenu('Vendas')
        self.cb.select_btnMenu('Pedido')
        self.hm.carregando('Pedidos')
        self.hm.select_cnpj_origem(origem, 'incCentral:incCentralVenda:formConteudo:formEmitente:selFiltroEmiCoCnpj')
        self.cb.select_btnMenu('Pesquisar', 'btnPedPesquisar')
        self.hm.carregando('pagCrudTitle')
        self.select_pd(pd_number, 'tblPrdBodyPesquisa', 5)
        self.liberar_faturamento()
        self.accept_confirm()
        logging.info(f"STATUS PD.{pd_number}-Liberado")
        

    def _listar(self, origem, operation, pd_number):
        logging.info(f"Vendas>Faturamento")
        self.cb.select_btnMenu('Vendas')
        self.cb.select_btnMenu('Faturamento')
        self.hm.carregando('Pedido de Venda Faturamento')
        self.hm.select_cnpj_origem(origem, 'incCentral:incCentralVenda:formConteudo:formEmitente:selFiltroEmiCoCnpj')
        self.cb.select_btnMenu('Pesquisar', 'btnPdfPesquisar')
        self.select_pd(pd_number, 'tblPrdBodyPesquisa', 7)
        self.accept_confirm()
        self.select_operation(operation)
        logging.info(f"STATUS PD.{pd_number}-Liberado-Listado")