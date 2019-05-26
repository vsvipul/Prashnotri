use djangoproject;

CREATE VIEW get_avg AS 
    SELECT AVG(score) AS average,quiz_id 
    FROM classroom_takenquiz
    GROUP BY quiz_id;