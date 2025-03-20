import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    @staticmethod
    def get_connection():
        # Caminho relativo ao raiz a partir de api/
        db_path = os.path.join(os.path.dirname(__file__), "..", "ampla_sofisticacao.db")
        return sqlite3.connect(db_path)

class Usuario:
    @staticmethod
    def criar_tabela():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user'
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def adicionar(username, password, role='user'):
        password_hash = generate_password_hash(password)
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)", (username, password_hash, role))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_por_username(username):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        usuario = cursor.fetchone()
        conn.close()
        if usuario:
            if len(usuario) >= 4:
                return {"id": usuario[0], "username": usuario[1], "password_hash": usuario[2], "role": usuario[3]}
            elif len(usuario) == 3:
                return {"id": usuario[0], "username": usuario[1], "password_hash": usuario[2], "role": "user"}
        return None

class Empresa:
    @staticmethod
    def criar_tabela():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS empresas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cnpj TEXT NOT NULL UNIQUE,
                endereco TEXT NOT NULL,
                telefone TEXT NOT NULL,
                email TEXT NOT NULL,
                logotipo TEXT
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def adicionar(nome, cnpj, endereco, telefone, email, logotipo=None):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO empresas (nome, cnpj, endereco, telefone, email, logotipo) VALUES (?, ?, ?, ?, ?, ?)",
                       (nome, cnpj, endereco, telefone, email, logotipo))
        conn.commit()
        conn.close()

    @staticmethod
    def editar(empresa_id, nome, cnpj, endereco, telefone, email, logotipo=None):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE empresas SET nome = ?, cnpj = ?, endereco = ?, telefone = ?, email = ?, logotipo = ? WHERE id = ?",
                       (nome, cnpj, endereco, telefone, email, logotipo, empresa_id))
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(empresa_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM empresas WHERE id = ?", (empresa_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM empresas")
        empresas = cursor.fetchall()
        conn.close()
        return [{"id": e[0], "nome": e[1], "cnpj": e[2], "endereco": e[3], "telefone": e[4], "email": e[5], "logotipo": e[6]} for e in empresas]

    @staticmethod
    def buscar_por_id(empresa_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM empresas WHERE id = ?", (empresa_id,))
        empresa = cursor.fetchone()
        conn.close()
        if empresa:
            return {"id": empresa[0], "nome": empresa[1], "cnpj": empresa[2], "endereco": empresa[3], "telefone": empresa[4], "email": empresa[5], "logotipo": empresa[6]}
        return None

class Cliente:
    @staticmethod
    def criar_tabela():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT NOT NULL,
                email TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def adicionar(nome, telefone, email):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?)", (nome, telefone, email))
        conn.commit()
        conn.close()

    @staticmethod
    def editar(cliente_id, nome, telefone, email):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE clientes SET nome = ?, telefone = ?, email = ? WHERE id = ?", (nome, telefone, email, cliente_id))
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(cliente_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()
        conn.close()
        return [{"id": c[0], "nome": c[1], "telefone": c[2], "email": c[3]} for c in clientes]

    @staticmethod
    def buscar_por_id(cliente_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        cliente = cursor.fetchone()
        conn.close()
        if cliente:
            return {"id": cliente[0], "nome": cliente[1], "telefone": cliente[2], "email": cliente[3]}
        return None

    @staticmethod
    def buscar_por_nome(nome):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE nome LIKE ?", (f"%{nome}%",))
        clientes = cursor.fetchall()
        conn.close()
        return [{"id": c[0], "nome": c[1], "telefone": c[2], "email": c[3]} for c in clientes]

    @staticmethod
    def total_clientes():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clientes")
        total = cursor.fetchone()[0]
        conn.close()
        return total

class Compra:
    @staticmethod
    def criar_tabela():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                material TEXT NOT NULL,
                quantidade REAL NOT NULL,
                preco REAL NOT NULL,
                data TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def adicionar(material, quantidade, preco):
        data = datetime.now().strftime("%Y-%m-%d")
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO compras (material, quantidade, preco, data) VALUES (?, ?, ?, ?)", (material, quantidade, preco, data))
        conn.commit()
        conn.close()

    @staticmethod
    def editar(compra_id, material, quantidade, preco):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE compras SET material = ?, quantidade = ?, preco = ? WHERE id = ?", (material, quantidade, preco, compra_id))
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(compra_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM compras WHERE id = ?", (compra_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM compras")
        compras = cursor.fetchall()
        conn.close()
        return [{"id": c[0], "material": c[1], "quantidade": c[2], "preco": c[3], "data": c[4]} for c in compras]

    @staticmethod
    def buscar_por_id(compra_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM compras WHERE id = ?", (compra_id,))
        compra = cursor.fetchone()
        conn.close()
        if compra:
            return {"id": compra[0], "material": compra[1], "quantidade": compra[2], "preco": compra[3], "data": compra[4]}
        return None

    @staticmethod
    def total_compras():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM compras")
        total = cursor.fetchone()[0]
        conn.close()
        return total

    @staticmethod
    def buscar_por_semana():
        conn = Database.get_connection()
        cursor = conn.cursor()
        hoje = datetime.now()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        dias = [(inicio_semana + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        compras_por_dia = {dia: 0 for dia in dias}
        cursor.execute("SELECT data, COUNT(*) FROM compras WHERE data >= ? GROUP BY data", (inicio_semana.strftime("%Y-%m-%d"),))
        for data, total in cursor.fetchall():
            if data in compras_por_dia:
                compras_por_dia[data] = total
        conn.close()
        return compras_por_dia

class Venda:
    @staticmethod
    def criar_tabela():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                cliente_id INTEGER NOT NULL,
                produto TEXT NOT NULL,
                quantidade REAL NOT NULL,
                preco REAL NOT NULL,
                data TEXT NOT NULL,
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        ''')
        cursor.execute("PRAGMA table_info(vendas)")
        columns = [col[1] for col in cursor.fetchall()]
        if "empresa_id" not in columns:
            cursor.execute("ALTER TABLE vendas ADD COLUMN empresa_id INTEGER REFERENCES empresas(id)")
        conn.commit()
        conn.close()

    @staticmethod
    def adicionar(empresa_id, cliente_id, produto, quantidade, preco):
        data = datetime.now().strftime("%Y-%m-%d")
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO vendas (empresa_id, cliente_id, produto, quantidade, preco, data) VALUES (?, ?, ?, ?, ?, ?)",
                       (empresa_id, cliente_id, produto, quantidade, preco, data))
        conn.commit()
        conn.close()

    @staticmethod
    def editar(venda_id, empresa_id, cliente_id, produto, quantidade, preco):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE vendas SET empresa_id = ?, cliente_id = ?, produto = ?, quantidade = ?, preco = ? WHERE id = ?",
                       (empresa_id, cliente_id, produto, quantidade, preco, venda_id))
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(venda_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vendas WHERE id = ?", (venda_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.id, e.nome, c.nome, v.produto, v.quantidade, v.preco, v.data
            FROM vendas v
            LEFT JOIN empresas e ON v.empresa_id = e.id
            LEFT JOIN clientes c ON v.cliente_id = c.id
        ''')
        vendas = cursor.fetchall()
        conn.close()
        return [{"id": v[0], "empresa_nome": v[1] if v[1] else "Desconhecida", "cliente_nome": v[2] if v[2] else "Desconhecido", "produto": v[3], "quantidade": v[4], "preco": v[5], "data": v[6]} for v in vendas]

    @staticmethod
    def buscar_por_empresa(empresa_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.id, e.nome, c.nome, v.produto, v.quantidade, v.preco, v.data
            FROM vendas v
            LEFT JOIN empresas e ON v.empresa_id = e.id
            LEFT JOIN clientes c ON v.cliente_id = c.id
            WHERE v.empresa_id = ?
        ''', (empresa_id,))
        vendas = cursor.fetchall()
        conn.close()
        return [{"id": v[0], "empresa_nome": v[1] if v[1] else "Desconhecida", "cliente_nome": v[2] if v[2] else "Desconhecido", "produto": v[3], "quantidade": v[4], "preco": v[5], "data": v[6]} for v in vendas]

    @staticmethod
    def buscar_por_id(venda_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.id, e.nome, v.empresa_id, c.nome, v.cliente_id, v.produto, v.quantidade, v.preco, v.data
            FROM vendas v
            LEFT JOIN empresas e ON v.empresa_id = e.id
            LEFT JOIN clientes c ON v.cliente_id = c.id
            WHERE v.id = ?
        ''', (venda_id,))
        venda = cursor.fetchone()
        conn.close()
        if venda:
            return {"id": venda[0], "empresa_nome": venda[1] if venda[1] else "Desconhecida", "empresa_id": venda[2], "cliente_nome": venda[3] if venda[3] else "Desconhecido", "cliente_id": venda[4], "produto": venda[5], "quantidade": venda[6], "preco": venda[7], "data": venda[8]}
        return None

    @staticmethod
    def total_vendas():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vendas")
        total = cursor.fetchone()[0]
        conn.close()
        return total

    @staticmethod
    def buscar_por_semana():
        conn = Database.get_connection()
        cursor = conn.cursor()
        hoje = datetime.now()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        dias = [(inicio_semana + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        vendas_por_dia = {dia: 0 for dia in dias}
        cursor.execute("SELECT data, COUNT(*) FROM vendas WHERE data >= ? GROUP BY data", (inicio_semana.strftime("%Y-%m-%d"),))
        for data, total in cursor.fetchall():
            if data in vendas_por_dia:
                vendas_por_dia[data] = total
        conn.close()
        return vendas_por_dia

class Estoque:
    @staticmethod
    def criar_tabela():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estoque (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item TEXT NOT NULL,
                quantidade REAL NOT NULL,
                limite_minimo REAL NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def adicionar(item, quantidade, limite_minimo):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO estoque (item, quantidade, limite_minimo) VALUES (?, ?, ?)", (item, quantidade, limite_minimo))
        conn.commit()
        conn.close()

    @staticmethod
    def editar(estoque_id, item, quantidade, limite_minimo):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE estoque SET item = ?, quantidade = ?, limite_minimo = ? WHERE id = ?", (item, quantidade, limite_minimo, estoque_id))
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(estoque_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM estoque WHERE id = ?", (estoque_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estoque")
        itens = cursor.fetchall()
        conn.close()
        return [{"id": i[0], "item": i[1], "quantidade": i[2], "limite_minimo": i[3]} for i in itens]

    @staticmethod
    def buscar_por_id(estoque_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estoque WHERE id = ?", (estoque_id,))
        item = cursor.fetchone()
        conn.close()
        if item:
            return {"id": item[0], "item": item[1], "quantidade": item[2], "limite_minimo": item[3]}
        return None

    @staticmethod
    def total_itens():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantidade) FROM estoque")
        total = cursor.fetchone()[0] or 0
        conn.close()
        return total

    @staticmethod
    def verificar_estoque_baixo():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT item, quantidade, limite_minimo FROM estoque WHERE quantidade <= limite_minimo")
        itens = cursor.fetchall()
        conn.close()
        return [{"item": i[0], "quantidade": i[1], "limite_minimo": i[2]} for i in itens]

class Orcamento:
    @staticmethod
    def criar_tabela():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orcamentos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                empresa_id INTEGER,
                cliente_id INTEGER NOT NULL,
                descricao TEXT NOT NULL,
                valor REAL NOT NULL,
                data_criacao TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pendente',
                FOREIGN KEY (empresa_id) REFERENCES empresas(id)
            )
        ''')
        cursor.execute("PRAGMA table_info(orcamentos)")
        columns = [col[1] for col in cursor.fetchall()]
        if "empresa_id" not in columns:
            cursor.execute("ALTER TABLE orcamentos ADD COLUMN empresa_id INTEGER REFERENCES empresas(id)")
        conn.commit()
        conn.close()

    @staticmethod
    def adicionar(empresa_id, cliente_id, descricao, valor):
        data_criacao = datetime.now().strftime("%Y-%m-%d")
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO orcamentos (empresa_id, cliente_id, descricao, valor, data_criacao, status) VALUES (?, ?, ?, ?, ?, ?)",
                       (empresa_id, cliente_id, descricao, valor, data_criacao, "Pendente"))
        conn.commit()
        conn.close()

    @staticmethod
    def editar(orcamento_id, empresa_id, cliente_id, descricao, valor):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE orcamentos SET empresa_id = ?, cliente_id = ?, descricao = ?, valor = ? WHERE id = ?",
                       (empresa_id, cliente_id, descricao, valor, orcamento_id))
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(orcamento_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orcamentos WHERE id = ?", (orcamento_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.id, e.nome, c.nome, o.descricao, o.valor, o.data_criacao, o.status
            FROM orcamentos o
            LEFT JOIN empresas e ON o.empresa_id = e.id
            LEFT JOIN clientes c ON o.cliente_id = c.id
        ''')
        orcamentos = cursor.fetchall()
        conn.close()
        return [{"id": o[0], "empresa_nome": o[1] if o[1] else "Desconhecida", "cliente_nome": o[2] if o[2] else "Desconhecido", "descricao": o[3], "valor": o[4], "data_criacao": o[5], "status": o[6]} for o in orcamentos]

    @staticmethod
    def buscar_por_empresa(empresa_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.id, e.nome, c.nome, o.descricao, o.valor, o.data_criacao, o.status
            FROM orcamentos o
            LEFT JOIN empresas e ON o.empresa_id = e.id
            LEFT JOIN clientes c ON o.cliente_id = c.id
            WHERE o.empresa_id = ?
        ''', (empresa_id,))
        orcamentos = cursor.fetchall()
        conn.close()
        return [{"id": o[0], "empresa_nome": o[1] if o[1] else "Desconhecida", "cliente_nome": o[2] if o[2] else "Desconhecido", "descricao": o[3], "valor": o[4], "data_criacao": o[5], "status": o[6]} for o in orcamentos]

    @staticmethod
    def buscar_por_id(orcamento_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.id, e.nome, o.empresa_id, c.nome, o.cliente_id, o.descricao, o.valor, o.data_criacao, o.status
            FROM orcamentos o
            LEFT JOIN empresas e ON o.empresa_id = e.id
            LEFT JOIN clientes c ON o.cliente_id = c.id
            WHERE o.id = ?
        ''', (orcamento_id,))
        orcamento = cursor.fetchone()
        conn.close()
        if orcamento:
            return {"id": orcamento[0], "empresa_nome": orcamento[1] if orcamento[1] else "Desconhecida", "empresa_id": orcamento[2], "cliente_nome": orcamento[3] if orcamento[3] else "Desconhecido", "cliente_id": orcamento[4], "descricao": orcamento[5], "valor": orcamento[6], "data_criacao": orcamento[7], "status": orcamento[8]}
        return None

    @staticmethod
    def aprovar(orcamento_id):
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE orcamentos SET status = ? WHERE id = ?", ("Aprovado", orcamento_id))
        conn.commit()
        conn.close()

    @staticmethod
    def total_pendente():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orcamentos WHERE status = ?", ("Pendente",))
        total = cursor.fetchone()[0]
        conn.close()
        return total

class Financeiro:
    @staticmethod
    def criar_tabela():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS financeiro (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL,
                valor REAL NOT NULL,
                data TEXT NOT NULL,
                descricao TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def registrar_transacao(tipo, valor, descricao):
        data = datetime.now().strftime("%Y-%m-%d")
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO financeiro (tipo, valor, data, descricao) VALUES (?, ?, ?, ?)", (tipo, valor, data, descricao))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM financeiro")
        transacoes = cursor.fetchall()
        conn.close()
        return [{"id": t[0], "tipo": t[1], "valor": t[2], "data": t[3], "descricao": t[4]} for t in transacoes]

    @staticmethod
    def calcular_saldo():
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT tipo, valor FROM financeiro")
        transacoes = cursor.fetchall()
        saldo = 0
        for tipo, valor in transacoes:
            if tipo == "Entrada":
                saldo += valor
            else:
                saldo -= valor
        conn.close()
        return saldo

    @staticmethod
    def buscar_fluxo_semanal():
        conn = Database.get_connection()
        cursor = conn.cursor()
        hoje = datetime.now()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        dias = [(inicio_semana + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        entradas_por_dia = {dia: 0 for dia in dias}
        saidas_por_dia = {dia: 0 for dia in dias}
        cursor.execute("SELECT data, tipo, valor FROM financeiro WHERE data >= ?", (inicio_semana.strftime("%Y-%m-%d"),))
        for data, tipo, valor in cursor.fetchall():
            if data in entradas_por_dia:
                if tipo == "Entrada":
                    entradas_por_dia[data] += valor
                else:
                    saidas_por_dia[data] += valor
        conn.close()
        return entradas_por_dia, saidas_por_dia

# Inicializar as tabelas
Usuario.criar_tabela()
Empresa.criar_tabela()
Cliente.criar_tabela()
Compra.criar_tabela()
Venda.criar_tabela()
Estoque.criar_tabela()
Orcamento.criar_tabela()
Financeiro.criar_tabela()
