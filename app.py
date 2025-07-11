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

# --- ESTILO PERSONALIZADO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@400;500&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Fredoka', sans-serif;
        background-color: #fffaf3;
        color: #333333;
    }
    .stButton>button {
        background-color: #ffa07a;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
    }
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ff7043;
    }
    </style>
""", unsafe_allow_html=True)
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
st.subheader("🍇 Vinos compatibles con tu personalidad")

variedad = perfil["vino"]

# Filtrar vinos por variedad normalizando texto
vinoselec = df_wine[df_wine['variety'].apply(lambda x: contiene_palabra(str(x), variedad))]

# Validación de resultados
if vinoselec.empty:
    st.warning("🥲 No se encontraron vinos compatibles con esta variedad. Prueba con otro tipo MBTI.")
else:
    # Ordenar si existe columna points
    if "points" in vinoselec.columns:
        vinoselec = vinoselec.sort_values("points", ascending=False).head(3)
    else:
        vinoselec = vinoselec.head(3)

    for _, row in vinoselec.iterrows():
        # Elegir mejor nombre disponible
        titulo = (
            row.get('title') or
            row.get(' title') or
            row.get('designation') or
            row.get('variety') or
            row.get('winery') or
            "Vino sin nombre 🍷"
        )

        pais = row.get('country') or row.get(' country') or "País no disponible"
        puntos = row.get('points', 'N/A')
        descripcion = row.get('description') or "Sin descripción disponible."

        with st.container():
            st.markdown(f"### 🍷 {titulo}")
            st.markdown(f"**Origen:** {pais} &nbsp;&nbsp;&nbsp; ⭐ **{puntos} puntos**")
            st.caption(f"📝 *{descripcion}*")
            st.markdown("---")

# --- MAPA MUNDIAL DE VINOS ---
st.subheader("🌍 Mapa mundial de vinos según puntuación")

# Convertir columna 'points' a numérica
df_wine["points"] = pd.to_numeric(df_wine["points"], errors="coerce")

# Agrupar por país
mapa_df = df_wine[df_wine["country"].notna()]
mapa_df = mapa_df.groupby("country", as_index=False).agg(
    promedio_puntos=("points", "mean"),
    cantidad_vinos=("points", "count")
)

# Crear choropleth
fig = px.choropleth(
    mapa_df,
    locations="country",
    locationmode="country names",
    color="promedio_puntos",
    hover_name="country",
    hover_data={"promedio_puntos": True, "cantidad_vinos": True},
    color_continuous_scale="Oranges",
    title="🌍 Promedio de puntuación de vinos por país"
)

fig.update_layout(margin={"r":0,"t":50,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)
