import qrcode
import qrcode.image.svg
import re


def create_qr_code_as_svg_string(url):

    img = qrcode.make(url, image_factory=qrcode.image.svg.SvgFragmentImage)

    svg_string = img.to_string().decode("utf-8")

    # Format for HTML
    svg_string = svg_string.replace("svg:rect", 'rect')

    svg_string = svg_string.replace("svg:svg", "svg")

    svg_string = re.sub('<svg .+height="41mm".+version="1\.1"*>',
                        '<svg fill="#292f61" width="100%" viewBox="0 0 155 155" preserveAspectRatio="xMidYMid meet">', svg_string)

    svg_string = re.sub('<svg .+height="45mm".+version="1\.1"*>',
                        '<svg fill="#292f61" width="100%" viewBox="0 0 170 170" preserveAspectRatio="xMidYMid meet">', svg_string)
    return svg_string
