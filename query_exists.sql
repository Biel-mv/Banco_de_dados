USE trabalho_bd;

SELECT d.id, d.nome, d.professor, d.semestre
FROM Disciplinas d
WHERE EXISTS (
    SELECT 1 
    FROM Atividades a 
    WHERE a.disciplina_id = d.id
);