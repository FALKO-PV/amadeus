from evaluation_tool.subjects import color_mapping
def get_subject_color(subject):
    return color_mapping.get(subject, None)
