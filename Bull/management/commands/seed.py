from django.core.management.base import BaseCommand
from Bull.models import User, Student, Teacher, Classroom, Subject, Grade, SchoolYear, Term, Sequence
from faker import Faker
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Remplit la base avec des données fictives'

    def handle(self, *args, **kwargs):
        fake = Faker('fr_FR')

        # Crée une année scolaire active
        sy = SchoolYear.objects.create(
            name='2024-2025',
            start_date='2024-09-01',
            end_date='2025-06-30',
            is_active=True
        )

        # Crée 3 trimestres et 2 séquences par trimestre
        terms = []
        for i in range(1, 4):
            term = Term.objects.create(
                school_year=sy,
                name=f'T{i}',
                order=i,
                weight=1
            )
            terms.append(term)
            for j in range(1, 3):
                Sequence.objects.create(
                    term=term,
                    name=f'S{j}',
                    order=j,
                    weight=1
                )

        # Crée 5 classes
        classrooms = []
        for i in range(1, 6):
            c = Classroom.objects.create(
                name=f'Classe {i}',
                level=f'Niveau {i}',
                series='A'
            )
            classrooms.append(c)

        # Crée 10 enseignants
        for i in range(10):
            username = f'teacher{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.email(),
                    role='teacher'
                )
                Teacher.objects.create(user=user, phone=fake.phone_number())

        # Crée 50 élèves répartis dans les classes
        for i in range(50):
            username = f'student{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.email(),
                    role='student'
                )
                Student.objects.create(
                    matricule=f'MAT{i}',
                    first_name=user.first_name,
                    last_name=user.last_name,
                    gender=random.choice(['M', 'F']),
                    birth_date=fake.date_of_birth(minimum_age=10, maximum_age=18),
                    birth_place=fake.city(),
                    classroom=random.choice(classrooms)
                )

        # Crée 8 matières
        subjects = []
        for i in range(1, 9):
            code = f'SUB{i}'
            if not Subject.objects.filter(code=code).exists():
                subjects.append(Subject.objects.create(code=code, name=f'Matière {i}', category='core'))
            else:
                subjects.append(Subject.objects.get(code=code))

        # Crée les ClassSubject pour chaque classe et matière
        class_subjects = []
        for classroom in classrooms:
            for subject in subjects:
                cs = classroom.class_subjects.filter(subject=subject).first()
                if not cs:
                    cs = classroom.class_subjects.create(subject=subject, coefficient=random.randint(1, 3))
                class_subjects.append(cs)

        # Crée des notes fictives pour chaque élève, matière, séquence
        for student in Student.objects.all():
            for class_subject in class_subjects:
                if class_subject.classroom == student.classroom:
                    for term in terms:
                        for seq in term.sequences.all():
                            Grade.objects.create(
                                student=student,
                                class_subject=class_subject,
                                sequence=seq,
                                value=random.uniform(5, 20),
                                status='validated'
                            )

        self.stdout.write(self.style.SUCCESS('Base de données remplie avec succès !'))