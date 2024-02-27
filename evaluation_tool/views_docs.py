from django.shortcuts import render

def get_tutorial_page(request):
    return render(request, 'evaluation_tool/pages/docs/tutorial-page.html')


def get_modelling_info_page(request):
    return render(request, 'evaluation_tool/pages/docs/modelling-info-page.html')


def get_evaluation_info_page(request):
    return render(request, 'evaluation_tool/pages/docs/evaluation-info-page.html')


def get_faq_page(request):
    return render(request, 'evaluation_tool/pages/docs/faq-page.html')