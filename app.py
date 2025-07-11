import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata

# --- FUNCIONES ---
def normalizar_texto(texto):
    texto = texto.lower()
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('utf-8')
    return texto.strip()

def contiene_palabra(texto, palabra):
    texto_norm = normalizar_texto(texto)
    palabra_norm = normalizar_texto(palabra)
    return palabra_norm in texto_norm

# --- PERFILES MBTI ---
mbti_perfiles = {
    "INFP": {"descripcion": "Soñador, sensible, introspectivo", "vino": "Pinot Noir", "color": "#e6ccff"},
    "ENFP": {"descripcion": "Espontáneo, creativo, sociable", "vino": "Sauvignon Blanc", "color": "#ffe680"},
    "INTJ": {"descripcion": "Analítico, reservado, estratégico", "vino": "Cabernet Sauvignon", "color": "#c2f0c2"},
    "ISFJ": {"descripcion": "Cálido, protector, leal", "vino": "Merlot", "color": "#f0d9b5"},
    "ENTP": {"descripcion": "Innovador, conversador, curioso", "vino": "Rosé", "color": "#ffcce6"},
    "ESFP": {"descripcion": "Alegre, impulsivo, enérgico", "vino": "Espumante", "color": "#ffcccc"},
    "INFJ": {"descripcion": "Visionario, intuitivo, profundo", "vino": "Syrah", "color": "#d9d2e9"},
    "ISTJ": {"descripcion": "Tradicional, metódico, práctico", "vino": "Malbec", "color": "#d9ead3"}
}

# --- CARGA DE DATOS ---
df_music = pd.read_csv("spotify-2023.csv", encoding="latin1")
import pycountry

def es_pais(nombre):
    try:
        return bool(pycountry.countries.lookup(nombre))
    except LookupError:
        return False

df_wine = pd.read_csv("winemag-data_first150k.csv", encoding="latin1", on_bad_lines='skip', low_memory=False)
df_wine.columns = df_wine.columns.str.strip()
df_wine = df_wine[df_wine["country"].apply(lambda x: es_pais(str(x)) if pd.notna(x) else False)]

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config("MBTI x Música x Vino", layout="wide")
st.title("🎧 Tu personalidad en música y vino 🍷")

# --- SELECCIÓN MBTI ---
tipo = st.selectbox("Selecciona tu tipo de personalidad MBTI:", list(mbti_perfiles.keys()))
perfil = mbti_perfiles[tipo]
st.markdown(f"## {tipo} — {perfil['descripcion']} {perfil['color']}")
st.markdown(f"🍷 Vino ideal: **{perfil['vino']}**")

# --- CANCIONES RECOMENDADAS ---
st.subheader("🎵 Tus canciones ideales")
canciones_filtradas = df_music[(df_music['valence_%'] >= 50) & (df_music['energy_%'] >= 50)]
recomendadas = canciones_filtradas.sample(5)
for _, row in recomendadas.iterrows():
    st.markdown(f"- **{row['track_name']}** — *{row['artist(s)_name']}*")

# --- VINOS COMPATIBLES ---
st.subheader("🍇 Vinos compatibles")
variedad = perfil['vino']

# Filtrar vinos por variedad (comparación sin tildes, mayúsculas, etc.)
vinoselec = df_wine[df_wine['variety'].apply(lambda x: contiene_palabra(str(x), variedad))]

# Mostrar mensaje si no se encuentra la columna "points"
if "points" not in vinoselec.columns:
    st.warning("No se encontró la columna 'points' en los datos filtrados.")
elif vinoselec.empty:
    st.warning("No se encontraron vinos compatibles con esta variedad. Prueba otro tipo MBTI o revisa tu base de datos.")
else:
    vinoselec = vinoselec.sort_values("points", ascending=False).head(3)
    for _, row in vinoselec.iterrows():
        st.markdown(f"**{row['title']}** ({row['country']}) — {row['points']} pts")
        st.caption(row['description'])
