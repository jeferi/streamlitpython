import streamlit as st
import pandas as pd
import yfinance as yf
import time

# Função para obter o preço real de um ativo
def obter_preco_ativo(ativo):
    try:
        dados = yf.Ticker(ativo).history(period="1d")
        preco = dados['Close'].iloc[-1]  # Preço de fechamento do último dia
        return preco
    except Exception as e:
        st.error(f"Erro ao obter o preço do ativo {ativo}. Detalhes do erro: {e}")
        return None

# Função para salvar a operação
def salvar_operacao(ativo1, ativo2, limite_superior, limite_inferior):
    if 'operacoes' not in st.session_state:
        st.session_state.operacoes = []  # Inicializa 'operacoes' se não existir

    st.session_state.operacoes.append({
        'Ativo 1': ativo1,
        'Ativo 2': ativo2,
        'Limite Superior': limite_superior,
        'Limite Inferior': limite_inferior,
        'Diferença': None,  # Inicializa a diferença como None
        'Limite Atingido': ""  # Inicializa a coluna "Limite Atingido" vazia
    })

# Interface do usuário
st.markdown("<h1 style='text-align: center; font-size: 40px;'>Simulador de Comparação de Ativos</h1>", unsafe_allow_html=True)

# Inicializar os valores no session_state antes de criar os widgets
if 'ativo1' not in st.session_state:
    st.session_state.ativo1 = "------"
if 'ativo2' not in st.session_state:
    st.session_state.ativo2 = "------"
if 'limite_superior' not in st.session_state:
    st.session_state.limite_superior = 0.00
if 'limite_inferior' not in st.session_state:
    st.session_state.limite_inferior = 0.00

# Criação de uma linha de colunas para os campos lado a lado
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

# Ativos válidos (sem o ".SA" na lista)
ativos_validos = ["PETR4", "ELET3", "BBDC4", "BBDC3", "VALE3", "SANB11",
    "ITUB4", "ITUB3", "CPLE3", "CPLE6", "CMIG3", "CMIG4", "BRAV3",
    "PRIO3", "BBSE3", "BBAS3", "TAEE11", "PSSA3", "ELET6", "PETR3"
]

# Entradas de ativos com selectbox (exibindo apenas o nome do ativo sem ".SA")
with col1:
    ativo1 = st.selectbox("Ativo 1", ["------"] + ativos_validos, key="ativo1")
    
with col2:
    ativo2 = st.selectbox("Ativo 2", ["------"] + ativos_validos, key="ativo2")

# Entradas de limites
with col3:
    limite_superior = st.number_input("Limite Superior", min_value=-100.0, max_value=100.0, value=0.00, key="limite_superior")
    
with col4:
    limite_inferior = st.number_input("Limite Inferior", min_value=-100.0, max_value=100.0, value=0.00, key="limite_inferior")

# Criação dos espaços para mensagens temporárias
mensagem_erro = st.empty()
mensagem_sucesso = st.empty()

# Colocando o botão "Iniciar Operação" abaixo dos selects
if st.button("Iniciar Operação"):
    # Verifica se os ativos foram escolhidos corretamente
    if ativo1 == "------" or ativo2 == "------":
        # Exibe a mensagem de erro por 2 segundos
        mensagem_erro.error("Por favor, selecione dois ativos válidos!")
        time.sleep(2)
        mensagem_erro.empty()
    elif ativo1 == ativo2:
        # Exibe a mensagem de erro por 3 segundos
        mensagem_erro.error("Os ativos selecionados não podem ser iguais!")
        time.sleep(3)
        mensagem_erro.empty()
    else:
        # Adicionando ".SA" automaticamente aos ativos para consulta
        ativo1_completo = ativo1 + ".SA"
        ativo2_completo = ativo2 + ".SA"
        
        # Salvar operação
        salvar_operacao(ativo1_completo, ativo2_completo, limite_superior, limite_inferior)
        
        # Exibe a mensagem de sucesso por 2 segundos
        mensagem_sucesso.success(f"Operação iniciada para {ativo1_completo} e {ativo2_completo}!")
        time.sleep(2)
        mensagem_sucesso.empty()

# Função para monitorar as operações
def monitorar_operacoes():
    alertas = []  # Para armazenar os alertas a serem exibidos

    # Verificando a inicialização de 'operacoes'
    if 'operacoes' not in st.session_state:
        st.session_state.operacoes = []  # Inicializando a chave 'operacoes'

    for operacao in st.session_state.operacoes:
        ativo1, ativo2 = operacao['Ativo 1'], operacao['Ativo 2']
        limite_superior, limite_inferior = operacao['Limite Superior'], operacao['Limite Inferior']

        # Obter preços reais dos ativos (sem ".SA" na entrada)
        preco_ativo1 = obter_preco_ativo(ativo1)
        preco_ativo2 = obter_preco_ativo(ativo2)

        if preco_ativo1 is None or preco_ativo2 is None:
            continue  # Se não conseguir obter o preço de algum ativo, continua para a próxima operação

        # Calcular a diferença
        diferenca = preco_ativo1 - preco_ativo2
        operacao['Diferença'] = diferenca  # Atualizar a diferença

        # Lógica para disparar alertas e atualizar "Limite Atingido"
        limite_atingido = ""
        if diferenca >= limite_superior:
            alertas.append(f"🟢 Alerta! A diferença de {ativo1} e {ativo2} ultrapassou o limite superior: {diferenca:.2f}")
            limite_atingido = "Limite Superior Atingido"
        elif diferenca >= limite_inferior:
            alertas.append(f"🟢 Alerta! A diferença de {ativo1} e {ativo2} ultrapassou o limite inferior: {diferenca:.2f}")
            limite_atingido = "Limite Inferior Atingido"

        # Atualizar a coluna "Limite Atingido"
        operacao['Limite Atingido'] = limite_atingido
    
    return alertas

# Monitorando as operações
alertas = monitorar_operacoes()

# Exibindo as operações em uma tabela
st.subheader("Operações Realizadas")

# Exibindo a tabela de operações
if st.session_state.operacoes:
    operacoes_display = [
        {
            'Ativo': f"{operacao['Ativo 1'].replace('.SA', '')} - {operacao['Ativo 2'].replace('.SA', '')}",
            'Diferença': f"{operacao['Diferença']:.2f}",
            'Limite Atingido': operacao['Limite Atingido'],  # Nova coluna
        }
        for operacao in st.session_state.operacoes
    ]
    
    # Exibindo a tabela com maior largura
    st.markdown("""<style>.streamlit-table { width: 100% !important; }</style>""", unsafe_allow_html=True)

    df_operacoes = pd.DataFrame(operacoes_display)
    st.dataframe(df_operacoes, use_container_width=True)

# Exibindo os alertas abaixo da tabela
if alertas:
    for alerta in alertas:
        st.warning(alerta)
