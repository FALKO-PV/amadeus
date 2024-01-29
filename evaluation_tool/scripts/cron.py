from datetime import datetime
from .email_handler import send_mail_time_over_class_evaluation
from evaluation_tool.models import ClassEvaluation
from evaluation_tool.scripts.data_exporter import DataExporter, save_full_data_as_csv
import time
import logging

logger = logging.getLogger('main')


def send_mail_if_classeval_ended():
    finished_class_evaluations = ClassEvaluation.objects.filter(evaluation_end__lte=datetime.now()).filter(
        email_sent_evaluation_end=False)
    for class_evaluation in finished_class_evaluations:
        class_evaluation.email_sent_evaluation_end = True
        send_mail_time_over_class_evaluation(class_evaluation=class_evaluation.pk,
                                             to_email_address=class_evaluation.email,
                                             status_code=class_evaluation.status_url_token)
        class_evaluation.completed = True
        class_evaluation.save()


def export_full_data_as_csv():
    t1 = time.time()
    da = DataExporter()
    data = da.get_full_data()
    now = datetime.now()
    save_full_data_as_csv(data, f"export/export_{now.year}-{now.month}-{now.day}.csv")
    t2 = time.time()
    duration = t2 - t1
    logger.info(f"Finished Data Export in {duration} seconds!")

