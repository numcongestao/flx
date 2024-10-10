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
    nome_controlador = st.text_input("Nome do Controlador")
    senha_controlador = st.text_input("Senha", type="password")

    if st.button("Entrar"):
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

    # Inserir novos dados
    st.subheader("Inserir nova transação")
    data = st.date_input("Data da Entrada/Saída")
    tipo = st.selectbox("Tipo", ["Entrada", "Saída"])
    descricao = st.text_input("Descrição")
    forma_pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "Cartão", "Boleto", "PIX"])
    valor = st.text_input("Valor (R$)")

    # Conversão do valor para float
    if st.button("Inserir"):
        try:
            valor = float(valor.replace(",", "."))
            inserir_dados(dados, data.strftime("%d/%m/%Y"), tipo, descricao, forma_pagamento, valor, st.session_state.controlador)
            st.success("Dados inseridos com sucesso!")
        except ValueError:
            st.error("Por favor, insira um valor numérico válido.")

    # Sidebar: Visualizar tabela e Download
    st.sidebar.header("Menu")
    if st.sidebar.button("Visualizar tabela completa"):
        st.sidebar.write("Tabela completa dos dados")
        df = pd.DataFrame(dados["dados"])
        st.sidebar.dataframe(df)

    if st.sidebar.button("Download dos dados"):
        df = pd.DataFrame(dados["dados"])
        st.sidebar.download_button(label="Baixar CSV", data=df.to_csv(index=False), file_name="fluxo_caixa.csv", mime="text/csv")

    # Opção de sair
    if st.sidebar.button("Sair"):
       st.session_state.autenticado = False
       st.session_state.controlador = None
       st.rerun()  # Reiniciar a aplicação para voltar à tela de login
