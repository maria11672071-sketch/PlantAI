st.divider()
st.subheader("🌸 Plantas cadastradas")
cols = st.columns(3)

for col, (nome, dados) in zip(cols, PLANTAS.items()):
    with col:
        st.image(dados["arquivo"], caption=nome, use_container_width=True)
        st.write(dados["cientifico"])

st.info(
    "Protótipo educacional: para identificação científica confiável, é necessário um conjunto maior de imagens e validação."
)
sefrom pathlib import Path
import numpy as np
from PIL import Image
import streamlit as st
import torch
import torch.nn.functional as F
from torchvision.models import MobileNet_V3_Small_Weights, mobilenet_v3_small

st.set_page_config(page_title="PlantAI", page_icon="🌿", layout="wide")

PLANTAS = {
    "Rosa do deserto": {
        "arquivo": "rosa_do_deserto.jpg",
        "cientifico": "Adenium obesum",
        "naturalidade": "Ornamental / cultivada",
        "descricao": "Planta ornamental de caule engrossado e flores vistosas.",
    },
    "Ypê": {
        "arquivo": "ipe.jpg",
        "cientifico": "Handroanthus spp.",
        "naturalidade": "Árvore nativa / paisagística",
        "descricao": "Árvore brasileira conhecida pela floração intensa.",
    },
    "Lírio": {
        "arquivo": "lirio.jpg",
        "cientifico": "Lilium spp.",
        "naturalidade": "Ornamental / cultivada",
        "descricao": "Planta ornamental com flores grandes e pétalas abertas.",
    },
}


@st.cache_resource
def carregar_modelo():
    pesos = MobileNet_V3_Small_Weights.DEFAULT
    modelo = mobilenet_v3_small(weights=pesos)
    modelo.classifier = torch.nn.Identity()
    modelo.eval()
    return modelo, pesos.transforms()


@st.cache_resource
def referencias():
    modelo, transformar = carregar_modelo()
    pasta = Path(__file__).parent
    refs = {}
    with torch.inference_mode():
        for nome, dados in PLANTAS.items():
            img = Image.open(pasta / dados["arquivo"]).convert("RGB")
            v = modelo(transformar(img).unsqueeze(0))
            refs[nome] = F.normalize(v, dim=1)
    return refs


def classificar(img):
    modelo, transformar = carregar_modelo()
    refs = referencias()
    with torch.inference_mode():
        v = modelo(transformar(img.convert("RGB")).unsqueeze(0))
        v = F.normalize(v, dim=1)
        ranking = sorted(
            [
                (nome, float(F.cosine_similarity(v, ref).item()))
                for nome, ref in refs.items()
            ],
            key=lambda x: x[1],
            reverse=True,
        )
    return ranking


def cor_predominante(img):
    a = np.asarray(img.convert("RGB").resize((160, 160))).astype(float) / 255
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    scores = {
        "Rosa": np.mean((r > g * 1.18) & (r > b * 1.05)),
        "Roxo/Lilás": np.mean((r > g * 1.10) & (b > g * 1.10)),
        "Amarelo": np.mean((r > b * 1.25) & (g > b * 1.20)),
        "Verde": np.mean((g > r * 1.12) & (g > b * 1.08)),
        "Branco": np.mean((r > 0.78) & (g > 0.78) & (b > 0.78)),
    }
    return max(scores, key=scores.get)


st.title("🌿 PlantAI")
st.subheader("Identificador e classificador de plantas")
st.write("Identifica visualmente Rosa do deserto, Ypê e Lírio.")

arquivo = st.file_uploader(
    "📷 Envie uma foto da planta", type=["jpg", "jpeg", "png", "webp"]
)

if arquivo:
    img = Image.open(arquivo).convert("RGB")
    col1, col2 = st.columns(2)

    with col1:
        st.image(img, caption="Imagem enviada", use_container_width=True)

    with col2:
        with st.spinner("Analisando..."):
            ranking = classificar(img)
            nome, score = ranking[0]
            cor = cor_predominante(img)
            dados = PLANTAS[nome]

            st.success(f"🌱 Planta identificada: {nome}")
            st.metric("Similaridade visual", f"{score:.3f}")
            st.write(f"**Nome científico:** {dados['cientifico']}")
            st.write(f"**Cor predominante:** {cor}")
            st.write(f"**Naturalidade:** {dados['naturalidade']}")
            st.write(f"**Descrição:** {dados['descricao']}")

        with st.expander("Ver comparação"):
            for n, s in ranking:
                st.write(f"**{n}:** {s:.3f}")

