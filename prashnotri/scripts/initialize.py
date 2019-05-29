from classroom.models import Subject
def run():
    s = Subject(name="History",color="red")
    s.save()
    s = Subject(name="English",color="blue")
    s.save()
    s = Subject(name="Science",color="yellow")
    s.save()

