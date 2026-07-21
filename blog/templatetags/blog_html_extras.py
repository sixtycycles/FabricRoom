import re

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

IMG_TAG_PATTERN = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
IMG_ALT_PATTERN = re.compile(
    r"\balt\s*=\s*(\"([^\"]*)\"|'([^']*)'|([^\s>]+))", re.IGNORECASE
)


@register.filter(name="ensure_img_alt")
def ensure_img_alt(value):
    html = value or ""

    def add_or_fix_alt(match):
        img_tag = match.group(0)
        alt_match = IMG_ALT_PATTERN.search(img_tag)

        if alt_match:
            alt_value = next(
                (group for group in alt_match.groups()[1:] if group is not None),
                "",
            )
            if alt_value.strip():
                return img_tag
            return IMG_ALT_PATTERN.sub('alt="Blog image"', img_tag, count=1)

        return img_tag[:-1] + ' alt="Blog image">'

    return mark_safe(IMG_TAG_PATTERN.sub(add_or_fix_alt, html))
