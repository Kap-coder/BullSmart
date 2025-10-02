from django.core.management.base import BaseCommand
from Bull.models import Classroom, ClassSubject, Student, StudentSubject

class Command(BaseCommand):
    help = "Synchronise les élèves avec toutes les matières de leur classe (ClassSubject) et crée les liens StudentSubject."

    def handle(self, *args, **options):
        count = 0
        for classroom in Classroom.objects.all():
            students = classroom.students.all()
            class_subjects = ClassSubject.objects.filter(classroom=classroom)
            for student in students:
                for cs in class_subjects:
                    obj, created = StudentSubject.objects.get_or_create(
                        student=student,
                        subject=cs.subject,
                        defaults={'is_optional': False}
                    )
                    if created:
                        count += 1
        self.stdout.write(self.style.SUCCESS(f"Synchronisation terminée : {count} liens créés."))
