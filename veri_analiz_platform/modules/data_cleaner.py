"""
data_cleaner.py
----------------
Dosya yükleme (CSV/Excel) ve otomatik veri temizleme işlemlerini içerir.
"""

import pandas as pd
import numpy as np
import io


def load_data(uploaded_file):
    """
    Streamlit file_uploader nesnesinden CSV veya Excel dosyasını okur.

    Returns
    -------
    df : pd.DataFrame
    file_type : str
    """
    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        # Farklı encoding ve ayraç ihtimallerine karşı deneme yapıyoruz
        raw_bytes = uploaded_file.read()
        for encoding in ["utf-8", "utf-8-sig", "iso-8859-9", "cp1254", "latin1"]:
            try:
                text = raw_bytes.decode(encoding)
                # Ayracı otomatik algılamayı dene
                sep = _detect_separator(text)
                df = pd.read_csv(io.StringIO(text), sep=sep)
                return df, "csv"
            except (UnicodeDecodeError, pd.errors.ParserError):
                continue
        raise ValueError("CSV dosyası okunamadı. Encoding veya ayraç formatı desteklenmiyor.")

    elif filename.endswith((".xlsx", ".xls")):
        df = pd.read_excel(uploaded_file)
        return df, "excel"

    else:
        raise ValueError("Desteklenmeyen dosya formatı. Lütfen CSV veya Excel yükleyin.")


def _detect_separator(text_sample):
    """İlk birkaç satıra bakarak en olası ayracı tahmin eder."""
    first_line = text_sample.split("\n")[0]
    candidates = [",", ";", "\t", "|"]
    counts = {c: first_line.count(c) for c in candidates}
    best = max(counts, key=counts.get)
    return best if counts[best] > 0 else ","


def clean_data(df):
    """
    Otomatik veri temizleme adımlarını uygular ve yapılan işlemlerin
    bir log'unu döndürür.

    Adımlar:
    - Sütun isimlerindeki boşlukları temizleme
    - Tamamen boş satır/sütunları kaldırma
    - Metin sütunlarındaki baş/son boşlukları kırpma
    - Tekrarlayan satırları kaldırma
    - Sayısal görünen metin sütunlarını sayıya çevirme
    - Tarih görünen sütunları datetime'a çevirme (best-effort)

    Returns
    -------
    cleaned_df : pd.DataFrame
    log : list[str]
    """
    log = []
    cleaned_df = df.copy()

    # 1. Sütun isimlerini temizle
    original_cols = list(cleaned_df.columns)
    cleaned_df.columns = [str(c).strip() for c in cleaned_df.columns]
    if list(cleaned_df.columns) != original_cols:
        log.append("Sütun isimlerindeki baş/son boşluklar temizlendi.")

    # 2. Tamamen boş satır/sütunları kaldır
    n_rows_before = len(cleaned_df)
    cleaned_df.dropna(how="all", inplace=True)
    n_rows_after = len(cleaned_df)
    if n_rows_before != n_rows_after:
        log.append(f"{n_rows_before - n_rows_after} adet tamamen boş satır kaldırıldı.")

    n_cols_before = cleaned_df.shape[1]
    cleaned_df.dropna(axis=1, how="all", inplace=True)
    n_cols_after = cleaned_df.shape[1]
    if n_cols_before != n_cols_after:
        log.append(f"{n_cols_before - n_cols_after} adet tamamen boş sütun kaldırıldı.")

    # 3. Metin sütunlarını kırp
    text_cols = cleaned_df.select_dtypes(include="object").columns
    for col in text_cols:
        try:
            cleaned_df[col] = cleaned_df[col].apply(
                lambda x: x.strip() if isinstance(x, str) else x
            )
        except Exception:
            pass
    if len(text_cols) > 0:
        log.append(f"{len(text_cols)} metin sütununda baş/son boşluklar kırpıldı.")

    # 4. Tekrarlayan satırları kaldır
    n_before_dup = len(cleaned_df)
    cleaned_df.drop_duplicates(inplace=True)
    n_after_dup = len(cleaned_df)
    if n_before_dup != n_after_dup:
        log.append(f"{n_before_dup - n_after_dup} adet tekrarlayan satır kaldırıldı.")

    # 5. Sayısal görünen metin sütunlarını dönüştür
    converted_numeric = []
    for col in cleaned_df.select_dtypes(include="object").columns:
        converted = pd.to_numeric(
            cleaned_df[col].astype(str).str.replace(",", ".", regex=False),
            errors="coerce",
        )
        # Eğer değerlerin en az %90'ı sayıya çevrilebiliyorsa dönüştür
        non_null_ratio = converted.notna().sum() / max(cleaned_df[col].notna().sum(), 1)
        if non_null_ratio >= 0.9 and cleaned_df[col].notna().sum() > 0:
            cleaned_df[col] = converted
            converted_numeric.append(col)
    if converted_numeric:
        log.append(f"Sayısal içerikli metin sütunları sayıya çevrildi: {', '.join(converted_numeric)}")

    # 6. Tarih görünen sütunları dönüştür (best-effort, sadece isim ipucu varsa dene)
    converted_dates = []
    date_hint_keywords = ["tarih", "date", "zaman", "time"]
    for col in cleaned_df.select_dtypes(include="object").columns:
        if any(k in col.lower() for k in date_hint_keywords):
            try:
                denom = max(cleaned_df[col].notna().sum(), 1)
                # Hem gün-önce hem ay-önce varsayımını dene, hangisi daha başarılıysa onu kullan
                # (ör. ISO formatı '2020-01-13' dayfirst=True ile yanlış ayrıştırılabiliyor)
                converted_default = pd.to_datetime(cleaned_df[col], errors="coerce", dayfirst=False)
                converted_dayfirst = pd.to_datetime(cleaned_df[col], errors="coerce", dayfirst=True)
                ratio_default = converted_default.notna().sum() / denom
                ratio_dayfirst = converted_dayfirst.notna().sum() / denom

                if ratio_default >= ratio_dayfirst:
                    converted, best_ratio = converted_default, ratio_default
                else:
                    converted, best_ratio = converted_dayfirst, ratio_dayfirst

                if best_ratio >= 0.8:
                    cleaned_df[col] = converted
                    converted_dates.append(col)
            except Exception:
                pass
    if converted_dates:
        log.append(f"Tarih formatına çevrilen sütunlar: {', '.join(converted_dates)}")

    cleaned_df.reset_index(drop=True, inplace=True)

    if not log:
        log.append("Veri seti zaten temizdi, herhangi bir düzeltme gerekmedi.")

    return cleaned_df, log


def get_missing_data_report(df):
    """
    Her sütun için eksik veri sayısı ve yüzdesini içeren bir rapor üretir.
    """
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)
    report = pd.DataFrame(
        {
            "Sütun": df.columns,
            "Eksik Değer Sayısı": missing_count.values,
            "Eksik Yüzde (%)": missing_pct.values,
            "Veri Tipi": [str(dt) for dt in df.dtypes.values],
        }
    )
    report = report.sort_values("Eksik Değer Sayısı", ascending=False).reset_index(drop=True)
    return report


def handle_missing_data(df, strategy="none", columns=None):
    """
    Kullanıcının seçtiği stratejiye göre eksik verileri doldurur/kaldırır.

    strategy: 'none' | 'drop_rows' | 'mean' | 'median' | 'mode' | 'ffill' | 'zero'
    """
    result = df.copy()
    target_cols = columns if columns else result.columns

    if strategy == "none":
        return result

    if strategy == "drop_rows":
        return result.dropna(subset=target_cols)

    for col in target_cols:
        if col not in result.columns:
            continue
        if strategy == "mean" and pd.api.types.is_numeric_dtype(result[col]):
            result[col] = result[col].fillna(result[col].mean())
        elif strategy == "median" and pd.api.types.is_numeric_dtype(result[col]):
            result[col] = result[col].fillna(result[col].median())
        elif strategy == "mode":
            mode_val = result[col].mode()
            if not mode_val.empty:
                result[col] = result[col].fillna(mode_val[0])
        elif strategy == "ffill":
            result[col] = result[col].ffill()
        elif strategy == "zero" and pd.api.types.is_numeric_dtype(result[col]):
            result[col] = result[col].fillna(0)

    return result
