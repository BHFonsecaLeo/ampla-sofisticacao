import sys
import os
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

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "chave_secreta_muito_segura")  # Usa variável de ambiente no Vercel

# Configuração para upload de logotipos
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # exist_ok evita erros se já existir

# Função para verificar se o usuário é admin
def is_admin():
    if "usuario" not in session:
        return False
    usuario = Usuario.buscar_por_username(session["usuario"])
    return usuario and usuario["role"] == "admin"

# Registrar a função is_admin no ambiente Jinja2
app.jinja_env.globals['is_admin'] = is_admin

@app.route("/")
@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect(url_for("login"))
    clientes = Cliente.total_clientes()
    compras = Compra.total_compras()
    vendas = Venda.total_vendas()
    estoque = Estoque.total_itens()
    orcamentos = Orcamento.total_pendente()
    saldo = Financeiro.calcular_saldo()
    vendas_semanal = Venda.buscar_por_semana()
    compras_semanal = Compra.buscar_por_semana()
    entradas_semanal, saidas_semanal = Financeiro.buscar_fluxo_semanal()
    estoque_baixo = Estoque.verificar_estoque_baixo()
    return render_template(
        "dashboard.html",
        clientes=clientes,
        compras=compras,
        vendas=vendas,
        estoque=estoque,
        orcamentos=orcamentos,
        saldo=saldo,
        vendas_semanal=vendas_semanal,
        compras_semanal=compras_semanal,
        entradas_semanal=entradas_semanal,
        saidas_semanal=saidas_semanal,
        estoque_baixo=estoque_baixo
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        usuario = Usuario.buscar_por_username(username)
        if usuario and check_password_hash(usuario["password_hash"], password):
            session["usuario"] = username
            return redirect(url_for("dashboard"))
        else:
            flash("Usuário ou senha inválidos!", "danger")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = "user"
        if username == "admin":
            role = "admin"
        if Usuario.buscar_por_username(username):
            flash("Usuário já existe!", "danger")
        else:
            try:
                Usuario.adicionar(username, password, role)
                flash("Usuário registrado com sucesso! Faça login.", "success")
                return redirect(url_for("login"))
            except Exception as e:
                flash(f"Erro ao registrar usuário: {e}", "danger")
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("usuario", None)
    return redirect(url_for("login"))

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

@app.route("/clientes", methods=["GET", "POST"])
def clientes():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        if "search" in request.form:
            nome = request.form["search"]
            clientes = Cliente.buscar_por_nome(nome)
        elif "edit" in request.form:
            try:
                Cliente.editar(
                    request.form["cliente_id"],
                    request.form["nome"],
                    request.form["telefone"],
                    request.form["email"]
                )
                flash("Cliente editado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao editar cliente: {e}", "danger")
            return redirect(url_for("clientes"))
        elif "delete" in request.form:
            if not is_admin():
                flash("Apenas administradores podem excluir registros!", "danger")
                return redirect(url_for("clientes"))
            try:
                Cliente.excluir(request.form["cliente_id"])
                flash("Cliente excluído com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao excluir cliente: {e}", "danger")
            return redirect(url_for("clientes"))
        else:
            try:
                Cliente.adicionar(
                    request.form["nome"],
                    request.form["telefone"],
                    request.form["email"]
                )
                flash("Cliente adicionado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao adicionar cliente: {e}", "danger")
            return redirect(url_for("clientes"))
    clientes = Cliente.buscar_todos()
    return render_template("clientes.html", clientes=clientes)

@app.route("/compras", methods=["GET", "POST"])
def compras():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        if "edit" in request.form:
            try:
                Compra.editar(
                    request.form["compra_id"],
                    request.form["material"],
                    float(request.form["quantidade"]),
                    float(request.form["preco"])
                )
                flash("Compra editada com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao editar compra: {e}", "danger")
            return redirect(url_for("compras"))
        elif "delete" in request.form:
            if not is_admin():
                flash("Apenas administradores podem excluir registros!", "danger")
                return redirect(url_for("compras"))
            try:
                Compra.excluir(request.form["compra_id"])
                flash("Compra excluída com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao excluir compra: {e}", "danger")
            return redirect(url_for("compras"))
        else:
            try:
                material = request.form["material"]
                quantidade = float(request.form["quantidade"])
                preco = float(request.form["preco"])
                Compra.adicionar(material, quantidade, preco)
                Financeiro.registrar_transacao("Saída", preco, f"Compra de {material}")
                flash("Compra registrada com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao registrar compra: {e}", "danger")
            return redirect(url_for("compras"))
    compras = Compra.buscar_todos()
    return render_template("compras.html", compras=compras)

@app.route("/vendas", methods=["GET", "POST"])
def vendas():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        if "edit" in request.form:
            try:
                Venda.editar(
                    request.form["venda_id"],
                    int(request.form["empresa_id"]),
                    int(request.form["cliente_id"]),
                    request.form["produto"],
                    float(request.form["quantidade"]),
                    float(request.form["preco"])
                )
                flash("Venda editada com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao editar venda: {e}", "danger")
            return redirect(url_for("vendas"))
        elif "delete" in request.form:
            if not is_admin():
                flash("Apenas administradores podem excluir registros!", "danger")
                return redirect(url_for("vendas"))
            try:
                Venda.excluir(request.form["venda_id"])
                flash("Venda excluída com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao excluir venda: {e}", "danger")
            return redirect(url_for("vendas"))
        else:
            try:
                empresa_id = int(request.form["empresa_id"])
                cliente_id = int(request.form["cliente_id"])
                produto = request.form["produto"]
                quantidade = float(request.form["quantidade"])
                preco = float(request.form["preco"])
                Venda.adicionar(empresa_id, cliente_id, produto, quantidade, preco)
                Financeiro.registrar_transacao("Entrada", preco, f"Venda de {produto}")
                flash("Venda registrada com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao registrar venda: {e}", "danger")
            return redirect(url_for("vendas"))
    empresas = Empresa.buscar_todos()
    clientes = Cliente.buscar_todos()
    vendas = Venda.buscar_todos()
    return render_template("vendas.html", empresas=empresas, clientes=clientes, vendas=vendas)

@app.route("/exportar_vendas_pdf/<int:empresa_id>")
def exportar_vendas_pdf(empresa_id):
    if "usuario" not in session:
        return redirect(url_for("login"))
    if not is_admin():
        flash("Apenas administradores podem exportar relatórios!", "danger")
        return redirect(url_for("vendas"))
    
    empresa = Empresa.buscar_por_id(empresa_id)
    vendas = Venda.buscar_por_empresa(empresa_id)
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Cabeçalho com logotipo e informações da empresa
    if empresa["logotipo"] and os.path.exists(empresa["logotipo"]):
        logo = Image(empresa["logotipo"], width=100, height=50)
        elements.append(logo)
    elements.append(Paragraph(f"{empresa['nome']}", styles['Title']))
    elements.append(Paragraph(f"CNPJ: {empresa['cnpj']} | Endereço: {empresa['endereco']}", styles['Normal']))
    elements.append(Paragraph(f"Telefone: {empresa['telefone']} | Email: {empresa['email']}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Título do relatório
    elements.append(Paragraph("Relatório de Vendas", styles['Heading1']))
    elements.append(Spacer(1, 12))

    # Tabela de vendas
    data = [["ID", "Cliente", "Produto", "Quantidade", "Preço (R$)", "Data"]]
    for venda in vendas:
        data.append([
            str(venda["id"]),
            venda["cliente_nome"],
            venda["produto"],
            str(venda["quantidade"]),
            f"{venda['preco']:.2f}",
            venda["data"]
        ])
    
    table = Table(data, colWidths=[50, 150, 150, 70, 70, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    # Rodapé
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Ampla Sofisticação", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"relatorio_vendas_{empresa['nome']}.pdf")

@app.route("/estoque", methods=["GET", "POST"])
def estoque():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        if "edit" in request.form:
            try:
                Estoque.editar(
                    request.form["estoque_id"],
                    request.form["item"],
                    float(request.form["quantidade"]),
                    float(request.form["limite_minimo"])
                )
                flash("Item editado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao editar item: {e}", "danger")
            return redirect(url_for("estoque"))
        elif "delete" in request.form:
            if not is_admin():
                flash("Apenas administradores podem excluir registros!", "danger")
                return redirect(url_for("estoque"))
            try:
                Estoque.excluir(request.form["estoque_id"])
                flash("Item excluído com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao excluir item: {e}", "danger")
            return redirect(url_for("estoque"))
        else:
            try:
                Estoque.adicionar(
                    request.form["item"],
                    float(request.form["quantidade"]),
                    float(request.form["limite_minimo"])
                )
                flash("Item adicionado ao estoque com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao adicionar item ao estoque: {e}", "danger")
            return redirect(url_for("estoque"))
    itens = Estoque.buscar_todos()
    return render_template("estoque.html", itens=itens)

@app.route("/orcamentos", methods=["GET", "POST"])
def orcamentos():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        if "edit" in request.form:
            try:
                Orcamento.editar(
                    request.form["orcamento_id"],
                    int(request.form["empresa_id"]),
                    int(request.form["cliente_id"]),
                    request.form["descricao"],
                    float(request.form["valor"])
                )
                flash("Orçamento editado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao editar orçamento: {e}", "danger")
            return redirect(url_for("orcamentos"))
        elif "delete" in request.form:
            if not is_admin():
                flash("Apenas administradores podem excluir registros!", "danger")
                return redirect(url_for("orcamentos"))
            try:
                Orcamento.excluir(request.form["orcamento_id"])
                flash("Orçamento excluído com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao excluir orçamento: {e}", "danger")
            return redirect(url_for("orcamentos"))
        elif "aprovar" in request.form:
            try:
                Orcamento.aprovar(request.form["orcamento_id"])
                flash("Orçamento aprovado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao aprovar orçamento: {e}", "danger")
            return redirect(url_for("orcamentos"))
        else:
            try:
                empresa_id = int(request.form["empresa_id"])
                cliente_id = int(request.form["cliente_id"])
                descricao = request.form["descricao"]
                valor = float(request.form["valor"])
                Orcamento.adicionar(empresa_id, cliente_id, descricao, valor)
                flash("Orçamento criado com sucesso!", "success")
            except Exception as e:
                flash(f"Erro ao criar orçamento: {e}", "danger")
            return redirect(url_for("orcamentos"))
    empresas = Empresa.buscar_todos()
    clientes = Cliente.buscar_todos()
    orcamentos = Orcamento.buscar_todos()
    return render_template("orcamentos.html", empresas=empresas, clientes=clientes, orcamentos=orcamentos)

@app.route("/exportar_orcamento_pdf/<int:orcamento_id>")
def exportar_orcamento_pdf(orcamento_id):
    if "usuario" not in session:
        return redirect(url_for("login"))
    
    orcamento = Orcamento.buscar_por_id(orcamento_id)
    if not orcamento:
        flash("Orçamento não encontrado!", "danger")
        return redirect(url_for("orcamentos"))
    
    empresa = Empresa.buscar_por_id(orcamento["empresa_id"])
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Cabeçalho com logotipo e informações da empresa
    if empresa["logotipo"] and os.path.exists(empresa["logotipo"]):
        logo = Image(empresa["logotipo"], width=100, height=50)
        elements.append(logo)
    elements.append(Paragraph(f"{empresa['nome']}", styles['Title']))
    elements.append(Paragraph(f"CNPJ: {empresa['cnpj']} | Endereço: {empresa['endereco']}", styles['Normal']))
    elements.append(Paragraph(f"Telefone: {empresa['telefone']} | Email: {empresa['email']}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Título do orçamento
    elements.append(Paragraph(f"Orçamento #{orcamento['id']}", styles['Heading1']))
    elements.append(Spacer(1, 12))

    # Informações do cliente e orçamento
    elements.append(Paragraph(f"Cliente: {orcamento['cliente_nome']}", styles['Normal']))
    elements.append(Paragraph(f"Data de Criação: {orcamento['data_criacao']}", styles['Normal']))
    elements.append(Paragraph(f"Status: {orcamento['status']}", styles['Normal']))
    elements.append(Spacer(1, 12))

    # Tabela do orçamento
    data = [["Descrição", "Valor (R$)"]]
    data.append([orcamento["descricao"], f"{orcamento['valor']:.2f}"])
    
    table = Table(data, colWidths=[400, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    # Total
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Total: R$ {orcamento['valor']:.2f}", styles['Heading2']))

    # Rodapé
    elements.append(Spacer(1, 24))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Ampla Sofisticação", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"orcamento_{orcamento['id']}_{empresa['nome']}.pdf")

@app.route("/financeiro")
def financeiro():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if not is_admin():
        flash("Apenas administradores podem acessar o financeiro!", "danger")
        return redirect(url_for("dashboard"))
    transacoes = Financeiro.buscar_todos()
    saldo = Financeiro.calcular_saldo()
    return render_template("financeiro.html", transacoes=transacoes, saldo=saldo)

@app.route("/exportar_financeiro_pdf")
def exportar_financeiro_pdf():
    if "usuario" not in session:
        return redirect(url_for("login"))
    if not is_admin():
        flash("Apenas administradores podem exportar relatórios!", "danger")
        return redirect(url_for("dashboard"))
    transacoes = Financeiro.buscar_todos()
    saldo = Financeiro.calcular_saldo()
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Relatório Financeiro - Ampla Sofisticação", styles['Heading1']))
    elements.append(Paragraph(f"Saldo Atual: R$ {saldo:.2f}", styles['Normal']))
    elements.append(Spacer(1, 12))

    data = [["ID", "Tipo", "Valor (R$)", "Data", "Descrição"]]
    for transacao in transacoes:
        data.append([
            str(transacao["id"]),
            transacao["tipo"],
            f"{transacao['valor']:.2f}",
            transacao["data"],
            transacao["descricao"]
        ])
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')} - Ampla Sofisticação", styles['Normal']))

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="relatorio_financeiro.pdf")

# Exportar a aplicação para o Vercel como WSGI
application = app

# Para teste local (remover antes de enviar ao Vercel)
# if __name__ == "__main__":
#     app.run(debug=True)