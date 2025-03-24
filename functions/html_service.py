def get_html_from_events(events):
    events.sort(key=lambda event: event.date)
    html = (
        '<div style="background-color:powderblue;">'
        + '<table width="100%" border="0" cellspacing="0" cellpadding="0">'
        + '<tr><td align="center">'
        + '<h1 style="color: brown;">woah look at these shows</h1>'
        + '<hr style="border:none;background-color:purple;height:2px;width:80%;"/>'
    )
    for event in events:
        html += event.to_html()
        html += (
            '<hr style="border:none;background-color:purple;height:1px;width:80%;"/>'
        )
    html += "</td></tr></table></div>"
    return html
