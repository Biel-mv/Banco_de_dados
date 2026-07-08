USE trabalho_bd;

SELECT id, nome, matricula 
FROM Alunos 
WHERE NOT id = ANY (
    SELECT DISTINCT aluno_id 
    FROM Entregas
);