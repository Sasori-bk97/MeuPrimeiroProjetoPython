import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.write("# Sistema de Vendas")

NOME_ARQUIVO = "vendas.csv"

# 1. Carrega ou cria a tabela inicial de forma segura
if os.path.exists(NOME_ARQUIVO):
    tabela = pd.read_csv(NOME_ARQUIVO)
else:
    tabela = pd.DataFrame(columns=["data", "vendedor", "produto", "quantidade", "valor"])

# Garantir tipos numéricos para evitar erros no Dashboard
if not tabela.empty:
    tabela["quantidade"] = pd.to_numeric(tabela["quantidade"], errors="coerce").fillna(0)
    tabela["valor"] = pd.to_numeric(tabela["valor"], errors="coerce").fillna(0.0)

# 2. Secção de Cadastrar Vendas
st.sidebar.write("## Cadastra vendas")
data = st.sidebar.date_input("Data")
vendedor = st.sidebar.text_input("Nome do Vendedor")
produto = st.sidebar.selectbox("Produto", ["Notebook", "Celular", "Fone"])
quantidade = st.sidebar.number_input("Quantidade", min_value=1, step=1)
valor = st.sidebar.number_input("Valor", min_value=0.0)
botao = st.sidebar.button("Cadastrar Venda")

if botao:
    nova_venda = [data, vendedor, produto, quantidade, valor]
    tabela.loc[len(tabela)] = nova_venda
    tabela.to_csv(NOME_ARQUIVO, index=False)
    st.sidebar.success("Venda Cadastrada!")
    st.rerun()

# 3. Secção de Excluir Venda
st.sidebar.write("## Excluir Venda")
data_exc = st.sidebar.date_input("Data", key="data.exc")
vendedor_exc = st.sidebar.text_input("Nome do Vendedor", key="Vendedor")
produto_exc = st.sidebar.selectbox("Produto", ["Notebook", "Celular", "Fone"], key="Produto")
quantidade_exc = st.sidebar.number_input("Quantidade", step=1, key="Quantidade")
valor_exc = st.sidebar.number_input("Valor", key="Valor")
botao1 = st.sidebar.button("Excluir")

if botao1:
    if not tabela.empty:
        # Converter tudo para texto de forma limpa antes de comparar
        data_sel = str(data_exc)
        vendedor_sel = str(vendedor_exc).strip().lower()
        produto_sel = str(produto_exc).strip().lower()
        qtd_sel = int(quantidade_exc)
        valor_sel = float(valor_exc)

        # Filtro com tolerância a formatação
        condicao = (
            (tabela["data"].astype(str) == data_sel) &
            (tabela["vendedor"].astype(str).str.strip().str.lower() == vendedor_sel) &
            (tabela["produto"].astype(str).str.strip().str.lower() == produto_sel) &
            (pd.to_numeric(tabela["quantidade"], errors="coerce").fillna(0).astype(int) == qtd_sel) &
            (pd.to_numeric(tabela["valor"], errors="coerce").fillna(0.0).round(2) == round(valor_sel, 2))
        )
        
        vendas_encontradas = tabela[condicao]
        
        if not vendas_encontradas.empty:
            # Apaga a primeira ocorrência encontrada
            indice_para_remover = vendas_encontradas.index[0]
            tabela = tabela.drop(indice_para_remover)
            tabela.to_csv(NOME_ARQUIVO, index=False)
            st.sidebar.success("Venda excluída com sucesso!")
            st.rerun()
        else:
            st.sidebar.error("Nenhuma venda encontrada com estes dados exatos!")
    else:
        st.sidebar.warning("A tabela está vazia!")

# 4. Exibição da Tabela
st.write("## Vendas Cadastradas")
st.dataframe(tabela)

# 5. Dashboard (Métricas e Gráfico)
st.write("## Dashboard")

if not tabela.empty:
    soma = tabela["valor"].sum()
    st.metric("Faturamento total", f"R$ {soma:,.2f}".replace(",", "v").replace(".", ",").replace("v", "."))

    grafico = px.bar(tabela, x="vendedor", y="valor", color="produto")
    st.plotly_chart(grafico)
    
    grafico = px.pie(tabela, names = "produto",values = "valor")
    st.plotly_chart(grafico)
    
else:
    st.metric("Faturamento total", "R$ 0,00")
    st.info("Cadastre uma venda para exibir o gráfico.")