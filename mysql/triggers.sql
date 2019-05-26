use djangoproject;

DROP TRIGGER IF EXISTS update_avg;

DELIMITER $$
CREATE TRIGGER update_avg
    AFTER INSERT ON classroom_takenquiz
    FOR EACH ROW 
BEGIN
    UPDATE classroom_quiz
    SET averagescore=(
        SELECT average 
        FROM get_avg 
        WHERE quiz_id=NEW.quiz_id)
    WHERE id=NEW.quiz_id;
END$$
DELIMITER ;