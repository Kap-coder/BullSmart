from django.core.management.base import BaseCommand
from Bull.models import Student, ClassSubject, StudentSubject, Sequence, Grade
from django.contrib.auth import get_user_model

User = get_user_model()
system_user = User.objects.filter(role='admin').first()

class Command(BaseCommand):
    help = "Lie tous les élèves existants aux matières de leur classe et initialise les notes (Grade) pour chaque séquence."

    def handle(self, *args, **options):
        ss_count = 0
        grade_count = 0
        # Supprimer tous les liens et notes existants
        StudentSubject.objects.all().delete()
        Grade.objects.all().delete()
        for student in Student.objects.all():
            if student.classroom:
                class_subjects = ClassSubject.objects.filter(classroom=student.classroom)
                for cs in class_subjects:
                    obj, created = StudentSubject.objects.get_or_create(student=student, subject=cs.subject, defaults={'is_optional': False})
                    if created:
                        ss_count += 1
                    for seq in Sequence.objects.all():
                        gobj, gcreated = Grade.objects.get_or_create(
                            student=student,
                            class_subject=cs,
                            sequence=seq,
                            defaults={
                                'value': 0,
                                'coefficient': cs.coefficient,
                                'status': 'draft',
                                'created_by': system_user,
                                'updated_by': system_user
                            }
                        )
                        if gcreated:
                            grade_count += 1
        self.stdout.write(self.style.SUCCESS(f"{ss_count} liens élève-matière créés."))
        self.stdout.write(self.style.SUCCESS(f"{grade_count} notes (Grade) initialisées."))