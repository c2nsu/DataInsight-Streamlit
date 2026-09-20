"""
visualizer.py
--------------
Matplotlib/Seaborn tabanlı otomatik grafik üretimi.
Bu fonksiyonlar hem Streamlit arayüzünde göstermek hem de
PDF raporuna gömmek için kullanılan matplotlib Figure nesneleri döndürür.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

sns.set_style("whitegrid")
PALETTE = "viridis"


def plot_missing_data(df):
    """Eksik veri dağılımını yatay bar chart olarak gösterir."""
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=True)

    fig, ax = plt.subplots(figsize=(8, max(3, len(missing) * 0.4)))
    if missing.empty:
        ax.text(0.5, 0.5, "Eksik veri bulunmuyor", ha="center", va="center", fontsize=12)
        ax.axis("off")
    else:
        ax.barh(missing.index.astype(str), missing.values, color="#e15759")
        ax.set_xlabel("Eksik Değer Sayısı")
        ax.set_title("Sütunlara Göre Eksik Veri Dağılımı")
        for i, v in enumerate(missing.values):
            ax.text(v, i, f" {v}", va="center", fontsize=9)
    fig.tight_layout()
    return fig


def plot_correlation_heatmap(corr_matrix):
    """Korelasyon matrisini ısı haritası olarak çizer."""
    fig, ax = plt.subplots(figsize=(max(6, corr_matrix.shape[1] * 0.8), max(5, corr_matrix.shape[0] * 0.7)))
    if corr_matrix.empty:
        ax.text(0.5, 0.5, "Korelasyon hesaplamak için yeterli sayısal sütun yok", ha="center", va="center")
        ax.axis("off")
    else:
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt=".2f",
            cmap="coolwarm",
            center=0,
            square=True,
            linewidths=0.5,
            ax=ax,
            cbar_kws={"shrink": 0.8},
        )
        ax.set_title("Korelasyon Matrisi")
    fig.tight_layout()
    return fig


def plot_outliers_boxplot(df, columns, max_cols=6):
    """Seçilen sayısal sütunlar için kutu grafiği (boxplot) çizer."""
    columns = columns[:max_cols]
    n = len(columns)
    if n == 0:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.text(0.5, 0.5, "Sayısal sütun bulunamadı", ha="center", va="center")
        ax.axis("off")
        return fig

    fig, axes = plt.subplots(1, n, figsize=(max(4, 3 * n), 4))
    if n == 1:
        axes = [axes]
    for ax, col in zip(axes, columns):
        sns.boxplot(y=df[col].dropna(), ax=ax, color="#4e79a7")
        ax.set_title(col, fontsize=10)
        ax.set_ylabel("")
    fig.suptitle("Aykırı Değer Analizi (Boxplot)")
    fig.tight_layout()
    return fig


def plot_distribution(df, column, bins=30):
    """Sayısal bir sütunun histogram + KDE dağılımını çizer."""
    fig, ax = plt.subplots(figsize=(6, 4))
    data = df[column].dropna()
    sns.histplot(data, bins=bins, kde=True, ax=ax, color="#59a14f")
    ax.set_title(f"{column} Dağılımı")
    ax.set_xlabel(column)
    ax.set_ylabel("Frekans")
    fig.tight_layout()
    return fig


def plot_categorical_bar(df, column, top_n=10):
    """Kategorik bir sütunun en sık görülen değerlerini bar chart olarak çizer."""
    counts = df[column].value_counts().head(top_n)
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.barplot(
        x=counts.values,
        y=counts.index.astype(str),
        hue=counts.index.astype(str),
        palette=PALETTE,
        legend=False,
        ax=ax,
    )
    ax.set_title(f"{column} - En Sık Görülen {len(counts)} Değer")
    ax.set_xlabel("Frekans")
    fig.tight_layout()
    return fig


def plot_scatter(df, col_x, col_y):
    """İki sayısal değişken arasındaki ilişkiyi scatter plot ile gösterir."""
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.scatterplot(data=df, x=col_x, y=col_y, ax=ax, alpha=0.6, color="#f28e2b")
    sns.regplot(data=df, x=col_x, y=col_y, ax=ax, scatter=False, color="#e15759", line_kws={"linewidth": 1.5})
    ax.set_title(f"{col_x} vs {col_y}")
    fig.tight_layout()
    return fig


def auto_generate_charts(df, numeric_cols, categorical_cols, strong_corr_pairs=None, max_numeric=4, max_categorical=3):
    """
    Veri setine göre otomatik olarak anlamlı grafikler üretir.

    Returns
    -------
    list[dict]: [{"title": str, "fig": matplotlib.Figure}, ...]
    """
    charts = []

    # Sayısal dağılımlar
    for col in numeric_cols[:max_numeric]:
        charts.append({"title": f"{col} Dağılımı", "fig": plot_distribution(df, col)})

    # Kategorik dağılımlar
    for col in categorical_cols[:max_categorical]:
        if df[col].nunique() <= 50:  # çok fazla kategori varsa anlamsız olur
            charts.append({"title": f"{col} Frekans Dağılımı", "fig": plot_categorical_bar(df, col)})

    # Güçlü korelasyonlu ikililer için scatter plot
    if strong_corr_pairs is not None and not strong_corr_pairs.empty:
        for _, row in strong_corr_pairs.head(3).iterrows():
            charts.append(
                {
                    "title": f"{row['Değişken 1']} vs {row['Değişken 2']} İlişkisi",
                    "fig": plot_scatter(df, row["Değişken 1"], row["Değişken 2"]),
                }
            )

    return charts


def fig_to_bytes(fig, dpi=150):
    """Matplotlib figürünü PNG byte dizisine çevirir (PDF raporuna gömmek için)."""
    import io
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight")
    buf.seek(0)
    return buf
