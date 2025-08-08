
from typing import Dict

BRAND_SIGNATURE = (
    "Kind regards,\n\n"
    "Customer Support Team\n"
    "Professional Holiday Homes\n"
    "https://professionalholidayhomes.com.au"
)

def render_reply(context: Dict) -> str:
    body = context.get("body", "")
    ref = context.get("references_html", "")
    footer = (
        "<hr/>"
        "<p style='font-size:12px;color:#666;'>"
        "This is an automated draft. A team member may review before sending."
        "</p>"
    )
    html = f"""<div>
    <p>{body}</p>
    {ref}
    <p>{BRAND_SIGNATURE.replace('\n','<br/>')}</p>
    {footer}
    </div>"""
    return html
