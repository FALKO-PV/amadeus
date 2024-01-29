from django import forms
from captcha.fields import CaptchaField, CaptchaTextInput
from django.core.validators import RegexValidator
from django import forms

class NewEvaluationForm(forms.Form):
    captcha = CaptchaField(widget=CaptchaTextInput(
        attrs={"placeholder": "Zeichen eingeben..."}))
    email = forms.EmailField(required=True)
    is_for_nwfg_study = forms.BooleanField(required=False)
    nwfg_code = forms.CharField(required=False)
    teacher_name = forms.CharField(required=False)
    subject = forms.CharField(validators=[RegexValidator("^(Allgemeine Lehrevaluation|Deutsch|Englisch|"
                                                         "Evangelische Religion|Latein|Mathematik|Musik)$")],
                              required=True)
    context_of_use = forms.ChoiceField(
        choices=[
           ('', 'Bitte wählen Sie aus.'),
           ('US', ' ... meiner Unterrichtstätigkeit an Schulen an.'),
           ('UA', ' ... meiner außerschulischen Unterrichtstätigkeit an.'),
           ('P', ' ... eines Praktikums während meines Lehramtsstudiums an.'),
           ('T', ' ... von Ansichts- und Testzwecken an.'),
           ('S', ' ... eines anderen Kontexts an.'),
        ],
        required=True,
    )
    start_evaluation_immediately = forms.BooleanField(required=False)
    evaluation_start = forms.DateTimeField(required=False)
    evaluation_end = forms.DateTimeField(required=False)
    allow_data_processing = forms.BooleanField(required=True)


class ItemsForm(forms.Form):
    q1 = forms.CharField(
        validators=[RegexValidator("^[1,2,3,4,5]$")], required=True)
    q2 = forms.CharField(
        validators=[RegexValidator("^[1,2,3,4,5]$")], required=True)
    q3 = forms.CharField(
        validators=[RegexValidator("^[1,2,3,4,5]$")], required=True)
    q4 = forms.CharField(
        validators=[RegexValidator("^[1,2,3,4,5]$")], required=True)
    q5 = forms.CharField(
        validators=[RegexValidator("^[1,2,3,4,5]$")], required=True)
    action = forms.CharField(validators=[RegexValidator(
        "^(back|next|send)_?(\d+)?$")], required=True)


class DownloadForm(forms.Form):
    subject = forms.ChoiceField(choices=(
        ('all', 'Alle Fächer'),
        ('_allgemeine_lehrevaluation', 'Allgemeine Lehrevaluation'),
        ('_deutsch', 'Deutsch'),
        ('_englisch', 'Englisch'),
        ('_latein', 'Latein'),
        ('_mathematik', 'Mathematik'),
        ('_musik', 'Musik'),
        ('_evangelische_religion', 'Evangelische Religion'),
    ), label='Auswahl Fach')
    min_answered = forms.IntegerField(
        label='Minimum an Teilnehmer:innen',
        min_value=1,
    )
