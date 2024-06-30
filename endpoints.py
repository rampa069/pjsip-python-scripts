#!/usr/bin/env python3

"""
endpoints.py
Este módulo contiene funciones y clases para analizar y generar un reporte de los endpoints y su estado.
"""

import subprocess
import pandas as pd
from jinja2 import Template

# Ejecutar el comando "asterisk -rx 'pjsip show endpoints'"
result = subprocess.run(
    ["asterisk", "-rx", "pjsip show endpoints"], 
    stdout=subprocess.PIPE,
    check=True
)
output = result.stdout.decode()

# Procesar la salida para convertirla en un DataFrame de pandas
data_lines = output.strip().split('\n')[2:]  # Saltar las primeras 2 líneas

# Filtrar y limpiar los datos
data = []
CURRENT_ENDPOINT = None
CURRENT_AOR = None
ENDPOINT_NAME = None  # Variable para almacenar el nombre del endpoint

for line in data_lines:
    if line.startswith(" Endpoint:"):
        if CURRENT_ENDPOINT:
            CURRENT_ENDPOINT["Endpoint"] = ENDPOINT_NAME.split()[0]  # Obtener solo la primera palabra del nombre
            data.append(CURRENT_ENDPOINT)
        CURRENT_ENDPOINT = {"Endpoint": "", "Aor": CURRENT_AOR, "Channels": [], "Contact": {}}
        CURRENT_AOR = None
        ENDPOINT_NAME = line.split(":")[1].strip()  # Obtener el nombre completo del nuevo endpoint
    elif line.startswith("        Aor:"):
        CURRENT_AOR = line.split(":")[1].strip()
    elif line.startswith("    Channel:"):
        if CURRENT_ENDPOINT is None:
            continue
        parts = line.split()
        channel_info = {
            "ChannelId": parts[1],
            "State": parts[2],
            "Time": parts[3]
        }
        CURRENT_ENDPOINT["Channels"].append(channel_info)
    elif line.startswith("      Contact:"):
        if CURRENT_ENDPOINT is None:
            continue
        parts = line.split()
        contact_info = {
            "ContactUri": parts[1],
            "Hash": parts[2],
            "Status": parts[3],
            "RTT": parts[4]
        }
        CURRENT_ENDPOINT["Contact"] = contact_info

# Añadir el último endpoint procesado
if CURRENT_ENDPOINT:
    CURRENT_ENDPOINT["Endpoint"] = ENDPOINT_NAME.split()[0]  # Obtener solo la primera palabra del nombre
    data.append(CURRENT_ENDPOINT)

# Crear el DataFrame
df = pd.DataFrame(data)

# Plantilla HTML para el informe con diseño moderno y fichas de endpoints
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PJSIP Endpoints Report</title>
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
        .endpoint-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 20px;
            background-color: #f9f9f9;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        .endpoint-card-header {
            background-color: #f2f2f2;
            padding: 8px;
            border-bottom: 1px solid #ddd;
            border-radius: 8px 8px 0 0;
        }
        .endpoint-info {
            margin-top: 10px;
        }
        .channel-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        .channel-table th, .channel-table td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        .channel-table th {
            background-color: #f2f2f2;
            color: #333;
        }
        .channel-table tr:nth-child(odd) {
            background-color: #cfe2f3;  /* Azul claro */
        }
        .channel-table tr:nth-child(even) {
            background-color: #a6c8e2;  /* Azul más oscuro */
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
        <h1>PJSIP Endpoints Report</h1>
        {% for endpoint in endpoints %}
        <div class="endpoint-card">
            <div class="endpoint-card-header">
                <h2>{{ endpoint["Endpoint"] }}</h2>
            </div>
            <div class="endpoint-info">
                <p><strong>Endpoint:</strong> {{ endpoint.get("Endpoint", "N/A") }}</p>
                <p><strong>State:</strong> {{ endpoint.get("State", "N/A") }}</p>
                {% if endpoint.get("Contact") %}
                <table>
                    <tr>
                        <th>ContactUri</th>
                        <th>Hash</th>
                        <th>Status</th>
                        <th>RTT(ms)</th>
                    </tr>
                    <tr>
                        <td>{{ endpoint["Contact"].get("ContactUri", "") }}</td>
                        <td>{{ endpoint["Contact"].get("Hash", "") }}</td>
                        <td>{{ endpoint["Contact"].get("Status", "") }}</td>
                        <td>{{ endpoint["Contact"].get("RTT", "") }}</td>
                    </tr>
                </table>
                {% endif %}
                <table class="channel-table">
                    <tr>
                        <th>ChannelId</th>
                        <th>State</th>
                        <th>Time</th>
                    </tr>
                    {% for channel in endpoint.get("Channels", []) %}
                    <tr>
                        <td>{{ channel.get("ChannelId", "") }}</td>
                        <td>{{ channel.get("State", "") }}</td>
                        <td>{{ channel.get("Time", "") }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </div>
        {% endfor %}
    </div>
    <footer>GibFibreSpeed SBC v0.1-ShoeStringBudget</footer>
</body>
</html>
"""

# Renderizar el informe HTML
template = Template(HTML_TEMPLATE)
html_content = template.render(endpoints=df.to_dict(orient='records'))

# Guardar el informe HTML en un archivo
with open("pjsip_endpoints_report.html", "w", encoding='utf-8') as file:
    file.write(html_content)

print("El informe de endpoints PJSIP se ha generado como 'pjsip_endpoints_report.html'")
