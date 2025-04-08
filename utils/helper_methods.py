import time
from plyer import notification
from selenium.webdriver.common.by import By

class HelperMethods:
    def __init__(self, driver):
        self.driver = driver

    def notificar(self, titulo, mensagem):
        notification.notify(
            title=titulo,
            message=mensagem,
            app_name="Robozinho",
            timeout=6  # Tempo em segundos que a notificação ficará visível
        )

    def carregando(self, id_html):
        time_out = 10
        while time_out > 0:
            html = self.driver.page_source
            if id_html in html:
                return
            time.sleep(0.5)
            time_out -= 0.5
        raise Exception

    def is_display_on(self, by_type, contem):
        time_out = 10
        while time_out > 0:
            elemento = self.driver.find_element(by_type, contem)
            if elemento.is_displayed():
                return
            time.sleep(0.5)
            time_out -= 0.5
        raise Exception
    
    def item_update(self):
        elemento_itens = self.driver.find_element(By.XPATH, "//span[contains(., 'ITENS:')]")
        first_item = elemento_itens.text
        print(f'first_elemnt {first_item}')
        time_out = 15
        while time_out > 0 :
            elemento_itens = self.driver.find_element(By.XPATH, "//span[contains(., 'ITENS:')]")
            second_item = elemento_itens.text
            if first_item != second_item:
                print(f'second_elemnt {second_item}')
                return
            time_out -= 1
            time.sleep(1)
        raise Exception
    

    def tbody_childrens_tr(self, tbody_id):
        time_out = 5
        while time_out > 0:
            linhas = self.driver.find_elements(By.XPATH, f"//tbody[@id='{tbody_id}']/tr")
            linhas_validas = [linha for linha in linhas if linha.get_attribute("class")]
            if linhas_validas:
                return linhas_validas
            time.sleep(0.5)
            time_out -= 0.5
        raise Exception
    
    def wait_select_done(self, select):
        time_out = 5
        while time_out > 0:
            selected_option = select.first_selected_option
            if selected_option.is_selected():
                return
            time.sleep(0.5)
            time_out -= 0.5
        raise Exception
    
    def select_cnpj_origem(self, cnpj_origem, task):
        self.carregando(task)
        cnpj_origem = str(cnpj_origem)
        select_cnpj = self.driver.find_element(By.XPATH, f".//option[contains(@value, '{cnpj_origem}')]")
        select_cnpj.click()