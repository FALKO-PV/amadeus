from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.utils.timezone import now
import uuid

# BASELINE #


class ClassEvaluation(models.Model):

    class Meta:
        verbose_name = 'ClassEvaluation'
        verbose_name_plural = 'ClassEvaluations'

    class_evaluation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    evaluation_start = models.DateTimeField(
        blank=False,
        null=False
    )
    evaluation_end = models.DateTimeField(
        blank=False,
        null=False
    )
    start_evaluation_immediately = models.BooleanField(
        blank=False,
        default=False
    )
    creation_timestamp = models.DateTimeField(
        default=now,
        blank=False,
        null=False
    )
    evaluation_stopped_timestamp = models.DateTimeField(
        blank=True,
        null=True
    )
    teacher_name = models.CharField(
        blank=True,
        max_length=200
    )
    email = models.EmailField(blank=True)

    subject = models.CharField(
        blank=False,
        max_length=25,
        validators=[RegexValidator(
            regex=r'^(Allgemeine Lehrevaluation|Deutsch|Englisch|Evangelische Religion|Latein|Mathematik|Musik)$',
        ), ]
    )
    status_url_token = models.UUIDField(default=uuid.uuid4)

    context_of_use = models.CharField(
        max_length=100,
        choices=[
            ('US', ' ... meiner Unterrichtstätigkeit an Schulen an.'),
            ('UA', ' ... meiner außerschulischen Unterrichtstätigkeit an.'),
            ('P', ' ... eines Praktikums während meines Lehramtsstudiums an.'),
            ('T', ' ... von Ansichts- und Testzwecken an.'),
            ('S', ' ... eines anderen Kontexts an.'),
        ],
        default="",
    )
    
    email_sent_evaluation_end = models.BooleanField(
        blank=False,
        default=False
    )
    completed = models.BooleanField(
        blank=False,
        default=False
    )
    deleted = models.BooleanField(
        blank=False,
        default=False
    )


class SingleEvaluation(models.Model):

    class Meta:
        verbose_name = 'SingleEvaluation'
        verbose_name_plural = 'SingleEvaluations'

    single_evaluation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    completed = models.BooleanField(
        blank=False,
        default=False
    )
    class_evaluation = models.ForeignKey(
        ClassEvaluation,
        on_delete=models.CASCADE
    )


class Item(models.Model):
    class Meta:
        verbose_name = 'Item'
        verbose_name_plural = 'Items'
        ordering = ('question_index_for_student',)

    item_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    code = models.CharField(
        blank=False,
        max_length=16,
    )
    recoded = models.BooleanField(
        blank=False,
        null=False,
        default=True,
    )
    selected_likert_item = models.IntegerField(
        validators=[MaxValueValidator(5), MinValueValidator(1)],
        blank=True,
        null=True
    )
    single_evaluation = models.ForeignKey(
        SingleEvaluation,
        on_delete=models.CASCADE
    )
    question_index_for_student = models.IntegerField(
        null=False,
        blank=False,
        default=1
    )


# STUDY #

class NWFGEvaluation(models.Model):

    SCHOOL_TYPE = {
        "GYM": "Gymnasium",
        "RE": "Realschule",
    }

    class Meta:
        verbose_name = 'NWFGEvaluation'
        verbose_name_plural = 'NWFGEvaluations'

    nwfg_evaluation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    nwfg_code = models.CharField(
        blank=False,
        max_length=50
    )
    creation_timestamp = models.DateTimeField(
        default=now,
        blank=False,
        null=False
    )
    current_erhebungszeitpunkt = models.IntegerField(
        default=1,
        validators=[MaxValueValidator(3), MinValueValidator(1)],
        blank=False
    )
    current_befragungsrunde = models.IntegerField(
        default=1,
        validators=[MaxValueValidator(2), MinValueValidator(1)],
        blank=False
    )
    teacher_name = models.CharField(
        blank=True,
        max_length=200
    )
    email = models.EmailField(blank=False)
    school_type = models.CharField(
        max_length=6,
        default=SCHOOL_TYPE['RE'],
        blank=False,
        choices=SCHOOL_TYPE,
    )
    subject = models.CharField(
        blank=False,
        max_length=21,
        validators=[RegexValidator(
            regex=r'^(Deutsch|Englisch|Evangelische Religion|Latein|Mathematik|Musik)$',
        ), ]
    )
    status_url_token = models.UUIDField(default=uuid.uuid4)

    completed = models.BooleanField(
        blank=False,
        default=False
    )


class NWFGEvaluationPart(models.Model):

    class Meta:
        verbose_name = 'NWFGEvaluationPart'
        verbose_name_plural = 'NWFGEvaluationParts'
        ordering = ('erhebungszeitpunkt', 'befragungsrunde')

    nwfg_evaluation_part_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    creation_timestamp = models.DateTimeField(
        default=now,
        blank=False,
        null=False
    )
    evaluation_stopped_timestamp = models.DateTimeField(
        blank=True,
        null=True
    )
    erhebungszeitpunkt = models.IntegerField(
        default=1,
        validators=[MaxValueValidator(3), MinValueValidator(1)],
        blank=False
    )
    befragungsrunde = models.IntegerField(
        default=1,
        validators=[MaxValueValidator(2), MinValueValidator(1)],
        blank=False
    )
    completed = models.BooleanField(
        blank=False,
        default=False
    )
    nwfg_evaluation = models.ForeignKey(
        NWFGEvaluation,
        on_delete=models.CASCADE
    )

class NWFGEvaluationAcronym(models.Model):
    class Meta:
        verbose_name = "NWFGEvaluationAcronym"
        verbose_name_plural = "NWFGEvaluationAcronyms"

    nwfg_evaluation_acronym_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    acronym = models.CharField(
        blank=False,
        max_length=5,
        validators=[RegexValidator(regex=r'\d+',), ]
    )
    
    pool = models.IntegerField(
        default=1,
        validators=[MaxValueValidator(3), MinValueValidator(1)],
        blank=False
    )
    
    nwfg_evaluation = models.ForeignKey(
        NWFGEvaluation,
        on_delete=models.CASCADE
    )

    
class NWFGSingleEvaluation(models.Model):

    class Meta:
        verbose_name = 'NWFGSingleEvaluation'
        verbose_name_plural = 'NWFGSingleEvaluations'

    nwfg_single_evaluation_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    acronym = models.ForeignKey(
        NWFGEvaluationAcronym,
        on_delete=models.PROTECT
    )
    completed = models.BooleanField(
        blank=False,
        default=False
    )
    nwfg_evaluation_part = models.ForeignKey(
        NWFGEvaluationPart,
        on_delete=models.CASCADE
    )


class NWFGItem(models.Model):

    class Meta:
        verbose_name = 'NWFGItem'
        verbose_name_plural = 'NWFGItems'
        ordering = ('question_index_for_student',)

    nwfg_item_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    code = models.CharField(
        blank=False,
        max_length=16,
    )
    recoded = models.BooleanField(
        blank=False,
        null=False,
        default=True,
    )
    selected_likert_item = models.IntegerField(
        blank=True,
        validators=[MaxValueValidator(5), MinValueValidator(1)],
        null=True
    )
    nwfg_single_evaluation = models.ForeignKey(
        NWFGSingleEvaluation,
        on_delete=models.CASCADE
    )
    question_index_for_student = models.IntegerField(
        null=False,
        blank=False,
        default=1
    )
