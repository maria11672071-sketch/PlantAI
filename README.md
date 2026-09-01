# PlantAI

Identificador visual de Rosa do deserto, Ypê e Lírio.

## Executar
```bash
pip install -r requirements.txt
streamlot run app.py
```

## Publicar
Envie os arquivos para um repositório GitHub e publique `app.py` no Streamlit Community Cloud.
import streamlit as st
import os
import numpy as np
from PIL import Image
import cv2

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Identificador de Plantas",
    page_icon="🌱",
    layout="wide"
)

# ============================================================
# ESTILO
# ============================================================

st.markdown("""
<style>

.main {
    background-color: #f5fff5;
}

.titulo {
    text-align: center;
    font-size: 42px;
    font-weight: bold;
    color: #176b32;
}

.subtitulo {
    text-align: center;
    font-size: 20px;
    color: #444444;
}

.caixa {
    padding: 20px;
    border-radius: 15px;
    background-color: #ffffff;
    border: 1px solid #dddddd;
    margin-bottom: 20px;
}

.resultado {
    padding: 20px;
    border-radius: 15px;
    background-color: #e9f8eb;
    border: 2px solid #4caf50;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# TÍTULO
# ============================================================

st.markdown(
    '<div class="titulo">🌱 Identificador de Plantas</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitulo">'
    'Identifique e classifique plantas através de imagens'
    '</div>',
    unsafe_allow_html=True
)

st.write("")

st.info(
    "O sistema foi desenvolvido para reconhecer três categorias: "
    "**Lírio, Ypê e Rosa-do-deserto**."
)

# ============================================================
# DADOS DAS PLANTAS
# ============================================================

plantas = {

    "Lírio": {
        "pasta": "imagens/lirio",
        "descricao": (
            "O lírio é uma planta ornamental conhecida por suas flores "
            "grandes e vistosas. Suas flores podem apresentar diversas "
            "cores, como branco, rosa, vermelho, amarelo e laranja."
        ),
        "caracteristicas": [
            "Flores grandes e vistosas",
            "Pétalas geralmente alongadas",
            "Possui estames bem visíveis",
            "Pode apresentar várias cores"
        ],
        "cores": ["Branco", "Rosa", "Vermelho", "Amarelo", "Laranja"]
    },

    "Ypê": {
        "pasta": "imagens/ype",
        "descricao": (
            "O Ypê é uma árvore muito conhecida no Brasil. Durante sua "
            "floração, pode apresentar uma grande quantidade de flores, "
            "criando uma copa bastante colorida."
        ),
        "caracteristicas": [
            "Árvore de médio ou grande porte",
            "Floração abundante",
            "Flores agrupadas",
            "Pode apresentar flores amarelas, rosas, brancas ou roxas"
        ],
        "cores": ["Roxo", "Amarelo", "Rosa", "Branco"]
    },

             "Caule engrossado",
            "Folhas alongadas",
            "Flores em formato de estrela",
            "Muito utilizada como planta ornamental"
        ],
        "cores": ["Rosa", "Vermelho", "Branco"]
    }
}

# ============================================================
# FUNÇÃO PARA CONVERTER IMAGEM EM CARACTERÍSTICAS
# ============================================================

def extrair_caracteristicas(imagem):

    imagem = imagem.convert("RGB")

    # Redimensionamento
    imagem = imagem.resize((224, 224))

    # Converte para numpy
    img = np.array(imagem)

    # Converte RGB para HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    # Características de cor
    media_rgb = np.mean(img, axis=(0, 1))
    media_hsv = np.mean(hsv, axis=(0, 1))

    # Histograma de cores
    hist = cv2.calcHist(
        [img],
        [0, 1, 2],
        None,
        [8, 8, 8],
        [0, 256, 0, 256, 0, 256]
    )

    hist = cv2.normalize(hist, hist).flatten()

    return {
        "rgb": media_rgb,
        "hsv": media_hsv,
        "hist": hist
    }


# ============================================================
# FUNÇÃO PARA COMPARAR IMAGENS
# ============================================================

def comparar_imagens(imagem1, imagem2):

    img1 = np.array(imagem1.convert("RGB").resize((224, 224)))
    img2 = np.array(imagem2.convert("RGB").resize((224, 224)))

    # HSV
    hsv1 = cv2.cvtColor(img1, cv2.COLOR_RGB2HSV)
    hsv2 = cv2.cvtColor(img2, cv2.COLOR_RGB2HSV)

    # Histogramas
    hist1 = cv2.calcHist(
        [hsv1],
        [0, 1],
        None,
        [50, 60],
        [0, 180, 0, 256]
    )

    hist2 = cv2.calcHist(
        [hsv2],
        [0, 1],
        None,
        [50, 60],
        [0, 180, 0, 256]
    )

    cv2.normalize(hist1, hist1)
    cv2.normalize(hist2, hist2)

    semelhanca = cv2.compareHist(
        hist1,
        hist2,
        cv2.HISTCMP_CORREL
    )

    # Converte para porcentagem
    porcentagem = ((semelhanca + 1) / 2) * 100

    return max(0, min(100, porcentagem))


# ============================================================
# FUNÇÃO PARA ENCONTRAR A COR PREDOMINANTE
# ============================================================

def identificar_cor(imagem):

    imagem = imagem.convert("RGB").resize((200, 200))

    img = np.array(imagem)

    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)

    h = np.mean(hsv[:, :, 0])
    s = np.mean(hsv[:, :, 1])
    v = np.mean(hsv[:, :, 2])

    # Branco
    if s < 45 and v > 170:
        return "Branco"

    # Preto
    if v < 60:
        return "Preto"

    # Pouca saturação
    if s < 80:
        return "Cinza"

    # Cores aproximadas
    if h < 10 or h >= 170:
        return "Vermelho"

    if h < 25:
        return "Laranja"

    if h < 38:
        return "Amarelo"

    if h < 85:
        return "Verde"

    if h < 135:
        return "Azul/Roxo"

    if h < 170:
        return "Roxo/Rosa"

    return "Indefinida"


# ============================================================
# FUNÇÃO DE CLASSIFICAÇÃO
# ============================================================

def classificar_planta(imagem_enviada):

    resultados = {}

    for nome, dados in plantas.items():

        pasta = dados["pasta"]

        # Se a pasta não existir
        if not os.path.exists(pasta):
            resultados[nome] = 0
            continue

        arquivos = os.listdir(pasta)

        semelhancas = []

        for arquivo in arquivos:

            caminho = os.path.join(pasta, arquivo)

            # Apenas arquivos de imagem
            if not arquivo.lower().endswith(
                (".jpg", ".jpeg", ".png", ".webp")
            ):
                continue

            try:

                imagem_referencia = Image.open(caminho)

                score = comparar_imagens(
                    imagem_enviada,
                    imagem_referencia
                )

                semelhancas.append(score)

            except Exception:
                pass

        if semelhancas:

            # Usa as melhores referências
            semelhancas.sort(reverse=True)

            melhores = semelhancas[:3]

            resultados[nome] = np.mean(melhores)

        else:
            resultados[nome] = 0

    if max(resultados.values()) == 0:
        return None, resultados

    planta_identificada = max(
        resultados,
        key=resultados.get
    )

    return planta_identificada, resultados


# ============================================================
# UPLOAD DA IMAGEM
# ============================================================

st.markdown("## 📷 Envie uma imagem da planta")

arquivo = st.file_uploader(
    "Escolha uma imagem",
    type=["jpg", "jpeg", "png", "webp"]
)

# ============================================================
# PROCESSAMENTO
# ============================================================

if arquivo is not None:

    imagem = Image.open(arquivo)

    st.markdown("---")

    col1, col2 = st.columns(2)

    # --------------------------------------------------------
    # IMAGEM ENVIADA
    # --------------------------------------------------------

    with col1:

        st.markdown("### 🖼️ Imagem enviada")

        st.image(
            imagem,
            use_container_width=True
        )

    # --------------------------------------------------------
    # CLASSIFICAÇÃO
    # --------------------------------------------------------

    with col2:

        st.markdown("### 🔎 Analisando imagem...")

        with st.spinner("Identificando a planta..."):

            planta, resultados = classificar_planta(
                imagem
            )

        if planta is not None:

            confianca = resultados[planta]

            st.markdown(
                '<div class="resultado">',
                unsafe_allow_html=True
            )

            st.success(
                f"🌱 Planta identificada: **{planta}**"
            )

            st.metric(
                "Semelhança com as imagens de referência",
                f"{confianca:.1f}%"
            )

            st.markdown("</div>", unsafe_allow_html=True)

            # ------------------------------------------------
            # COR
            # ------------------------------------------------

            cor = identificar_cor(imagem)

            st.write("")
            st.write(
                f"🎨 **Cor predominante identificada:** {cor}"
            )

        else:

            st.warning(
                "Não foi possível realizar a classificação. "
                "Verifique se as imagens de referência foram "
                "colocadas nas pastas corretas."
            )

    # ========================================================
    # RESULTADOS DAS TRÊS CATEGORIAS
    # ========================================================

    if planta is not None:

        st.markdown("---")

        st.markdown("## 📊 Resultado da classificação")

        col1, col2, col3 = st.columns(3)

        nomes = list(plantas.keys())

        for coluna, nome in zip(
            [col1, col2, col3],
            nomes
        ):

            with coluna:

                st.markdown(f"### 🌿 {nome}")

                valor = resultados[nome]

                st.progress(
                    int(min(100, valor))
                )

                st.write(
                    f"Semelhança: **{valor:.1f}%**"
                )

        # ====================================================
        # DESCRIÇÃO
        # ====================================================

        st.markdown("---")

        st.markdown(
            f"## 🌱 Sobre a planta: {planta}"
        )

        st.write(
            plantas[planta]["descricao"]
        )

        st.markdown("### 🔬 Características")

        for caracteristica in plantas[planta]["caracteristicas"]:

            st.write(
                f"• {caracteristica}"
            )

        st.markdown("### 🎨 Cores comuns")

        st.write(
            ", ".join(
                plantas[planta]["cores"]
            )
        )


# ============================================================
# GALERIA DE IMAGENS DE REFERÊNCIA
# ============================================================

st.markdown("---")

st.markdown(
    "## 🖼️ Imagens utilizadas como referência"
)

for nome, dados in plantas.items():

    st.markdown(f"### 🌿 {nome}")

    pasta = dados["pasta"]

    if os.path.exists(pasta):

        arquivos = [
            arquivo
            for arquivo in os.listdir(pasta)
            if arquivo.lower().endswith(
                (".jpg", ".jpeg", ".png", ".webp")
            )
        ]

        if arquivos:

            colunas = st.columns(
                min(len(arquivos), 3)
            )

            for i, arquivo in enumerate(arquivos):

                caminho = os.path.join(
                    pasta,
                    arquivo
                )

                try:

                    with colunas[i % len(colunas)]:

                        st.image(
                            caminho,
                            caption=nome,
                            use_container_width=True
                        )

                except Exception:
                    pass

        else:

            st.info(
                "Nenhuma imagem foi adicionada nesta pasta."
            )

    else:

        st.warning(
            f"A pasta `{pasta}` ainda não existe."
        )


# ============================================================
# RODAPÉ
# ============================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center">

    🌱 **Projeto de Identificação de Plantas**

    Desenvolvido com Python + Streamlit

    Categorias: Lírio • Ypê • Rosa-do-deserto

    </div>
    """,
    unsafe_allow_html=True
)