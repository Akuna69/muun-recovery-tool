import os
import zipfile
import re
import tempfile
import json

print("=== ESCANEO Y EXTRACCIÓN PARA MUUN RECOVERY TOOL ===")

zip_path = None
search_roots = [os.path.expanduser("~/storage/shared/Download"), "/sdcard/Download", "/storage/emulated/0/Download", "."]

for root in search_roots:
    potential_path = os.path.join(root, "muun.zip")
    if os.path.exists(potential_path):
        zip_path = potential_path
        break

if not zip_path:
    for root_dir in [os.path.expanduser("~/storage/shared"), "/sdcard", "/storage/emulated/0"]:
        if os.path.exists(root_dir):
            for dirpath, _, filenames in os.walk(root_dir):
                if "muun.zip" in filenames:
                    zip_path = os.path.join(dirpath, "muun.zip")
                    break
            if zip_path:
                break

if not zip_path or not os.path.exists(zip_path):
    print("[!] Error: No se encontró el archivo muun.zip en el almacenamiento.")
    exit(1)

extracted_data = []

with tempfile.TemporaryDirectory() as tmpdir:
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(tmpdir)
        
    for root, _, files in os.walk(tmpdir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Buscar códigos de recuperación del kit de emergencia Muun
                    codes = re.findall(r'[A-Z0-9]{4}[\s\-][A-Z0-9]{4}[\s\-][A-Z0-9]{4}[\s\-][A-Z0-9]{4}[\s\-][A-Z0-9]{4}[\s\-][A-Z0-9]{4}[\s\-][A-Z0-9]{4}[\s\-][A-Z0-9]{4}', content.upper())
                    amounts = re.findall(r'(?:amount|balance|satoshis|value)[\s"\'\:=]+([0-9]+)', content, re.IGNORECASE)
                    
                    for i, code in enumerate(codes):
                        norm_code = code.replace(' ', '-')
                        real_amt = int(amounts[i]) if i < len(amounts) else 0
                        if norm_code not in [d[0] for d in extracted_data]:
                            extracted_data.append((norm_code, real_amt))
            except Exception:
                pass

if not extracted_data:
    with zipfile.ZipFile(zip_path, 'r') as z:
        for filename in z.namelist():
            codes = re.findall(r'[A-Z0-9]{4}[\s\-][A-Z0-9]{4}[\s\-][A-Z0-9]{4}[\s\-][A-Z0-9]{4}[\s\-][A-Z0-9]{4}[\s\-][A-Z0-9]{4}[\s\-][A-Z0-9]{4}[\s\-][A-Z0-9]{4}', filename.upper())
            for code in codes:
                norm_code = code.replace(' ', '-')
                if norm_code not in [d[0] for d in extracted_data]:
                    extracted_data.append((norm_code, 0))

if not extracted_data:
    print("[!] No se encontraron datos válidos de recuperación en el ZIP.")
    exit(1)

print(f"[+] ¡Éxito! Se procesaron {len(extracted_data)} registros desde el kit.")
print("=" * 90)
print(f"{'Nº':<4} {'CÓDIGO DE RECUPERACIÓN':<42} {'SALDO / AMT (SATS)':<18}")
print("-" * 90)

total_balance = 0
for idx, (code, amt) in enumerate(extracted_data, 1):
    total_balance += amt
    print(f"{idx:<4} [{code}]   {amt:<18}")

print("=" * 90)
print(f"[*] Saldo total detectado: {total_balance} sats")

# Guardar los códigos extraídos en un formato JSON listo para que tu herramienta de Go los consuma
output_json = "recovery_keys.json"
with open(output_json, "w") as f:
    json.dump([item[0] for item in extracted_data], f, indent=2)

print(f"[+] Códigos exportados correctamente a '{output_json}' para ser escaneados por los nodos Electrum.")
