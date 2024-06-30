#!/usr/bin/env python3

"""
channels.py
Este módulo genera un reporte de los canales activos en Asterisk utilizando el comando 'core show channels concise'.
"""

import subprocess
from jinja2 import Template
from collections import defaultdict
from datetime import datetime

def get_channel_info():
    """
    Obtiene la información de los canales ejecutando un comando Asterisk.
    """
    result = subprocess.run(
        ["asterisk", "-rx", "core show channels concise"],
        stdout=subprocess.PIPE,
        check=True
    )
    output = result.stdout.decode()
    channels = []
    for line in output.strip().split('\n'):
        parts = line.split('!')
        if len(parts) >= 13:
            channels.append({
                "channel": parts[0],
                "context": parts[1],
                "exten": parts[2],
                "prio": parts[3],
                "state": parts[4],
                "appl": parts[5],
                "data": parts[6],
                "cid": parts[7],
                "empty1": parts[8],  # Primer campo vacío
                "empty2": parts[9],  # Segundo campo vacío
                "amaflags": parts[10],
                "duration": parts[11],
                "bridged_context": parts[12],
                "timestamp": datetime.fromtimestamp(float(parts[13])).strftime('%Y-%m-%d %H:%M:%S')
            })
    return channels

def group_channels_by_call(channels):
    """
    Agrupa los canales relacionados usando el bridged_context o el channel como call_id.
    """
    calls = defaultdict(list)
    for channel in channels:
        call_id = channel["bridged_context"] if channel["bridged_context"] else channel["channel"]
        calls[call_id].append(channel)
    return calls

def create_channel_report(calls):
    """
    Crea un reporte HTML con la información de los canales agrupados por llamada.
    """
    html_template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="refresh" content="60">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PJSIP Channels Report</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f0f7ff;
                margin: 0;
                padding: 0;
            }
            .container {
                width: 80%;
                margin: 20px auto;
                background-color: #fff;
                padding: 20px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
                color: #333;
            }
            tr:nth-child(odd) {
                background-color: #cfe2f3;
            }
            tr:nth-child(even) {
                background-color: #a6c8e2;
            }
            footer {
                text-align: center;
                margin-top: 20px;
                color: #666;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PJSIP Channels Report</h1>
            {% for call_id, channels in calls.items() %}
            <h2>Call ID: {{ call_id }}</h2>
            <table>
                <tr>
                    <th>Channel</th>
                    <th>Context</th>
                    <th>Exten</th>
                    <th>State</th>
                    <th>Application</th>
                    <th>Caller ID</th>
                    <th>Duration</th>
                    <th>Bridged Context</th>
                    <th>Timestamp</th>
                </tr>
                {% for channel in channels %}
                <tr>
                    <td>{{ channel["channel"] }}</td>
                    <td>{{ channel["context"] }}</td>
                    <td>{{ channel["exten"] }}</td>
                    <td>{{ channel["state"] }}</td>
                    <td>{{ channel["appl"] }}</td>
                    <td>{{ channel["cid"] }}</td>
                    <td>{{ channel["duration"] }}</td>
                    <td>{{ channel["bridged_context"] }}</td>
                    <td>{{ channel["timestamp"] }}</td>
                </tr>
                {% endfor %}
            </table>
            {% endfor %}
        </div>
        <footer>GibFibreSpeed SBC v0.1-ShoeStringBudget</footer>
    </body>
    </html>
    """
    template = Template(html_template)
    html_content = template.render(calls=calls)
    with open('pjsip_channels_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    """
    Función principal para obtener los datos y crear el reporte.
    """
    channels = get_channel_info()
    calls = group_channels_by_call(channels)
    create_channel_report(calls)

if __name__ == '__main__':
    main()
