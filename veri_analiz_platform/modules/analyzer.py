"""
analyzer.py
------------
Aykırı değer tespiti, korelasyon analizi ve temel istatistiksel özetler.
"""

import pandas as pd
import numpy as np
from scipy import stats


def get_numeric_columns(df):
    return df.select_dtypes(include=np.number).columns.tolist()


def get_categorical_columns(df):
    return df.select_dtypes(include=["object", "category"]).columns.tolist()


def detect_outliers_iqr(df, column, k=1.5):
    """IQR yöntemiyle aykırı değerleri tespit eder."""
    series = df[column].dropna()
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1
    lower = q1 - k * iqr
    upper = q3 + k * iqr
    outlier_mask = (df[column] < lower) | (df[column] > upper)
    return {
        "column": column,
        "method": "IQR",
        "lower_bound": lower,
        "upper_bound": upper,
        "outlier_count": int(outlier_mask.sum()),
        "outlier_pct": round(outlier_mask.sum() / len(df) * 100, 2) if len(df) else 0,
        "indices": df.index[outlier_mask].tolist(),
    }


def detect_outliers_zscore(df, column, threshold=3):
    """Z-score yöntemiyle aykırı değerleri tespit eder."""
    series = df[column].dropna()
    if series.std(ddof=0) == 0 or len(series) == 0:
        return {
            "column": column,
            "method": "Z-Score",
            "threshold": threshold,
            "outlier_count": 0,
            "outlier_pct": 0,
            "indices": [],
        }
    z_scores = pd.Series(stats.zscore(series), index=series.index)
    outlier_idx = z_scores[abs(z_scores) > threshold].index
    return {
        "column": column,
        "method": "Z-Score",
        "threshold": threshold,
        "outlier_count": len(outlier_idx),
        "outlier_pct": round(len(outlier_idx) / len(df) * 100, 2) if len(df) else 0,
        "indices": list(outlier_idx),
    }


def get_outliers_summary(df, method="iqr", k=1.5, z_threshold=3):
    """Tüm sayısal sütunlar için aykırı değer özet tablosu üretir."""
    numeric_cols = get_numeric_columns(df)
    rows = []
    for col in numeric_cols:
        if method == "iqr":
            result = detect_outliers_iqr(df, col, k=k)
        else:
            result = detect_outliers_zscore(df, col, threshold=z_threshold)
        rows.append(
            {
                "Sütun": col,
                "Yöntem": result["method"],
                "Aykırı Değer Sayısı": result["outlier_count"],
                "Aykırı Değer Yüzdesi (%)": result["outlier_pct"],
            }
        )
    return pd.DataFrame(rows)


def compute_correlation(df, method="pearson"):
    """Sayısal sütunlar arasındaki korelasyon matrisini hesaplar."""
    numeric_df = df.select_dtypes(include=np.number)
    if numeric_df.shape[1] < 2:
        return pd.DataFrame()
    return numeric_df.corr(method=method)


def get_strong_correlations(corr_matrix, threshold=0.7):
    """Belirli bir eşiğin üzerindeki (mutlak değer) korelasyon çiftlerini listeler."""
    if corr_matrix.empty:
        return pd.DataFrame(columns=["Değişken 1", "Değişken 2", "Korelasyon"])

    pairs = []
    cols = corr_matrix.columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            val = corr_matrix.iloc[i, j]
            if pd.notna(val) and abs(val) >= threshold:
                pairs.append(
                    {
                        "Değişken 1": cols[i],
                        "Değişken 2": cols[j],
                        "Korelasyon": round(val, 3),
                    }
                )
    if not pairs:
        return pd.DataFrame(columns=["Değişken 1", "Değişken 2", "Korelasyon"])

    result = pd.DataFrame(pairs)
    result = result.reindex(
        result["Korelasyon"].abs().sort_values(ascending=False).index
    ).reset_index(drop=True)
    return result


def get_basic_stats(df):
    """
    Sayısal sütunlar için genişletilmiş temel istatistikler:
    ortalama, medyan, std, min, max, çeyrekler, çarpıklık (skewness), basıklık (kurtosis).
    """
    numeric_cols = get_numeric_columns(df)
    if not numeric_cols:
        return pd.DataFrame()

    stats_rows = []
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        stats_rows.append(
            {
                "Sütun": col,
                "Adet": int(series.count()),
                "Ortalama": round(series.mean(), 3),
                "Medyan": round(series.median(), 3),
                "Std. Sapma": round(series.std(), 3),
                "Min": round(series.min(), 3),
                "Maks": round(series.max(), 3),
                "Çeyrek (%25)": round(series.quantile(0.25), 3),
                "Çeyrek (%75)": round(series.quantile(0.75), 3),
                "Çarpıklık": round(series.skew(), 3),
                "Basıklık": round(series.kurt(), 3),
            }
        )
    return pd.DataFrame(stats_rows)


def get_categorical_summary(df):
    """Kategorik sütunlar için özet: benzersiz değer sayısı ve en sık değer."""
    cat_cols = get_categorical_columns(df)
    rows = []
    for col in cat_cols:
        series = df[col].dropna()
        if len(series) == 0:
            continue
        value_counts = series.value_counts()
        rows.append(
            {
                "Sütun": col,
                "Benzersiz Değer Sayısı": series.nunique(),
                "En Sık Değer": value_counts.index[0] if len(value_counts) else "-",
                "En Sık Değer Frekansı": int(value_counts.iloc[0]) if len(value_counts) else 0,
            }
        )
    return pd.DataFrame(rows)


def get_dataset_overview(df):
    """Genel veri seti özeti: boyut, bellek kullanımı, sütun tipleri dağılımı."""
    return {
        "Satır Sayısı": df.shape[0],
        "Sütun Sayısı": df.shape[1],
        "Toplam Hücre": df.shape[0] * df.shape[1],
        "Bellek Kullanımı (KB)": round(df.memory_usage(deep=True).sum() / 1024, 2),
        "Sayısal Sütun Sayısı": len(get_numeric_columns(df)),
        "Kategorik Sütun Sayısı": len(get_categorical_columns(df)),
        "Toplam Eksik Değer": int(df.isnull().sum().sum()),
        "Tekrarlayan Satır Sayısı": int(df.duplicated().sum()),
    }
