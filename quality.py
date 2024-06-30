#!/usr/bin/env python3

"""
quality.py
Este módulo genera un reporte de calidad de los puentes en Asterisk.
"""

import subprocess
import pandas as pd
from jinja2 import Template

def get_bridge_quality():
    """
    Obtiene la calidad de los puentes ejecutando un comando Asterisk.
    """
    result = subprocess.run(
        ["asterisk", "-rx", "bridge show all"],
        stdout=subprocess.PIPE,
        check=True
    )
    output = result.stdout.decode()
    BRIDGE_ID = None
    data = []
    for line in output.split('\n'):
        if line.startswith('Bridge ID:'):
            BRIDGE_ID = line.split()[-1]
        elif BRIDGE_ID and line.startswith(' '):
            data.append((BRIDGE_ID, line.strip()))
    return data

def create_quality_report(data):
    """
    Crea un reporte HTML con la calidad de los puentes.
    """
    HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Bridge Quality Report</title>
    </head>
    <body>
        <h1>Bridge Quality Report</h1>
        <table border="1">
            <tr><th>Bridge ID</th><th>Details</th></tr>
            {% for bridge_id, details in data %}
            <tr><td>{{ bridge_id }}</td><td>{{ details }}</td></tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    template = Template(HTML_TEMPLATE)
    html_content = template.render(data=data)
    with open('bridge_quality_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    """
    Función principal para obtener los datos y crear el reporte.
    """
    data = get_bridge_quality()
    create_quality_report(data)

if __name__ == '__main__':
    main()
