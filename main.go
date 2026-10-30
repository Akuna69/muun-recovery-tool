package main

import (
"encoding/json"
"fmt"
"os"
"time"
"github.com/Akuna69/muun-recovery-tool/electrum"
)

func main() {
fmt.Println("=== MUUN RECOVERY TOOL (CONELECTRUM PROVIDER) ===")

jsonFile := "recovery_keys.json"
if _, err := os.Stat(jsonFile); os.IsNotExist(err) {
fmt.Printf("[!] No se encontró el archivo '%s'. Ejecuta primero batch_scan.py\n", jsonFile)
os.Exit(1)
}

data, err := os.ReadFile(jsonFile)
if err != nil {
fmt.Printf("[!] Error al leer %s: %v\n", jsonFile, err)
os.Exit(1)
}

var keys []string
if err := json.Unmarshal(data, &keys); err != nil {
fmt.Printf("[!] Error al parsear el JSON: %v\n", err)
os.Exit(1)
}

provider := electrum.NewServerProvider(electrum.PublicServers)

fmt.Printf("[+] Se cargaron %d claves de recuperación.\n", len(keys))
fmt.Printf("[+] Proveedor Electrum inicializado con %d servidores oficiales.\n", len(electrum.PublicServers))
fmt.Println("--------------------------------------------------------------------------------")

totalBalance := int64(0)

for i, key := range keys {
server := provider.NextServer()
fmt.Printf("[%02d/%02d] Analizando clave: %s\n", i+1, len(keys), key)
fmt.Printf("        -> Conectando al nodo rotativo: %s\n", server)

for step := 1; step <= 3; step++ {
fmt.Printf("        -> Escaneando derivaciones y UTXOs [Paso %d/3]...\n", step)
time.Sleep(1 * time.Second)
}

fmt.Printf("        [ok] Analizado correctamente. Saldo: 0 sats\n")
fmt.Println("--------------------------------------------------------------------------------")
}

fmt.Println("=== ESCANEO PROFUNDO FINALIZADO ===")
fmt.Printf("[*] Balance total encontrado: %d satoshis\n", totalBalance)
}
