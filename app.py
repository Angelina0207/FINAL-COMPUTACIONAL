import streamlit as st
import pandas as pd
import plotly.express as px
import unicodedata

# --- CONFIGURACIÓN DE LA APP ---
st.set_page_config("MBTI x Música x Vino", layout="wide")

# --- ESTILO PERSONALIZADO ---
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Fredoka:wght@400;600&display=swap" rel="stylesheet">
    <style>
    html, body, [class*="css"]  {
        font-family: 'Fredoka', sans-serif;
        background-color: #fffaf3;
        color: #333333;
    }
    h1, h2, h3 {
        color: #ff7043;
        font-weight: 600;
    }
    .stButton>button {
        background-color: #ffa07a;
        color: white;
        border-radius: 10px;
        padding: 10px 20px;
        font-weight: bold;
        border: none;
    }
    .stSelectbox label {
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

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
df_wine = pd.read_csv("winemag-data_first150k.csv", encoding="latin1", on_bad_lines='skip', low_memory=False)
df_wine.columns = df_wine.columns.str.strip()
df_wine["points"] = pd.to_numeric(df_wine["points"], errors="coerce")

# --- PESTAÑAS ---
tabs = st.tabs(["🎧 Recomendación Clásica", "🚀 Modo Interactivo"])

# --- PESTAÑA 1 ---
with tabs[0]:
    st.title("🎧 Tu personalidad en música y vino 🍷")

    tipo = st.selectbox("Selecciona tu tipo de personalidad MBTI:", list(mbti_perfiles.keys()))
    perfil = mbti_perfiles[tipo]
    st.markdown(f"## {tipo} — {perfil['descripcion']} {perfil['color']}")
    st.markdown(f"🍷 Vino ideal: **{perfil['vino']}**")

    st.subheader("🎵 Tus canciones ideales")
    canciones_filtradas = df_music[(df_music['valence_%'] >= 50) & (df_music['energy_%'] >= 50)]
    recomendadas = canciones_filtradas.sample(5)
    for _, row in recomendadas.iterrows():
        st.markdown(f"- **{row['track_name']}** — *{row['artist(s)_name']}*")

    st.subheader("🍇 Vinos compatibles con tu personalidad")
    variedad = perfil["vino"]
    vinoselec = df_wine[df_wine['variety'].apply(lambda x: contiene_palabra(str(x), variedad))]

    if vinoselec.empty:
        st.warning("🥲 No se encontraron vinos compatibles con esta variedad. Prueba con otro tipo MBTI.")
    else:
        if "points" in vinoselec.columns:
            vinoselec = vinoselec.sort_values("points", ascending=False).head(3)
        else:
            vinoselec = vinoselec.head(3)

        for _, row in vinoselec.iterrows():
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

    st.subheader("📊 Promedio musical por tipo MBTI")
    if "mbti" in df_music.columns:
        media = df_music.groupby("mbti")[["valence_%", "energy_%", "danceability_%"]].mean().reset_index()
        fig = px.line(media, x="mbti", y=["valence_%", "energy_%", "danceability_%"], markers=True)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🌍 Mapa mundial de vinos según puntuación")
    if "country" in df_wine.columns and "points" in df_wine.columns:
        mapa_df = df_wine[df_wine["country"].notna() & df_wine["points"].notna()]
        mapa_df = mapa_df.groupby("country", as_index=False).agg(
            promedio_puntos=("points", "mean"),
            cantidad_vinos=("points", "count")
        )
        if not mapa_df.empty:
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
        else:
            st.warning("No hay suficientes datos para generar el mapa.")
    else:
        st.warning("No se encuentran columnas válidas para crear el mapa.")

    st.markdown("---")
    st.info("Las descripciones pueden estar en inglés para mantener el contexto original y fomentar la comprensión cultural y lingüística. Puedes usar esta app también para reforzar tu comprensión de términos musicales y enológicos en su idioma original. ✨")

# --- PESTAÑA 2 ---
with tabs[1]:
    st.header("🚀 ¡Descubre tu mood musical y vinícola ideal!")

    tipo = st.selectbox("1️⃣ ¿Cuál es tu tipo de personalidad MBTI?", list(mbti_perfiles.keys()), key="interactivo")
    perfil = mbti_perfiles[tipo]

    st.subheader("2️⃣ Ajusta tu mood musical 🎚️")
    energia = st.slider("Nivel de energía 🎧", 0, 100, (50, 100))
    valence = st.slider("Nivel de felicidad 😊", 0, 100, (50, 100))
    bailabilidad = st.slider("¿Qué tan bailable? 💃", 0, 100, (50, 100))

    filtro_canciones = df_music[
        (df_music['valence_%'].between(valence[0], valence[1])) &
        (df_music['energy_%'].between(energia[0], energia[1])) &
        (df_music['danceability_%'].between(bailabilidad[0], bailabilidad[1]))
    ]

    if not filtro_canciones.empty:
        sugerencia = filtro_canciones.sample(1).iloc[0]
        st.markdown(f"🎶 **Canción recomendada:** {sugerencia['track_name']} — *{sugerencia['artist(s)_name']}*")
    else:
        st.warning("No se encontraron canciones con esos parámetros. ¡Ajusta los sliders!")

    st.markdown(f"🍷 **Vino perfecto para ti:** {perfil['vino']}")

    st.subheader("3️⃣ Comparación musical por tipo MBTI")
    if 'mbti' in df_music.columns:
        media = df_music.groupby("mbti")[["valence_%", "energy_%", "danceability_%"]].mean().reset_index()
        fig = px.bar(media, x="mbti", y=["valence_%", "energy_%", "danceability_%"], barmode="group")
        st.plotly_chart(fig, use_container_width=True)
