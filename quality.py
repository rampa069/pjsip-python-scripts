#!/usr/bin/env python3
import subprocess
import pandas as pd
from jinja2 import Template

# Ejecutar el comando "asterisk -rx 'pjsip show channelstats'"
result = subprocess.run(["asterisk", "-rx", "pjsip show channelstats"], stdout=subprocess.PIPE)
output = result.stdout.decode()

# Procesar la salida para convertirla en un DataFrame de pandas
data_lines = output.strip().split('\n')[4:-2]  # Saltar las primeras 4 líneas y las últimas 2 líneas

# Filtrar y limpiar los datos
data = []
for line in data_lines:
    if "not valid" in line or line.startswith(" " * 8):
        continue  # Omitir líneas que contienen "not valid" o empiezan con 8 espacios
    parts = line.split()
    if len(parts) == 13:  # Asegurar que haya 13 columnas en cada línea
        bridge_id = parts[0]
        if bridge_id.startswith(" " * 8):
            bridge_id = ""  # Rellenar BridgeId con vacío si empieza con 8 espacios
        data.append(parts)

# Crear el DataFrame
columns = ["BridgeId", "ChannelId", "UpTime", "Codec", "Count1", "Lost1", "Pct1", "Jitter1", "Count2", "Lost2", "Pct2", "Jitter2", "RTT"]
df = pd.DataFrame(data, columns=columns)

# Limpiar los datos, removiendo caracteres no numéricos y reemplazando con un valor por defecto si es necesario
def clean_value(value):
    if value is None:
        return 0
    try:
        return int(value.replace('K', '000'))
    except ValueError:
        return 0

df["Count1"] = df["Count1"].apply(clean_value)
df["Lost1"] = df["Lost1"].apply(clean_value)
df["Pct1"] = df["Pct1"].astype(float)
df["Jitter1"] = df["Jitter1"].astype(float)
df["Count2"] = df["Count2"].apply(clean_value)
df["Lost2"] = df["Lost2"].apply(clean_value)
df["Pct2"] = df["Pct2"].astype(float)
df["Jitter2"] = df["Jitter2"].astype(float)
df["RTT"] = df["RTT"].astype(float)

# Función para evaluar la calidad de la llamada
def evaluate_quality(row):
    jitter_threshold_good = 20.0  # 20 ms
    packet_loss_threshold = 1.0   # 1%

    jitter1 = row['Jitter1'] * 1000
    jitter2 = row['Jitter2'] * 1000
    loss_pct1 = row['Pct1']
    loss_pct2 = row['Pct2']

    if jitter1 > jitter_threshold_good or jitter2 > jitter_threshold_good:
        return "Poor Quality"
    if loss_pct1 >= packet_loss_threshold or loss_pct2 >= packet_loss_threshold:
        return "Poor Quality"
    return "Good Quality"

# Evaluar la calidad de cada llamada
df['Quality'] = df.apply(evaluate_quality, axis=1)

# Plantilla HTML para el informe con diseño moderno
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="60">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Call Quality Report</title>
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
        h1 {
            color: #333;
            text-align: center;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        table, th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            color: #333;
        }
        .poor-quality {
            background-color: #ffcccc;
        }
        .good-quality {
            background-color: #ccffcc;
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
        <h1>Call Quality Report</h1>
        <table>
            <tr>
                <th>BridgeId</th>
                <th>ChannelId</th>
                <th>UpTime</th>
                <th>Codec</th>
                <th>Count1</th>
                <th>Lost1</th>
                <th>Pct1</th>
                <th>Jitter1 (ms)</th>
                <th>Count2</th>
                <th>Lost2</th>
                <th>Pct2</th>
                <th>Jitter2 (ms)</th>
                <th>RTT</th>
                <th>Quality</th>
            </tr>
            {% for row in rows %}
            <tr class="{{ 'poor-quality' if row['Quality'] == 'Poor Quality' else 'good-quality' }}">
                <td>{{ row['BridgeId'] }}</td>
                <td>{{ row['ChannelId'] }}</td>
                <td>{{ row['UpTime'] }}</td>
                <td>{{ row['Codec'] }}</td>
                <td>{{ row['Count1'] }}</td>
                <td>{{ row['Lost1'] }}</td>
                <td>{{ row['Pct1'] }}</td>
                <td>{{ row['Jitter1'] * 1000 }}</td>
                <td>{{ row['Count2'] }}</td>
                <td>{{ row['Lost2'] }}</td>
                <td>{{ row['Pct2'] }}</td>
                <td>{{ row['Jitter2'] * 1000 }}</td>
                <td>{{ row['RTT'] }}</td>
                <td>{{ row['Quality'] }}</td>
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
html_content = template.render(rows=df.to_dict(orient='records'))

# Guardar el informe HTML en un archivo
with open("call_quality_report.html", "w") as file:
    file.write(html_content)

print("El informe de calidad de las llamadas se ha generado como 'call_quality_report.html'")
