import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from Bull.models import Grade, Student, Sequence, Term, Classroom

@pytest.mark.django_db
def test_note_validation():
    student = Student.objects.create(matricule='S1', user=get_user_model().objects.create(username='eleve1'))
    sequence = Sequence.objects.create(name='S1', order=1, weight=1, term=Term.objects.create(name='T1', order=1, weight=1, school_year_id=1))
    # Note valide
    grade = Grade(student=student, sequence=sequence, value=15, coefficient=2)
    grade.full_clean()  # Ne doit pas lever d'exception
    # Note invalide (>20)
    grade.value = 21
    with pytest.raises(Exception):
        grade.full_clean()
    # Coefficient négatif
    grade.value = 10
    grade.coefficient = -1
    with pytest.raises(Exception):
        grade.full_clean()

@pytest.mark.django_db
def test_permissions_teacher_only():
    client = APIClient()
    teacher = get_user_model().objects.create_user(username='teacher1', password='pass', role='teacher')
    parent = get_user_model().objects.create_user(username='parent1', password='pass', role='parent')
    student = Student.objects.create(matricule='S2', user=get_user_model().objects.create(username='eleve2'))
    sequence = Sequence.objects.create(name='S2', order=2, weight=1, term=Term.objects.create(name='T2', order=2, weight=1, school_year_id=1))
    client.force_authenticate(user=teacher)
    response = client.post('/api/grades/', {'student': student.id, 'sequence': sequence.id, 'value': 12, 'coefficient': 2})
    assert response.status_code in [201, 200]
    client.force_authenticate(user=parent)
    response = client.post('/api/grades/', {'student': student.id, 'sequence': sequence.id, 'value': 12, 'coefficient': 2})
    assert response.status_code == 403

@pytest.mark.django_db
def test_calcul_moyenne_rang():
    # Crée 3 élèves et notes
    classroom = Classroom.objects.create(name='Classe1')
    students = [Student.objects.create(matricule=f'S{i}', user=get_user_model().objects.create(username=f'e{i}')) for i in range(3)]
    for s in students:
        classroom.students.add(s)
    sequence = Sequence.objects.create(name='S3', order=3, weight=1, term=Term.objects.create(name='T3', order=3, weight=1, school_year_id=1))
    Grade.objects.create(student=students[0], sequence=sequence, value=10, coefficient=2)
    Grade.objects.create(student=students[1], sequence=sequence, value=15, coefficient=2)
    Grade.objects.create(student=students[2], sequence=sequence, value=20, coefficient=2)
    # Test calcul moyenne
    avg = Grade.calculate_student_average(students[0], sequence)
    assert avg == 10
    # Test rangs
    ranks = Grade.get_class_ranks(classroom, sequence)
    assert ranks[0]['rank'] == 3  # Le plus faible
    assert ranks[-1]['rank'] == 1  # Le meilleur
