from django.core.management.base import BaseCommand
from Bull.models import Classroom, Subject, ClassSubject, Student, StudentSubject, Sequence, Grade
from django.contrib.auth import get_user_model

User = get_user_model()
system_user = User.objects.filter(role='admin').first()

class Command(BaseCommand):
    help = "Lie toutes les classes à toutes les matières ; crée aussi StudentSubject et Grade manquants."

    def handle(self, *args, **options):
        cs_created = 0
        ss_created = 0
        grades_created = 0

        subjects = Subject.objects.all()
        classrooms = Classroom.objects.all()
        sequences = Sequence.objects.select_related('term').all()

        for classroom in classrooms:
            for subject in subjects:
                cs, created = ClassSubject.objects.get_or_create(
                    classroom=classroom,
                    subject=subject,
                    defaults={'coefficient': 1.0, 'teacher': None}
                )
                if created:
                    cs_created += 1
                # for each student in classroom ensure StudentSubject and Grades
                students = Student.objects.filter(classroom=classroom)
                for student in students:
                    try:
                        ss, screated = StudentSubject.objects.get_or_create(
                            student=student,
                            subject=subject,
                            defaults={'is_optional': False}
                        )
                        if screated:
                            ss_created += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Erreur création StudentSubject pour student={student.id} subject={subject.id}: {e}"))
                        continue
                    # create grades for each sequence
                    for seq in sequences:
                        try:
                            g, gcreated = Grade.objects.get_or_create(
                                student=student,
                                class_subject=cs,
                                sequence=seq,
                                term=seq.term,
                                defaults={
                                    'value': 0.0,
                                    'status': 'draft',
                                        'created_by': system_user,
                                        'updated_by': system_user
                                }
                            )
                            if gcreated:
                                grades_created += 1
                        except Exception as e:
                            # skip problematic entries but print a warning
                            self.stdout.write(self.style.WARNING(f"Erreur création grade pour student={student.id} seq={seq.id}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"ClassSubject créés: {cs_created}"))
        self.stdout.write(self.style.SUCCESS(f"StudentSubject créés: {ss_created}"))
        self.stdout.write(self.style.SUCCESS(f"Grades créés: {grades_created}"))
