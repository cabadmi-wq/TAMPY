# ==============================================
# 🤖 TAMPY - Asistente Inteligente - Versión Final
# ==============================================

from flask import Flask, render_template_string, request, jsonify
import requests

app = Flask(__name__)

# 🔑 Configuración
HF_API_URL = “https://api-inference.huggingface.co/models/gpt2”
HF_API_TOKEN = "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"
headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

# 🧠 Historial de conversación
historial = [
    {
        "role": "system",
        "content": "Eres TAMPY, una asistente amable y servicial. Respondes siempre en español de forma clara y útil."
    }
]

def consultar_ia(mensaje_nuevo):
    historial.append({"role": "user", "content": mensaje_nuevo})
    
    prompt = ""
    for msg in historial:
        if msg["role"] == "system":
            prompt += f"<|system|>\n{msg['content']}\n"
        elif msg["role"] == "user":
            prompt += f"<|user|>\n{msg['content']}\n"
        else:
            prompt += f"<|assistant|>\n{msg['content']}\n"
    prompt += "<|assistant|>\n"
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "return_full_text": False
        }
    }
    
    try:
        respuesta = requests.post(HF_API_URL, headers=headers, json=payload, timeout=120)
        respuesta.raise_for_status()
        resultado = respuesta.json()
        if isinstance(resultado, list) and len(resultado) > 0:
            texto = resultado[0].get('generated_text', '').strip()
            historial.append({"role": "assistant", "content": texto})
            return texto
        return "No recibí respuesta del modelo."
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# 🌐 INTERFAZ WEB
@app.route('/')
def index():
    return render_template_string("""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🤖 TAMPY - Tu Asistente Inteligente</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', sans-serif; }
        body {
            background: linear-gradient(135deg, #0f172a, #1e293b);
            color: #f1f5f9;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        header {
            background: linear-gradient(90deg, #0284c7, #38bdf8);
            padding: 20px;
            text-align: center;
        }
        header h1 { font-size: 24px; }
        .chat {
            flex: 1;
            max-width: 700px;
            width: 100%;
            margin: 0 auto;
            padding: 20px;
            padding-bottom: 100px;
        }
        .mensaje { margin-bottom: 20px; animation: aparecer 0.3s ease; }
        @keyframes aparecer {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .usuario { text-align: right; }
        .tampy { text-align: left; }
        .burbuja {
            display: inline-block;
            padding: 14px 18px;
            border-radius: 18px;
            max-width: 85%;
            line-height: 1.6;
        }
        .usuario .burbuja {
            background: #0369a1;
            border-bottom-right-radius: 4px;
        }
        .tampy .burbuja {
            background: #334155;
            border-bottom-left-radius: 4px;
        }
        .entrada {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #1e293b;
            border-top: 1px solid #475569;
            padding: 15px 20px;
        }
        .fila-entrada {
            max-width: 700px;
            margin: 0 auto;
            display: flex;
            gap: 10px;
        }
        textarea {
            flex: 1;
            background: #334155;
            border: 1px solid #475569;
            border-radius: 12px;
            padding: 12px 15px;
            color: white;
            font-size: 15px;
            resize: none;
            height: 50px;
        }
        textarea:focus { outline: none; border-color: #38bdf8; }
        button {
            background: linear-gradient(90deg, #0284c7, #38bdf8);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0 25px;
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            height: 50px;
        }
        button:disabled { opacity: 0.6; cursor: not-allowed; }
        .escribiendo { color: #7dd3fc; font-size: 14px; margin-bottom: 15px; }
    </style>
</head>
<body>
    <header>
        <h1>🤖 TAMPY - Tu Asistente Inteligente</h1>
    </header>
    
    <div class="chat" id="chat">
        <div class="mensaje tampy">
            <div class="burbuja">¡Hola! Soy TAMPY 🤖<br>¿En qué puedo ayudarte hoy?</div>
        </div>
    </div>
    
    <div class="entrada">
        <div class="fila-entrada">
            <textarea id="texto" placeholder="Escribe tu mensaje..." onkeydown="teclaEnter(event)"></textarea>
            <button id="btn-enviar" onclick="enviar()">Enviar</button>
        </div>
    </div>

<script>
const chat = document.getElementById('chat');
const texto = document.getElementById('texto');
const btn = document.getElementById('btn-enviar');

function teclaEnter(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        enviar();
    }
}

function agregarMensaje(quien, contenido) {
    const div = document.createElement('div');
    div.className = `mensaje ${quien}`;
    div.innerHTML = `<div class="burbuja">${contenido.replace(/\\n/g, '<br>')}</div>`;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

async function enviar() {
    const mensaje = texto.value.trim();
    if (!mensaje) return;
    
    agregarMensaje('usuario', mensaje);
    texto.value = '';
    btn.disabled = true;
    btn.textContent = '...';
    
    const escribiendo = document.createElement('div');
    escribiendo.className = 'escribiendo';
    escribiendo.textContent = '🤖 TAMPY está pensando...';
    chat.appendChild(escribiendo);
    chat.scrollTop = chat.scrollHeight;
    
    try {
        const respuesta = await fetch('/preguntar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ pregunta: mensaje })
        });
        const datos = await respuesta.json();
        escribiendo.remove();
        agregarMensaje('tampy', datos.respuesta || 'No obtuve respuesta.');
    } catch (error) {
        escribiendo.remove();
        agregarMensaje('tampy', '⚠️ Error de conexión. Intenta de nuevo.');
    }
    
    btn.disabled = false;
    btn.textContent = 'Enviar';
    texto.focus();
}
</script>
</body>
</html>
    """)

# 📨 Ruta para recibir preguntas
@app.route('/preguntar', methods=['POST'])
def preguntar():
    datos = request.get_json()
    pregunta = datos.get('pregunta', '')
    respuesta = consultar_ia(pregunta)
    return jsonify({"respuesta": respuesta})

if __name__ == '__main__':
    app.run(debug=False)
