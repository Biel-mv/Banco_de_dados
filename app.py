from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost", user="root", password="", database="trabalho_bd"
    )

@app.template_filter('br_nota')
def formata_nota(valor):
    if valor is None: return "0"
    valor_float = round(float(valor), 2)
    if valor_float.is_integer():
        texto = f"{int(valor_float)}"
    else:
        texto = f"{valor_float:.2f}".rstrip('0').rstrip('.')
    return texto.replace('.', ',')

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)              
    query_boletim = """
        SELECT 
            Entregas.id AS entrega_id,
            Alunos.nome AS aluno,
            Alunos.curso,
            Disciplinas.nome AS disciplina,
            Atividades.titulo AS atividade,
            Entregas.nota_obtida AS media_aluno
        FROM Entregas
        INNER JOIN Alunos ON Entregas.aluno_id = Alunos.id
        INNER JOIN Atividades ON Entregas.atividade_id = Atividades.id
        INNER JOIN Disciplinas ON Atividades.disciplina_id = Disciplinas.id
        ORDER BY Entregas.id DESC
    """
    cursor.execute(query_boletim)
    boletim = cursor.fetchall()
    query_desempenho = """
        SELECT 
            Atividades.titulo AS atividade,
            Disciplinas.nome AS disciplina,
            AVG(Entregas.nota_obtida) AS media_nota,
            Atividades.nota_maxima
        FROM Entregas
        INNER JOIN Atividades ON Entregas.atividade_id = Atividades.id
        INNER JOIN Disciplinas ON Atividades.disciplina_id = Disciplinas.id
        GROUP BY Atividades.id
    """
    cursor.execute(query_desempenho)
    desempenho = cursor.fetchall()
    query_risco = """
        SELECT 
            Alunos.nome AS aluno,
            Atividades.titulo AS atividade,
            Disciplinas.nome AS disciplina,
            Entregas.nota_obtida AS nota
        FROM Entregas
        INNER JOIN Alunos ON Entregas.aluno_id = Alunos.id
        INNER JOIN Atividades ON Entregas.atividade_id = Atividades.id
        INNER JOIN Disciplinas ON Atividades.disciplina_id = Disciplinas.id
        WHERE Entregas.nota_obtida < 6.0
        ORDER BY Entregas.nota_obtida ASC
    """
    cursor.execute(query_risco)
    risco = cursor.fetchall()
    query_inadimplentes = """
        SELECT id, nome, matricula 
        FROM Alunos 
        WHERE id NOT IN (SELECT DISTINCT aluno_id FROM Entregas)
    """
    cursor.execute(query_inadimplentes)
    inadimplentes = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('index.html', 
                           boletim=boletim, 
                           desempenho=desempenho, 
                           risco=risco, 
                           inadimplentes=inadimplentes)

@app.route('/alunos', methods=['GET', 'POST'])
def crud_alunos():
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cursor.execute("""
                INSERT INTO Alunos (matricula, nome, data_nascimento, curso, email) 
                VALUES (%s, %s, %s, %s, %s)
            """, (request.form['matricula'], request.form['nome'], request.form['data_nascimento'], request.form['curso'], request.form['email']))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao inserir: {err}")
        return redirect(url_for('crud_alunos'))
                                                                            
    search_query = request.args.get('search', '').strip()
    if search_query:
        sql = """
            SELECT id, matricula, nome, curso, email,
                   TIMESTAMPDIFF(YEAR, data_nascimento, CURDATE()) AS idade 
            FROM Alunos
            WHERE nome LIKE %s OR curso LIKE %s
            ORDER BY nome ASC
        """
        cursor.execute(sql, (f"%{search_query}%", f"%{search_query}%"))
    else:
        cursor.execute("""
            SELECT id, matricula, nome, curso, email,
                   TIMESTAMPDIFF(YEAR, data_nascimento, CURDATE()) AS idade 
            FROM Alunos
            ORDER BY nome ASC
        """)
        
    alunos = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('alunos.html', alunos=alunos, aluno_edicao=None, search_query=search_query)

@app.route('/alunos/editar/<int:id>', methods=['GET', 'POST'])
def editar_aluno(id):
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE Alunos 
                SET matricula = %s, nome = %s, data_nascimento = %s, curso = %s, email = %s 
                WHERE id = %s
            """, (request.form['matricula'], request.form['nome'], request.form['data_nascimento'], request.form['curso'], request.form['email'], id))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao atualizar: {err}")
        return redirect(url_for('crud_alunos'))
        
    cursor.execute("SELECT * FROM Alunos WHERE id = %s", (id,))
    aluno_edicao = cursor.fetchone()
    
    search_query = request.args.get('search', '').strip()
    if search_query:
        sql = """
            SELECT id, matricula, nome, curso, email,
                   TIMESTAMPDIFF(YEAR, data_nascimento, CURDATE()) AS idade 
            FROM Alunos
            WHERE nome LIKE %s OR curso LIKE %s
            ORDER BY nome ASC
        """
        cursor.execute(sql, (f"%{search_query}%", f"%{search_query}%"))
    else:
        cursor.execute("""
            SELECT id, matricula, nome, curso, email,
                   TIMESTAMPDIFF(YEAR, data_nascimento, CURDATE()) AS idade 
            FROM Alunos
            ORDER BY nome ASC
        """)
    
    alunos = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('alunos.html', alunos=alunos, aluno_edicao=aluno_edicao, search_query=search_query)

@app.route('/alunos/deletar/<int:id>')
def deletar_aluno(id):
    conn = get_db_connection(); cursor = conn.cursor()
    try: 
        cursor.execute("DELETE FROM Alunos WHERE id = %s", (id,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao deletar aluno (provavelmente possui vínculos): {err}")
    cursor.close(); conn.close()
    return redirect(url_for('crud_alunos'))

@app.route('/disciplinas', methods=['GET', 'POST'])
def crud_disciplinas():
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cursor.execute("""
                INSERT INTO Disciplinas (nome, carga_horaria, professor, sala, semestre) 
                VALUES (%s, %s, %s, %s, %s)
            """, (request.form['nome'], int(request.form['carga_horaria']), request.form['professor'], request.form['sala'], request.form['semestre']))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao inserir disciplina: {err}")
        return redirect(url_for('crud_disciplinas'))
        
    cursor.execute("SELECT * FROM Disciplinas ORDER BY nome")
    disciplinas = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('disciplinas.html', disciplinas=disciplinas, disciplina_edicao=None)

@app.route('/disciplinas/editar/<int:id>', methods=['GET', 'POST'])
def editar_disciplina(id):
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE Disciplinas 
                SET nome = %s, carga_horaria = %s, professor = %s, sala = %s, semestre = %s 
                WHERE id = %s
            """, (request.form['nome'], int(request.form['carga_horaria']), request.form['professor'], request.form['sala'], request.form['semestre'], id))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao atualizar disciplina: {err}")
        return redirect(url_for('crud_disciplinas'))
        
    cursor.execute("SELECT * FROM Disciplinas WHERE id = %s", (id,))
    disciplina_edicao = cursor.fetchone()
    cursor.execute("SELECT * FROM Disciplinas ORDER BY nome")
    disciplinas = cursor.fetchall()
    
    cursor.close(); conn.close()
    return render_template('disciplinas.html', disciplinas=disciplinas, disciplina_edicao=disciplina_edicao)

@app.route('/disciplinas/deletar/<int:id>')
def deletar_disciplina(id):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Disciplinas WHERE id = %s", (id,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao deletar disciplina: {err}")
    cursor.close(); conn.close()
    return redirect(url_for('crud_disciplinas'))

@app.route('/matriculas', methods=['GET', 'POST'])
def crud_matriculas():
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cursor.execute("""
                INSERT INTO Matriculas_Disciplinas (aluno_id, disciplina_id) 
                VALUES (%s, %s)
            """, (request.form['aluno_id'], request.form['disciplina_id']))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao vincular matrícula: {err}")
        return redirect(url_for('crud_matriculas'))
        
    cursor.execute("SELECT id, nome FROM Alunos ORDER BY nome")
    alunos = cursor.fetchall()
    cursor.execute("SELECT id, nome FROM Disciplinas ORDER BY nome")
    disciplinas = cursor.fetchall()
    
    cursor.execute("""
        SELECT Matriculas_Disciplinas.id, Alunos.nome AS aluno, Disciplinas.nome AS disciplina 
        FROM Matriculas_Disciplinas
        INNER JOIN Alunos ON Matriculas_Disciplinas.aluno_id = Alunos.id
        INNER JOIN Disciplinas ON Matriculas_Disciplinas.disciplina_id = Disciplinas.id
        ORDER BY Alunos.nome
    """)
    matriculas = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('matriculas.html', alunos=alunos, disciplinas=disciplinas, matriculas=matriculas, matricula_edicao=None)

@app.route('/matriculas/editar/<int:id>', methods=['GET', 'POST'])
def editar_matricula(id):
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            cursor.execute("""
                UPDATE Matriculas_Disciplinas 
                SET aluno_id = %s, disciplina_id = %s 
                WHERE id = %s
            """, (request.form['aluno_id'], request.form['disciplina_id'], id))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao atualizar matrícula: {err}")
        return redirect(url_for('crud_matriculas'))
        
    cursor.execute("SELECT * FROM Matriculas_Disciplinas WHERE id = %s", (id,))
    matricula_edicao = cursor.fetchone()
    
    cursor.execute("SELECT id, nome FROM Alunos ORDER BY nome")
    alunos = cursor.fetchall()
    cursor.execute("SELECT id, nome FROM Disciplinas ORDER BY nome")
    disciplinas = cursor.fetchall()
    
    cursor.execute("""
        SELECT Matriculas_Disciplinas.id, Alunos.nome AS aluno, Disciplinas.nome AS disciplina 
        FROM Matriculas_Disciplinas
        INNER JOIN Alunos ON Matriculas_Disciplinas.aluno_id = Alunos.id
        INNER JOIN Disciplinas ON Matriculas_Disciplinas.disciplina_id = Disciplinas.id
        ORDER BY Alunos.nome
    """)
    matriculas = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('matriculas.html', alunos=alunos, disciplinas=disciplinas, matriculas=matriculas, matricula_edicao=matricula_edicao)

@app.route('/matriculas/deletar/<int:id>')
def deletar_matricula(id):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Matriculas_Disciplinas WHERE id = %s", (id,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao deletar matrícula: {err}")
    cursor.close(); conn.close()
    return redirect(url_for('crud_matriculas')) # <-- CORRIGIDO AQUI

@app.route('/atividades', methods=['GET', 'POST'])
def crud_atividades():
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            nota_max = request.form['nota_maxima'].replace(',', '.')
            cursor.execute("""
                INSERT INTO Atividades (disciplina_id, titulo, tipo, data_entrega, nota_maxima) 
                VALUES (%s, %s, %s, %s, %s)
            """, (request.form['disciplina_id'], request.form['titulo'], request.form['tipo'], request.form['data_entrega'], float(nota_max)))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao inserir atividade: {err}")
        return redirect(url_for('crud_atividades'))
        
    cursor.execute("SELECT id, nome FROM Disciplinas ORDER BY nome")
    disciplinas = cursor.fetchall()
    
    search_query = request.args.get('search', '').strip()
    if search_query:
        sql = """
            SELECT Atividades.*, Disciplinas.nome AS disciplina 
            FROM Atividades 
            INNER JOIN Disciplinas ON Atividades.disciplina_id = Disciplinas.id 
            WHERE Atividades.titulo LIKE %s
            ORDER BY Atividades.id DESC
        """
        cursor.execute(sql, (f"%{search_query}%",))
    else:
        sql = """
            SELECT Atividades.*, Disciplinas.nome AS disciplina 
            FROM Atividades 
            INNER JOIN Disciplinas ON Atividades.disciplina_id = Disciplinas.id 
            ORDER BY Atividades.id DESC
        """
        cursor.execute(sql)
        
    atividades = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('atividades.html', disciplinas=disciplinas, atividades=atividades, atividade_edicao=None, search_query=search_query)

@app.route('/atividades/editar/<int:id>', methods=['GET', 'POST'])
def editar_atividade(id):
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            nota_max = request.form['nota_maxima'].replace(',', '.')
            cursor.execute("""
                UPDATE Atividades 
                SET disciplina_id = %s, titulo = %s, tipo = %s, data_entrega = %s, nota_maxima = %s 
                WHERE id = %s
            """, (request.form['disciplina_id'], request.form['titulo'], request.form['tipo'], request.form['data_entrega'], float(nota_max), id))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao atualizar atividade: {err}")
        return redirect(url_for('crud_atividades'))
        
    cursor.execute("SELECT * FROM Atividades WHERE id = %s", (id,))
    atividade_edicao = cursor.fetchone()
    
    cursor.execute("SELECT id, nome FROM Disciplinas ORDER BY nome")
    disciplinas = cursor.fetchall()
    
    # Preserva o comportamento da busca mesmo na tela de edição
    search_query = request.args.get('search', '').strip()
    if search_query:
        sql = """
            SELECT Atividades.*, Disciplinas.nome AS disciplina 
            FROM Atividades 
            INNER JOIN Disciplinas ON Atividades.disciplina_id = Disciplinas.id 
            WHERE Atividades.titulo LIKE %s
            ORDER BY Atividades.id DESC
        """
        cursor.execute(sql, (f"%{search_query}%",))
    else:
        sql = """
            SELECT Atividades.*, Disciplinas.nome AS disciplina 
            FROM Atividades 
            INNER JOIN Disciplinas ON Atividades.disciplina_id = Disciplinas.id 
            ORDER BY Atividades.id DESC
        """
        cursor.execute(sql)
        
    atividades = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('atividades.html', disciplinas=disciplinas, atividades=atividades, atividade_edicao=atividade_edicao, search_query=search_query)

@app.route('/atividades/deletar/<int:id>')
def deletar_atividade(id):
    conn = get_db_connection(); cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Atividades WHERE id = %s", (id,))
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Erro ao deletar atividade (provavelmente possui notas atreladas): {err}")
    cursor.close(); conn.close()
    return redirect(url_for('crud_atividades'))

@app.route('/notas', methods=['GET', 'POST'])
def lancar_notas():
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            nota_texto = request.form['nota_obtida'].replace(',', '.')
            cursor.execute("""
                INSERT INTO Entregas (aluno_id, atividade_id, nota_obtida, data_lancamento, observacoes) 
                VALUES (%s, %s, %s, %s, %s)
            """, (request.form['aluno_id'], request.form['atividade_id'], float(nota_texto), request.form['data_lancamento'], request.form['observacoes']))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao salvar nota: {err}")
        return redirect(url_for('lancar_notas'))
        
    cursor.execute("SELECT id, nome FROM Alunos ORDER BY nome")
    alunos = cursor.fetchall()
    cursor.execute("SELECT id, titulo FROM Atividades ORDER BY titulo")
    atividades = cursor.fetchall()
    cursor.execute("""
        SELECT Entregas.*, Alunos.nome AS aluno, Atividades.titulo AS atividade 
        FROM Entregas
        INNER JOIN Alunos ON Entregas.aluno_id = Alunos.id
        INNER JOIN Atividades ON Entregas.atividade_id = Atividades.id
        ORDER BY Entregas.id DESC
    """)
    entregas = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('notas.html', alunos=alunos, atividades=atividades, entregas=entregas, nota_edicao=None)

@app.route('/notas/editar/<int:id>', methods=['GET', 'POST'])
def editar_nota(id):
    conn = get_db_connection(); cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        try:
            nota_texto = request.form['nota_obtida'].replace(',', '.')
            cursor.execute("""
                UPDATE Entregas 
                SET aluno_id = %s, atividade_id = %s, nota_obtida = %s, data_lancamento = %s, observacoes = %s 
                WHERE id = %s
            """, (request.form['aluno_id'], request.form['atividade_id'], float(nota_texto), request.form['data_lancamento'], request.form['observacoes'], id))
            conn.commit()
        except mysql.connector.Error as err:
            print(f"Erro ao editar nota: {err}")
        return redirect(url_for('lancar_notas'))
        
    cursor.execute("SELECT * FROM Entregas WHERE id = %s", (id,))
    nota_edicao = cursor.fetchone()
    
    cursor.execute("SELECT id, nome FROM Alunos ORDER BY nome")
    alunos = cursor.fetchall()
    cursor.execute("SELECT id, titulo FROM Atividades ORDER BY titulo")
    atividades = cursor.fetchall()
    
    cursor.execute("""
        SELECT Entregas.*, Alunos.nome AS aluno, Atividades.titulo AS atividade 
        FROM Entregas
        INNER JOIN Alunos ON Entregas.aluno_id = Alunos.id
        INNER JOIN Atividades ON Entregas.atividade_id = Atividades.id
        ORDER BY Entregas.id DESC
    """)
    entregas = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template('notas.html', alunos=alunos, atividades=atividades, entregas=entregas, nota_edicao=nota_edicao)

@app.route('/notas/excluir/<int:id>')
def deletar_nota(id):
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("DELETE FROM Entregas WHERE id = %s", (id,))
    conn.commit()
    cursor.close(); conn.close()
    return redirect(url_for('lancar_notas'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')