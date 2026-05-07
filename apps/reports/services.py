"""PDF report-card generation using ReportLab."""
from collections import OrderedDict
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from apps.assessments.models import Assessment, Mark


TROPICAL = colors.HexColor("#006400")
TROPICAL_LIGHT = colors.HexColor("#008000")
LIGHT_BG = colors.HexColor("#e6f4e6")


def _styles():
    base = getSampleStyleSheet()
    return {
        "h1": ParagraphStyle("h1", parent=base["Heading1"], textColor=TROPICAL, fontSize=18, alignment=1),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], textColor=TROPICAL_LIGHT, fontSize=12, alignment=1),
        "small": ParagraphStyle("small", parent=base["Normal"], fontSize=8),
        "normal": ParagraphStyle("normal", parent=base["Normal"], fontSize=10),
        "label": ParagraphStyle("label", parent=base["Normal"], fontSize=9, textColor=TROPICAL),
    }


def render_student_report_pdf(student, assessment: Assessment) -> bytes:
    """Return PDF bytes for one student's CBC report card for one assessment."""
    institution = student.institution
    styles = _styles()
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        title=f"{student.full_name} — {assessment.name}",
    )

    story = []

    # ----- Header -----
    header_cells = []
    if institution.logo:
        try:
            header_cells.append(Image(institution.logo.path, width=2 * cm, height=2 * cm))
        except Exception:
            header_cells.append(Paragraph("", styles["normal"]))
    else:
        header_cells.append(Paragraph("", styles["normal"]))

    inst_block = (
        f"<b>{institution.name}</b><br/>"
        f"<font size=8>{institution.address or ''}</font><br/>"
        f"<font size=8>{institution.phone or ''}  {institution.email or ''}</font>"
    )
    if institution.motto:
        inst_block += f"<br/><i><font size=8>{institution.motto}</font></i>"

    header_table = Table(
        [[header_cells[0], Paragraph(inst_block, styles["normal"])]],
        colWidths=[3 * cm, 14 * cm],
    )
    header_table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(header_table)
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("LEARNER PROGRESS REPORT", styles["h1"]))
    story.append(Paragraph(f"{assessment.name} · {assessment.session.name}", styles["h2"]))
    story.append(Spacer(1, 0.4 * cm))

    # ----- Student details -----
    details = [
        ["Name", student.full_name, "Adm. No.", student.admission_number],
        [
            "Class",
            student.class_level.name + (f" {student.stream.name}" if student.stream else ""),
            "Gender",
            student.get_gender_display() if student.gender else "—",
        ],
    ]
    t = Table(details, colWidths=[2.5 * cm, 6 * cm, 2.5 * cm, 6 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
                ("BACKGROUND", (2, 0), (2, -1), LIGHT_BG),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))

    # ----- Marks table -----
    marks_qs = (
        Mark.objects.filter(assessment=assessment, student=student)
        .select_related("subject", "teacher")
        .order_by("subject__name")
    )
    table_data = [["Subject", "Marks", f"/{assessment.max_marks}", "Rubric", "Points", "Teacher"]]
    total = 0
    n = 0
    points_total = 0
    for m in marks_qs:
        teacher = m.teacher.full_name if m.teacher else "—"
        table_data.append(
            [
                m.subject.name,
                f"{m.marks:g}",
                f"{assessment.max_marks}",
                m.rubric_label or "—",
                f"{m.points}",
                teacher,
            ]
        )
        total += float(m.marks)
        n += 1
        points_total += int(m.points)

    if n == 0:
        table_data.append(["—", "—", "—", "—", "—", "No marks recorded yet."])
        avg_marks = 0.0
        avg_pts = 0.0
    else:
        avg_marks = total / n
        avg_pts = points_total / n

    marks_table = Table(table_data, colWidths=[5 * cm, 2 * cm, 1.5 * cm, 2 * cm, 2 * cm, 5 * cm])
    marks_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TROPICAL),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BOX", (0, 0), (-1, -1), 0.5, TROPICAL),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("ALIGN", (1, 1), (4, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(marks_table)
    story.append(Spacer(1, 0.4 * cm))

    # ----- Summary -----
    summary_data = [
        ["Subjects taken", str(n)],
        ["Total marks", f"{total:g} / {n * assessment.max_marks if n else 0}"],
        ["Average marks", f"{avg_marks:.2f}"],
        ["Average points", f"{avg_pts:.2f}"],
    ]
    summary = Table(summary_data, colWidths=[8 * cm, 9.5 * cm])
    summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_BG),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOX", (0, 0), (-1, -1), 0.4, colors.lightgrey),
                ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(summary)
    story.append(Spacer(1, 0.6 * cm))

    # ----- Signatures -----
    sig_data = [
        ["Class Teacher: __________________________", "Principal: __________________________"],
        ["Date: ___________", "Date: ___________"],
    ]
    sig = Table(sig_data, colWidths=[8.5 * cm, 9 * cm])
    sig.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 9)]))
    story.append(sig)
    story.append(Spacer(1, 0.4 * cm))

    if institution.vision:
        story.append(
            Paragraph(
                f"<i><font color='#008000'>Vision:</font> {institution.vision}</i>",
                styles["small"],
            )
        )

    doc.build(story)
    return buf.getvalue()
