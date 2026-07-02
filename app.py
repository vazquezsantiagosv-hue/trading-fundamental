import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# Configuración de página ancha para visualización profesional
st.set_page_config(page_title="Terminal de Análisis Fundamental", layout="wide")

st.title("📈 Terminal Avanzada de Análisis Fundamental")
st.write("Cruzá el análisis algorítmico y visual con tus gráficos técnicos.")

# Diccionario de ayuda para los parámetros (Explicaciones críticas)
ayuda_parametros = {
    "P/E Ratio": "Price-to-Earnings. Mide cuántos años de ganancias necesitás para recuperar tu inversión. Un P/E alto puede significar sobrevaloración o altas expectativas de crecimiento; un P/E bajo indica que la acción está barata o el negocio tiene problemas.",
    "Beta": "Mide la volatilidad y riesgo del activo frente al mercado general (S&P 500 = 1.0). Si es mayor a 1, la acción amplifica los movimientos del mercado (más nafta); si es menor, es más defensiva.",
    "Margen Neto": "Porcentaje de ingresos que se convierte en ganancia neta real después de pagar todos los costos, impuestos e intereses. Mide la eficiencia operativa pura del negocio.",
    "ROE": "Return on Equity. Mide la rentabilidad que genera la empresa con el dinero aportado por los propios accionistas. Es el indicador definitivo de eficiencia de capital.",
    "Liquidez": "Ratio de Liquidez (Current Ratio). Capacidad de la empresa para pagar sus deudas de corto plazo (menos de un año) con sus activos corrientes. Idealmente debe ser mayor a 1.0 para evitar estrés financiero.",
    "EBITDA": "Ganancias antes de intereses, impuestos, depreciación y amortización. Mide el flujo operativo bruto que genera el negocio principal, sin distorsiones contables o financieras.",
    "Free Cash Flow": "El dinero en efectivo real que le queda a la empresa después de pagar sus gastos de operación y de capital (reinversiones). Es el oxígeno financiero para recomprar acciones o pagar dividendos."
}

# Entrada de tickers
tickers_usuario = st.text_input("Ingresá los tickers a comparar (separados por coma):", "AAPL, MSFT, NVDA, AMD")

if tickers_usuario:
    lista_tickers = [t.strip().upper() for t in tickers_usuario.split(",") if t.strip()]
    datos_tabla = []
    
    with st.spinner("Conectando con los mercados financieros en vivo..."):
        for ticker in lista_tickers:
            try:
                accion = yf.Ticker(ticker)
                info = accion.info
                
                pe = info.get("trailingPE")
                beta = info.get("beta")
                margen_neto = info.get("profitMargins", 0) * 100 if info.get("profitMargins") else 0
                roe = info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else 0
                liquidez = info.get("currentRatio")
                fcf = info.get("freeCashflow", 0)
                ebitda = info.get("ebitda", 0)
                
                datos_tabla.append({
                    "Ticker": ticker,
                    "P/E Ratio": round(pe, 2) if pe else None,
                    "Beta": round(beta, 2) if beta else None,
                    "Margen Neto (%)": round(margen_neto, 2),
                    "ROE (%)": round(roe, 2),
                    "Liquidez": round(liquidez, 2) if liquidez else None,
                    "EBITDA (USD)": ebitda,
                    "Free Cash Flow (USD)": fcf
                })
            except Exception as e:
                st.error(f"Error cargando datos de {ticker}: {e}")

    if datos_tabla:
        df = pd.DataFrame(datos_tabla)
        
        # 1. TABLA INTERACTIVA
        st.subheader("📋 Métricas Consolidadas")
        df_visual = df.copy()
        df_visual["EBITDA (USD)"] = df_visual["EBITDA (USD)"].apply(lambda x: f"${x:,.0f}" if x else "N/D")
        df_visual["Free Cash Flow (USD)"] = df_visual["Free Cash Flow (USD)"].apply(lambda x: f"${x:,.0f}" if x else "N/D")
        st.dataframe(df_visual, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # 2. SECCIÓN DE GRÁFICOS CON ICONOS DE INFORMACIÓN INTEGRADOS (help=)
        st.subheader("📊 Visualización Gráfica Parámetro por Parámetro")
        st.caption("ℹ️ Pasá el mouse por el ícono circular (?) de cada título para entender el uso técnico de cada métrica.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Valoración (P/E Ratio)", help=ayuda_parametros["P/E Ratio"])
            fig_pe = px.bar(df, x="Ticker", y="P/E Ratio", title="Múltiplo de Valoración - Menor es más barato", text_auto=True, color="Ticker")
            st.plotly_chart(fig_pe, use_container_width=True)
            
            st.markdown("#### Riesgo Sistémico (Beta)", help=ayuda_parametros["Beta"])
            fig_beta = px.scatter(df, x="Ticker", y="Beta", title="Sensibilidad de Riesgo - Mercado base = 1.0", size=[15]*len(df), color="Ticker")
            fig_beta.add_hline(y=1.0, line_dash="dash", line_color="red")
            st.plotly_chart(fig_beta, use_container_width=True)

        with col2:
            st.markdown("#### Rentabilidad Operativa (ROE y Margen Neto)", help=f"ROE: {ayuda_parametros['ROE']}\n\nMargen: {ayuda_parametros['Margen Neto']}")
            fig_rent = px.bar(df, x="Ticker", y=["ROE (%)", "Margen Neto (%)"], title="Eficacia Operativa: ROE vs Margen Neto", barmode="group")
            st.plotly_chart(fig_rent, use_container_width=True)
            
            st.markdown("#### Generación de Caja (Free Cash Flow)", help=ayuda_parametros["Free Cash Flow"])
            fig_fcf = px.bar(df, x="Ticker", y="Free Cash Flow (USD)", title="Flujo de Caja Libre Real (Caja Neta)", text_auto='.2s', color="Ticker")
            st.plotly_chart(fig_fcf, use_container_width=True)

        st.markdown("---")
        
        # 3. CONCLUSIÓN CRÍTICA ALGORÍTMICA
        st.subheader("🧠 Conclusión Fundamental y Filtro de Selección")
        
        df_valid_pe = df[df["P/E Ratio"].notna()]
        ticker_barato = df_valid_pe.loc[df_valid_pe["P/E Ratio"].idxmin()]["Ticker"] if not df_valid_pe.empty else "N/D"
        ticker_eficiente = df.loc[df["ROE (%)"].idxmax()]["Ticker"]
        ticker_defensivo = df[df["Beta"].notna()].loc[df[df["Beta"].notna()]["Beta"].idxmin()]["Ticker"] if not df[df["Beta"].notna()].empty else "N/D"
        ticker_caja = df.loc[df["Free Cash Flow (USD)"].idxmax()]["Ticker"]
        
        st.markdown(f"""
        Basado estrictamente en los datos numéricos extraídos de los balances consolidados, se desprenden las siguientes observaciones clave para tu toma de decisiones:
        
        * 🔍 **Atractivo por Valoración:** **{ticker_barato}** presenta el múltiplo *Price-to-Earnings* ($P/E$) más bajo del grupo examinado, lo que implica que es la empresa donde estás pagando menos por cada dólar de beneficio generado actualmente.
        * ⚡ **Eficiencia de Capital:** **{ticker_eficiente}** lidera el Retorno sobre el Capital (*ROE*), demostrando una capacidad superior para exprimir y rentabilizar los fondos de sus accionistas.
        * 🛡️ **Mitigación de Volatilidad:** Si buscás reducir la exposición sistémica antes de ejecutar una entrada técnica, **{ticker_defensivo}** es el activo con la *Beta* más
o}** es el activo con la *Beta* más baja. Te va a ofrecer mayor estabilidad en escenarios de corrección.
* 💰 **Salud de Caja (Oxígeno Financiero):** **{ticker_caja}** se destaca por registrar el mayor volumen de *Free Cash Flow* disponible, lo que reduce drásticamente su riesgo de liquidez y le otorga flexibilidad para recomprar acciones o pagar deuda.

**Veredicto Crítico:** No te limites a comprar ciegamente el ticker con el gráfico técnico más lindo. Si tu estrategia busca valor puro, cruzá el patrón de reversión técnica con **{ticker_barato}**. Si preferís sumarte a una tendencia de fuerte *momentum* institucional respaldada por métricas operativas implacables, priorizá **{ticker_eficiente}**.
""")
