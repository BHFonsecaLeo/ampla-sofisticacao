import sqlite3
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Usar /tmp no Vercel, caso contrário, o caminho local
DB_PATH = '/tmp/ampla_sofisticacao.db' if os.getenv('VERCEL') else os.path.join(os.path.dirname(__file__), 'ampla_sofisticacao.db')

# Função auxiliar para conectar ao banco
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Retorna resultados como dicionários
    return conn

# Inicializar o banco de dados com tabelas
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        )
    ''')

    # Tabela de Empresas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cnpj TEXT UNIQUE NOT NULL,
            endereco TEXT,
            telefone TEXT,
            email TEXT,
            logotipo TEXT
        )
    ''')

    # Tabela de Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT,
            email TEXT
        )
    ''')

    # Tabela de Compras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            material TEXT NOT NULL,
            quantidade REAL NOT NULL,
            preco REAL NOT NULL,
            data TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de Vendas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER,
            cliente_id INTEGER,
            produto TEXT NOT NULL,
            quantidade REAL NOT NULL,
            preco REAL NOT NULL,
            data TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (empresa_id) REFERENCES empresas(id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')

    # Tabela de Estoque
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS estoque (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            quantidade REAL NOT NULL,
            limite_minimo REAL NOT NULL
        )
    ''')

    # Tabela de Orçamentos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa_id INTEGER,
            cliente_id INTEGER,
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            data_criacao TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Pendente',
            FOREIGN KEY (empresa_id) REFERENCES empresas(id),
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')

    # Tabela de Financeiro
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS financeiro (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            data TEXT DEFAULT CURRENT_TIMESTAMP,
            descricao TEXT
        )
    ''')

    conn.commit()
    conn.close()

# Classe para Usuários
class Usuario:
    @staticmethod
    def adicionar(username, password, role="user"):
        conn = get_db_connection()
        cursor = conn.cursor()
        password_hash = generate_password_hash(password)
        cursor.execute(
            "INSERT INTO usuarios (username, password_hash, role) VALUES (?, ?, ?)",
            (username, password_hash, role)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_por_username(username):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ?", (username,))
        usuario = cursor.fetchone()
        conn.close()
        return usuario

# Classe para Empresas
class Empresa:
    @staticmethod
    def adicionar(nome, cnpj, endereco, telefone, email, logotipo):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO empresas (nome, cnpj, endereco, telefone, email, logotipo) VALUES (?, ?, ?, ?, ?, ?)",
            (nome, cnpj, endereco, telefone, email, logotipo)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def editar(empresa_id, nome, cnpj, endereco, telefone, email, logotipo):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE empresas SET nome = ?, cnpj = ?, endereco = ?, telefone = ?, email = ?, logotipo = ? WHERE id = ?",
            (nome, cnpj, endereco, telefone, email, logotipo, empresa_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(empresa_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM empresas WHERE id = ?", (empresa_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM empresas")
        empresas = cursor.fetchall()
        conn.close()
        return empresas

    @staticmethod
    def buscar_por_id(empresa_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM empresas WHERE id = ?", (empresa_id,))
        empresa = cursor.fetchone()
        conn.close()
        return empresa

# Classe para Clientes
class Cliente:
    @staticmethod
    def adicionar(nome, telefone, email):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clientes (nome, telefone, email) VALUES (?, ?, ?)",
            (nome, telefone, email)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def editar(cliente_id, nome, telefone, email):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE clientes SET nome = ?, telefone = ?, email = ? WHERE id = ?",
            (nome, telefone, email, cliente_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(cliente_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes")
        clientes = cursor.fetchall()
        conn.close()
        return clientes

    @staticmethod
    def buscar_por_nome(nome):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE nome LIKE ?", (f"%{nome}%",))
        clientes = cursor.fetchall()
        conn.close()
        return clientes

    @staticmethod
    def total_clientes():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM clientes")
        total = cursor.fetchone()[0]
        conn.close()
        return total

# Classe para Compras
class Compra:
    @staticmethod
    def adicionar(material, quantidade, preco):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO compras (material, quantidade, preco) VALUES (?, ?, ?)",
            (material, quantidade, preco)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def editar(compra_id, material, quantidade, preco):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE compras SET material = ?, quantidade = ?, preco = ? WHERE id = ?",
            (material, quantidade, preco, compra_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(compra_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM compras WHERE id = ?", (compra_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM compras")
        compras = cursor.fetchall()
        conn.close()
        return compras

    @staticmethod
    def total_compras():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM compras")
        total = cursor.fetchone()[0]
        conn.close()
        return total

    @staticmethod
    def buscar_por_semana():
        conn = get_db_connection()
        cursor = conn.cursor()
        data_inicio = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM compras WHERE data >= ?", (data_inicio,))
        total = cursor.fetchone()[0]
        conn.close()
        return total

# Classe para Vendas
class Venda:
    @staticmethod
    def adicionar(empresa_id, cliente_id, produto, quantidade, preco):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO vendas (empresa_id, cliente_id, produto, quantidade, preco) VALUES (?, ?, ?, ?, ?)",
            (empresa_id, cliente_id, produto, quantidade, preco)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def editar(venda_id, empresa_id, cliente_id, produto, quantidade, preco):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE vendas SET empresa_id = ?, cliente_id = ?, produto = ?, quantidade = ?, preco = ? WHERE id = ?",
            (empresa_id, cliente_id, produto, quantidade, preco, venda_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(venda_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM vendas WHERE id = ?", (venda_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, c.nome AS cliente_nome 
            FROM vendas v 
            JOIN clientes c ON v.cliente_id = c.id
        ''')
        vendas = cursor.fetchall()
        conn.close()
        return vendas

    @staticmethod
    def buscar_por_empresa(empresa_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, c.nome AS cliente_nome 
            FROM vendas v 
            JOIN clientes c ON v.cliente_id = c.id 
            WHERE v.empresa_id = ?
        ''', (empresa_id,))
        vendas = cursor.fetchall()
        conn.close()
        return vendas

    @staticmethod
    def total_vendas():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM vendas")
        total = cursor.fetchone()[0]
        conn.close()
        return total

    @staticmethod
    def buscar_por_semana():
        conn = get_db_connection()
        cursor = conn.cursor()
        data_inicio = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM vendas WHERE data >= ?", (data_inicio,))
        total = cursor.fetchone()[0]
        conn.close()
        return total

# Classe para Estoque
class Estoque:
    @staticmethod
    def adicionar(item, quantidade, limite_minimo):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO estoque (item, quantidade, limite_minimo) VALUES (?, ?, ?)",
            (item, quantidade, limite_minimo)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def editar(estoque_id, item, quantidade, limite_minimo):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE estoque SET item = ?, quantidade = ?, limite_minimo = ? WHERE id = ?",
            (item, quantidade, limite_minimo, estoque_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(estoque_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM estoque WHERE id = ?", (estoque_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estoque")
        itens = cursor.fetchall()
        conn.close()
        return itens

    @staticmethod
    def total_itens():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantidade) FROM estoque")
        total = cursor.fetchone()[0] or 0
        conn.close()
        return total

    @staticmethod
    def verificar_estoque_baixo():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM estoque WHERE quantidade < limite_minimo")
        itens = cursor.fetchall()
        conn.close()
        return itens

# Classe para Orçamentos
class Orcamento:
    @staticmethod
    def adicionar(empresa_id, cliente_id, descricao, valor):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO orcamentos (empresa_id, cliente_id, descricao, valor) VALUES (?, ?, ?, ?)",
            (empresa_id, cliente_id, descricao, valor)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def editar(orcamento_id, empresa_id, cliente_id, descricao, valor):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE orcamentos SET empresa_id = ?, cliente_id = ?, descricao = ?, valor = ? WHERE id = ?",
            (empresa_id, cliente_id, descricao, valor, orcamento_id)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def excluir(orcamento_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orcamentos WHERE id = ?", (orcamento_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def aprovar(orcamento_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE orcamentos SET status = 'Aprovado' WHERE id = ?", (orcamento_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.*, c.nome AS cliente_nome 
            FROM orcamentos o 
            JOIN clientes c ON o.cliente_id = c.id
        ''')
        orcamentos = cursor.fetchall()
        conn.close()
        return orcamentos

    @staticmethod
    def buscar_por_id(orcamento_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.*, c.nome AS cliente_nome 
            FROM orcamentos o 
            JOIN clientes c ON o.cliente_id = c.id 
            WHERE o.id = ?
        ''', (orcamento_id,))
        orcamento = cursor.fetchone()
        conn.close()
        return orcamento

    @staticmethod
    def total_pendente():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM orcamentos WHERE status = 'Pendente'")
        total = cursor.fetchone()[0]
        conn.close()
        return total

# Classe para Financeiro
class Financeiro:
    @staticmethod
    def registrar_transacao(tipo, valor, descricao):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO financeiro (tipo, valor, descricao) VALUES (?, ?, ?)",
            (tipo, valor, descricao)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def buscar_todos():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM financeiro")
        transacoes = cursor.fetchall()
        conn.close()
        return transacoes

    @staticmethod
    def calcular_saldo():
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(CASE WHEN tipo = 'Entrada' THEN valor ELSE -valor END) FROM financeiro")
        saldo = cursor.fetchone()[0] or 0
        conn.close()
        return saldo

    @staticmethod
    def buscar_fluxo_semanal():
        conn = get_db_connection()
        cursor = conn.cursor()
        data_inicio = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Entrada' AND data >= ?", (data_inicio,))
        entradas = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(valor) FROM financeiro WHERE tipo = 'Saída' AND data >= ?", (data_inicio,))
        saidas = cursor.fetchone()[0] or 0
        conn.close()
        return entradas, saidas

# Inicializar o banco ao importar o módulo
init_db()

