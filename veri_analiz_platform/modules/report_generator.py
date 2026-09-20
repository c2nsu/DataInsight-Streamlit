"""
report_generator.py
---------------------
Analiz sonuçlarından profesyonel PDF ve Excel raporları üretir.
"""

import io
import os
from datetime import datetime, time

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)


# ---------------------------------------------------------------------------
# TÜRKÇE KARAKTER DESTEĞİ (ı, ş, ğ, ü, ö, ç, İ vb.)
# ReportLab'ın yerleşik Helvetica fontu Latin-1 dışı Türkçe karakterleri
# (ı, ş, ğ, İ) desteklemediği için DejaVu Sans (Unicode) fontunu, işletim
# sisteminden bağımsız olsun diye PROJENİN İÇİNDEKİ fonts/ klasöründen gömüyoruz.
# (Sistem fontlarına güvenmiyoruz çünkü Windows/Mac/Linux'ta yolları farklıdır
# ve hatta hiç yüklü olmayabilir.)
# ---------------------------------------------------------------------------
_MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_MODULE_DIR)  # modules/ klasörünün bir üstü
_FONTS_DIR = os.path.join(_PROJECT_ROOT, "fonts")

_regular_path = os.path.join(_FONTS_DIR, "DejaVuSans.ttf")
_bold_path = os.path.join(_FONTS_DIR, "DejaVuSans-Bold.ttf")

FONT_REGULAR = "Helvetica"
FONT_BOLD = "Helvetica-Bold"

if os.path.exists(_regular_path) and os.path.exists(_bold_path):
    try:
        pdfmetrics.registerFont(TTFont("DejaVuSans", _regular_path))
        pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", _bold_path))
        FONT_REGULAR = "DejaVuSans"
        FONT_BOLD = "DejaVuSans-Bold"
    except Exception:
        pass  # Font bozuksa varsayılan Helvetica'ya geri düşülür
else:
    # fonts/ klasörü eksikse Türkçe karakterler PDF'te kutu (□) olarak görünür.
    # Bu, projeyi kopyalarken fonts/ klasörünün unutulduğu anlamına gelir.
    import warnings
    warnings.warn(
        f"DejaVu Sans fontu bulunamadı ({_FONTS_DIR}). "
        "Türkçe karakterler (ı, ş, ğ, İ vb.) PDF raporunda düzgün görünmeyebilir. "
        "'fonts/' klasörünün proje kök dizininde olduğundan emin olun."
    )


# ---------------------------------------------------------------------------
# EXCEL RAPORU
# ---------------------------------------------------------------------------

def _datetime_columns_need_time(df):
    """
    Veri setindeki tarih/saat sütunlarından herhangi birinde saat bileşeni
    (00:00:00'dan farklı) varsa True döner. Bu, Excel'e yazarken tam
    'YYYY-MM-DD HH:MM:SS' formatı mı yoksa sade 'YYYY-MM-DD' formatı mı
    kullanılacağına karar vermek için kullanılır.
    """
    datetime_cols = df.select_dtypes(include="datetime64[ns]").columns.tolist()
    # Bazı pandas sürümlerinde datetime64[us] gibi farklı çözünürlükler olabilir
    if not datetime_cols:
        datetime_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]

    for col in datetime_cols:
        non_null = df[col].dropna()
        if len(non_null) == 0:
            continue
        if not (non_null.dt.time == time(0, 0, 0)).all():
            return True
    return False


def generate_excel_report(
    original_df,
    cleaned_df,
    cleaning_log,
    missing_report,
    outliers_summary,
    corr_matrix,
    strong_corr,
    basic_stats,
    categorical_summary,
    overview,
):
    """Tüm analiz sonuçlarını çok sayfalı bir Excel dosyasına yazar."""
    output = io.BytesIO()

    # Tarih sütunlarında saat bilgisi yoksa (çoğu iş verisinde durum budur),
    # Excel'e sade 'YYYY-MM-DD' formatıyla yazıyoruz; varsa tam saat formatını kullanıyoruz.
    # Bu hem daha okunur bir görünüm sağlar hem de sütun genişliği hesabıyla tutarlı olur.
    needs_time = _datetime_columns_need_time(cleaned_df) or _datetime_columns_need_time(original_df)
    dt_format = "YYYY-MM-DD HH:MM:SS" if needs_time else "YYYY-MM-DD"
    dt_column_width = 21 if needs_time else 13

    with pd.ExcelWriter(
        output, engine="xlsxwriter", datetime_format=dt_format, date_format=dt_format
    ) as writer:
        workbook = writer.book

        header_format = workbook.add_format(
            {"bold": True, "bg_color": "#4472C4", "font_color": "white", "border": 1}
        )
        title_format = workbook.add_format({"bold": True, "font_size": 14})

        # --- Özet sayfası ---
        summary_sheet = workbook.add_worksheet("Özet")
        writer.sheets["Özet"] = summary_sheet
        summary_sheet.write("A1", "Veri Analizi Raporu - Özet", title_format)
        summary_sheet.write("A2", f"Oluşturulma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}")

        row = 4
        for key, value in overview.items():
            summary_sheet.write(row, 0, key)
            summary_sheet.write(row, 1, value)
            row += 1

        row += 1
        summary_sheet.write(row, 0, "Uygulanan Temizleme İşlemleri:", header_format)
        row += 1
        for item in cleaning_log:
            summary_sheet.write(row, 0, f"- {item}")
            row += 1

        summary_sheet.set_column("A:A", 35)
        summary_sheet.set_column("B:B", 20)

        # --- Eksik veri ---
        missing_report.to_excel(writer, sheet_name="Eksik Veri", index=False)
        _format_sheet(writer, "Eksik Veri", missing_report, header_format)

        # --- Aykırı değerler ---
        if not outliers_summary.empty:
            outliers_summary.to_excel(writer, sheet_name="Aykırı Değerler", index=False)
            _format_sheet(writer, "Aykırı Değerler", outliers_summary, header_format)

        # --- Temel istatistikler ---
        if not basic_stats.empty:
            basic_stats.to_excel(writer, sheet_name="Temel İstatistikler", index=False)
            _format_sheet(writer, "Temel İstatistikler", basic_stats, header_format)

        # --- Kategorik özet ---
        if not categorical_summary.empty:
            categorical_summary.to_excel(writer, sheet_name="Kategorik Özet", index=False)
            _format_sheet(writer, "Kategorik Özet", categorical_summary, header_format)

        # --- Korelasyon matrisi ---
        if not corr_matrix.empty:
            corr_matrix.round(3).to_excel(writer, sheet_name="Korelasyon Matrisi")
            ws = writer.sheets["Korelasyon Matrisi"]
            ws.set_column(0, corr_matrix.shape[1], 14)

        if not strong_corr.empty:
            strong_corr.to_excel(writer, sheet_name="Güçlü Korelasyonlar", index=False)
            _format_sheet(writer, "Güçlü Korelasyonlar", strong_corr, header_format)

        # --- Temizlenmiş veri ---
        # Çok büyük veri setlerinde Excel satır limitine dikkat
        max_rows = 1_000_000
        cleaned_df.iloc[:max_rows].to_excel(writer, sheet_name="Temizlenmiş Veri", index=False)
        _format_sheet(writer, "Temizlenmiş Veri", cleaned_df.iloc[:max_rows], header_format, dt_column_width=dt_column_width)

    output.seek(0)
    return output


def _format_sheet(writer, sheet_name, df, header_format, dt_column_width=None):
    """Excel sayfasındaki başlık satırını biçimlendirir ve sütun genişliğini ayarlar."""
    ws = writer.sheets[sheet_name]
    for col_num, col_name in enumerate(df.columns):
        ws.write(0, col_num, col_name, header_format)

        is_datetime_col = pd.api.types.is_datetime64_any_dtype(df[col_name])
        if is_datetime_col and dt_column_width is not None:
            # Tarih sütunlarında str() temsili ile Excel'in gerçekte uyguladığı
            # sayı formatı (saat dahil/hariç) farklı olabileceğinden, genişliği
            # yazma sırasında belirlenen sabit tarih formatına göre ayarlıyoruz.
            width = max(dt_column_width, len(str(col_name)) + 2)
        else:
            try:
                max_len = max(df[col_name].astype(str).map(len).max(), len(str(col_name))) + 2
            except Exception:
                max_len = 15
            width = min(max_len, 40)

        ws.set_column(col_num, col_num, width)


# ---------------------------------------------------------------------------
# PDF RAPORU
# ---------------------------------------------------------------------------

def generate_pdf_report(
    filename_label,
    cleaning_log,
    missing_report,
    outliers_summary,
    strong_corr,
    basic_stats,
    overview,
    chart_images,
):
    """
    Analiz sonuçlarından tasarımlı bir PDF raporu üretir.

    chart_images: list[dict] -> [{"title": str, "buffer": BytesIO}, ...]
    """
    output = io.BytesIO()
    doc = SimpleDocTemplate(
        output,
        pagesize=A4,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom", parent=styles["Title"], fontName=FONT_BOLD, fontSize=22,
        textColor=colors.HexColor("#1f3864"), spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"], fontName=FONT_REGULAR, fontSize=11,
        textColor=colors.grey, spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        "HeadingCustom",
        parent=styles["Heading2"],
        fontName=FONT_BOLD,
        fontSize=15,
        textColor=colors.HexColor("#1f3864"),
        spaceBefore=16,
        spaceAfter=8,
    )
    heading3_style = ParagraphStyle(
        "Heading3Custom", parent=styles["Heading3"], fontName=FONT_BOLD, fontSize=12,
    )
    normal_style = ParagraphStyle(
        "NormalCustom", parent=styles["Normal"], fontName=FONT_REGULAR, fontSize=10,
    )

    elements = []

    # --- Kapak / Başlık ---
    elements.append(Paragraph("Veri Analizi Raporu", title_style))
    elements.append(
        Paragraph(
            f"Veri Kaynağı: {filename_label} &nbsp;|&nbsp; Oluşturulma Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
            subtitle_style,
        )
    )

    # --- Genel Bakış ---
    elements.append(Paragraph("1. Genel Bakış", heading_style))
    overview_data = [["Metrik", "Değer"]] + [[k, str(v)] for k, v in overview.items()]
    elements.append(_make_table(overview_data, col_widths=[8 * cm, 8 * cm]))

    # --- Temizleme Log ---
    elements.append(Paragraph("2. Uygulanan Veri Temizleme İşlemleri", heading_style))
    for item in cleaning_log:
        elements.append(Paragraph(f"• {item}", normal_style))

    # --- Eksik Veri ---
    elements.append(Paragraph("3. Eksik Veri Analizi", heading_style))
    if missing_report["Eksik Değer Sayısı"].sum() == 0:
        elements.append(Paragraph("Veri setinde eksik değer bulunmamaktadır.", normal_style))
    else:
        top_missing = missing_report[missing_report["Eksik Değer Sayısı"] > 0].head(15)
        table_data = [list(top_missing.columns)] + top_missing.astype(str).values.tolist()
        elements.append(_make_table(table_data))

    # --- Aykırı Değerler ---
    elements.append(Paragraph("4. Aykırı Değer Tespiti", heading_style))
    if outliers_summary.empty or outliers_summary["Aykırı Değer Sayısı"].sum() == 0:
        elements.append(Paragraph("Belirgin bir aykırı değer tespit edilmemiştir.", normal_style))
    else:
        table_data = [list(outliers_summary.columns)] + outliers_summary.astype(str).values.tolist()
        elements.append(_make_table(table_data))

    # --- Temel İstatistikler ---
    if not basic_stats.empty:
        elements.append(Paragraph("5. Temel İstatistikler", heading_style))
        cols_to_show = ["Sütun", "Ortalama", "Medyan", "Std. Sapma", "Min", "Maks"]
        subset = basic_stats[cols_to_show].head(15)
        table_data = [list(subset.columns)] + subset.astype(str).values.tolist()
        elements.append(_make_table(table_data, font_size=8))

    # --- Korelasyon ---
    elements.append(Paragraph("6. Korelasyon Analizi", heading_style))
    if strong_corr.empty:
        elements.append(Paragraph("0.7 eşiğinin üzerinde güçlü bir korelasyon bulunamadı.", normal_style))
    else:
        table_data = [list(strong_corr.columns)] + strong_corr.astype(str).values.tolist()
        elements.append(_make_table(table_data))

    elements.append(PageBreak())

    # --- Grafikler ---
    if chart_images:
        elements.append(Paragraph("7. Görselleştirmeler", heading_style))
        for i, chart in enumerate(chart_images):
            elements.append(Paragraph(chart["title"], heading3_style))
            img = Image(chart["buffer"], width=15 * cm, height=15 * cm * 0.62)
            elements.append(img)
            elements.append(Spacer(1, 12))
            if (i + 1) % 2 == 0 and i != len(chart_images) - 1:
                elements.append(PageBreak())

    doc.build(elements)
    output.seek(0)
    return output


def _make_table(data, col_widths=None, font_size=9):
    """Ortak tablo stiliyle bir Reportlab Table nesnesi oluşturur."""
    table = Table(data, colWidths=col_widths, repeatRows=1)
    style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
            ("FONTNAME", (0, 1), (-1, -1), FONT_REGULAR),
            ("FONTSIZE", (0, 0), (-1, -1), font_size),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )
    table.setStyle(style)
    return table
