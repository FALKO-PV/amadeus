import os
from datetime import datetime
from django.core.mail import EmailMessage
from dotenv import load_dotenv
import logging

logger = logging.getLogger('main')

load_dotenv("../.env")

BASE_URL = os.getenv("WEBSITE_URL")

HTML_HEADER = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
</head>
<body>
"""

HTML_END = """
</body>
</html>
"""


def send_falko_mail(subject, message, email):
    msg = EmailMessage(
        subject,
        HTML_HEADER + message + HTML_END,
        'forschungsgruppe@falko-pv.de',
        [email],
    )
    msg.content_subtype = "html"
    msg.send(fail_silently=False)
    logger.info(f"E-Mail an {email} gesendet. Betreff: {subject}")


def send_mail(subject, message, to_email_address):
    send_falko_mail(subject, message, to_email_address)


def construct_message(message_content):
    return f"""
    {HTML_HEADER}
    {message_content}
    {HTML_END}
    """

def send_mail_new_nwfg_evaluation(to_email_address, class_evaluation=None, status_code=None, subject=None):
    share_link = f"{BASE_URL}evaluation/{str(class_evaluation)}/share"
    link_status_site = f"{BASE_URL}evaluation/{str(class_evaluation)}/status/{str(status_code)}"
    message_content = f"""
    <p>Sehr geehrte:r Teilnehmer:in,</p>
    <p>Sie haben AMADEUS, die Web-App zur Unterrichtsevaluation von FALKO-PV, erfolgreich initialisiert und Ihre Klasse angelegt.
    Während des Studienverlaufs werden Ihre Schüler:innen verschiedene Fragebögen und Tests ausfüllen. Dabei ist es für uns sehr wichtig, zuordnen zu können, welche Dokumente und Daten jeweils zusammengehören. Dies gelingt uns über ein spezielles Verfahren mit <strong>Bildmustern</strong>, die sich Ihre Schüler:innen selbst erstellen.
    </p>
    <p>Unter nachstehendem Link erhalten Sie einen QR-Code. Mit diesem können Ihre Schüler:innen per Smartphone oder Tablet ein persönliches Muster erstellen. Bitte geben Sie diesen QR-Code nun an Ihre Schüler:innen weiter.</p>
    <p><a href="{share_link}">{share_link}</a>.</p>
    <p>Auf Ihrer Statusseite können Sie den Fortschritt des Initialisierungsprozesses verfolgen. Hier sehen Sie, wie viele Schüler:innen bereits ein Bildmuster erstellt haben. Wenn die Anzahl der eingetragenen Bildmuster der Zahl der Schüler:innen, die an der Studie teilnehmen, entspricht, haben alle erfolgreich ein Muster erstellt.</p>
    <p>Zu <strong>Ihrer persönlichen Statusseite</strong> gelangen Sie, wenn Sie folgenden Link aufrufen:</p>
    <p><a href="{link_status_site}">{link_status_site}</a>.</p>
    <p>Der QR-Code sowie der Link zu Ihrer persönlichen Statusseite bleiben auch bei jeder weiteren Nutzung unverändert. Sie können unter diesem stets den aktuellen Stand bzw. Fortschritt Ihrer Unterrichtsevaluation einsehen.</p>
    <p><strong>Bitte bewahren Sie den Link zu Ihrer persönlichen Statusseite daher sorgfältig auf und geben Sie diesen nicht an Ihre Schüler:innen weiter.</strong></p>
    <p>Sobald alle Schüler:innen registriert sind, können Sie die erste Evaluation starten. Bitte beachten Sie, dass dann keine weiteren Bildmuster erstellt werden können. Sie können für diesen nächsten Schritt also gerne den nächsten Erhebungszeitpunkt abwarten.</p>
    <p>Wir freuen uns, dass Sie an FALKO-PV teilnehmen</p>
    <p>Mit freundlichen Grüßen</p>
    <p>Ihre Forschungsgruppe FALKO-PV</p>
    """

    send_mail("Neue AMADEUS Evaluation erstellt", construct_message(message_content), to_email_address)


def send_mail_new_nwfg_evaluation_round(to_email_address, class_evaluation=None, nwfg_evaluation_part=None, status_code=None, subject=None):
    share_link = f"{BASE_URL}evaluation/{str(class_evaluation)}/share"
    link_status_site = f"{BASE_URL}evaluation/{str(class_evaluation)}/status/{str(status_code)}"
    message_content = f"""
    <p> Sehr geehrte:r Teilnehmer:in,</p>
    <p>Sie haben eine neue Befragungsrunde zur Qualität Ihres Unterrichts im Fach {subject} gestartet. Unter nachstehendem Link erhalten Sie einen QR-Code, über den Ihre Schüler:innen an der Evaluation teilnehmen können:</p>
    <p><a href="{share_link}">{share_link}</a>.</p>
    <p>Bitte geben Sie diesen QR-Code nun an Ihre Schüler:innen weiter. Damit können diese unmittelbar per Smartphone oder Tablet an der aktuellen Evaluationsrunde teilnehmen.</p>
    <p>Bitte beachten Sie, dass die erstellte Befragungsrunde nur so lange für Ihre Schüler:innen verfügbar ist, bis diese von Ihnen beendet oder die nächste Befragungsrunde gestartet wird. Spätere Anmeldeversuche können dann nicht mehr berücksichtigt werden.</p>
    <p>Zu <strong>Ihrer persönlichen Statusseite</strong> gelangen Sie, wenn Sie folgenden Link aufrufen:</p>
    <p><a href="{link_status_site}">{link_status_site}</a>.</p>
    <p>Über diesen können Sie den Fortschritt der aktuellen Befragungsrunde verfolgen, die Evaluation stoppen oder eine neue Befragungsrunde beginnen. Nach Beendigung von zwei Befragungsrunden können Ihre Evaluationsergebnisse über diese persönliche Statusseite abgerufen werden. Hierzu erhalten Sie eine separate Benachrichtigung.
    Der QR-Code sowie der Link zu Ihrer persönlichen Statusseite bleiben auch bei jeder neuen Befragungsrunde unverändert. </p>
    <p><strong>Bitte bewahren Sie den Link zu Ihrer persönlichen Statusseite sorgfältig auf und geben Sie diesen nicht an Ihre Schüler:innen weiter.</strong> Er ermöglicht Ihnen auch das Löschen Ihrer Evaluationsergebnisse.</p>
    <br>
    <p>Wir freuen uns, dass Sie AMADEUS zur Evaluation Ihres Unterrichts verwenden.</p>
    <p>Mit freundlichen Grüßen</p>
    <p>Ihre Forschungsgruppe FALKO-PV</p>
    """

    send_mail("Neue Befragungsrunde einer AMADEUS Evaluation gestartet", construct_message(message_content), to_email_address)


def send_mail_finished_nwfg_evaluation(to_email_address, class_evaluation=None, status_code=None):
    link_status_site = f"{BASE_URL}evaluation/{str(class_evaluation)}/status/{str(status_code)}"
    message_content = f"""
    <p>Sehr geehrte:r Teilnehmer:in,</p>
    <p>Sie haben zwei Befragungsrunden durchgeführt und somit einen Evaluationszeitpunkt abgeschlossen. Sie können ab sofort Ihre Ergebnisse des abgeschlossenen Evaluationszeitpunkts unter <strong>Ihrer persönlichen Statusseite einsehen</strong> und von dort herunterladen:</p>
    <p><a href="{link_status_site}">{link_status_site}</a>.</p>
    <br>
    <p>Herzlichen Dank, dass Sie das Forschungsvorhaben von FALKO-PV unterstützen.</p>
    <p>Mit freundlichen Grüßen</p>
    <p>Ihre Forschungsgruppe FALKO-PV</p>
    """

    send_mail("Erhebungszeitpunkt einer AMADEUS Evaluation abgeschlossen", construct_message(message_content), to_email_address)


def send_mail_new_class_evaluation(to_email_address, class_evaluation, status_code, evaluation_end, subject):
    share_link = f"{BASE_URL}evaluation/{str(class_evaluation)}/share"
    link_status_site = f"{BASE_URL}evaluation/{str(class_evaluation)}/status/{str(status_code)}"
    end_date_and_time = evaluation_end.strftime("%d.%m.%Y um %H:%M Uhr")

    message_content = f"""
    <p>Sehr geehrte:r Nutzer:in der Evaluationsapp AMADEUS,</p>
    <p>Sie haben eine neue Unterrichtsevaluation im Fach {subject} gestartet.</p>
    <p>Unter <strong>nachstehendem Link</strong> erhalten Sie einen QR-Code, über den Ihre Schüler:innen an der Evaluation teilnehmen können:</p>
    <p><a href="{share_link}">{share_link}</a>.</p>
    <p>Bitte beachten Sie, dass die erstellte Evaluation nur bis {end_date_and_time} gültig ist. Spätere Anmeldeversuche können dann nicht mehr berücksichtigt werden.</p> 
    <p>Bitte geben Sie diesen QR-Code nun an Ihre Schüler:innen weiter. Damit können diese unmittelbar per Smartphone oder Tablet an der Evaluation teilnehmen.</p>
    <br>
    <p>Zu <strong>Ihrer persönlichen Statusseite</strong> gelangen Sie, wenn Sie folgenden Link aufrufen:</p>
    <p><a href="{link_status_site}">{link_status_site}</a>.</p> 
    <p>Unter diesem können Sie den Fortschritt Ihrer Evaluation verfolgen und die Evaluation gegebenenfalls vorzeitig beenden. Spätestens nach Ende der Gültigkeitsdauer Ihrer Evaluation können Sie hier auch Ihre Ergebnisse einsehen. Hierzu erhalten Sie eine separate Benachrichtigung.</p>
    <p><strong>Bitte bewahren Sie den Link zu Ihrer persönlichen Statusseite sorgfältig auf und geben Sie diesen nicht an Ihre Schüler:innen weiter.</strong> Er ermöglicht Ihnen auch das Löschen Ihrer Evaluationsergebnisse.</p>
    <br>
    <p>Wir freuen uns, dass Sie AMADEUS zur Evaluation Ihres Unterrichts verwenden.</p>
    <p>Mit freundlichen Grüßen</p>
    <p>Ihre Forschungsgruppe FALKO-PV</p>
    """

    send_mail("Neue AMADEUS Evaluation angelegt", construct_message(message_content), to_email_address)


def send_mail_time_over_class_evaluation(to_email_address, class_evaluation=None, status_code=None):
    link_status_site = f"{BASE_URL}evaluation/{str(class_evaluation)}/status/{str(status_code)}"
    message_content = f"""
    <p>Sehr geehrte:r Nutzer:in der Evaluationsapp AMADEUS,</p>
    <p>der Gültigkeitszeitraum Ihrer Unterrichtsevaluation ist abgelaufen oder Sie haben Ihre Evaluation manuell beendet. Sie können ab sofort Ihre persönlichen Ergebnisse über <strong>Ihre Statusseite</strong> einsehen und von dort herunterladen:</p>
    <p><a href="{link_status_site}">{link_status_site}</a>.</p> 
    <br>
    <p>Wir freuen uns, dass Sie AMADEUS zur Evaluation Ihres Unterrichts verwenden.</p>
    <p>Mit freundlichen Grüßen</p>
    <p>Ihre Forschungsgruppe FALKO-PV</p>
    """

    send_mail("AMADEUS Evaluation abgeschlossen", construct_message(message_content), to_email_address)


def send_mail_finished_class_evaluation(to_email_address, class_evaluation=None, status_code=None):
    link_status_site = f"{BASE_URL}evaluation/{str(class_evaluation)}/status/{str(status_code)}"
    message_content = f"""
    <p>Sehr geehrte:r Nutzer:in der Evaluationsapp AMADEUS,</p>
    <p>der Gültigkeitszeitraum Ihrer Unterrichtsevaluation ist abgelaufen oder Sie haben Ihre Evaluation manuell beendet. Sie können ab sofort Ihre persönlichen Ergebnisse über <strong>Ihre Statusseite</strong> einsehen und von dort herunterladen:</p>
    <p><a href="{link_status_site}">{link_status_site}</a>.</p> 
    <br>
    <p>Wir freuen uns, dass Sie AMADEUS zur Evaluation Ihres Unterrichts verwenden.</p>
    <p>Mit freundlichen Grüßen</p>
    <p>Ihre Forschungsgruppe FALKO-PV</p>
    """

    send_mail("AMADEUS Evaluation abgeschlossen", construct_message(message_content), to_email_address)

