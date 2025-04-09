import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
import os
from utils.store_mapper import StoreMapper
from logic.open_driver import OpenDriver
from utils.helper_methods import HelperMethods
import logging
from logic.release_listOrder import ReleaseAndListOrder
import uuid


# Configuração do log
logging.basicConfig(
    filename="log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

class TransferRequest:
    def __init__(self, caminho, type):
        self.type = type
        self.caminho = caminho
        self.driver = None  # Driver será atribuído dinamicamente
        self.hm = None
        self.rl = None


    def path_control(self):
        dir_name, file_name = os.path.split(self.caminho)
        base_name, ext = os.path.splitext(file_name)      
        control_file_name = f"{base_name}_CONTROLE{ext}"
        control_file_path = os.path.join(dir_name, control_file_name)
        return control_file_path


    def open_excel(self):
        store_mapper = StoreMapper()
        df = pd.read_excel(self.caminho, engine='openpyxl')
        df["Loja Origem"] = df["Loja Origem"].astype(str).map(store_mapper.dict_num_lojas).fillna(df["Loja Origem"])
        df["Loja Destino"] = df["Loja Destino"].astype(str).map(store_mapper.dict_num_lojas).fillna(df["Loja Destino"])
        
        if "ID" not in df.columns:
            input_uuid = [str(uuid.uuid4()) for _ in range(len(df))]
            df["ID"] = input_uuid
            df["ID"] = df.get("ID", input_uuid)
        df.to_excel(self.path_control(), index=False)
        return df

    
    def df_by_group(self):
        try:
            df = pd.read_excel(self.path_control())
        except:
            df = self.open_excel()
        df["Status"] = df["Status"].astype(str)
        df_filtrado = df[pd.isna(df["Status"]) | 
                        (df["Status"] == "nan") | 
                        (~df["Status"].str.contains("-Listado", na=False))]
        if df_filtrado.empty:
            
            return None
        grouped_dfs = df_filtrado.groupby(["Loja Origem", "Loja Destino", "Cond. Pagamento", "Operacao"])
        return grouped_dfs


    def update_status(self, row, info):
        df = pd.read_excel(self.path_control())
        mask = df["ID"] == row["ID"]
        df["Status"] = df["Status"].astype(str).replace('nan', '').fillna('')
        if mask.any():
            df.loc[mask, "Status"] = df.loc[mask, "Status"] + f"{info}"
            df.to_excel(self.path_control(), index=False)
            return True
        else:
            self.hm.notificar("STATUS ERRO", f"'{info}' não atualizado.")
            return False


    def select_mov_int(self):
        self.hm.carregando("opMovInterna")
        self.driver.find_element(By.ID, "opMovInterna").click()


    def select_type(self):
        self.hm.carregando("Leitura por Código de Barras")
        select_field = self.driver.find_element(By.ID, "incCentral:formConteudo:selPadraoLancamento")
        select = Select(select_field)
        select.select_by_visible_text(self.type)
        self.hm.wait_select_done(select)
        iniciar = self.driver.find_element(By.ID, 'incCentral:formConteudo:btnIniciar')
        iniciar.click()


    def import_item(self, lista):
        for row in lista:
            logging.info(row)
            quantite_field = self.driver.find_element(By.ID, 'incCentral:formConteudo:txtProduto')
            quantite_field.click()
            quantite_field.clear()
            quantite_field.send_keys(row)
            self.driver.find_element(By.ID, 'incCentral:formConteudo:btnAdicionar').click()
            self.hm.item_update()


    def click_cnpj_field(self, cnpj_destino):
        rows = self.hm.tbody_childrens_tr('incCentral:formPnlModalPesquisaParticipante:tblPsqInfoPtcControladoBody:tbody_element')
        for idx, row in enumerate(rows):
            cnpj_text = row.find_element(By.XPATH, ".//td[contains(@class, 'tblLinha')]").text
            if cnpj_destino in cnpj_text:
                botao_alterar = row.find_element(By.XPATH, ".//input[@type='image']")
                botao_alterar.click()
                return
        raise Exception
        

    def wait_select_destino(self, cnpj_destino):
        time_out = 5
        while time_out > 0:
            painel = self.driver.find_element(By.ID, "incCentral:formConteudo:selFiltroCliente")
            if cnpj_destino in painel.text:
                return
            time.sleep(0.5)
            time_out -= 0.5
        raise Exception


    def select_cnpj_destino(self, cnpj_destino):
        self.driver.find_element(By.ID, "incCentral:formConteudo:btnPesqCliente").click()
        self.hm.is_display_on('Pesquisa - Participante')
        cnpj = self.driver.find_element(By.ID, 'incCentral:formPnlModalPesquisaParticipante:txtPtcCoCnpjFiltro')
        cnpj.click()
        cnpj.send_keys(cnpj_destino)
        self.driver.find_element(By.ID, 'incCentral:formPnlModalPesquisaParticipante:btnPsqPtcControlado').click()
        self.click_cnpj_field(cnpj_destino)
        self.wait_select_destino(cnpj_destino)
        time.sleep(1)


    def select_payment_condition(self, value):
        select_element = self.driver.find_element(By.ID, "incCentral:formConteudo:selCondicaoPagto")
        select = Select(select_element)
        select.select_by_value(value)
        self.hm.wait_select_done(select)


    def finalizar_processo(self):
        self.driver.find_element(By.ID, 'incCentral:formConteudo:btnFinalizar').click()
        self.hm.carregando('okMessageGrande')
        

    def colect_pd_number(self):
        element = self.driver.find_element(By.XPATH, "//li[contains(@class, 'okMessageGrande')]")
        number = element.text.split(' ')[2]
        return number


    def update_status_order(self, group_df, sufixo, tag_error):
        for _, row in group_df.iterrows():
            if not self.update_status(row, sufixo):
                logging.error(tag_error)
                raise Exception
            
    def processo_inclusao_pedidos(self):
        open_driver = OpenDriver()
        self.driver = open_driver.open_driver("vendas")
        self.hm = HelperMethods(self.driver)
        self.rl = ReleaseAndListOrder(self.driver)
        grouped_dfs = self.df_by_group()
        if grouped_dfs is None:
            logging.info(f"Concluído: Sem Pedidos Novos\n\n")
            self.hm.notificar("Concluido", "Sem Pedidos Novos")
            self.driver.close()
            return

        for group_name, group_df in grouped_dfs:
            origem, destino, payment, operation = map(str, group_name)
            group_df['Qtd&Code'] = group_df['Quantidade'].astype(str) + "&" + group_df['Codigo'].astype(str)
            lista = group_df['Qtd&Code'].tolist()
            status = group_df.iloc[0]['Status']
            
            if pd.isna(status) or status == 'nan':
                logging.info(f"STATUS NaN")
                logging.info(f"Movimentacao Interna")
                logging.info(f"ORIGEM {StoreMapper().get_loja_by_cnpj(origem)}")
                logging.info(f"DESTINO {StoreMapper().get_loja_by_cnpj(destino)}")
                self.select_mov_int()
                self.select_type()
                self.hm.select_cnpj_origem(origem, 'incCentral:formConteudo:selEmiCoCnpj')
                self.import_item(lista)
                self.select_cnpj_destino(destino)
                self.select_payment_condition(payment)
                self.finalizar_processo()
                pd_number = self.colect_pd_number()
                logging.info(f"STATUS PD.{pd_number}")
                self.update_status_order(group_df, f"PD.{pd_number}", "Erro ao atualizar status inicial.")
               
                self.rl._liberar(origem, pd_number)
                self.update_status_order(group_df, "-Liberado", "Erro ao atualizar status durante o processo de liberação.")

                self.rl._listar(origem, operation, pd_number)
                self.update_status_order(group_df, "-Listado", "Erro ao atualizar status durante o processo de listagem.")
                    
            elif "PD." in status and "-Liberado" not in status:
                logging.info(f"Liberar Pedido")
                pd_number = status.split('.')[1]
                self.rl._liberar(origem, pd_number)
                self.update_status_order(group_df, "-Liberado", "Erro ao atualizar status durante o processo de liberação.")
                self.rl._listar(origem, operation, pd_number)
                self.update_status_order(group_df, "-Listado", "Erro ao atualizar status durante o processo de listagem.")
            elif "-Liberado" in status and "-Listado" not in status:
                logging.info(f"Listar Pedido")
                pd_number = status.split('.')[1].split('-')[0]
                self.rl._listar(origem, operation, pd_number)
                self.update_status_order(group_df, "-Listado", "Erro ao atualizar status durante o processo de listagem.")
                logging.info(f"Finalizado com sucesso.\n\n")
        self.hm.notificar("Concluído", "Pedidos Finalizados")
        self.driver.close()
    