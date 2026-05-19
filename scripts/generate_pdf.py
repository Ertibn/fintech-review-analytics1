from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

in_md = 'final_report.md'
out_pdf = 'final_report.pdf'

styles = getSampleStyleSheet()
styleN = styles['Normal']
styleH = styles['Heading1']

# Read markdown and split into blocks separated by blank lines
with open(in_md, 'r', encoding='utf-8') as f:
    lines = f.read().splitlines()

story = []
for line in lines:
    if line.strip().startswith('# '):
        story.append(Paragraph(line.strip('# ').strip(), styleH))
        story.append(Spacer(1, 12))
    elif line.strip().startswith('## '):
        p = Paragraph(line.strip('# ').strip(), styles['Heading2'])
        story.append(p)
        story.append(Spacer(1, 8))
    elif line.strip().startswith('### '):
        p = Paragraph(line.strip('# ').strip(), styles['Heading3'])
        story.append(p)
        story.append(Spacer(1, 6))
    elif line.strip() == '':
        story.append(Spacer(1, 6))
    else:
        # escape problematic characters
        text = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        story.append(Paragraph(text, styleN))

# Build PDF
pdf = SimpleDocTemplate(out_pdf, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=60, bottomMargin=40)
pdf.build(story)
print(f"Saved {out_pdf}")
