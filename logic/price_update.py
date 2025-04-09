from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from selenium.webdriver.common.keys import Keys
import os
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
from logic.open_driver import OpenDriver
from utils.helper_methods import HelperMethods
from utils.store_mapper import StoreMapper
from logic.click_btnMenu import ClickBtnMenu
import logging
import uuid
from bs4 import BeautifulSoup


# Configuração do log
logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class PriceUpdate:
    def __init__(self, caminho):
        self.caminho = caminho
        self.driver = None  # Driver será atribuído dinamicamente
        self.hm = None
        self.rl = None
        self.cb = None
        self.sm = None
        self.first_run = None


    def novo_nome_csv(self):
        dir_name, file_name = os.path.split(self.caminho)
        base_name, ext = os.path.splitext(file_name)
        csv_file_name = f"{base_name}_alteracao_preco_parcial.csv"
        return os.path.join(dir_name, csv_file_name)

    def xml_csv(self):
        df = pd.read_excel(self.caminho, engine='openpyxl')
        df['Tipo do Codigo'] = df['Tipo do Codigo'].str.lower()

        try:
            df['Vl. Custo'] = df['Vl. Custo'].astype(str).str.replace(',', '.').astype(float)
        except:
            pass
        try:
            df['Vl. Revenda'] = df['Vl. Revenda'].astype(str).str.replace(',', '.').astype(float)
        except:
            pass
        try:
            df['Data inicio'] = pd.to_datetime(df['Data inicio'], errors='coerce')
            df['Data inicio'] = df['Data inicio'].dt.strftime('%d/%m/%Y')
        except:
            pass

        df.to_csv(self.novo_nome_csv(), sep=";", index=False)
        return df

    def arquivo_final(self):
        old_file_path = self.novo_nome_csv()
        dir_name, file_name = os.path.split(old_file_path)
        new_file_name = file_name.replace('parcial', 'final')
        new_file_path = os.path.join(dir_name, new_file_name)
        os.rename(old_file_path, new_file_path)

    def select_price_alt(self):
        self.hm.carregando('opCadastros')
        self.driver.find_element(By.ID, "opCadastros").click()
        self.hm.carregando('Preços')
        self.hm.is_display_on(By.CSS_SELECTOR, "input[value='Preços']")
        self.driver.find_element(By.CSS_SELECTOR, "input[value='Preços']").click()
        self.hm.carregando('Manut. Custo Prod.')
        self.hm.is_display_on(By.CSS_SELECTOR, "input[value='Manut. Custo Prod.']")
        self.driver.find_element(By.CSS_SELECTOR, "input[value='Manut. Custo Prod.']").click()

    def click_element(self, elemento):
        timeout = 5
        while timeout > 0:
            html = self.driver.page_source
            if elemento in html:
                soup = BeautifulSoup(html, 'html.parser')
                for tag in soup.find_all(True):
                    attrs = tag.attrs
                    if any(elemento in str(v) for v in attrs.values()):
                        for attr_name, attr_val in attrs.items():
                            if elemento in str(attr_val):
                                if isinstance(attr_val, list):
                                    partes = attr_val
                                else:
                                    partes = str(attr_val).split()
                                valor = max(partes, key=len)
                                xpath = f"//*[contains(@{attr_name}, '{valor}')]"
                                try:
                                    element_click = self.driver.find_element(By.XPATH, xpath)
                                    element_click.click()
                                    return element_click
                                except:
                                    return xpath
            else:
                time.sleep(0.5)
                timeout -= 0.5
        raise Exception

    def inclusao_data_inicio(self, data):
        field_data = self.click_element('hasDatepicker')
        self.driver.execute_script("""
            const campo = arguments[0];
            campo.value = '';
            campo.value = arguments[1];
            campo.dispatchEvent(new Event('input', { bubbles: true }));
            campo.dispatchEvent(new Event('change', { bubbles: true }));
        """, field_data, data)

    def wait_option(self, select_element, timeout=3):
        select = Select(select_element)
        elapsed = 0
        while len(select.options) == 0:
            if elapsed >= timeout:
                raise Exception
            time.sleep(0.5)
            elapsed += 0.5
            select = Select(select_element)
        return select
    
    def seleciona_loja(self, loja):
        container = "incCentral:incCentralDiversos:incCentralDiversos:formConteudo:pnlBasePrecoVendaAdd"
        self.hm.is_display_on(By.ID, container)
        select_container = self.driver.find_element(By.ID, container)
        select_element = select_container.find_element(By.TAG_NAME, "select")
        select = self.wait_option(select_element)
        for opt in select.options:
            text = opt.text.strip()
            value = opt.get_attribute("value")
            match = re.search(r"\[(\d+)\]", text)
            if match:
                cod_loja = match.group(1)
                if cod_loja == loja:
                    select.select_by_value(value)
                    self.hm.wait_select_done(select)
                    logging.info(f"{text} ALTERADO")
                    return True
        logging.info(f"{loja} não encontrada nas opções.")
        self.hm.notificar('Erro', f'{loja} não encontrada.')
        return False
        
    def selecionar_produto(self, type_code, code):
        self.abre_pesquisa_produto()
        retorno = self.search_code(type_code, code)
        if retorno == 'OK':
            self.selecionar_code(code)
            return
        else:
            return f'ERRO-{retorno}'
        
        
    def selecionar_grupo(self, type_code, code):
        self.abre_pesquisa_grupo()
        retorno = self.search_code(type_code, code)
        if retorno == 'OK':
            self.selecionar_code(code)
            return
        else:
            return f'ERRO-{retorno}'
        
    def abre_pesquisa_grupo(self):
        self.cb.select_btnMenu('Sel. o Grupo Preço')
        self.hm.is_display_on(By.ID, 'incCentral:incCentralDiversos:incCentralDiversos:pnlPsqGrupoPrecoCDiv')

    def abre_pesquisa_produto(self):
        self.cb.select_btnMenu('Selecionar o Produto')
        self.hm.is_display_on(By.ID, 'incCentral:incCentralDiversos:incCentralDiversos:pnlPsqProdutoCDiv')

    def btn_pesquisar(self, type_code):
        if type_code.lower() == 'produto':
            container_id = 'incCentral:incCentralDiversos:incCentralDiversos:pnlPsqProdutoCDiv'
        else:
            container_id = 'incCentral:incCentralDiversos:incCentralDiversos:pnlPsqGrupoPrecoCDiv'
        self.cb.select_btnMenu('Pesquisar', container_id)

    def select_tblLinha(self, info):
        linhas = self.driver.find_elements(By.CSS_SELECTOR, ".tblLinha")
        for i in range(len(linhas)):
            texto = linhas[i].text.strip()
            if info in texto:
                proxima_linha = linhas[i + 1]
                input_element = proxima_linha.find_element(By.TAG_NAME, "input")
                input_element.click()

    def shift_value(self, id, value):
        field = self.driver.find_element(By.ID, id)
        field.click()
        field.clear()
        field.send_keys(value)
        field.send_keys(Keys.TAB)

    def shift_all_price(self, type_code, vl_custo, vl_revenda):
        if type_code.lower() == 'produto':
            id_custo = 'incCentral:incCentralDiversos:incCentralDiversos:formConteudo:txtPvdVlCustoReposicao'
            id_revenda = 'incCentral:incCentralDiversos:incCentralDiversos:formConteudo:txtPvdVlVendaRevenda'     
        else:
            id_custo = 'incCentral:incCentralDiversos:incCentralDiversos:formConteudo:txtGpvVlCustoReposicao'
            id_revenda = 'incCentral:incCentralDiversos:incCentralDiversos:formConteudo:txtGpvVlVendaRevenda'      
        self.shift_value(id_custo, vl_custo)
        self.shift_value(id_revenda, vl_revenda)
        self.cb.select_btnMenu('Salvar')


    def inclusao_preco(self, type_code, vl_custo, vl_revenda):
        self.shift_all_price(type_code, vl_custo, vl_revenda)
        if self.hm.carregando('okMessage'):
            return True
        else:
            return False

    def search_code(self, type_code, code):
        if type_code.lower() == 'produto':
            input_id = 'incCentral:incCentralDiversos:incCentralDiversos:formPnlModalPesquisaPrd:txtPrdCoProdutoFiltro'
        else:
            input_id = 'incCentral:incCentralDiversos:incCentralDiversos:formPnlModalPesquisaGpr:txtGrpCoGrupoFiltro'
        input_element = self.driver.find_element(By.ID, input_id)
        input_element.clear()
        input_element.send_keys(code)
        self.btn_pesquisar(type_code)
        self.update_status(type_code)
        return self.status_time(type_code)
    
    def selecionar_code(self, code):
        self.select_tblLinha(code)
        self.hm.carregando('Salvar')


    def update_status(self, type_code):
        first_txt = self.status_time(type_code)
        start_time = time.time()
        while (time.time() - start_time) <= 7:
            second_txt = self.status_time(type_code)
            if first_txt != second_txt:
                return
            time.sleep(1)
        raise Exception


    def text_class(self, class_name, type_code):
        if type_code.lower() == 'produto':
            container_id = 'incCentral:incCentralDiversos:incCentralDiversos:pnlPsqProdutoCDiv'
        else:
            container_id = 'incCentral:incCentralDiversos:incCentralDiversos:pnlPsqGrupoPrecoCDiv'
        container = self.driver.find_element(By.ID, container_id)
        div_element = container.find_element(By.CLASS_NAME, class_name)
        return div_element.text.strip()

    def fechar_modal(self, type_code):
        if type_code.lower() == 'produto':
            container_id = 'incCentral:incCentralDiversos:incCentralDiversos:pnlPsqProdutoCDiv'
        else:
            container_id = 'incCentral:incCentralDiversos:incCentralDiversos:pnlPsqGrupoPrecoCDiv'

        container = self.driver.find_element(By.ID, container_id)
        close_btn = container.find_element(By.CLASS_NAME, "hidelink")
        close_btn.click()
    
    def tag_in_class(self, class_name, tag_name):
        try:
            div = self.driver.find_element(By.CLASS_NAME, class_name)
            rows_tr = div.find_elements(By.TAG_NAME, tag_name)
            for row in rows_tr:
                if row.text.strip():
                    return True
            return False
        except Exception:
            return False
    
    def status_time(self, type_code):
        txt = self.text_class('errorMessageGlobal', type_code)
        if txt:
            return 'firstRun' if self.first_run is True else txt
        txt = self.text_class('divNenhumaLinha', type_code)
        if txt:
            return 'divNenhuma'
        txt = self.text_class('pagAlinhamento', type_code)
        if txt:
            return 'OK'
        return None

    def update_df_status(self, row, info):
        df = pd.read_csv(self.novo_nome_csv(), sep=";")
        mask = df["ID"] == row["ID"]
        df["Status"] = df["Status"].astype(str).replace('nan', '').fillna('')
        if mask.any():
            df.loc[mask, "Status"] = info
            df.to_csv(self.novo_nome_csv(), sep=';', index=False)
            return True
        else:
            self.hm.notificar("STATUS ERRO", f"'{info}' não atualizado.")
            return False
        
    def analisar_linha(self, df):
        open_driver = OpenDriver()
        self.driver = open_driver.open_driver("vendas")  # O driver é iniciado aqui
        self.hm = HelperMethods(self.driver)
        self.cb = ClickBtnMenu(self.driver)
        self.sm = StoreMapper()
        self.select_price_alt()
        logging.info(f"Manutencao de Preco")

        for idx, row in df.iterrows():
            data = row['Data inicio']
            status = str(row['Status'])
            codigo = row['Produto/Grupo']
            lojas_total = row['Loja/Grupo']
            lojas = str(lojas_total).split(',')
            tipo = row['Tipo do Codigo']
            vl_custo = row['Vl. Custo']
            vl_revenda = row['Vl. Revenda']

            if status.startswith("OK") or status.startswith("ERRO"):
                continue

            elif status.startswith("PARCIAL"):
                lojas_analisadas = status.split('-')[-1].split(',')
                lojas_pendentes = [loja for loja in lojas if loja not in lojas_analisadas]
                analisadas = status
                if len(lojas_pendentes) == 0:
                    self.update_df_status(row, 'OK')
                    continue
            else:
                lojas_pendentes = lojas
                analisadas = "PARCIAL-"
            self.inclusao_data_inicio(data)
            logging.info(f"Data Inicio {data}")

            for loja in lojas_pendentes:
                bool_loja = self.seleciona_loja(loja)
                if bool_loja is False:
                    analisadas_parcial = analisadas.split("-")[0] + f" Loja {loja} nao localizada."
                    logging.info(f"Loja Nao Localizada: {loja}")
                    if analisadas.split("-")[-1]:
                        analisadas = analisadas_parcial + "-" + analisadas.split("-")[-1]
                    else:
                        analisadas = analisadas_parcial + "-"
                    self.update_df_status(row, analisadas)
                    continue
                else:
                    if tipo == 'produto':
                        logging.info(f"Produto: {codigo}")
                        self.first_run = True
                        mensagem = self.selecionar_produto(tipo, codigo)
                    else:
                        logging.info(f"Grupo: {codigo}")
                        self.first_run = True
                        mensagem = self.selecionar_grupo(tipo, codigo)
                    if mensagem.startswith("ERRO"):
                        self.update_df_status(row, mensagem)
                        logging.info(f"Codigo Nao Localizado: {codigo}")
                        break
                    else:
                        logging.info(f"PRECO CUSTO: {vl_custo}")
                        logging.info(f"PRECO REVENDA: {vl_revenda}")
                        bool_conclude = self.inclusao_preco(tipo, codigo, vl_custo, vl_revenda)
                        if bool_conclude is False:
                            logging.info(f"ERRO NA INCLUSAO DE PRECO")
                            self.update_df_status(row, 'CHECK CODE')
                            continue
                        else:
                            if analisadas.split("-")[-1]:
                                analisadas = analisadas + "," + loja
                            else:
                                analisadas = analisadas + loja
                            self.update_df_status(row, analisadas)
                            logging.info(f"ALTERACAO REALIZADA")
                            logging.info("")
                            logging.info("")

            new_status = analisadas.split("-")[-1]
            if lojas_total == new_status:
                self.update_df_status(row, 'OK')

    def analisar_planilha(self):
        try:
            df = pd.read_csv(self.novo_nome_csv(), sep=";")
        except Exception:
            df = self.xml_csv()
        if 'ID' not in df.columns:
            df['ID'] = [str(uuid.uuid4()) for _ in range(len(df))]
            df.to_csv(self.novo_nome_csv(), sep=";", index=False)

        # tentativas = 0
        # while tentativas <= 10:
        #     try:
                # Verificar se há algum status "PARCIAL" ou em branco
        if df['Status'].isnull().any() or any(df['Status'].str.startswith("PARCIAL")):
            # Rodar a função para continuar o processamento
            self.analisar_linha(df)
            # Após finalizar analisar_linha, rodar arquivo_final e notificar sucesso
            self.arquivo_final()
            self.hm.notificar("Concluído", "Alteração de preço concluída")

        else:
            # Se todos os status forem "OK" ou "ERRO", rodar arquivo_final
            self.arquivo_final()
            self.hm.notificar("Concluído", "Alteração de preço concluída")

    # except Exception as e:
    #     # Em caso de erro, notificar falha
    #     self.hm.notificar('Erro', 'Falha na Alteração de preço.')
    #     print(f"Erro durante o processamento: {e}")
    #         # tentativas += 1
            
