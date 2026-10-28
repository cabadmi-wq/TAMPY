# ==============================================
# 🤖 TAMPY - Asistente Inteligente Completo
# ✅ Lee archivos de texto
# ✅ Analiza imágenes
# ✅ Memoria de conversación
# ✅ Diseño profesional oscuro / azul celeste
# ==============================================

from flask import Flask, render_template_string, request, jsonify
import requests
import base64

app = Flask(__name__)

# 🔑 Configuración de Hugging Face
HF_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"
HF_VISION_URL = "https://api-inference.huggingface.co/models/microsoft/phi-4-vision-instruct"
HF_API_TOKEN = "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"  # ← Pon tu token aquí

headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# 🧠 Memoria de conversación
historial = [
    {
        "role": "system",
        "content": "Eres TAMPY, una asistente amable, profesional y servicial. Respondes en español de forma clara y útil. Puedes leer archivos, analizar imágenes y ayudar con cualquier consulta."
    }
]

def consultar_ia(mensaje_nuevo):
    historial.append({"role": "user", "content": mensaje_nuevo})
    
    prompt = ""
    for msg in historial:
        if msg["role"] == "system":
            prompt += f"<<SYS>>\n{msg['content']}\n<</SYS>>\n\n"
        elif msg["role"] == "user":
            prompt += f"Usuario: {msg['content']}\n"
        else:
            prompt += f"TAMPY: {msg['content']}\n"
    prompt += "TAMPY:"
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1000,
            "temperature": 0.7,
            "top_p": 0.9,
            "return_full_text": False
        }
    }
    
    try:
        respuesta = requests.post(HF_API_URL, headers=headers, json=payload, timeout=90)
        respuesta.raise_for_status()
        resultado = respuesta.json()
        if isinstance(resultado, list) and len(resultado) > 0:
            texto = resultado[0].get('generated_text', '').strip()
            historial.append({"role": "assistant", "content": texto})
            return texto
        return "No entendí eso, intenta de nuevo."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

def analizar_imagen(datos_imagen, consulta="Describe esta imagen"):
    try:
        payload = {
            "inputs": [
                {
                    "image": datos_imagen,
                    "prompt": consulta
                }
            ],
            "parameters": {"max_new_tokens": 500}
        }
        respuesta = requests.post(HF_VISION_URL, headers=headers, json=payload, timeout=120)
        respuesta.raise_for_status()
        resultado = respuesta.json()
        if isinstance(resultado, list) and len(resultado) > 0:
            return resultado[0].get('generated_text', 'No pude analizar la imagen.')
        return "Imagen recibida correctamente."
    except Exception as e:
        return f"✅ Imagen cargada. (Análisis: {str(e)})"

def leer_archivo(contenido, nombre):
    try:
        if nombre.endswith('.txt') or nombre.endswith('.py') or nombre.endswith('.md') or nombre.endswith('.csv'):
            if len(contenido) > 8000:
                contenido = contenido[:8000] + "\n... [contenido recortado por longitud]"
            return f"📄 Contenido de {nombre}:\n\n{contenido}"
        return f"✅ Archivo '{nombre}' recibido. Tipo de archivo no soportado para lectura directa."
    except Exception as e:
        return f"⚠️ No pude leer el archivo: {str(e)}"

# 🌐 INTERFAZ WEB
HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 TAMPY - Asistente Inteligente</title>
    <style>
        :root {
            --bg-main: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --accent: #38bdf8;
            --accent-dark: #0ea5e9;
            --accent-light: #7dd3fc;
            --text: #f1f5f9;
            --text-muted: #94a3b8;
            --user-bubble: #0369a1;
            --tampy-bubble: #1e293b;
            --border: #475569;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', 'Inter', sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, var(--bg-main) 0%, #1a2744 100%);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        /* === CABECERA === */
        header {
            background: linear-gradient(90deg, var(--accent-dark), var(--accent));
            padding: 18px 24px;
            box-shadow: 0 4px 20px rgba(56, 189, 248, 0.15);
        }
        
        .header-content {
            max-width: 800px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .logo-section {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        
        .logo-icon {
            font-size: 28px;
        }
        
        h1 {
            font-size: 22px;
            font-weight: 700;
            color: white;
            letter-spacing: 0.5px;
        }
        
        .status {
            font-size: 13px;
            color: rgba(255,255,255,0.9);
            background: rgba(0,0,0,0.15);
            padding: 6px 12px;
            border-radius: 20px;
            display: flex;
            align-items: center;
            gap: 6px;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            background: #86efac;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.2); }
        }
        
        /* === BARRA DE HERRAMIENTAS === */
        .toolbar {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 10px 24px;
        }
        
        .toolbar-content {
            max-width: 800px;
            margin: 0 auto;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            align-items: center;
        }
        
        .btn-tool {
            background: var(--bg-tertiary);
            color: var(--text);
            border: none;
            padding: 8px 14px;
            border-radius: 8px;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }
        
        .btn-tool:hover {
            background: var(--accent-dark);
            transform: translateY(-1px);
        }
        
        .btn-tool.primary {
            background: var(--accent);
            color: white;
        }
        
        .file-input {
            display: none;
        }
        
        .file-name {
            font-size: 13px;
            color: var(--accent-light);
            margin-left: 8px;
        }
        
        /* === ÁREA DE CHAT === */
        .chat-container {
            flex: 1;
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
            padding: 24px;
            padding-bottom: 120px;
            overflow-y: auto;
        }
        
        .msg {
            margin-bottom: 24px;
            animation: slideIn 0.3s ease;
            display: flex;
        }
        
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .tu {
            justify-content: flex-end;
        }
        
        .tampy {
            justify-content: flex-start;
        }
        
        .bubble {
            max-width: 85%;
            padding: 14px 18px;
            border-radius: 16px;
            line-height: 1.6;
            font-size: 15px;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .tu .bubble {
            background: linear-gradient(135deg, var(--user-bubble), #0284c7);
            border-bottom-right-radius: 4px;
            box-shadow: 0 2px 10px rgba(14, 165, 233, 0.2);
        }
        
        .tampy .bubble {
            background: var(--tampy-bubble);
            border: 1px solid var(--border);
            border-bottom-left-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        
        .bubble img {
            max-width: 100%;
            border-radius: 8px;
            margin-top: 8px;
        }
        
        .file-preview {
            background: var(--bg-tertiary);
            padding: 10px 12px;
            border-radius: 6px;
            margin-top: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14px;
        }
        
        /* === ÁREA DE ESCRITURA === */
        .input-area {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--bg-secondary);
            border-top: 1px solid var(--border);
            padding: 16px 24px;
            box-shadow: 0 -4px 20px rgba(0,0,0,0.2);
        }
        
        .input-wrap {
            max-width: 800px;
            margin: 0 auto;
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }
        
        .input-left {
            flex: 1;
            position: relative;
        }
        
        textarea {
            width: 100%;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px 16px;
            color: var(--text);
            font-size: 15px;
            resize: none;
            height: 52px;
            max-height: 140px;
            transition: border 0.2s ease;
        }
        
        textarea:focus {
            outline: none;
            border-color: var(--accent);
        }
        
        .btn-send {
            background: linear-gradient(135deg, var(--accent-dark), var(--accent));
            color: white;
            border: none;
            border-radius: 12px;
            padding: 14px 28px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            height: 52px;
            transition: all 0.2s ease;
        }
        
        .btn-send:hover {
            transform: scale(1.02);
            box-shadow: 0 4px 15px rgba(56, 189, 248, 0.3);
        }
        
        .btn-send:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .pensando {
            color: var(--accent-light);
            font-size: 14px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .typing-dots span {
            animation: blink 1.4s infinite both;
        }
        
        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes blink {
            0%, 80%, 100% { opacity: 0; }
            40% { opacity: 1; }
        }
        
        /* Responsivo */
        @media (max-width: 640px) {
            header { padding: 14px 16px; }
            .chat-container { padding: 16px; padding-bottom: 100px; }
            .input-area { padding: 12px 16px; }
            .btn-send { padding: 14px 20px; }
        }
    </style>
</head>
<body>
    <!-- CABECERA -->
    <header>
        <div class="header-content">
            <div class="logo-section">
                <span class="logo-icon">🤖</span>
                <div>
                    <h1>TAMPY</h1>
                </div>
            </div>
            <div class="status">
                <span class="status-dot"></span>
                <span>En línea</span>
            </div>
        </div>
    </header>
    
    <!-- BARRA DE HERRAMIENTAS -->
    <div class="toolbar">
        <div class="toolbar-content">
            <label class="btn-tool" for="file-input">
                📄 Subir archivo
            </label>
            <label class="btn-tool" for="image-input">
                🖼️ Subir imagen
            </label>
            <span class="file-name" id="file-info"></span>
            <div style="flex:1;"></div>
            <button class="btn-tool" onclick="reiniciarChat()">
                🔄 Nueva conversación
            </button>
        </div>
        <input type="file" id="file-input" class="file-input" accept=".txt,.py,.md,.csv,.json">
        <input type="file" id="image-input" class="file-input" accept="image/*">
    </div>
    
    <!-- ÁREA DE CHAT -->
    <div class="chat-container" id="chat">
        <div class="msg tampy">
            <div class="bubble">¡Hola! Soy <strong>TAMPY</strong> 🤖<br><br>
Puedo ayudarte con:
💬 Preguntas y respuestas
📄 Leer archivos de texto (.txt, .py, .csv, etc.)
🖼️ Analizar imágenes
💻 Explicar y escribir código<br><br>
¡Sube un archivo o imagen, o simplemente pregúntame lo que necesitas!</div>
        </div>
    </div>
    
    <!-- ÁREA DE ENTRADA -->
    <div class="input-area">
        <div class="input-wrap">
            <div class="input-left">
                <textarea 
                    id="mensaje" 
                    placeholder="Escribe tu mensaje... Enter = enviar | Shift+Enter = nueva línea"
                    onkeydown="handleKey(event)"
                ></textarea>
            </div>
            <button class="btn-send" id="btn" onclick="enviarMensaje()">
                Enviar →
            </button>
        </div>
    </div>
    
<script>
const chat = document.getElementById('chat');
const mensaje = document.getElementById('mensaje');
const btn = document.getElementById('btn');
const fileInput = document.getElementById('file-input');
const imageInput = document.getElementById('image-input');
const fileInfo = document.getElementById('file-info');

let archivoPendiente = null;
let imagenPendiente = null;

// === Manejo de teclado ===
function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        enviarMensaje();
    }
}

// === Subir archivo ===
fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    fileInfo.textContent = `📄 ${file.name}`;
    
    const lector = new FileReader();
    le