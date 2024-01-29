import io

from reportlab.graphics import renderPDF

from evaluation_tool.scripts.data_analysis import create_bullet_graph, DataAnalyzer
import pandas as pd
from io import BytesIO
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.platypus import Paragraph, SimpleDocTemplate, Frame, Image, Table, TableStyle
import reportlab.rl_config as config
from svglib.svglib import svg2rlg


def create_test_pdf(file_name: str, evaluation_id, subject, is_nwfg=False):
    pdf_file = SimpleDocTemplate(file_name)

    # create and get statistical data
    da = DataAnalyzer(evaluation_id)
    data = da.get_stats_per_dim()

    # define styles, shapes, margins, etc.
    styles = getSampleStyleSheet()
    styleN = styles["Normal"]
    styleH1 = styles["Heading1"]
    styleH3 = styles["Heading3"]
    story = []
    width, height = A4
    margin = 1.2 * cm

    # define dimension independent paragraphs
    first_heading = Paragraph("Auswertung ihrer Unterrichtsevaluation", styleH1)
    story.append(first_heading)

    info_heading = Paragraph("Informationen zur Darstellung der Ergebnisse", styleH3)
    story.append(info_heading)

    info_text = Paragraph(
        """
        <para firstLineIndent = 24>
        Die Ergebnisse der digitalen Unterrichtsevaluation werden Ihnen in neun Dimensionen von Unterrichtsqualität
        berichtet, die – wie nachstehend erläutert – jeweils unterschiedliche inhaltliche Facetten umfassen. Aus
        Gründen der Übersichtlichkeit erhalten Sie Ihre Rückmeldung in der Regel auf Dimensionsebene; in zwei
        Fällen möchten wir Ihnen jedoch auch einen etwas differenzierteren Einblick in Ihre Ergebnisse gewähren.
        </para>
        """, styleN
    )
    story.append(info_text)

    feedback_heading = Paragraph("Rückmeldung zur Ihrem Unterricht", styleH3)
    story.append(feedback_heading)

    # define dimension paragraphs
    dim_texts = {
        "1": Paragraph("""
        Lerngegenstände und Fachmethoden sind für den Unterricht von besonderer Bedeutung. Deshalb werden hier 
        Aspekte wie Altersangemessenheit, Lebensweltbezug, Relevanz, Strukturierung und didaktische Aufbereitung 
        berücksichtigt.
        """, styleN),
        "2": Paragraph("""
        Der Anregungsgehalt des Unterrichts zu selbstständigem vertieftem Nachdenken, zu einer elaborierten 
        Auseinandersetzung mit dem Lerngegenstand und zu metakognitiven Prozessen bei Schüler:innen sind Facetten 
        kognitiver Aktivierung, die hier unter anderem evaluiert werden.
        """, styleN),
        "3": Paragraph("""
        Wiederholung und Variationsreichtum sind nur zwei Aspekte des Übens, die diese Dimension umfasst. Auch ein 
        konstruktiver Umgang mit hierbei auftretenden Fehlern zählt hierzu.
        """, styleN),
        "4": Paragraph("""
        Eine klare Ausrichtung der Beurteilung auf die zu erlernenden Kompetenzen, eine regelmäßige Überprüfung des 
        Verständnisses der Schüler:innen und ein differenziertes Feedback an die Schüler:innen sind einige Aspekte, 
        die zu einem lernförderlichen formativen Assessment gehören.
        """, styleN),
        "5": Paragraph("""
        Die aktive Beteiligung und Mitwirkung aller Schüler:innen unter Berücksichtigung ihrer individuellen 
        Lernvoraussetzungen und -bedürfnisse ist ein weiteres Kriterium qualitätsvollen Unterrichts. Hierzu zählen 
        unter anderem ein produktives Lernumfeld ebenso wie Ansätze innerer und äußerer Differenzierung.
        """, styleN),
        "6": Paragraph("""
        Ein gutes Klassenklima, das durch wertschätzende Aufmerksamkeit, gegenseitigen Respekt und einen freundlichen 
        Umgangston geprägt ist, gilt als wesentliche Determinante von Unterrichtsqualität.
        """, styleN),
        "6_1": Paragraph("""
        Es lässt sich einerseits durch die <i>Interaktionen zwischen Lehrperson und Schüler:innen</i> beschreiben.
        """, styleN),
        "6_2": Paragraph("""
        Andererseits spielen auch die <i>Beziehungen der Schüler:innen untereinander</i> eine große Rolle.
        """, styleN),
        "7": Paragraph("""
        Unter dem Aspekt der Klassenführung werden im Allgemeinen zwei Gütekriterien
        gefasst: Verhaltens- und Zeitmanagement.
        """, styleN),
        "7_1": Paragraph("""
        Die Bewertung des <i>Verhaltensmanagements</i> berücksichtigt unter anderem den Umgang mit auftretenden 
        Unterrichtsstörungen, die Prävention von Unterbrechungen des Unterrichts und auch die Kommunikation von 
        Verhaltensegeln.
        """, styleN),
        "7_2": Paragraph("""
        In das <i>Zeitmanagement</i> gehen Prozessmerkmale wie Unterrichtstempo und -organisation ein.
        """, styleN),
        "8": Paragraph("""
        Unterricht zielt nicht nur auf das Erreichen kognitiver Lernziele, sondern ebenso auf ästhetisch-emotionales 
        Lernen ab. Aspekte wie die Anregung ästhetischer Wahrnehmungsprozesse, die Schaffung von Freiräumen für 
        emotionale Erfahrungen und eine kritische Reflexion über Gefahren ästhetisch-emotionaler Beeinflussung werden 
        hier abgebildet.
        """),
        "9": {
            "Deutsch": Paragraph("""
            Darüber hinaus hat jedes Fach seine eigenen Qualitätsmerkmale. In Deutsch sind dies beispielsweise ...
            """, styleN),
            "Englisch": Paragraph("""
            Darüber hinaus hat jedes Fach seine eigenen Qualitätsmerkmale. In Englisch sind dies beispielsweise ...
            """, styleN),
            "Evangelische Religion": Paragraph("""
            Darüber hinaus hat jedes Fach seine eigenen Qualitätsmerkmale. In Evangelischer Religion sind dies 
            beispielsweise ...
            """, styleN),
            "Mathematik": Paragraph("""
            Darüber hinaus hat jedes Fach seine eigenen Qualitätsmerkmale. In Mathematik sind dies 
            beispielsweise ...
            """, styleN),
            "Latein": Paragraph("""
            Darüber hinaus hat jedes Fach seine eigenen Qualitätsmerkmale. In Latein sind dies beispielsweise ...
            """, styleN),
            "Musik": Paragraph("""
            Darüber hinaus hat jedes Fach seine eigenen Qualitätsmerkmale. In Musik sind dies beispielsweise ...
            """, styleN),
        }
    }

    # create story
    for key in data.keys():
        # at dim 6 and 7 there are sub dims to be reported with text and stats
        if len(key) > 1:
            story.append(dim_texts[key])
            # ToDo: plus stats
        # at dim 1 to 5 and 8 the text has to be shown with the stats
        elif (1 <= int(key) < 6) or int(key) == 8:
            story.append(Paragraph(f"{key}. <i>{data[key]['name']}</i>"))
            stats_table = Table([
                ["Anzahl Antworten:", sum(data[key]['counts'][1]), "Mittelwert:", data[key]['mean']],
                ["Standardabweichung:", data[key]['std'], "Median:", data[key]['median']],
            ])
            stats_table.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), colors.red)
            ]))
            text_plus_stats = Table([
                [dim_texts[key], stats_table]
            ])
            text_plus_stats.setStyle(TableStyle([
                ('GRID', (0, 0), (-1, -1), colors.black),
                ('VALIGN', (0, 1), (0, 1), 'TOP'),
                ('TEXTCOLOR', (0, 1), (0, 1), colors.green),
            ]))
            story.append(text_plus_stats)
        # at dim 6 and 7 only the text without stats should be shown
        elif 6 <= int(key) <= 7:
            story.append(Paragraph(f"{key}. <i>{data[key]['name']}</i>"))
            story.append(dim_texts[key])
        elif int(key) == 9:
            story.append(Paragraph(f"{key}. <i>Fachspezifische Qualitätsmerkmale im Unterrichtsfach {subject}</i>"))
            story.append(dim_texts[key][subject])
            # ToDo: plus stats

    final_text = Paragraph("""
    Sollten Sie zu Ihren Umfrageergebnissen Rückfragen oder Anmerkungen haben, gerne mehr über das Vorhaben FALKO-PV 
    wissen wollen oder am weiteren Projektverlauf interessiert sein, können Sie sich jederzeit via E-Mail an 
    falko-pv@ur.de melden oder unsere Homepage <a href='www.falko-pv.de'>www.falko-pv.de</a> besuchen.
    """, styleN)
    story.append(final_text)

    # imgdata = BytesIO()
    # imgdata = create_bullet_graph(counts, "Kognitive Aktivierung", 3.5, 0.8, imgdata)
    # imgdata.seek(0)
    #
    # drawing = svg2rlg(imgdata)

    # c = Canvas(file_name)

    # renderPDF.draw(drawing, c, margin, height - margin - 7 * cm)

    # f = Frame(margin, margin, 19 * cm, 27 * cm, showBoundary=1)
    # f.addFromList(story, c)
    # c.save()

    pdf_file.build(story)
