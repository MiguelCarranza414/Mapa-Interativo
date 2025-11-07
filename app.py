import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from pathlib import Path

st.set_page_config(layout="wide")
st.title("📦 Inventario Anual 2025")
st.subheader("Mapa de áreas interactivas")

# --- Cache helpers ---
@st.cache_data(show_spinner=False)
def load_excel(path: str) -> pd.DataFrame:
    return pd.read_excel(path)

@st.cache_data(show_spinner=False)
def load_svg(path: Path) -> str:
    return path.read_text(encoding="utf-8")

# --- Cargar datos ---
EXCEL_URL = "C:/Inventario/data/roles_areas.xlsx"
df = None
try:
    df = load_excel(EXCEL_URL)
except Exception as e:
    st.warning(f"No pude cargar el Excel en {EXCEL_URL}. Detalle: {e}")

# --- Cargar SVG ---
SVG_PATH = Path("data/mapa.svg")
if not SVG_PATH.exists():
    st.error(f"No se encontró el archivo SVG en {SVG_PATH.resolve()}")
    st.stop()

svg_content = load_svg(SVG_PATH)

# --- HTML + JS: enviar el id clicado a Streamlit ---
html_code = f"""
<div id="svg-container">{svg_content}</div>
<script>
(function() {{
  function init() {{
    const svg = document.querySelector('#svg-container svg');
    if (!svg) {{
       setTimeout(init, 50);
       return;
    }}

    // Haz clickables todos los elementos con id (ajusta a 'rect[id]' si lo prefieres)
    svg.querySelectorAll('[id]').forEach(el => {{
      try {{ el.style.cursor = 'pointer'; }} catch (e) {{}}
      el.addEventListener('click', (ev) => {{
        // Evita clics múltiples por bubbling
        ev.stopPropagation();
        const clickedId = el.id || null;
        if (window.Streamlit && typeof window.Streamlit.setComponentValue === 'function') {{
          window.Streamlit.setComponentValue(clickedId);
          if (typeof window.Streamlit.setFrameHeight === 'function') {{
            window.Streamlit.setFrameHeight(document.body.scrollHeight);
          }}
        }} else {{
          window.parent.postMessage({{ type: 'areaClick', area: clickedId }}, '*');
        }}
      }});
    }});

    if (window.Streamlit && typeof window.Streamlit.setFrameHeight === 'function') {{
      window.Streamlit.setFrameHeight(document.body.scrollHeight);
    }}
  }}
  init();
}})();
</script>
"""

# Renderiza el componente y RECIBE el valor cuando hay clic
clicked_area = components.html(html_code, height=500, scrolling=False)

st.write("👉 Haz clic en un área del mapa (cualquier elemento con atributo `id`).")

if clicked_area:
    st.session_state["clicked_area"] = clicked_area
    st.success(f"Área seleccionada: **{clicked_area}**")

    if df is not None:
        # Detecta columna 'Area' sin sensib. a mayúsculas
        col_name = next((c for c in df.columns if str(c).strip().lower() == "Location"), None)

        if col_name:
            filtered = df[df[col_name].astype(str) == str(clicked_area)]

            if filtered.empty:
                st.info("No hay coincidencias para el área seleccionada.")
            else:
                st.caption("Filtrado por área seleccionada:")
                st.dataframe(filtered, use_container_width=True)
                # Descarga opcional
                csv = filtered.to_csv(index=False).encode("utf-8")
                st.download_button("Descargar filtrado (CSV)", csv, file_name=f"inventario_{clicked_area}.csv", mime="text/csv")
        else:
            st.info("El Excel no tiene una columna llamada 'Area'. Si la agregas, mostraré aquí el filtro.")
else:
    last = st.session_state.get("clicked_area")
    if last:
        st.info(f"Última área seleccionada (sesión): **{last}**")
