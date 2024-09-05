from flask import Flask, g, render_template, request, redirect, url_for, session
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = '12345678'  
DATABASE = 'neabi.db'

# Função para conectar ao banco de dados
def conexaodb():
    db = getattr(g, 'conexao_db', None)
    if db is None:
        db = g.conexao_db = sqlite3.connect(DATABASE)
    return db

# Função para fechar a conexão com o banco de dados após a requisição
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'conexao_db', None)
    if db is not None:
        db.close()

# Rota para a página inicial
@app.route('/')
def index():
    return "Página inicial"

# Rota para exibir o formulário de cadastro de usuário
@app.route('/formcadastroU')
def form_cadastro():
    return render_template('formcadastroU.html')

# Rota para processar o cadastro de usuário
@app.route('/cadastrar_usuario', methods=['POST'])
def cadastrar_usuario():
    nome = request.form['nome']
    matricula = request.form['matricula']
    telefone = request.form['telefone']
    email = request.form['email']
    senha = request.form['senha']
    tipo_usuario_id = request.form['tipo_usuario_id']

    # criptografia da senha usando SHA-256
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()

    db = conexaodb()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO usuarios (nome, matricula, telefone, senha_hash, tipo_usuario_id) 
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, matricula, telefone, senha_hash, tipo_usuario_id))
        db.commit()
        return 'Usuário cadastrado com sucesso!'
    except sqlite3.IntegrityError as e:
        return f'Erro: {e}'
    finally:
        db.close()

# Rota para exibir o formulário de login
@app.route('/loginU')
def login_form():
    return render_template('loginU.html')

# Rota para processar o login do usuário
@app.route('/login_usuario', methods=['POST'])
def login_usuario():
    matricula = request.form['matricula']
    senha = request.form['senha']

    senha_hash = hashlib.sha256(senha.encode()).hexdigest()

    db = conexaodb()
    cursor = db.cursor()
    
    cursor.execute('''
        SELECT * FROM usuarios WHERE matricula = ? AND senha_hash = ?
    ''', (matricula, senha_hash))
    
    user = cursor.fetchone()
    db.close()
    
    if user:
        # Usuário autenticado com sucesso
        session['user_id'] = user[0]  # Salva o ID do usuário na sessão
        return 'Login bem-sucedido!'
    else:
        return 'Matrícula ou senha inválidos.'
    

@app.route('/denuncia')
def denuncia_form():
    return render_template('denuncia.html')

@app.route('/registrar_denuncia', methods=['POST'])
def registrar_denuncia():
    usuario_id = request.form['usuario_id']
    tipo_denuncia_id = request.form['tipo_denuncia_id']
    status_denuncia_id = request.form['status_denuncia_id']
    denuncia = request.form['denuncia']
    data_denuncia = request.form['data_denuncia']

    db = conexaodb()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO denuncias (usuario_id, tipo_denuncia_id, status_denuncia_id, denuncia, data_denuncia)
            VALUES (?, ?, ?, ?, ?)
        ''', (usuario_id, tipo_denuncia_id, status_denuncia_id, denuncia, data_denuncia))
        db.commit()
        return 'Denúncia registrada com sucesso!'
    except sqlite3.IntegrityError as e:
        return f'Erro: {e}'
    finally:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
