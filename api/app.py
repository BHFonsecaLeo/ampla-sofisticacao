import sys
import os
import logging
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models import Usuario, Empresa, Cliente, Compra, Venda, Estoque, Orcamento, Financeiro
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')))
app.secret_key = os.getenv("FLASK_SECRET_KEY", "chave_secreta_muito_segura")
logger.info("Aplicação Flask iniciada")

# Configuração para upload de logotipos
UPLOAD_FOLDER = '/tmp/uploads' if os.getenv('VERCEL') else os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.getenv('VERCEL'):  # Criar diretório apenas localmente, não no Vercel ao iniciar
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def is_admin():
    if "usuario" not in session:
        return False
    usuario = Usuario.buscar_por_username(session["usuario"])
    return usuario and usuario["role"] == "admin"

app.jinja_env.globals['is_admin'] = is_admin

# ... (outras rotas permanecem iguais até /empresas)

@app.route("/empresas", methods=["GET", "POST"])
def empresas():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        if "edit" in request.form:
            try:
                logotipo = None
                if 'logotipo' in request.files and request.files['logotipo'].filename != '':
                    file = request.files['logotipo']
                    logotipo = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    # Criar o diretório se não existir (necessário no Vercel)
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    file.save(logotipo)
                Empresa.editar(
                    request.form["empresa_id"],
                    request.form["nome"],
                    request.form["cnpj"],
                    request.form["endereco"],
                    request.form["telefone"],
                    request.form["email"],
                    logotipo
                )
                flash("Empresa editada com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao editar empresa: {e}", "danger")
            return redirect(url_for("empresas"))
        elif "delete" in request.form:
            if not is_admin():
                flash("Apenas administradores podem excluir registros!", "danger")
                return redirect(url_for("empresas"))
            try:
                Empresa.excluir(request.form["empresa_id"])
                flash("Empresa excluída com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao excluir empresa: {e}", "danger")
            return redirect(url_for("empresas"))
        else:
            try:
                logotipo = None
                if 'logotipo' in request.files and request.files['logotipo'].filename != '':
                    file = request.files['logotipo']
                    logotipo = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    # Criar o diretório se não existir (necessário no Vercel)
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    file.save(logotipo)
                Empresa.adicionar(
                    request.form["nome"],
                    request.form["cnpj"],
                    request.form["endereco"],
                    request.form["telefone"],
                    request.form["email"],
                    logotipo
                )
                flash("Empresa adicionada com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao adicionar empresa: {e}", "danger")
            return redirect(url_for("empresas"))
    empresas = Empresa.buscar_todos()
    return render_template("empresas.html", empresas=empresas)

# ... (outras rotas permanecem iguais)

application = app
