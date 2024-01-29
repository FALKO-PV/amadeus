from evaluation_tool.scripts.data_analysis import create_dim_barplot
from datetime import date
import matplotlib.pyplot as plt
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, PageBreak, Image
from reportlab.rl_config import defaultPageSize
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def gather_data_from_dict(string_key, data_dict):
    out_array = []
    for value in data_dict.values():
        out_array.append([value["name"], value[string_key]])

    return out_array


class PdfWriter:
    """
    ToDo: Description
    """
    def __init__(self, buffer, data_dict, subject, count):
        self.datadict = data_dict
        self.buffer = buffer
        self.subject = subject
        self.count = count

        self.subdimensions = {
            "1": {
                "title": "1. Auswahl, Thematisierung und Sequenzierung von Inhalten und Fachmethoden",
                "text": """
                Lerngegenstände und Fachmethoden sind für den Unterricht von besonderer Bedeutung. 
                Deshalb werden hier Aspekte wie Altersangemessenheit, Lebensweltbezug, Relevanz, Strukturierung 
                und didaktische Aufbereitung beachtet.
                """
            },
            "2": {
                "title": "2. Kognitive Aktivierung",
                "text": """
                Der Anregungsgehalt des Unterrichts zu selbstständigem vertieftem Nachdenken, zu einer elaborierten 
                Auseinandersetzung mit dem Lerngegenstand und zu metakognitiven Prozessen bei Schüler:innen sind 
                Facetten kognitiver Aktivierung, die hier unter anderem evaluiert werden.
                """
            },
            "3": {
                "title": "3. Unterstützung des Übens",
                "text": """
                Wiederholung und Variationsreichtum sind nur zwei Aspekte des Übens, die diese Dimension umfasst. 
                Eine weitere Facette stellt der konstruktive Umgang mit hierbei auftretenden Fehlern dar.
                """
            },
            "4": {
                "title": "4. Formatives Assessment",
                "text": """
                Eine klare Ausrichtung der Beurteilung auf die zu erlernenden Kompetenzen, eine regelmäßige 
                Überprüfung des Verständnisses der Schüler:innen und ein differenziertes Feedback an die 
                Schüler:innen  sind einige Aspekte, die zu einem lernförderlichen formativen Assessment gehören.
                """
            },
            "5": {
                "title": "5. Unterstützung des Lernens aller Schüler:innen",
                "text": """
                Die aktive Beteiligung und Mitwirkung aller Schüler:innen unter Berücksichtigung ihrer 
                individuellen Lernvoraussetzungen und -bedürfnisse ist ein weiteres Kriterium qualitätsvollen 
                Unterrichts. Hierzu zählen unter anderem ein produktives Lernumfeld ebenso wie Ansätze innerer 
                und äußerer Differenzierung.
                """
            },
            "6_1": {
                "title": "6a. Sozio-emotionale Unterstützung: Beziehung Lehrkraft Schüler:innen",
                "text": """
                Ein gutes Klassenklima, das durch wertschätzende Aufmerksamkeit, gegenseitigen Respekt und einen 
                freundlichen Umgangston geprägt ist, gilt als wesentliche Determinante von Unterrichtsqualität. <br/>
                Es lässt sich einerseits durch die <i>Interaktion zwischen Lehrperson und Schüler:innen</i> beschreiben.
                """
            },
            "6_2": {
                "title": "6b. Sozio-emotionale Unterstützung: Beziehung der Schüler:innen untereinander",
                "text": """
                Andererseits spielen auch die <i>Beziehungen der Schüler*innen untereinander</i> eine große Rolle.
                """
            },
            "7_1": {
                "title": "7a. Klassenführung: Verhaltensmanagement",
                "text": """
                Unter dem Aspekt der Klassenführung werden im Allgemeinen zwei Gütekriterien
                gefasst: Verhaltens- und Zeitmanagement.<br/>
                Die Bewertung des <i>Verhaltensmanagements</i> berücksichtigt unter anderem den Umgang mit 
                auftretenden Unterrichtsstörungen, die Prävention von Unterbrechungen des Unterrichts und auch die 
                Kommunikation von Verhaltensregeln.
                """
            },
            "7_2": {
                "title": "7b. Klassenführung: Zeitmanagement",
                "text": """
                In das <i>Zeitmanagement</i> gehen Prozessmerkmale wie Unterrichtstempo und -organisation ein.
                """
            },
            "8": {
                "title": "8. Ästhetisch-emotionales Lernen",
                "text": """
                Unterricht zielt nicht nur auf das Erreichen kognitiver Lernziele, sondern ebenso auf 
                ästhe- tisch-emotionales Lernen ab. Aspekte wie die Anregung ästhetischer Wahrnehmungsprozesse, die 
                Schaffung von Freiräumen für emotionale Erfahrungen und eine kritische Reflexion über Gefahren 
                ästhetisch-emotionaler Beeinflussung werden hier abgebildet.
                """
            },
            "9": {
                "title": "9. Fachspezifische Qualitätsmerkmale",
                "text": "Darüber hinaus hat jedes Fach seine eigenen Qualitätsmerkmale.",
                "Deutsch": """
                In Deutsch sind dies beispielsweise Rückmeldung hinsichtlich Tiefenstrukturen, Berücksichtigung eines
                erweiterten Textbegriffs oder vielfältige Produktionsgelegenheiten.
                """,
                "Englisch": """
                In Englisch sind dies beispielsweise Kommunikation der Lehrkraft in sprachlich und fachlich korrektem 
                und/aber dem Lernstand angepasstem Englisch, Schaffung und Nutzung interdisziplinärer Bezüge zwischen 
                (schulischen) Fremdsprachen als Lerngelegenheiten oder Schaffung hoher Sprechanteile.
                """,
                "Evangelische Religion": """
                In Evangelischer Religion sind dies beispielsweise Authentizität, Dialogorientierung, Interreligiöses 
                Lernen, Subjektorientierung oder Seelsorge.
                """,
                "Mathematik": """
                In Mathematik sind dies beispielsweise Gendersensibler Unterricht, Modellierung, (Historische) 
                Kontextualisierung oder Sinnvolle Nutzung (digitaler) Medien.
                """,
                "Latein": """
                In Latein sind dies beispielsweise Verwendung der Sprache als Reflexionsgegenstand, Aktiver Gebrauch 
                der Sprache als Kommunikationsmedium, Auswahl und Berücksichtigung bedeutsamer Rezeptionsdokumente
                oder Kritische Reflexion über die gegenwärtige (und zukünftige) kulturelle wie auch gesellschaftliche 
                Relevanz des Fachs.
                """,
                "Musik": """
                In Musik sind dies beispielsweise Bewahrung der Würde des Einzelnen und Umgang mit Fehlern, 
                Raum- und Materialmanagement oder kognitiv-motorische Aktivierung.
                """,
            }
        }

    def get_eval_pdf(self):
        plt.switch_backend('Agg')
        styles = getSampleStyleSheet()
        PAGE_HEIGHT = defaultPageSize[1]
        PAGE_WIDTH = defaultPageSize[0]
        plt_cm = 1 / 2.54
        fig_width = 13 * plt_cm
        fig_height = 2 * plt_cm

        # register Frutiger Next Fonts
        pdfmetrics.registerFont(TTFont('FrutigerNextRegular', 'static/fonts/FrutigerNextLTW1G-Regular.ttf'))
        pdfmetrics.registerFont(TTFont('FrutigerNextItalic', 'static/fonts/FrutigerNextLTW1G-Italic.ttf'))
        pdfmetrics.registerFont(TTFont('FrutigerNextBold', 'static/fonts/FrutigerNextLTW1G-Bold.ttf'))

        today = date.today()
        eval_date = today.strftime("%d.%m.%Y")

        Title = "Auswertung Ihrer Unterrichtsevaluation"
        pageinfo = f"Evaluation im Fach {self.subject} | {eval_date}"

        space = Spacer(1, 0.3 * cm)

        doc = SimpleDocTemplate(self.buffer)

        def myFirstPage(canvas, doc):
            canvas.saveState()
            # Logo on top of page
            canvas.drawImage('static/img/foerderung/full_header_logo.png', 5 * cm, 22 * cm, width=PAGE_WIDTH / 2,
                             preserveAspectRatio=True, mask=None)
            canvas.setFont('FrutigerNextBold', 20)
            canvas.drawCentredString(PAGE_WIDTH / 2.0, PAGE_HEIGHT - 108, Title)
            canvas.setFont('FrutigerNextRegular', 9)
            canvas.drawString(cm, 0.75 * cm, "Seite %d %s" % (doc.page, pageinfo))
            canvas.restoreState()

        def myLaterPages(canvas, doc):
            canvas.saveState()
            canvas.setFont('FrutigerNextRegular', 9)
            canvas.drawString(cm, 0.75 * cm, "Seite %d %s" % (doc.page, pageinfo))
            canvas.restoreState()

        def create_explanation_visualisation_paragraph(heading, text, key, story, style, spacer, subject_text=""):
            # italic heading of subdimension title

            # individual styling for subdims 6a, 7a, 6b and 7b:
            if key == "6_1":
                head = heading.split()
                story.append(
                    Paragraph(f"<i>{head[0][0]}. {head[1]} {head[2][:-1]}</i>")
                )
            elif key == "6_2":
                pass
            elif key == "7_1":
                head = heading.split()
                story.append(
                    Paragraph(f"<i>{head[0][0]}. {head[1][:-1]}</i>")
                )
            elif key == "7_2":
                pass
            else:
                story.append(
                    Paragraph(f"<i>{heading}</i>", style)
                )
            story.append(spacer)
            story.append(Paragraph(text + subject_text))
            story.append(Spacer(1, 0.5 * cm))

            # create table
            table_data = [["Mittelwert:", str(round(self.datadict[key]["mean"], 1)).replace(".", ","),
                           "Median:", str(round(self.datadict[key]["median"], 1)).replace(".", ",")],
                          ["Standardabweichung:", str(round(self.datadict[key]["std"], 1)).replace(".", ","),
                           "Antwortanzahl:", sum(self.datadict[key]["counts"][1])]]
            t = Table(table_data)
            story.append(t)
            story.append(spacer)

            drawing = create_dim_barplot(self.datadict, key, fig_width, fig_height)
            story.append(Image(drawing))

            # --------------- individual Layout per dimensions
            if key in ["3", "7_2"]:
                story.append(PageBreak())
            elif key == "6_1":
                story.append(Spacer(1, 1.2 * cm))
            else:
                story.append(Spacer(1, 1.5 * cm))

        def build_pdf_from_story():
            Story = [Spacer(1, 2 * cm)]
            style = styles["Normal"]
            styleH3 = styles["h3"]

            ##------------- Einleitung ---------------------------------

            anrede = "Sehr geehrte Lehrkraft,"

            if self.count == 0:
                count_str = f"Daran nahm noch kein:e Schüler:in teil, der/die 25 % der Evaluation beantwortet hat und " \
                            f"damit in der Auswertung berücksichtigt werden konnte (Stand: <b>{eval_date}</b>)."
            elif self.count == 1:
                count_str = f"<b>Ein:e</b> Schüler:in beantwortete mindestens 25 % der Evaluation (Stand: " \
                            f"<b>{eval_date}</b>). Nur diese:r wurde in der Auswertung berücksichtigt."
            else:
                count_str = f"<b>{self.count}</b> Schüler:innen beantworteten mindestens 25 % der Evaluation " \
                            f"(Stand: <b>{eval_date}</b>). Nur diese werden in der Auswertung berücksichtigt."

            if self.subject == "Allgemeine Lehrevaluation":
                einleitung = f"""hiermit erhalten Sie die Ergebnisse Ihrer digitalen Unterrichtsevaluation mithilfe von
                 AMADEUS. {count_str}"""
            else:
                einleitung = f"""hiermit erhalten Sie die Ergebnisse Ihrer digitalen Unterrichtsevaluation im 
                Fach <b>{self.subject}</b> mithilfe von AMADEUS. {count_str}"""

            p_anrede = Paragraph(anrede, style)
            p_einleitung = Paragraph(einleitung, style)
            Story.append(p_anrede)
            Story.append(space)
            Story.append(p_einleitung)
            Story.append(space)

            ##------------- Erklärungen ----------------------------------

            Story.append(Paragraph("Erläuterungen zur Evaluation und zur Auswertung", styleH3))

            Story.append(Paragraph("<i>Theoretischer Hintergrund</i>", style))

            Story.append(space)

            hintergrund = """
            Der Unterrichtsevaluation mittels AMADEUS liegt ein theoretisches Modell zu Unterrichtsqualität zugrunde, 
            das auf aktuellen wissenschaftlichen Erkenntnissen basiert. Dieses beschreibt Unterrichtsqualität im 
            Wesentlichen durch neun Dimensionen, die auf den folgenden Seiten jeweils kurz erläutert werden. 
            Zu jeder dieser Dimensionen gehören weitere inhaltlich unterschiedliche Facetten, die auf Teilaspekte des 
            Unterrichts abheben und durch einzelne Aussagen (Items) in der Evaluation erfasst werden. Aus 
            Gründen der Einfachheit und Übersichtlichkeit erhalten Sie Ihre Rückmeldung aber in der Regel auf der Ebene 
            einer Dimension; in Bezug auf die zwei Dimensionen <i>sozio-emotionale Unterstützung</i> und 
            <i>Klassenführung</i> möchten wir Ihnen jedoch auch einen etwas differenzierteren Einblick in Ihre 
            Ergebnisse bieten.
            """

            p_hintergrund = Paragraph(hintergrund, style)
            Story.append(p_hintergrund)
            Story.append(space)

            Story.append(Paragraph("<i>Ergebnisdarstellung und Auswertung</i>", style))
            Story.append(space)

            erkl_darstell = """
            Jede Dimension wird im Folgenden zunächst anhand ihrer wesentlichen Facetten kurz beschrieben. Zu jeder 
            Facette wurden Ihren Schüler:innen Aussagen (Items) vorgelegt, die sie auf einer Skala mit fünf Stufen von 
            &bdquo;Trifft nicht zu (= 1)&ldquo; bis &bdquo;Trifft zu&ldquo; (= 5) bewerten sollten. Pro Dimension wurde 
            auf Grundlage der individuellen Bewertungen der Schüler:innen die durchschnittliche Gesamteinschätzung aller 
            Schüler:innen ermittelt. Die Zahlen in bzw. über den Säulen der nachstehenden Graphiken repräsentieren die 
            prozentualen Anteile aller Bewertungen, die auf die jeweilige Stufe (Antwortkategorie) entfallen. Folgende 
            Kenngrößen werden darüber hinaus pro Dimension angegeben:
            """

            p_erkl_darstell = Paragraph(erkl_darstell, style)
            Story.append(p_erkl_darstell)
            Story.append(space)

            erkl_mean = """
                        Der <b>Mittelwert</b> (arithmetisches Mittel) ist ein Maß für die zentrale Tendenz der 
                        Antworten. Er gibt an, wie die Schüler:innen die jeweilige Dimension durchschnittlich 
                        bewerteten, d. h., wie sehr sie den darauf bezogenen Aussagen im Mittel zustimmten oder diese 
                        ablehnten. Der mögliche Wertebereich liegt zwischen 1,0 (&bdquo;Trifft nicht zu&ldquo;) und 5,0 
                        (&bdquo;Trifft zu&ldquo;); der theoretisch bei durchschnittlicher Merkmalsausprägung zu 
                        erwartende Wert ist 3,0 (&bdquo;Teils, teils&ldquo;).
                        """
            p_erkl_mean = Paragraph(erkl_mean, style)
            Story.append(p_erkl_mean)
            Story.append(space)

            erkl_median = """
                        Der <b>Median</b> ist ebenfalls ein Maß für die zentrale Tendenz der Antworten, lässt aber 
                        gegenüber dem Mittelwert einen Rückschluss auf die Verteilung der Antworten zu. Unter bzw. 
                        über seinem Wert liegt nämlich immer die gleiche Anzahl an Bewertungen aller Schüler:innen. Sein 
                        möglicher Wertebereich erstreckt sich dabei von 1,0 (&bdquo;Trifft nicht zu&ldquo;) bis 5,0 
                        (&bdquo;Trifft zu&ldquo;); der theoretisch bei durchschnittlicher Merkmalsausprägung zu 
                        erwartende Wert ist 3,0 (&bdquo;Teils, teils&ldquo;).
                        """
            p_erkl_median = Paragraph(erkl_median, style)
            Story.append(p_erkl_median)
            Story.append(space)

            erkl_sd = """
                        Die <b>Standardabweichung</b> ist ein Maß für die Streuung der Antworten um den Mittelwert. 
                        Liegt eine hohe Standardabweichung vor, so waren sich die Schüler:innen bei der Bewertung der 
                        Merkmals- ausprägung eher uneinig. Ist die Standardabweichung gering, waren sich die Schüler:innen 
                        bei der Bewertung eher einig.
                        """
            p_erkl_sd = Paragraph(erkl_sd, style)
            Story.append(p_erkl_sd)
            Story.append(space)

            erkl_count = """
                        Bei der <b>Antwortanzahl</b> wird die Anzahl aller Antworten genannt, die bei dieser Dimension 
                        gegeben wurden. Da eine Dimension durch mehrere Items erfasst wird, entspricht die Antwortanzahl 
                        somit der Summe der Antworten auf alle Items dieser Dimension.
                        """
            p_erkl_count = Paragraph(erkl_count, style)
            Story.append(p_erkl_count)

            item_erkl = """
                        Die nachstehenden Auswertungen und Graphiken repräsentieren jeweils die Einschätzungen Ihrer 
                        Schüler:innen zu den verschiedenen Dimensionen der Qualität Ihres Unterrichts.
                        """

            p_item_erkl = Paragraph(item_erkl, style)

            Story.append(space)
            Story.append(p_item_erkl)

            Story.append(PageBreak())

            ##------------- Subdimensionen -------------------------------
            Story.append(Paragraph("Auswertung der Dimensionen", styleH3))

            subdimensions = self.subdimensions

            if self.subject == "Allgemeine Lehrevaluation":
                keys = list(subdimensions.keys())[:-2]
            else:
                keys = list(subdimensions.keys())

            for key in keys:
                cur_subject = ""
                if int(key[0]) == 9:
                    cur_subject = subdimensions[key][self.subject]
                    # heading = subdimensions[key]["title"] + f" im Fach {cur_subject}"

                # wenn dim 6 oder 7, dann nur Kurztitel
                # KEIN Titel bei 6b oder 7b

                create_explanation_visualisation_paragraph(
                    subdimensions[key]["title"],
                    subdimensions[key]["text"],
                    story=Story, style=style, spacer=space, key=key, subject_text=cur_subject
                )

            ## ------------ Kontaktinfos: --------------------
            Story.append(Spacer(1, 4 * cm))

            Story.append(Paragraph(
                """
                Sollten Sie zu Ihren Umfrageergebnissen Rückfragen oder Anmerkungen haben, gerne mehr über die Web-App 
                AMADEUS wissen wollen oder am weiteren Verlauf des Forschungsvorhabens von FALKO-PV interessiert sein, 
                können Sie sich jederzeit via E-Mail an die Forschungsgruppe 
                <link href='mailto:falko-pv@ur.de?subject=Anfrage bzgl. Auswertung AMADEUS' color='blue'>
                falko-pv@ur.de</link> wenden oder die Homepage <link href='https://falko-pv.de' color='blue'>
                falko-pv.de</link> besuchen.
                """, style
            ))

            Story.append(PageBreak())

            Story.append(Paragraph("Kontakt", styleH3))

            contact_data = [
                        ["Universität Regensburg"],
                        ["Methoden der empirischen Bildungsforschung"],
                        ["BMBF-Nachwuchsforschungsgruppe FALKO-PV"],
                        ["Projektleitung Dr. Alfred Lindl"],
                        [""],
                        ["Sedanstraße 1"],
                        ["93055 Regensburg"],
                        ["Telefon: +49 (0)941 943 7633"],
                        ["Büro: 1.OG / Räume 138B, 139 & 140"],
                    ]
            contact_t = Table(contact_data)

            Story.append(contact_t)

            doc.build(Story, onFirstPage=myFirstPage, onLaterPages=myLaterPages)

        build_pdf_from_story()
        self.buffer.seek(0)
        return self.buffer
