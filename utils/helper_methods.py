import time
from plyer import notification
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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

    def carregando(self, text):
        time_out = 10
        while time_out > 0:
            html = self.driver.page_source
            if text in html:
                return True
            else:
                time.sleep(0.5)
                time_out -= 0.5
        raise Exception

    def is_display_on(self, by_type, value, timeout=10):
        print(f"[is_display_on] Esperando exibição de elemento: {value}")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((by_type, value))
            )
            print(f"[is_display_on] Elemento visível: {value}")
            return True
        except Exception as e:
            print(f"[is_display_on] ERRO ao esperar elemento: {value} — {e}")
            return False
    
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
    
    def wait_select_done(self, select, expected_value):
        time_out = 5
        while time_out > 0:
            try:
                selected_option = select.first_selected_option
                current_value = selected_option.get_attribute("value")
                if current_value == expected_value:
                    return
            except Exception as e:
                # Em caso de transição de DOM ou recarregamento leve
                pass
            time.sleep(0.5)
            time_out -= 0.5
        raise Exception
    
    def select_cnpj_origem(self, cnpj_origem, task):
        self.carregando(task)
        cnpj_origem = str(cnpj_origem)
        select_cnpj = self.driver.find_element(By.XPATH, f".//option[contains(@value, '{cnpj_origem}')]")
        select_cnpj.click()