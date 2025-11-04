import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
try: 
    st.set_page_config(layout="wide")
    st.title("📦 Inventario Anual 2025")
    st.subheader("Mapa de áreas interactivas")

    # Cargar datos (mismo Excel)
    EXCEL_URL = 'https://github.com/MiguelCarranza414/Mapa-Interativo/blob/master/data/roles_areas.xlsx'
    df = pd.read_excel(EXCEL_URL)

    # Mapa SVG embebido
    with open("data/mapa.svg", "r", encoding="utf-8") as f:
        svg_content = f.read()

    # Agregar JavaScript para detectar clics
    html_code = f"""
    <div id="svg-container">{svg_content}</div>
    <script>
    const svg = document.querySelector('#svg-container svg');
    svg.querySelectorAll('rect').forEach(area => {{
        area.addEventListener('click', () => {{
        const areaId = area.id;
        window.parent.postMessage({{type: 'areaClick', area: areaId}}, '*');
        }});
    }});
    </script>
    """

    # Mostrar el SVG con JS
    components.html(html_code, height=500)

    # Captura de eventos
    clicked_area = st.session_state.get("clicked_area", None)
    st.write("Haz clic en un área del mapa.")

except Exception as e:
    input(e)