import os
import cv2
import numpy as np
import streamlit as st
from PIL import Image

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="PlantAI - Identificador Visual",
    page_icon="🌿",
    layout="wide",
)

# ============================================================
# BASE DE DADOS DAS PLANTAS
# ============================================================
PLANTAS_DB = {
    "Rosa-do-deserto": {
        "pasta": "imagens/rosa_do_deserto",
        "descricao": (
            "A rosa-do-deserto é uma planta ornamental conhecida pelo "
            "caule engrossado e pelas flores coloridas. É bastante "
            "cultivada em vasos e ambientes ensolarados."
        ),
        "caracteristicas": [
            "Caule suculento e estufado (cáudice)",
            "Flores tubulares em tons de rosa, vermelho, roxo ou branco",
            "Necessita de alta exposição solar e pouca rega",
        ],
    },
    "Ipê": {
        "pasta": "imagens/ipe",
        "descricao": (
            "O ipê é uma árvore símbolo do Brasil, famosa por sua florada "
            "intensa e exuberante que acontece principalmente no inverno e início da primavera."
        ),
        "caracteristicas": [
            "Perde totalmente as folhas antes de florir",
            "Flores em formato de sino (amarelas, rosas, brancas ou roxas)",
            "Porte arbóreo de médio a grande porte",
        ],
    },
    "Lírio": {
        "pasta": "imagens/lirio",
        "descricao": (
            "O lírio é uma planta bulbosa apreciada no mundo todo por suas "
            "flores grandes, perfumadas e com formato de trombeta."
        ),
        "caracteristicas": [
            "Flores grandes com 6 pétalas destacadas",
            "Estames proeminentes com bastante pólen",
            "Folhas dispostas de forma espiralada na haste",
        ],
    },
}

# ============================================================
# INTERFACE DO USUÁRIO (STREAMLIT)
# ============================================================
st.title("🌿 PlantAI - Identificador Visual")
st.markdown("Identificador visual de **Rosa-do-deserto**, **Ipê** e **Lírio**.")

st.sidebar.header("Menu de Opções")
opcao = st.sidebar.radio(
    "Escolha uma função:",
    ["Identificar por Imagem", "Consultar Catálogo"],
)

# ------------------------------------------------------------
# ABA 1: IDENTIFICAR POR IMAGEM
# ------------------------------------------------------------
if opcao == "Identificar por Imagem":
    st.subheader("Envie a foto da planta")
    
    arquivo_imagem = st.file_uploader(
        "Selecione uma imagem (JPG, JPEG, PNG)...", 
        type=["jpg", "jpeg", "png"]
    )

    if arquivo_imagem is not None:
        # Carregar e exibir a imagem enviada
        imagem = Image.open(arquivo_imagem)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(imagem, caption="Imagem Carregada", use_column_width=True)

        with col2:
            st.subheader("Resultado da Análise")
            
            # Seleção de simulação/classificação
            planta_detectada = st.selectbox(
                "Selecione a planta identificada no modelo:",
                list(PLANTAS_DB.keys())
            )
            
            dados = PLANTAS_DB[planta_detectada]
            
            st.success(f"**Planta Identificada:** {planta_detectada}")
            st.write(f"**Descrição:** {dados['descricao']}")
            
            st.markdown("**Características Principais:**")
            for carac in dados["caracteristicas"]:
                st.write(f"- {carac}")

# ------------------------------------------------------------
# ABA 2: CONSULTAR CATÁLOGO
# ------------------------------------------------------------
else:
    st.subheader("Catálogo de Plantas Suportadas")
    
    planta_selecionada = st.selectbox(
        "Escolha uma planta para ver mais detalhes:",
        list(PLANTAS_DB.keys())
    )
    
    detalhes = PLANTAS_DB[planta_selecionada]
    
    st.markdown(f"### {planta_selecionada}")
    st.write(detalhes["descricao"])
    
    st.markdown("**Características:**")
    for c in detalhes["caracteristicas"]
