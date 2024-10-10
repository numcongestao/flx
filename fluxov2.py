import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Arquivo de backup
DATA_FILE = "fluxo_caixa.json"

# Controladores e senha
controladores = {"Felipe": "1234", "Iolanda": "1234", "Wanney": "1234", "Junior": "1234"}

# Função para carregar dados do arquivo JSON
def carregar_dados():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return {"dados": []}

# Função para salvar dados no arquivo JSON
def salvar_dados(dados):
    with open(DATA_FILE, "w") as f:
        json.dump(dados, f)

# Função para inserir novos registros
def inserir_dados(dados, data, tipo, descricao, forma_pagamento, valor, controlador):
    dados["dados"].append({
        "data_insercao": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "data": data,
        "tipo": tipo,
        "descricao": descricao,
        "forma_pagamento": forma_pagamento,
        "valor": valor,
        "controlador": controlador
    })
    salvar_dados(dados)

# Função para editar registros
def editar_dados(dados, index, data, tipo, descricao, forma_pagamento, valor):
    dados["dados"][index]["data"] = data
    dados["dados"][index]["tipo"] = tipo
    dados["dados"][index]["descricao"] = descricao
    dados["dados"][index]["forma_pagamento"] = forma_pagamento
    dados["dados"][index]["valor"] = valor
    salvar_dados(dados)

# Função para excluir registros
def excluir_dados(dados, index):
    del dados["dados"][index]
    salvar_dados(dados)

# Função para calcular totais
def calcular_totais(dados):
    total_entradas = sum(float(item['valor']) for item in dados['dados'] if item['tipo'] == 'Entrada')
    total_saidas = sum(float(item['valor']) for item in dados['dados'] if item['tipo'] == 'Saída')
    saldo_caixa_dinheiro = sum(float(item['valor']) for item in dados['dados'] if item['forma_pagamento'] == 'Dinheiro' and item['tipo'] == 'Entrada') - \
                            sum(float(item['valor']) for item in dados['dados'] if item['forma_pagamento'] == 'Dinheiro' and item['tipo'] == 'Saída')
    return total_entradas, total_saidas, saldo_caixa_dinheiro

# Função para autenticação
def autenticar_controlador(nome, senha):
    return nome in controladores and controladores[nome] == senha

# Carregar dados no início
dados = carregar_dados()

# Usar session_state para manter o estado de autenticação
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    # Tela de autenticação
    st.title("Gerenciamento de Fluxo de Caixa")
    nome_controlador = st.text_input("Nome do Controlador", key="nome_controlador")
    senha_controlador = st.text_input("Senha", type="password", key="senha_controlador")

    if st.button("Entrar", key="entrar_button"):
        if autenticar_controlador(nome_controlador, senha_controlador):
            st.success(f"Bem-vindo(a), {nome_controlador}!")
            st.session_state.autenticado = True
            st.session_state.controlador = nome_controlador  # Salvar o nome do controlador autenticado
            st.rerun()  # Reiniciar para refletir a autenticação imediatamente
        else:
            st.error("Controlador ou senha incorretos.")
else:
    # Se o usuário já está autenticado
    st.title(f"Bem-vindo(a), {st.session_state.controlador}!")

    # Exibir totais
    total_entradas, total_saidas, saldo_caixa_dinheiro = calcular_totais(dados)
    st.metric("Saldo Total (Dinheiro)", f"R$ {saldo_caixa_dinheiro:,.2f}")
    st.metric("Total de Entradas", f"R$ {total_entradas:,.2f}")
    st.metric("Total de Saídas", f"R$ {total_saidas:,.2f}")

    # Exibir tabela para seleção de item a ser editado ou excluído
    st.subheader("Gerenciar Transações")
    df = pd.DataFrame(dados["dados"])
    
    if not df.empty:
        # Mostrar a tabela com botões de ação
        st.dataframe(df, key="tabela_dados")

        # Selecionar uma transação pelo índice
        selected_index = st.number_input("Selecione o índice da transação", min_value=0, max_value=len(df)-1, step=1, key="select_index")

        if st.button("Excluir", key="excluir_button"):
            excluir_dados(dados, selected_index)
            st.success("Transação excluída com sucesso!")
            st.rerun()  # Recarregar a página para refletir a exclusão

        # Carregar os dados da transação selecionada para edição
        st.subheader("Editar Transação")
        data_edit = st.date_input("Data", value=datetime.strptime(df["data"][selected_index], "%d/%m/%Y"), key="data_edit")
        tipo_edit = st.selectbox("Tipo", ["Entrada", "Saída"], index=["Entrada", "Saída"].index(df["tipo"][selected_index]), key="tipo_edit")
        descricao_edit = st.text_input("Descrição", value=df["descricao"][selected_index], key="descricao_edit")
        forma_pagamento_edit = st.selectbox("Forma de Pagamento", ["Dinheiro", "Cartão", "Boleto", "PIX"], index=["Dinheiro", "Cartão", "Boleto", "PIX"].index(df["forma_pagamento"][selected_index]), key="forma_pagamento_edit")
        valor_edit = st.text_input("Valor (R$)", value=str(df["valor"][selected_index]), key="valor_edit")

        if st.button("Salvar Alterações", key="salvar_alteracoes_button"):
            try:
                valor_edit = float(valor_edit.replace(",", "."))
                editar_dados(dados, selected_index, data_edit.strftime("%d/%m/%Y"), tipo_edit, descricao_edit, forma_pagamento_edit, valor_edit)
                st.success("Transação editada com sucesso!")
                st.rerun()  # Recarregar para refletir as alterações
            except ValueError:
                st.error("Por favor, insira um valor numérico válido.")

    # Inserir novos dados
    st.subheader("Inserir nova transação")
    data = st.date_input("Data da Entrada/Saída", key="data_nova_transacao")
    tipo = st.selectbox("Tipo", ["Entrada", "Saída"], key="tipo_nova_transacao")
    descricao = st.text_input("Descrição", key="descricao_nova_transacao")
    forma_pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "Cartão", "Boleto", "PIX"], key="forma_pagamento_nova_transacao")
    valor = st.text_input("Valor (R$)", key="valor_nova_transacao")

    # Conversão do valor para float
    if st.button("Inserir", key="inserir_button"):
        try:
            valor = float(valor.replace(",", "."))
            inserir_dados(dados, data.strftime("%d/%m/%Y"), tipo, descricao, forma_pagamento, valor, st.session_state.controlador)
            st.success("Dados inseridos com sucesso!")
        except ValueError:
            st.error("Por favor, insira um valor numérico válido.")

    # Sidebar: Visualizar tabela e Download
    st.sidebar.header("Menu")
    if st.sidebar.button("Visualizar tabela completa", key="visualizar_tabela"):
        st.sidebar.write("Tabela completa dos dados")
        df = pd.DataFrame(dados["dados"])
        st.sidebar.dataframe(df, key="tabela_completa")

    if st.sidebar.button("Download dos dados", key="download_dados"):
        df = pd.DataFrame(dados["dados"])
        st.sidebar.download_button(label="Baixar CSV", data=df.to_csv(index=False), file_name="fluxo_caixa.csv", mime="text/csv")

    # Opção de sair
    if st.sidebar.button("Sair", key="sair_button"):
        st.session_state.autenticado = False
        st.session_state.controlador = None
        st.rerun()  # Reiniciar a aplicação para voltar à tela de login
