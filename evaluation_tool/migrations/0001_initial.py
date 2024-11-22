# Generated by Django 5.0.9 on 2024-09-09 12:52

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ClassEvaluation',
            fields=[
                ('class_evaluation_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('evaluation_start', models.DateTimeField()),
                ('evaluation_end', models.DateTimeField()),
                ('start_evaluation_immediately', models.BooleanField(default=False)),
                ('creation_timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('evaluation_stopped_timestamp', models.DateTimeField(blank=True, null=True)),
                ('teacher_name', models.CharField(blank=True, max_length=200)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('subject', models.CharField(max_length=25, validators=[django.core.validators.RegexValidator(regex='^(Allgemeine Lehrevaluation|Deutsch|Englisch|Evangelische Religion|Latein|Mathematik|Musik)$')])),
                ('status_url_token', models.UUIDField(default=uuid.uuid4)),
                ('context_of_use', models.CharField(choices=[('US', ' ... meiner Unterrichtstätigkeit an Schulen an.'), ('UA', ' ... meiner außerschulischen Unterrichtstätigkeit an.'), ('P', ' ... eines Praktikums während meines Lehramtsstudiums an.'), ('T', ' ... von Ansichts- und Testzwecken an.'), ('S', ' ... eines anderen Kontexts an.')], default='', max_length=100)),
                ('email_sent_evaluation_end', models.BooleanField(default=False)),
                ('completed', models.BooleanField(default=False)),
                ('deleted', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'ClassEvaluation',
                'verbose_name_plural': 'ClassEvaluations',
            },
        ),
        migrations.CreateModel(
            name='NWFGEvaluation',
            fields=[
                ('nwfg_evaluation_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('nwfg_code', models.CharField(max_length=50)),
                ('creation_timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('current_erhebungszeitpunkt', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(3), django.core.validators.MinValueValidator(1)])),
                ('current_befragungsrunde', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(2), django.core.validators.MinValueValidator(1)])),
                ('teacher_name', models.CharField(blank=True, max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('school_type', models.CharField(choices=[('GYM', 'Gymnasium'), ('RE', 'Realschule')], default='Realschule', max_length=6)),
                ('subject', models.CharField(max_length=21, validators=[django.core.validators.RegexValidator(regex='^(Deutsch|Englisch|Evangelische Religion|Latein|Mathematik|Musik)$')])),
                ('status_url_token', models.UUIDField(default=uuid.uuid4)),
                ('completed', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'NWFGEvaluation',
                'verbose_name_plural': 'NWFGEvaluations',
            },
        ),
        migrations.CreateModel(
            name='NWFGEvaluationAcronym',
            fields=[
                ('nwfg_evaluation_acronym_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('acronym', models.CharField(max_length=5, validators=[django.core.validators.RegexValidator(regex='\\d+')])),
                ('pool', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(3), django.core.validators.MinValueValidator(1)])),
                ('nwfg_evaluation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluation_tool.nwfgevaluation')),
            ],
            options={
                'verbose_name': 'NWFGEvaluationAcronym',
                'verbose_name_plural': 'NWFGEvaluationAcronyms',
            },
        ),
        migrations.CreateModel(
            name='NWFGEvaluationPart',
            fields=[
                ('nwfg_evaluation_part_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('creation_timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('evaluation_stopped_timestamp', models.DateTimeField(blank=True, null=True)),
                ('erhebungszeitpunkt', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(3), django.core.validators.MinValueValidator(1)])),
                ('befragungsrunde', models.IntegerField(default=1, validators=[django.core.validators.MaxValueValidator(2), django.core.validators.MinValueValidator(1)])),
                ('completed', models.BooleanField(default=False)),
                ('nwfg_evaluation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluation_tool.nwfgevaluation')),
            ],
            options={
                'verbose_name': 'NWFGEvaluationPart',
                'verbose_name_plural': 'NWFGEvaluationParts',
                'ordering': ('erhebungszeitpunkt', 'befragungsrunde'),
            },
        ),
        migrations.CreateModel(
            name='NWFGSingleEvaluation',
            fields=[
                ('nwfg_single_evaluation_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('completed', models.BooleanField(default=False)),
                ('acronym', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='evaluation_tool.nwfgevaluationacronym')),
                ('nwfg_evaluation_part', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluation_tool.nwfgevaluationpart')),
            ],
            options={
                'verbose_name': 'NWFGSingleEvaluation',
                'verbose_name_plural': 'NWFGSingleEvaluations',
            },
        ),
        migrations.CreateModel(
            name='NWFGItem',
            fields=[
                ('nwfg_item_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=16)),
                ('recoded', models.BooleanField(default=True)),
                ('selected_likert_item', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('question_index_for_student', models.IntegerField(default=1)),
                ('nwfg_single_evaluation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluation_tool.nwfgsingleevaluation')),
            ],
            options={
                'verbose_name': 'NWFGItem',
                'verbose_name_plural': 'NWFGItems',
                'ordering': ('question_index_for_student',),
            },
        ),
        migrations.CreateModel(
            name='SingleEvaluation',
            fields=[
                ('single_evaluation_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('completed', models.BooleanField(default=False)),
                ('class_evaluation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluation_tool.classevaluation')),
            ],
            options={
                'verbose_name': 'SingleEvaluation',
                'verbose_name_plural': 'SingleEvaluations',
            },
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('item_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=16)),
                ('recoded', models.BooleanField(default=True)),
                ('selected_likert_item', models.IntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('question_index_for_student', models.IntegerField(default=1)),
                ('single_evaluation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='evaluation_tool.singleevaluation')),
            ],
            options={
                'verbose_name': 'Item',
                'verbose_name_plural': 'Items',
                'ordering': ('question_index_for_student',),
            },
        ),
    ]
