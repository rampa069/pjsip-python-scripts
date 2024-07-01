#!/usr/bin/env python3

import subprocess
import pandas as pd
from jinja2 import Template

# Función para ejecutar comandos y obtener su salida
def run_command(command):
    result = subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    return result.stdout.decode().strip()

# Obtener el uptime de Asterisk
def get_asterisk_uptime():
    output = run_command("asterisk -rx 'core show uptime'")
    for line in output.splitlines():
        if "System uptime:" in line:
            return line.split(":", 1)[1].strip()
    return "N/A"

# Obtener el uptime de la máquina
def get_system_uptime():
    output = run_command("uptime -p")
    return output

# Obtener el número total de llamadas en este momento
def get_current_calls():
    output = run_command("asterisk -rx 'core show channels'")
    for line in output.splitlines():
        if "active call" in line:
            return line.split()[0]
    return "N/A"

# Obtener el número de llamadas desde el inicio de Asterisk
def get_total_calls():
    output = run_command("asterisk -rx 'core show calls'")
    for line in output.splitlines():
        if "calls processed" in line:
            return line.split()[0]
    return "N/A"

# Obtener una lista de todos los endpoints con el número actual de llamadas
def get_endpoints_calls():
    output = run_command("asterisk -rx 'pjsip show endpoints'")
    data_lines = output.strip().split('\n')
    endpoints = []

    for line in data_lines:
        if line.startswith(" Endpoint:") and "In use" in line:
            parts = line.split()
            endpoint = parts[1]
            current_calls = parts[-3]
            endpoints.append({"Endpoint": endpoint, "CurrentCalls": current_calls})

    return pd.DataFrame(endpoints)

# Recopilar los datos
asterisk_uptime = get_asterisk_uptime()
system_uptime = get_system_uptime()
current_calls = get_current_calls()
total_calls = get_total_calls()
endpoints_df = get_endpoints_calls()

# Plantilla HTML para el informe
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="60">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SBC and System Status Report</title>
    <link rel="stylesheet" type="text/css" href="styles.css">
</head>
<body>
    <div class="container">
        <h1>SBC and System Status Report</h1>
        <p><strong>SBC Uptime:</strong> {{ asterisk_uptime }}</p>
        <p><strong>System Uptime:</strong> {{ system_uptime }}</p>
        <p><strong>Current Active Calls:</strong> {{ current_calls }}</p>
        <p><strong>Total Calls Since SBC Start:</strong> {{ total_calls }}</p>
        <h2>Endpoints and Current Calls</h2>
        <table class="channel-table">

            <tr>
                <th>Endpoint</th>
                <th>Current Calls</th>
            </tr>
            {% for row in rows %}
            <tr>
                <td>{{ row['Endpoint'] }}</td>
                <td>{{ row['CurrentCalls'] }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    <footer>GibFibreSpeed SBC v0.1-ShoeStringBudget</footer>
</body>
</html>
"""

# Renderizar el informe HTML
template = Template(html_template)
html_content = template.render(
    asterisk_uptime=asterisk_uptime,
    system_uptime=system_uptime,
    current_calls=current_calls,
    total_calls=total_calls,
    rows=endpoints_df.to_dict(orient='records')
)

# Guardar el informe HTML en un archivo
with open("asterisk_system_status_report.html", "w") as file:
    file.write(html_content)

print("El informe de estado del sistema y Asterisk se ha generado como 'asterisk_system_status_report.html'")
