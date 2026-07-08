CREATE DATABASE IF NOT EXISTS trabalho_bd;
USE trabalho_bd;

-- 1. ON DELETE CASCADE

CREATE TABLE Alunos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    matricula VARCHAR(11) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    data_nascimento DATE NOT NULL,
    curso VARCHAR(100) NOT NULL,
    email VARCHAR(100) NULL
);

CREATE TABLE Disciplinas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    carga_horaria INT NOT NULL,
    professor VARCHAR(100) NOT NULL,
    sala VARCHAR(50) NOT NULL,
    semestre VARCHAR(20) NOT NULL
);

CREATE TABLE Matriculas_Disciplinas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id INT NOT NULL,
    disciplina_id INT NOT NULL,
    FOREIGN KEY (aluno_id) REFERENCES Alunos(id) ON DELETE CASCADE,
    FOREIGN KEY (disciplina_id) REFERENCES Disciplinas(id) ON DELETE CASCADE,
    UNIQUE KEY uq_aluno_disciplina (aluno_id, disciplina_id)
);

CREATE TABLE Atividades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    disciplina_id INT NOT NULL,
    titulo VARCHAR(100) NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    data_entrega DATE NOT NULL,
    nota_maxima DECIMAL(4,2) NOT NULL,
    FOREIGN KEY (disciplina_id) REFERENCES Disciplinas(id) ON DELETE CASCADE
);

CREATE TABLE Entregas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    aluno_id INT NOT NULL,
    atividade_id INT NOT NULL,
    nota_obtida DECIMAL(4,2) NOT NULL,
    data_lancamento DATE NOT NULL,
    observacoes VARCHAR(255) NULL,
    FOREIGN KEY (aluno_id) REFERENCES Alunos(id) ON DELETE CASCADE,
    FOREIGN KEY (atividade_id) REFERENCES Atividades(id) ON DELETE CASCADE,
    CONSTRAINT chk_nota_escopo CHECK (nota_obtida >= 0.0 AND nota_obtida <= 10.0)
);

DELIMITER $$

-- Validar nota máxima e matrícula antes de INSERIR uma nota
CREATE TRIGGER tg_validar_nota_insercao
BEFORE INSERT ON Entregas
FOR EACH ROW
BEGIN
    DECLARE v_nota_max DECIMAL(4,2);
    DECLARE v_disc_id INT;
    DECLARE v_matriculado INT;

    -- Procurar a nota máxima e a disciplina da atividade
    SELECT nota_maxima, disciplina_id INTO v_nota_max, v_disc_id 
    FROM Atividades 
    WHERE id = NEW.atividade_id;

    -- Verificar se o aluno está devidamente matriculado nessa disciplina
    SELECT COUNT(*) INTO v_matriculado 
    FROM Matriculas_Disciplinas 
    WHERE aluno_id = NEW.aluno_id AND disciplina_id = v_disc_id;

    -- Nota obtida maior que a nota limite da atividade
    IF NEW.nota_obtida > v_nota_max THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro: A nota obtida não pode ser maior do que a nota máxima da atividade.';
    END IF;

    -- Aluno não está matriculado na disciplina
    IF v_matriculado = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro: O aluno selecionado não está matriculado na disciplina desta atividade.';
    END IF;
END$$

-- Validar nota máxima e matrícula antes de ATUALIZAR uma nota existente
CREATE TRIGGER tg_validar_nota_atualizacao
BEFORE UPDATE ON Entregas
FOR EACH ROW
BEGIN
    DECLARE v_nota_max DECIMAL(4,2);
    DECLARE v_disc_id INT;
    DECLARE v_matriculado INT;

    SELECT nota_maxima, disciplina_id INTO v_nota_max, v_disc_id 
    FROM Atividades 
    WHERE id = NEW.atividade_id;

    SELECT COUNT(*) INTO v_matriculado 
    FROM Matriculas_Disciplinas 
    WHERE aluno_id = NEW.aluno_id AND disciplina_id = v_disc_id;

    IF NEW.nota_obtida > v_nota_max THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro: A nota obtida não pode ser maior do que a nota máxima da atividade.';
    END IF;

    IF v_matriculado = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Erro: O aluno selecionado não está matriculado na disciplina desta atividade.';
    END IF;
END$$

DELIMITER ;