import datetime


def time_range_is_valid(start_evaluation_immediately, evaluation_start, evaluation_end):

    # Ignore Seconds / Microseconds
    datetime_now = datetime.datetime.now().replace(second=0, microsecond=0)
    evaluation_start = datetime.datetime.strptime(
        evaluation_start, "%Y-%m-%dT%H:%M").replace(second=0, microsecond=0)
    evaluation_end = datetime.datetime.strptime(
        evaluation_end, "%Y-%m-%dT%H:%M").replace(second=0, microsecond=0)

    if start_evaluation_immediately:
        evaluation_start = datetime_now
        evaluation_end = datetime.datetime.now().replace(
            second=0, microsecond=0) + datetime.timedelta(days=1)
        return True, start_evaluation_immediately, evaluation_start, evaluation_end

    range_length = evaluation_end - evaluation_start

    if evaluation_start + datetime.timedelta(minutes=5) >= datetime_now and evaluation_end >= datetime_now and evaluation_start < evaluation_end and range_length.days <= 30 and range_length.days >= 1:
        return True, start_evaluation_immediately, evaluation_start, evaluation_end

    return False, start_evaluation_immediately, evaluation_start, evaluation_end
