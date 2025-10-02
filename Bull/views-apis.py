from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model, authenticate, login, logout
from rest_framework.permissions import AllowAny, BasePermission
from .models import (
    User, SchoolYear, Term, Sequence, Classroom, Teacher, Student,
    Subject, ClassSubject, Grade, Discipline, MentionRule,
    Settings, Bulletin, ArchivedGrade, ArchivedBulletin
)
from .serializers import (
    UserSerializer, SchoolYearSerializer, TermSerializer, SequenceSerializer,
    ClassroomSerializer, TeacherSerializer, StudentSerializer, SubjectSerializer,
    ClassSubjectSerializer, GradeSerializer, DisciplineSerializer, MentionRuleSerializer,
    SettingsSerializer, BulletinSerializer, ArchivedGradeSerializer, ArchivedBulletinSerializer
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.http import FileResponse
import os



User = get_user_model()

# ---------------------------
# Permission personnalisée
# ---------------------------
class IsTeacherOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return hasattr(user, 'role') and user.role == 'teacher'


# ---------------------------
# Utilisateur
# ---------------------------
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# ---------------------------
# Register
# ---------------------------
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user).data,
            "message": "Inscription réussie."
        }, status=status.HTTP_201_CREATED)


# ---------------------------
# SchoolYear / Term / Sequence
# ---------------------------
class SchoolYearViewSet(viewsets.ModelViewSet):
    queryset = SchoolYear.objects.all()
    serializer_class = SchoolYearSerializer


class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer


class SequenceViewSet(viewsets.ModelViewSet):
    queryset = Sequence.objects.all()
    serializer_class = SequenceSerializer


# ---------------------------
# Classroom / Teacher / Student
# ---------------------------
class ClassroomViewSet(viewsets.ModelViewSet):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer


# ---------------------------
# Subject / ClassSubject
# ---------------------------
class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class ClassSubjectViewSet(viewsets.ModelViewSet):
    queryset = ClassSubject.objects.all()
    serializer_class = ClassSubjectSerializer


# ---------------------------
# Grade / Notes
# ---------------------------
class GradeViewSet(viewsets.ModelViewSet):
    queryset = Grade.objects.all()
    serializer_class = GradeSerializer
    permission_classes = [IsTeacherOrReadOnly]

    @action(detail=False, methods=['post'])
    def calculate_sequence(self, request):
        student_id = request.data.get('student_id')
        sequence_id = request.data.get('sequence_id')
        student = get_object_or_404(Student, id=student_id)
        sequence = get_object_or_404(Sequence, id=sequence_id)
        avg = Grade.calculate_student_average(student, sequence)
        return Response({'average': avg})

    @action(detail=False, methods=['post'])
    def calculate_term(self, request):
        student_id = request.data.get('student_id')
        term_id = request.data.get('term_id')
        student = get_object_or_404(Student, id=student_id)
        term = get_object_or_404(Term, id=term_id)
        avg = Grade.calculate_term_average(student, term)
        return Response({'term_average': avg})

    @action(detail=False, methods=['post'])
    def validate_grade(self, request):
        grade_id = request.data.get('grade_id')
        grade = get_object_or_404(Grade, id=grade_id)
        grade.status = 'validated'
        grade.save()
        return Response({'status': 'validated'})


# ---------------------------
# Discipline
# ---------------------------
class DisciplineViewSet(viewsets.ModelViewSet):
    queryset = Discipline.objects.all()
    serializer_class = DisciplineSerializer


# ---------------------------
# MentionRule / Settings
# ---------------------------
class MentionRuleViewSet(viewsets.ModelViewSet):
    queryset = MentionRule.objects.all()
    serializer_class = MentionRuleSerializer


class SettingsViewSet(viewsets.ModelViewSet):
    queryset = Settings.objects.all()
    serializer_class = SettingsSerializer


# ---------------------------
# Bulletin
# ---------------------------
class BulletinViewSet(viewsets.ModelViewSet):
    queryset = Bulletin.objects.all()
    serializer_class = BulletinSerializer

    @action(detail=False, methods=['post'])
    def generate(self, request):
        classroom_id = request.data.get('classroom_id')
        term_id = request.data.get('term_id')
        classroom = get_object_or_404(Classroom, id=classroom_id)
        term = get_object_or_404(Term, id=term_id)
        bulletins = []

        for student in classroom.students.all():
            bulletin = Bulletin.objects.create(
                student=student,
                term=term,
                pdf_path=f'bulletins/{student.matricule}_{term.name}.pdf'
            )
            bulletins.append(bulletin)

        serializer = BulletinSerializer(bulletins, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def ranks(self, request):
        classroom_id = request.query_params.get('classroom_id')
        sequence_id = request.query_params.get('sequence_id')
        classroom = get_object_or_404(Classroom, id=classroom_id)
        sequence = get_object_or_404(Sequence, id=sequence_id)
        ranks = Grade.get_class_ranks(classroom, sequence)
        result = [{'student': r['student'].matricule, 'average': r['average'], 'rank': r['rank']} for r in ranks]
        return Response(result)

    @action(detail=True, methods=['get'])
    def export_pdf(self, request, pk=None):
        bulletin = self.get_object()
        pdf_path = bulletin.pdf_path
        if not pdf_path or not os.path.exists(pdf_path):
            return Response({'error': 'PDF non généré ou introuvable.'}, status=404)
        return FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')


# ---------------------------
# Archivage
# ---------------------------
class ArchivedGradeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArchivedGrade.objects.all()
    serializer_class = ArchivedGradeSerializer


class ArchivedBulletinViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArchivedBulletin.objects.all()
    serializer_class = ArchivedBulletinSerializer


# ---------------------------
# Analyse Élève
# ---------------------------
class StudentAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        student_id = request.data.get('student_id')
        notes = Grade.objects.filter(student_id=student_id)
        weak_subjects = []
        suggestions = []
        for note in notes:
            if note.value < 10:
                weak_subjects.append(note.subject.name)
                suggestions.append(f"Travailler la matière {note.subject.name}")
        avg = sum([n.value for n in notes]) / notes.count() if notes.count() > 0 else 0
        performance = "Faible" if avg < 10 else "Moyen" if avg < 15 else "Bon"
        return Response({
            "weak_subjects": weak_subjects,
            "average": avg,
            "performance": performance,
            "suggestions": suggestions
        })
