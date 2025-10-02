import random
from django.core.management.base import BaseCommand
from Bull.models import SchoolYear, Term, Sequence, Classroom, Subject, Teacher, Student, ClassSubject, StudentSubject, Grade, User
from django.utils import timezone

class Command(BaseCommand):
    help = "Remplit la base avec des données de test pour l'application SmartBull."

    def handle(self, *args, **options):
        # Année scolaire
        from datetime import date
        sy, _ = SchoolYear.objects.get_or_create(
            name="2024-2025",
            is_active=True,
            defaults={
                "start_date": date(2024, 9, 1),
                "end_date": date(2025, 6, 30)
            }
        )
        # Si déjà existant, on met à jour les dates si besoin
        if not sy.start_date:
            sy.start_date = date(2024, 9, 1)
        if not sy.end_date:
            sy.end_date = date(2025, 6, 30)
        sy.save()
        # Trimestres
        terms = []
        for i in range(1, 4):
            t, _ = Term.objects.get_or_create(name=f"Trimestre {i}", order=i, school_year=sy)
            terms.append(t)
        # Séquences
        seqs = []
        for i, t in enumerate(terms, 1):
            for j in range(1, 3):
                active = (i == 1 and j == 1)  # S1 du T1 active
                s, _ = Sequence.objects.get_or_create(name=f"S{j + (i-1)*2}", order=j, term=t, weight=1, active=active)
                seqs.append(s)
        # Classes
        classes = []
        for cname in ["6ème A", "5ème B"]:
            c, _ = Classroom.objects.get_or_create(name=cname, level=cname.split()[0], series="Général")
            classes.append(c)
        # Matières
        subjects = []
        for sname in ["Maths", "Français"]:
            s, _ = Subject.objects.get_or_create(name=sname, code=sname[:3].upper(), category="Tronc commun")
            subjects.append(s)
        # Enseignants
        teachers = []
        for i, tname in enumerate(["Alice Prof", "Bob Prof"]):
            user, _ = User.objects.get_or_create(username=f"prof{i+1}", defaults={"role": "teacher", "first_name": tname.split()[0], "last_name": tname.split()[1]})
            t, _ = Teacher.objects.get_or_create(user=user)
            teachers.append(t)
        # Associe matières/classes/enseignants
        for c in classes:
            for s, t in zip(subjects, teachers):
                cs, _ = ClassSubject.objects.get_or_create(classroom=c, subject=s, teacher=t, coefficient=2)
        # Élèves
        for c in classes:
            for i in range(1, 11):
                user, _ = User.objects.get_or_create(username=f"eleve_{c.name}_{i}", defaults={"role": "student", "first_name": f"Prenom{i}", "last_name": f"Nom{i}"})
                s, _ = Student.objects.get_or_create(matricule=f"{c.name[:2]}{i:02d}", first_name=f"Prenom{i}", last_name=f"Nom{i}", gender="M" if i%2==0 else "F", birth_date=timezone.now().date(), birth_place="Ville", classroom=c)
        # Liens élèves/matières et notes
        for c in classes:
            for s in subjects:
                cs = ClassSubject.objects.get(classroom=c, subject=s)
                for student in c.students.all():
                    ss, _ = StudentSubject.objects.get_or_create(student=student, subject=s)
                    for seq in seqs:
                        val = round(random.uniform(8, 18), 2)
                        status = "validated" if val > 10 else "draft"
                        Grade.objects.get_or_create(student=student, class_subject=cs, term=seq.term, sequence=seq, value=val, status=status, created_by=cs.teacher.user, updated_by=cs.teacher.user)
        self.stdout.write(self.style.SUCCESS("Base de test remplie avec succès !"))
