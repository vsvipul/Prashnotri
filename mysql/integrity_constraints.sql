USE djangoproject;
ALTER TABLE classroom_user
ADD CONSTRAINT teacher_student
CHECK ((is_student XOR is_teacher)==1);

