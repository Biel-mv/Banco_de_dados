USE trabalho_bd;

INSERT INTO Alunos (matricula, nome, data_nascimento, curso, email) VALUES
('20261000001', 'Carlos Silva', '2002-05-14', 'Engenharia de Software', 'carlos@email.com'),
('20261000002', 'Ana Maria Souza', '2001-08-22', 'Ciência da Computação', 'ana.maria@email.com'),
('20261000003', 'Bruno Santos Oliveira', '2003-01-30', 'Sistemas de Informação', 'bruno.s@email.com'),
('20261000004', 'Mariana Costa', '2000-11-05', 'Engenharia de Software', 'mariana@email.com'),
('20261000005', 'Pedro Henrique Ramos', '2002-07-19', 'Ciência da Computação', 'pedro.h@email.com'),
('20261000006', 'Julia Almeida', '2003-04-12', 'Sistemas de Informação', 'julia@email.com'),
('20261000007', 'Lucas Gabriel Ferreira', '2001-09-30', 'Engenharia de Software', 'lucas@email.com'),
('20262000001', 'Beatriz Rocha', '2002-12-01', 'Ciência da Computação', 'beatriz@email.com'),
('20262000002', 'Thiago Martins', '2000-06-18', 'Sistemas de Informação', 'thiago@email.com'),
('20262000003', 'Amanda Lima', '2003-11-25', 'Engenharia de Software', 'amanda@email.com'),
('20262000004', 'Rodrigo Alves', '2001-02-10', 'Ciência da Computação', 'rodrigo@email.com'),
('20262000005', 'Camila Ribeiro', '2002-08-05', 'Sistemas de Informação', 'camila@email.com');

INSERT INTO Disciplinas (nome, carga_horaria, professor, sala, semestre) VALUES
('Banco de Dados I', 80, 'Prof. Roberto', 'Sala 201', '2026.1'),
('Cálculo I', 80, 'Profª. Sandra', 'Sala 105', '2026.1'),
('Estrutura de Dados', 60, 'Prof. Maurício', 'Laboratório 3', '2026.1'),
('Programação Web', 60, 'Prof. Alex', 'Laboratório 1', '2026.1'),
('Engenharia de Requisitos', 40, 'Profª. Flávia', 'Sala 302', '2026.1');

INSERT INTO Matriculas_Disciplinas (aluno_id, disciplina_id) VALUES
(1, 1), (2, 1), (3, 3), (4, 4), (5, 2), (6, 4), (7, 1);

INSERT INTO Atividades (disciplina_id, titulo, tipo, data_entrega, nota_maxima) VALUES
(1, 'Prova Teórica AV1', 'Prova', '2026-04-10', 10.00),
(1, 'Projeto Prático CRUD', 'Trabalho', '2026-05-15', 10.00),
(3, 'Exercício de Árvores Binárias', 'Exercício', '2026-04-18', 5.00),
(4, 'Desenvolvimento Frontend', 'Trabalho', '2026-05-20', 10.00),
(2, 'Lista de Exercícios de Limites', 'Lista', '2026-03-25', 4.00);

INSERT INTO Entregas (aluno_id, atividade_id, nota_obtida, data_lancamento, observacoes) VALUES
(1, 1, 8.50, '2026-04-11', 'Excelente desempenho teórico.'),
(2, 1, 5.50, '2026-04-11', 'Abaixo da média.'),
(3, 3, 4.50, '2026-04-19', 'Entregou no prazo correto.'),
(4, 4, 9.00, '2026-05-21', 'Layout Bootstrap muito bem estruturado.'),
(5, 5, 2.00, '2026-03-26', 'Abaixo da média.'),
(6, 4, 5.80, '2026-05-21', 'Faltou entregar a documentação.'),
(7, 2, 4.00, '2026-05-16', 'Erros na estrutura de dados.');