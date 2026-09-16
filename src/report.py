"""
PDF Report Generator — Solar Fleet Intelligence
Generates per-inverter performance report as PDF.
"""
import pandas as pd
import joblib
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from datetime import datetime

# ---------- Load data ----------
metrics = joblib.load('models/metrics.pkl')
health = pd.read_csv('data/fleet_health.csv')
cost = pd.read_csv('data/cost_impact.csv')
anomalies = pd.read_csv('data/anomaly_results.csv', parse_dates=['timestamp'])

TARIFF = 8.0  # ₹/kWh


def make_report(output_path='data/fleet_report.pdf'):
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=0.75 * inch, rightMargin=0.75 * inch,
        topMargin=0.75 * inch, bottomMargin=0.75 * inch
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleX', parent=styles['Title'],
        fontSize=20, textColor=colors.HexColor('#1A3A6B'), spaceAfter=12
    )
    h2 = ParagraphStyle(
        'H2', parent=styles['Heading2'],
        fontSize=14, textColor=colors.HexColor('#1A3A6B'), spaceBefore=16, spaceAfter=8
    )
    body = ParagraphStyle('Body', parent=styles['BodyText'], fontSize=10, leading=14)

    story = []

    # ---------- Cover ----------
    story.append(Paragraph("Solar Fleet Intelligence", title_style))
    story.append(Paragraph("Fleet Performance Report — TPREL", styles['Heading3']))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        f"<b>Generated:</b> {datetime.now().strftime('%d %B %Y, %H:%M')}<br/>"
        f"<b>Model:</b> {metrics['model_name']} | R² = {metrics['r2']:.4f} | MAE = {metrics['mae']:.4f}<br/>"
        f"<b>Inverters monitored:</b> {len(health)}<br/>"
        f"<b>Fleet annual loss:</b> ₹{cost['annual_loss_inr'].sum():,.0f}",
        body
    ))
    story.append(Spacer(1, 0.3 * inch))

    # ---------- Executive Summary ----------
    story.append(Paragraph("1. Executive Summary", h2))
    faulty = health[health['anomaly_rate_%'] > 2.0]
    story.append(Paragraph(
        f"Out of {len(health)} inverters analyzed, "
        f"<b>{len(faulty)}</b> show elevated anomaly rates above the fleet baseline. "
        f"These inverters account for the majority of the "
        f"<b>₹{cost['annual_loss_inr'].sum():,.0f}</b> annualized fleet loss. "
        f"Immediate maintenance attention is recommended for the top 3 underperformers.",
        body
    ))

    # ---------- Fleet Health Table ----------
    story.append(Paragraph("2. Fleet Health Overview", h2))
    health_data = [['Inverter', 'Anomaly Rate (%)', 'Avg Efficiency', 'Avg Residual']]
    for _, row in health.iterrows():
        health_data.append([
            row['inverter_id'],
            f"{row['anomaly_rate_%']:.2f}",
            f"{row['avg_efficiency']:.4f}",
            f"{row['avg_residual']:.6f}",
        ])
    health_table = Table(health_data, colWidths=[1.2*inch, 1.5*inch, 1.4*inch, 1.4*inch])
    health_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A3A6B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F4FA')]),
    ]))
    story.append(health_table)

    # ---------- Cost Impact ----------
    story.append(PageBreak())
    story.append(Paragraph("3. Cost Impact Analysis", h2))
    story.append(Paragraph(
        f"Assumptions: Tariff = ₹{TARIFF}/kWh, Nominal Efficiency = 95%. "
        f"Values represent annualized revenue loss per inverter.",
        body
    ))
    cost_data = [['Inverter', 'Avg Eff.', 'Energy Loss (kWh)', 'Annual Loss (₹)']]
    for _, row in cost.sort_values('annual_loss_inr', ascending=False).iterrows():
        cost_data.append([
            row['inverter_id'],
            f"{row['avg_efficiency']:.4f}",
            f"{row['energy_loss_kwh']:,.0f}",
            f"₹{row['annual_loss_inr']:,.0f}",
        ])
    cost_data.append([
        'TOTAL', '—', '—',
        f"₹{cost['annual_loss_inr'].sum():,.0f}"
    ])
    cost_table = Table(cost_data, colWidths=[1.2*inch, 1.2*inch, 1.8*inch, 1.5*inch])
    cost_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A3A6B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#FFE5B4')),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(cost_table)

    # ---------- Recommendations ----------
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("4. Recommendations", h2))
    recs = [
        "<b>INV-003</b> — Likely soiling issue. Schedule panel cleaning within 1 week.",
        "<b>INV-009</b> — Possible sensor fault. Verify sensor calibration.",
        "<b>INV-007</b> — Aging-related degradation. Consider component inspection.",
        "Monitor fleet baseline weekly; any inverter exceeding 2% anomaly rate should be escalated.",
        "Invest in cooling/ventilation if temperature-driven losses persist.",
    ]
    for r in recs:
        story.append(Paragraph(f"• {r}", body))

    # ---------- Footer ----------
    story.append(Spacer(1, 0.4 * inch))
    story.append(Paragraph(
        "<i>Generated by Solar Fleet Intelligence — Kanishka Nandini | "
        "Tata Power Renewable Energy Limited Internship</i>",
        styles['Italic']
    ))

    doc.build(story)
    print(f"✅ Report saved -> {output_path}")


if __name__ == '__main__':
    make_report()