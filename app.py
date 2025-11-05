import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
try: 
    st.set_page_config(layout="wide")
    st.title("📦 Inventario Anual 2025")
    st.subheader("Mapa de áreas interactivas")

    # Cargar datos (mismo Excel)
    EXCEL_URL = '/data/roles_areas.xlsx'
    df = pd.read_excel(EXCEL_URL)

    # Mapa SVG embebido
    with open("data/mapa.svg", "r", encoding="utf-8") as f:
        svg_content = f.read()

    # Agregar JavaScript para detectar clics
    html_code = f"""
    <div id="svg-container">{svg_content}</div>
    <script>
    const svg = document.querySelector('#svg-container svg');
    svg.querySelectorAll('rect, path, polygon, g').forEach(area => {{
        area.addEventListener('click', () => {{
            const areaId = area.id;
            const streamlitEvent = new CustomEvent("streamlit:setComponentValue", {{
                detail: areaId
            }});
            window.parent.document.dispatchEvent(streamlitEvent);
        }});
    }});
    </script>
    """


    # Mostrar el SVG con JS
    components.html(html_code, height=500)

    # Captura de eventos
    clicked_area = components.html(html_code, height=500)

    if clicked_area:
        st.write(f"Área seleccionada: **{clicked_area}**")
    else:
        st.write("Haz clic en un área del mapa.")

except Exception as e:
    input(e)