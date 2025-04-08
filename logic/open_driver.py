from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class OpenDriver:
    def __init__(self):
        self.driver = None

    def carregar_credenciais(self):
        with open('credentials.txt', 'r') as file:
            lines = file.readlines()
            username = lines[0].strip()
            password = lines[1].strip()
        return username, password

    def obter_url(self, terminal):
        http_venda = "https://sumire-phd.homeip.net:8590/eVendas/home.faces"
        http_sistema = "https://sumire-phd.homeip.net:8590/SistemasPHD/"
        return http_venda if terminal == "vendas" else http_sistema

    def realizar_login(self, username, password):
        wait = WebDriverWait(self.driver, 10)
        user_name = wait.until(EC.presence_of_element_located((By.ID, "form-login")))
        user_password = wait.until(EC.presence_of_element_located((By.ID, "form-senha")))

        user_name.send_keys(username)
        user_password.send_keys(password)

        button_login = self.driver.find_element(By.ID, "form-submit")
        button_login.click()

    def open_driver(self, terminal):
        username, password = self.carregar_credenciais()
        url = self.obter_url(terminal)
        options = Options()
        options.add_argument("--headless")
        self.driver = webdriver.Chrome()
        self.driver.get(url)
        self.realizar_login(username, password)

        return self.driver

    def close_driver(self):
        if self.driver:
            self.driver.quit()

# Exemplo de uso
if __name__ == "__main__":
    navegador = OpenDriver()
    navegador.open_driver("vendas")