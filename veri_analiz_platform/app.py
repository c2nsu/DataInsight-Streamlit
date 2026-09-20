"""
Veri Analizi + Otomatik Raporlama Platformu
=============================================
Streamlit tabanlı, CSV/Excel dosyalarını yükleyip otomatik olarak
temizleyen, analiz eden, görselleştiren ve PDF/Excel raporu üreten
uçtan uca bir veri analizi aracı.

Çalıştırmak için:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd

from modules import data_cleaner, analyzer, visualizer, report_generator


# ---------------------------------------------------------------------------
# SAYFA AYARLARI
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Veri Analizi & Raporlama Platformu",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
    .main-title {font-size: 2.1rem; font-weight: 700; color: #1f3864; margin-bottom: 0;}
    .subtitle {color: #666; font-size: 1rem; margin-top: 0;}
    .metric-card {background-color: #f8f9fb; border-radius: 10px; padding: 1rem; border: 1px solid #eee;}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<p class="main-title">📊 Veri Analizi & Otomatik Raporlama Platformu</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">CSV/Excel yükleyin — otomatik temizleme, eksik veri ve aykırı değer analizi, '
    'korelasyon, grafikler ve PDF/Excel raporu tek tıkla hazır.</p>',
    unsafe_allow_html=True,
)
st.divider()


# ---------------------------------------------------------------------------
# OTURUM DURUMU (SESSION STATE)
# ---------------------------------------------------------------------------
if "df_original" not in st.session_state:
    st.session_state.df_original = None
if "df_cleaned" not in st.session_state:
    st.session_state.df_cleaned = None
if "cleaning_log" not in st.session_state:
    st.session_state.cleaning_log = []
if "filename" not in st.session_state:
    st.session_state.filename = None


# ---------------------------------------------------------------------------
# 1. DOSYA YÜKLEME
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("1️⃣ Veri Yükleme")
    uploaded_file = st.file_uploader("CSV veya Excel dosyası seçin", type=["csv", "xlsx", "xls"])

    if uploaded_file is not None and uploaded_file.name != st.session_state.filename:
        try:
            with st.spinner("Dosya okunuyor..."):
                df_raw, file_type = data_cleaner.load_data(uploaded_file)
            with st.spinner("Otomatik temizlik uygulanıyor..."):
                df_cleaned, log = data_cleaner.clean_data(df_raw)

            st.session_state.df_original = df_raw
            st.session_state.df_cleaned = df_cleaned
            st.session_state.cleaning_log = log
            st.session_state.filename = uploaded_file.name
            st.success(f"'{uploaded_file.name}' başarıyla yüklendi ve temizlendi!")
        except Exception as e:
            st.error(f"Dosya okunurken hata oluştu: {e}")

    if st.session_state.df_cleaned is not None:
        st.divider()
        st.header("2️⃣ Eksik Veri Doldurma (opsiyonel)")
        strategy_label_map = {
            "Değişiklik yapma": "none",
            "Satırları sil": "drop_rows",
            "Ortalama ile doldur": "mean",
            "Medyan ile doldur": "median",
            "Mod (en sık değer) ile doldur": "mode",
            "Önceki değerle doldur (ffill)": "ffill",
            "Sıfır ile doldur": "zero",
        }
        strategy_label = st.selectbox("Strateji seçin", list(strategy_label_map.keys()))
        if st.button("Uygula", use_container_width=True):
            strategy = strategy_label_map[strategy_label]
            st.session_state.df_cleaned = data_cleaner.handle_missing_data(
                st.session_state.df_cleaned, strategy=strategy
            )
            st.success("Eksik veri işlemi uygulandı.")


# ---------------------------------------------------------------------------
# ANA İÇERİK
# ---------------------------------------------------------------------------
if st.session_state.df_cleaned is None:
    st.info("👈 Başlamak için soldaki menüden bir CSV veya Excel dosyası yükleyin.")
    st.markdown("""
    ### Bu platform neler yapar?
    - ✅ **Otomatik veri temizleme**: boş satır/sütun temizliği, tip dönüşümü, tekrar kaldırma
    - ✅ **Eksik veri analizi**: sütun bazında eksik oran ve doldurma stratejileri
    - ✅ **Aykırı değer tespiti**: IQR ve Z-Score yöntemleri
    - ✅ **Korelasyon analizi**: ısı haritası ve güçlü ilişki tespiti
    - ✅ **Otomatik grafikler**: dağılım, frekans ve ilişki grafikleri
    - ✅ **Temel istatistikler**: ortalama, medyan, çarpıklık, basıklık ve daha fazlası
    - ✅ **PDF / Excel raporu**: tek tıkla profesyonel rapor indirme
    """)
    st.stop()

df = st.session_state.df_cleaned
df_original = st.session_state.df_original

numeric_cols = analyzer.get_numeric_columns(df)
categorical_cols = analyzer.get_categorical_columns(df)
overview = analyzer.get_dataset_overview(df)

tabs = st.tabs(
    [
        "🧹 Genel Bakış & Temizlik",
        "❓ Eksik Veri",
        "🎯 Aykırı Değerler",
        "🔗 Korelasyon",
        "📈 Grafikler",
        "📐 İstatistikler",
        "📥 Rapor İndir",
    ]
)

# --- TAB 1: Genel Bakış ---
with tabs[0]:
    st.subheader("Veri Seti Genel Bakış")
    cols = st.columns(4)
    metrics = list(overview.items())
    for i, (key, value) in enumerate(metrics):
        with cols[i % 4]:
            st.metric(key, value)

    st.divider()
    st.subheader("🧹 Uygulanan Otomatik Temizleme İşlemleri")
    for item in st.session_state.cleaning_log:
        st.write(f"- {item}")

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.caption("Ham veri (ilk 10 satır)")
        st.dataframe(df_original.head(10), use_container_width=True)
    with col2:
        st.caption("Temizlenmiş veri (ilk 10 satır)")
        st.dataframe(df.head(10), use_container_width=True)

# --- TAB 2: Eksik Veri ---
with tabs[1]:
    st.subheader("Eksik Veri Analizi")
    missing_report = data_cleaner.get_missing_data_report(df)
    st.dataframe(missing_report, use_container_width=True)

    fig = visualizer.plot_missing_data(df)
    st.pyplot(fig, use_container_width=True)

# --- TAB 3: Aykırı Değerler ---
with tabs[2]:
    st.subheader("Aykırı Değer Tespiti")
    method = st.radio("Yöntem seçin", ["IQR (Çeyrekler Arası Açıklık)", "Z-Score"], horizontal=True)

    if numeric_cols:
        method_key = "iqr" if method.startswith("IQR") else "zscore"
        outliers_summary = analyzer.get_outliers_summary(df, method=method_key)
        st.dataframe(outliers_summary, use_container_width=True)

        st.divider()
        selected_cols = st.multiselect(
            "Boxplot ile incelemek istediğiniz sütunlar", numeric_cols, default=numeric_cols[:4]
        )
        if selected_cols:
            fig = visualizer.plot_outliers_boxplot(df, selected_cols)
            st.pyplot(fig, use_container_width=True)
    else:
        outliers_summary = pd.DataFrame()
        st.warning("Sayısal sütun bulunamadığı için aykırı değer analizi yapılamıyor.")

# --- TAB 4: Korelasyon ---
with tabs[3]:
    st.subheader("Korelasyon Analizi")
    if len(numeric_cols) >= 2:
        corr_method = st.selectbox("Korelasyon yöntemi", ["pearson", "spearman", "kendall"])
        corr_matrix = analyzer.compute_correlation(df, method=corr_method)
        fig = visualizer.plot_correlation_heatmap(corr_matrix)
        st.pyplot(fig, use_container_width=True)

        threshold = st.slider("Güçlü korelasyon eşiği", 0.0, 1.0, 0.7, 0.05)
        strong_corr = analyzer.get_strong_correlations(corr_matrix, threshold=threshold)
        st.markdown(f"**{threshold} eşiğinin üzerindeki ilişkiler:**")
        st.dataframe(strong_corr, use_container_width=True)
    else:
        corr_matrix = pd.DataFrame()
        strong_corr = pd.DataFrame()
        st.warning("Korelasyon hesaplamak için en az 2 sayısal sütun gerekiyor.")

# --- TAB 5: Grafikler ---
with tabs[4]:
    st.subheader("Otomatik Oluşturulan Grafikler")
    strong_corr_for_charts = strong_corr if "strong_corr" in dir() else None
    charts = visualizer.auto_generate_charts(
        df, numeric_cols, categorical_cols, strong_corr_pairs=strong_corr_for_charts
    )
    if charts:
        for chart in charts:
            st.caption(chart["title"])
            st.pyplot(chart["fig"], use_container_width=True)
    else:
        st.info("Grafik oluşturmak için uygun sütun bulunamadı.")

    st.divider()
    st.subheader("Manuel Grafik Oluştur")
    col1, col2 = st.columns(2)
    with col1:
        if numeric_cols:
            manual_col = st.selectbox("Sayısal sütun seçin (dağılım)", numeric_cols, key="manual_dist")
            st.pyplot(visualizer.plot_distribution(df, manual_col), use_container_width=True)
    with col2:
        if len(numeric_cols) >= 2:
            x_col = st.selectbox("X ekseni", numeric_cols, key="scatter_x")
            y_col = st.selectbox("Y ekseni", [c for c in numeric_cols if c != x_col], key="scatter_y")
            st.pyplot(visualizer.plot_scatter(df, x_col, y_col), use_container_width=True)

# --- TAB 6: İstatistikler ---
with tabs[5]:
    st.subheader("Temel İstatistikler (Sayısal Sütunlar)")
    basic_stats = analyzer.get_basic_stats(df)
    st.dataframe(basic_stats, use_container_width=True)

    st.subheader("Kategorik Sütun Özeti")
    categorical_summary = analyzer.get_categorical_summary(df)
    st.dataframe(categorical_summary, use_container_width=True)

# --- TAB 7: Rapor İndir ---
with tabs[6]:
    st.subheader("📥 Rapor Oluştur ve İndir")
    st.write("Tüm analiz sonuçlarını profesyonel bir PDF veya çok sayfalı Excel raporu olarak indirin.")

    missing_report = data_cleaner.get_missing_data_report(df)
    outliers_summary = analyzer.get_outliers_summary(df) if numeric_cols else pd.DataFrame(
        columns=["Sütun", "Yöntem", "Aykırı Değer Sayısı", "Aykırı Değer Yüzdesi (%)"]
    )
    corr_matrix = analyzer.compute_correlation(df) if len(numeric_cols) >= 2 else pd.DataFrame()
    strong_corr = analyzer.get_strong_correlations(corr_matrix) if not corr_matrix.empty else pd.DataFrame(
        columns=["Değişken 1", "Değişken 2", "Korelasyon"]
    )
    basic_stats = analyzer.get_basic_stats(df)
    categorical_summary = analyzer.get_categorical_summary(df)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📄 PDF Raporu")
        if st.button("PDF Raporu Oluştur", use_container_width=True, type="primary"):
            with st.spinner("PDF raporu hazırlanıyor..."):
                charts = visualizer.auto_generate_charts(df, numeric_cols, categorical_cols, strong_corr_pairs=strong_corr)
                chart_images = [
                    {"title": c["title"], "buffer": visualizer.fig_to_bytes(c["fig"])} for c in charts
                ]
                pdf_bytes = report_generator.generate_pdf_report(
                    filename_label=st.session_state.filename,
                    cleaning_log=st.session_state.cleaning_log,
                    missing_report=missing_report,
                    outliers_summary=outliers_summary,
                    strong_corr=strong_corr,
                    basic_stats=basic_stats,
                    overview=overview,
                    chart_images=chart_images,
                )
            st.download_button(
                "⬇️ PDF Dosyasını İndir",
                data=pdf_bytes,
                file_name=f"veri_analizi_raporu_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    with col2:
        st.markdown("#### 📊 Excel Raporu")
        if st.button("Excel Raporu Oluştur", use_container_width=True, type="primary"):
            with st.spinner("Excel raporu hazırlanıyor..."):
                excel_bytes = report_generator.generate_excel_report(
                    original_df=df_original,
                    cleaned_df=df,
                    cleaning_log=st.session_state.cleaning_log,
                    missing_report=missing_report,
                    outliers_summary=outliers_summary,
                    corr_matrix=corr_matrix,
                    strong_corr=strong_corr,
                    basic_stats=basic_stats,
                    categorical_summary=categorical_summary,
                    overview=overview,
                )
            st.download_button(
                "⬇️ Excel Dosyasını İndir",
                data=excel_bytes,
                file_name=f"veri_analizi_raporu_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
