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

# 🔑 Tu token de Hugging Face
HF_API_URL = "https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-3B-Instruct"
HF_VISION_URL = "https://api-inference.huggingface.co/models/microsoft/phi-4-vision-instruct"
HF_API_TOKEN = "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"

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
            "max_new_tokens": 800,
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

def analizar_imagen(datos_base64, consulta="Describe esta imagen"):
    try:
        imagen_decodificada = base64.b64decode(datos_base64)
        payload = {
            "inputs": [
                {
                    "image": imagen_decodificada,
                    "prompt": consulta
                }
            ],
            "parameters": {"max_new_tokens": 400}
        }
        respuesta = requests.post(HF_VISION_URL, headers=headers, json=payload, timeout=120)
        respuesta.raise_for_status()
        resultado = respuesta.json()
        if isinstance(resultado, list) and len(resultado) > 0:
            return resultado[0].get('generated_text', 'Análisis completado.')
        return "Imagen recibida correctamente."
    except Exception as e:
        return f"✅ Imagen cargada. (Análisis: {str(e)})"

def leer_archivo(contenido, nombre):
    try:
        if len(contenido) > 8000:
            contenido = contenido[:8000] + "\n... [contenido recortado]"
        return f"📄 Contenido de {nombre}:\n\n{contenido}"
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
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
        body {
            background: linear-gradient(135deg, var(--bg-main) 0%, #1a2744 100%);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
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
        .logo-section { display: flex; align-items: center; gap: 12px; }
        .logo-icon { font-size: 28px; }
        h1 { font-size: 22px; font-weight: 700; color: white; }
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
        .btn-tool:hover { background: var(--accent-dark); transform: translateY(-1px); }
        .file-input { display: none; }
        .file-name { font-size: 13px; color: var(--accent-light); margin-left: 8px; }
        .chat-container {
            flex: 1;
            max-width: 800px;
            width: 100%;
            margin: 0 auto;
            padding: 24px;
            padding-bottom: 120px;
            overflow-y: auto;
        }
        .msg { margin-bottom: 24px; animation: slideIn 0.3s ease; display: flex; }
        @keyframes slideIn {
            from { opacity: 0; transform: translateY(12px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .tu { justify-content: flex-end; }
        .tampy { justify-content: flex-start; }
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
        textarea {
            flex: 1;
            background: var(--bg-tertiary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 14px 16px;
            color: var(--text);
            font-size: 15px;
            resize: none;
            height: 52px;
            max-height: 140px;
        }
        textarea:focus { outline: none; border-color: var(--accent); }
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
        }
        .btn-send:disabled { opacity: 0.6; cursor: not-allowed; }
        .pensando {
            color: var(--accent-light);
            font-size: 14px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        @media (max-width: 640px) {
            header { padding: 14px 16px; }
            .chat-container { padding: 16px; padding-bottom: 100px; }
            .input-area { padding: 12px 16px; }
        }
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo-section">
                <span class="logo-icon">🤖</span>
                <h1>TAMPY</h1>
            </div>
            <div class="status">
                <span class="status-dot"></span>
                <span>En línea</span>
            </div>
        </div>
    </header>
    
    <div class="toolbar">
        <div class="toolbar-content">
            <label class="btn-tool" for="file-input">📄 Subir archivo</label>
            <label class="btn-tool" for="image-input">🖼️ Subir imagen</label>
            <span class="file-name" id="file-info"></span>
            <div style="flex:1;"></div>
            <button class="btn-tool" onclick="reiniciarChat()">🔄 Nueva conversación</button>
        </div>
        <input type="file" id="file-input" class="file-input" accept=".txt,.py,.md,.csv,.json">
        <input type="file" id="image-input" class="file-input" accept="image/*">
    </div>
    
    <div class="chat-container" id="chat">
        <div class="msg tampy">
            <div class="bubble">¡Hola! Soy <strong>TAMPY</strong> 🤖
            
Puedo ayudarte con:
💬 Preguntas y respuestas
📄 Leer archivos de texto
🖼️ Analizar imágenes
💻 Explicar y escribir código

¡Sube un archivo o pregúntame lo que necesitas!</div>
        </div>
    </div>
    
    <div class="input-area">
        <div class="input-wrap">
            <textarea id="mensaje" placeholder="Escribe tu mensaje..." onkeydown="handleKey(event)"></textarea>
            <button class="btn-send" id="btn" onclick="enviarMensaje()">Enviar</button>
        </div>
    </div>
    
<script>
const chat = document.getElementById('chat');
const mensaje = document.getElementById('mensaje');
const btn = document.getElementById('btn');
const fileInput = document.getElementById('file-input');
const imageInput = document.getElementById('image-input');
const fileInfo = document.getElementById('file-info');

let archivoParaEnviar = null;
let imagenParaEnviar = null;

function handleKey(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        enviarMensaje();
    }
}

fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    fileInfo.textContent = `📄 ${file.name}`;
    const lector = new FileReader();
    lector.onload = function(evento) {
        archivoParaEnviar = {
            nombre: file.name,
            contenido: evento.target.result
        };
    };
    lector.readAsText(file);
});

imageInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    fileInfo.textContent = `🖼️ ${file.name}`;
    const lector = new FileReader();
    lector.onload = function(evento) {
        imagenParaEnviar = {
            nombre: file.name,
            contenido: evento.target.result.split(',')[1]
        };
    };
    lector.readAsDataURL(file);
});

function agregarMensaje(quien, texto) {
    const div = document.createElement('div');
    div.className = `msg ${quien}`;
    div.innerHTML = `<div class="bubble">${texto.replace(/\\n/g, '<br>')}</div>`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

async function enviarMensaje() {
    const texto = mensaje.value.trim();
    if (!texto && !archivoParaEnviar && !imagenParaEnviar) return;
    
    let textoEnviar = texto;
    if (archivoParaEnviar) {
        textoEnviar = `Archivo: ${archivoParaEnviar.nombre}\\n\\n${archivoParaEnviar.contenido.substring(0, 3000)}`;
        archivoParaEnviar = null;
        fileInfo.textContent = '';
    }
    if (imagenParaEnviar) {
        textoEnviar = texto || 'Describe esta imagen';
        imagenParaEnviar = null;
        fileInfo.textContent = '';
    }
    
    agregarMensaje('tu', textoEnviar);
    mensaje.value = '';
    btn.disabled = true;
    btn.textContent = '...';
    
    const pensando = document.createElement('div');
    pensando.className = 'pensando';
    pensando.innerHTML = '🤖 TAMPY está pensando...';
    chat.appendChild(pensando);
    chat.scrollTop = chat.scrollHeight;
    
    try {
        const respuesta = await fetch('/preguntar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({pregunta: textoEnviar})
        });
        const datos = await respuesta.json();
        pensando.remove();
        agregarMensaje('tampy', datos.respuesta || 'Sin respuesta');
    } catch (error) {
        pensando.remove();
        agregarMensaje('tampy', '⚠️ Error de conexión. Intenta de nuevo.');
    }
    
    btn.disabled = false;
    btn.textContent = 'Enviar';
    mensaje.focus();
}

async function reiniciarChat() {
    if (confirm('¿Empezar conversación nueva?')) {
        await fetch('/reiniciar', {method: 'POST'});
        chat.innerHTML = '<div class
