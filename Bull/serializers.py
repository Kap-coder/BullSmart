GitHub: Sign out
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    SchoolYear, Term, Sequence, Classroom, Teacher, Student,
    Subject, ClassSubject, Grade, Discipline, MentionRule,
    Settings, Bulletin, ArchivedGrade, ArchivedBulletin
)

User = get_user_model()

# ---------------------------
# User Serializer
# ---------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role']
        extra_kwargs = {
            'username': {'label': 'Nom d’utilisateur'},
            'first_name': {'label': 'Prénom'},
            'last_name': {'label': 'Nom'},
            'email': {'label': 'Email'},
            'role': {'label': 'Rôle'}
        }


# ---------------------------
# SchoolYear / Term / Sequence
# ---------------------------
class SequenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sequence
        fields = ['id', 'name', 'order', 'weight', 'term']


class TermSerializer(serializers.ModelSerializer):
    sequences = SequenceSerializer(many=True, read_only=True)

    class Meta:
        model = Term
        fields = ['id', 'name', 'order', 'weight', 'school_year', 'sequences']


class SchoolYearSerializer(serializers.ModelSerializer):
    terms = TermSerializer(many=True, read_only=True)

    class Meta:
        model = SchoolYear
        fields = ['id', 'name', 'start_date', 'end_date', 'is_active', 'terms']


# ---------------------------
# Classroom / Teacher / Student
# ---------------------------
class TeacherSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), label='Utilisateur')
    phone = serializers.CharField(label='Téléphone')
    is_active = serializers.BooleanField(label='Actif')

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'phone', 'is_active']


class ClassroomSerializer(serializers.ModelSerializer):
    head_teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all(), label='Professeur principal')
    name = serializers.CharField(label='Nom de la classe')
    level = serializers.CharField(label='Niveau')
    series = serializers.CharField(label='Série')

    class Meta:
        model = Classroom
        fields = ['id', 'name', 'level', 'series', 'head_teacher']


class StudentSerializer(serializers.ModelSerializer):
    classroom = serializers.PrimaryKeyRelatedField(queryset=Classroom.objects.all(), label='Classe')
    matricule = serializers.CharField(label='Matricule')
    first_name = serializers.CharField(label='Prénom')
    last_name = serializers.CharField(label='Nom')
    gender = serializers.CharField(label='Sexe')
    birth_date = serializers.DateField(label='Date de naissance')
    birth_place = serializers.CharField(label='Lieu de naissance')
    photo = serializers.ImageField(label='Photo', required=False)
    repeater = serializers.BooleanField(label='Redoublant', required=False)

    class Meta:
        model = Student
        fields = [
            'id', 'matricule', 'first_name', 'last_name', 'gender',
            'birth_date', 'birth_place', 'photo', 'classroom', 'repeater'
        ]


# ---------------------------
# Subject / ClassSubject
# ---------------------------
class SubjectSerializer(serializers.ModelSerializer):
    code = serializers.CharField(label='Code')
    name = serializers.CharField(label='Nom de la matière')
    category = serializers.CharField(label='Catégorie')

    class Meta:
        model = Subject
        fields = ['id', 'code', 'name', 'category']


class ClassSubjectSerializer(serializers.ModelSerializer):
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), label='Matière')
    teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all(), label='Enseignant')
    classroom = serializers.PrimaryKeyRelatedField(queryset=Classroom.objects.all(), label='Classe')
    coefficient = serializers.FloatField(label='Coefficient')

    class Meta:
        model = ClassSubject
        fields = ['id', 'classroom', 'subject', 'coefficient', 'teacher']


# ---------------------------
# Grade Serializer
# ---------------------------
class GradeSerializer(serializers.ModelSerializer):
    def validate_value(self, value):
        if value < 0 or value > 20:
            raise serializers.ValidationError("La note doit être comprise entre 0 et 20.")
        return value

    def validate_coefficient(self, coefficient):
        if coefficient < 0:
            raise serializers.ValidationError("Le coefficient doit être positif.")
        return coefficient

    class_subject = ClassSubjectSerializer(read_only=True)
    student = StudentSerializer(read_only=True)
    sequence = SequenceSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    updated_by = UserSerializer(read_only=True)

    class Meta:
        model = Grade
        fields = [
            'id', 'student', 'class_subject', 'sequence',
            'value', 'comment', 'status', 'created_by', 'updated_by',
            'created_at', 'updated_at'
        ]


# ---------------------------
# Discipline
# ---------------------------
class DisciplineSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    term = TermSerializer(read_only=True)

    class Meta:
        model = Discipline
        fields = ['id', 'student', 'term', 'absences', 'lates', 'sanctions_text']


# ---------------------------
# MentionRule
# ---------------------------
class MentionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = MentionRule
        fields = ['id', 'school_year', 'label', 'min_avg', 'max_avg']


# ---------------------------
# Settings
# ---------------------------
class SettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Settings
        fields = ['id', 'school_year', 'scale_max', 'rounding', 'min_pass_avg', 'localization', 'enable_ai']


# ---------------------------
# Bulletin Serializer avec IA
# ---------------------------
class BulletinSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    term = TermSerializer(read_only=True)
    mention = serializers.SerializerMethodField()
    appreciation = serializers.SerializerMethodField()

    class Meta:
        model = Bulletin
        fields = [
            'id', 'student', 'term', 'pdf_path', 'generated_at',
            'checksum', 'verified_url', 'mention', 'appreciation'
        ]

    def get_mention(self, obj):
        return obj.assign_mention()

    def get_appreciation(self, obj):
        return obj.generate_appreciation()


# ---------------------------
# Archivage
# ---------------------------
class ArchivedGradeSerializer(serializers.ModelSerializer):
    grade = GradeSerializer(read_only=True)
    school_year = SchoolYearSerializer(read_only=True)

    class Meta:
        model = ArchivedGrade
        fields = ['id', 'grade', 'school_year', 'archived_at']


class ArchivedBulletinSerializer(serializers.ModelSerializer):
    bulletin = BulletinSerializer(read_only=True)

    class Meta:
        model = ArchivedBulletin
        fields = ['id', 'bulletin', 'archived_at']
