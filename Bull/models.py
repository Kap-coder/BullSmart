# Signal pour lier automatiquement l'élève aux matières de sa classe
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone

# ---------------------------
# User personnalisé avec rôles
# ---------------------------
class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN = 'admin', _('Administrateur')
        TEACHER = 'teacher', _('Enseignant')
        SECRETARY = 'secretary', _('Secrétariat')
        PARENT = 'parent', _('Parent')
        STUDENT = 'student', _('Élève')

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.STUDENT
    )

    def is_admin(self):
        return self.role == self.Roles.ADMIN

    def is_teacher(self):
        return self.role == self.Roles.TEACHER


# ---------------------------
# Année scolaire, Trimestres, Séquences
# ---------------------------
class SchoolYear(models.Model):
    name = models.CharField(max_length=20)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Term(models.Model):
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='terms')
    name = models.CharField(max_length=20)  # ex: T1, T2, T3
    order = models.PositiveSmallIntegerField()
    weight = models.FloatField(default=1)

    def __str__(self):
        return f"{self.name} - {self.school_year.name}"


class Sequence(models.Model):
    term = models.ForeignKey(Term, on_delete=models.CASCADE, related_name='sequences')
    name = models.CharField(max_length=20)  # ex: S1, S2, S3
    order = models.PositiveSmallIntegerField()
    weight = models.FloatField(default=1)
    active = models.BooleanField(default=False, help_text="Séquence active pour la saisie des notes")

    def __str__(self):
        return f"{self.name} - {self.term.name}"




# ---------------------------
# Sanction
# ---------------------------
class Sanction(models.Model):
    texte = models.CharField(max_length=255)
    min_heures_absence = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.texte} (≥ {self.min_heures_absence}h)"
    
# ---------------------------
# Classes et élèves
# ---------------------------
class Classroom(models.Model):
    name = models.CharField(max_length=50)
    level = models.CharField(max_length=20)
    series = models.CharField(max_length=20, blank=True, null=True)
    head_teacher = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name='head_classes')

    def __str__(self):
        return self.name


class Student(models.Model):
    matricule = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')])
    birth_date = models.DateField()
    birth_place = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='students/', null=True, blank=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='students')
    repeater = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.matricule} - {self.first_name} {self.last_name}"



@receiver(pre_save, sender=Student)
def check_classroom_change(sender, instance, **kwargs):
    if instance.pk:
        old = Student.objects.get(pk=instance.pk)
        instance._old_classroom_id = old.classroom_id

@receiver(post_save, sender=Student)
def link_student_to_class_subjects(sender, instance, created, **kwargs):
    from Bull.models import ClassSubject, StudentSubject, Sequence, Grade
    from django.contrib.auth import get_user_model
    User = get_user_model()
    # pick a fallback admin user for system-created records
    system_user = User.objects.filter(role='admin').first()
    # Si nouvel élève, ou si la classe a changé
    classroom_changed = hasattr(instance, '_old_classroom_id') and instance._old_classroom_id != instance.classroom_id
    if created or classroom_changed:
        # Supprimer les anciens liens
        StudentSubject.objects.filter(student=instance).delete()
        # Ajouter les matières de la nouvelle classe
        if instance.classroom:
            class_subjects = ClassSubject.objects.filter(classroom=instance.classroom)
            for cs in class_subjects:
                StudentSubject.objects.get_or_create(student=instance, subject=cs.subject, defaults={'is_optional': False})
                # Créer les notes pour chaque séquence existante
                for seq in Sequence.objects.all():
                    Grade.objects.get_or_create(
                        student=instance,
                        class_subject=cs,
                        sequence=seq,
                        defaults={
                            'value': 0,
                            'status': 'draft',
                            'created_by': system_user,
                            'updated_by': system_user
                        }
                    )



# ---------------------------
# Modèle pour le canevas bulletin (entête et pied de page Word)
class BulletinTemplate(models.Model):
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='bulletin_templates')
    name = models.CharField(max_length=100, default='Canevas bulletin')
    header_docx = models.FileField(upload_to='bulletin_templates/headers/', blank=True, null=True)
    footer_docx = models.FileField(upload_to='bulletin_templates/footers/', blank=True, null=True)
    html_canvas = models.TextField(blank=True, null=True, help_text="Canevas HTML personnalisé (entête, pied, images, etc.)")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.school_year})"

# ---------------------------
# Enseignants et matières
# ---------------------------
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


class Subject(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    CATEGORY_CHOICES = [
        ('core', 'Tronc commun'),
        ('optional', 'Option'),
        ('extra', 'Complémentaire')
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='core')

    def __str__(self):
        return self.name



# ---------------------------
# Lien explicite Élève-Matière
# ---------------------------
class StudentSubject(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name='students')
    is_optional = models.BooleanField(default=False)

    class Meta:
        unique_together = ('student', 'subject')

    def __str__(self):
        return f"{self.student} - {self.subject} ({'Option' if self.is_optional else 'Obligatoire'})"



class ClassSubject(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='class_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    coefficient = models.FloatField(default=1)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = ('classroom', 'subject')

    def __str__(self):
        return f"{self.subject.name} - {self.classroom.name}"


# ---------------------------
# Notes et calculs
# ---------------------------
class Grade(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('validated', 'Validé'),
        ('locked', 'Verrouillé')
    ]
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades')
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE)
    term = models.ForeignKey('Term', on_delete=models.CASCADE, null=True, blank=True, related_name='grades')
    sequence = models.ForeignKey(Sequence, on_delete=models.CASCADE)
    value = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(20)])
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='grades_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='grades_updated')
    validated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='grades_validated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ---------------------------------
    # Méthodes de calcul
    # ---------------------------------
    @staticmethod
    def calculate_student_average(student, sequence):
        grades = Grade.objects.filter(student=student, sequence=sequence, status='validated')
        if not grades.exists():
            return None
        total_coef = sum(g.class_subject.coefficient for g in grades)
        total = sum(g.value * g.class_subject.coefficient for g in grades)
        return round(total / total_coef, 2)

    @staticmethod
    def calculate_term_average(student, term):
        sequences = term.sequences.all()
        weighted_total = 0
        total_weight = 0
        for seq in sequences:
            avg = Grade.calculate_student_average(student, seq)
            if avg is not None:
                weighted_total += avg * seq.weight
                total_weight += seq.weight
        if total_weight == 0:
            return None
        return round(weighted_total / total_weight, 2)

    @staticmethod
    def calculate_annual_average(student, school_year):
        terms = school_year.terms.all()
        weighted_total = 0
        total_weight = 0
        for term in terms:
            avg = Grade.calculate_term_average(student, term)
            if avg is not None:
                weighted_total += avg * term.weight
                total_weight += term.weight
        if total_weight == 0:
            return None
        return round(weighted_total / total_weight, 2)

    @staticmethod
    def get_class_ranks(classroom, sequence):
        students = classroom.students.all()
        averages = []
        for s in students:
            avg = Grade.calculate_student_average(s, sequence)
            if avg is not None:
                averages.append((s, avg))
        averages.sort(key=lambda x: x[1], reverse=True)
        ranks = []
        current_rank = 1
        prev_avg = None
        for i, (student, avg) in enumerate(averages):
            if prev_avg is not None and avg < prev_avg:
                current_rank = i + 1
            ranks.append({'student': student, 'average': avg, 'rank': current_rank})
            prev_avg = avg
        return ranks


# ---------------------------
# Bulletins et IA
# ---------------------------
class Bulletin(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name='bulletins')
    classroom = models.ForeignKey('Classroom', on_delete=models.CASCADE, related_name='bulletins', default=1)
    sequence = models.ForeignKey('Sequence', on_delete=models.CASCADE, related_name='bulletins', default=1)
    pdf_path = models.FileField(upload_to='bulletins/')
    generated_at = models.DateTimeField(auto_now_add=True)
    average = models.FloatField(null=True, blank=True)
    rank = models.PositiveIntegerField(null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    checksum = models.CharField(max_length=64, blank=True, null=True)
    verified_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Bulletin {self.student} - {self.classroom} - {self.sequence}"

    def assign_mention(self):
        avg = Grade.calculate_term_average(self.student, self.sequence.term)
        if avg is None:
            return None
        mention = MentionRule.objects.filter(
            school_year=self.sequence.term.school_year,
            min_avg__lte=avg,
            max_avg__gte=avg
        ).first()
        return mention.label if mention else None

    def generate_appreciation(self):
        avg = Grade.calculate_term_average(self.student, self.sequence.term)
        if avg is None:
            return "Pas de données disponibles"
        if avg >= 16:
            return "Excellent travail, continuez ainsi !"
        elif avg >= 14:
            return "Très bon travail, poursuivez vos efforts."
        elif avg >= 12:
            return "Bon travail, mais attention aux points faibles."
        elif avg >= 10:
            return "Travail suffisant, il faut progresser."
        else:
            return "Résultats insuffisants, nécessite un accompagnement."



# ---------------------------
# Discipline et mentions
# ---------------------------
class Discipline(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='disciplines')
    term = models.ForeignKey(Term, on_delete=models.CASCADE)
    sequence = models.ForeignKey('Sequence', on_delete=models.CASCADE, null=True, blank=True)
    absences = models.PositiveIntegerField(default=0)
    lates = models.PositiveIntegerField(default=0)
    sanction = models.ForeignKey(Sanction, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Attribue automatiquement la sanction selon le nombre d'heures d'absence
        if self.absences is not None:
            sanction = Sanction.objects.filter(min_heures_absence__lte=self.absences).order_by('-min_heures_absence').first()
            self.sanction = sanction
        super().save(*args, **kwargs)


class MentionRule(models.Model):
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE, related_name='mention_rules')
    label = models.CharField(max_length=20)  # ex: TB, Bien, AB, Passable
    min_avg = models.FloatField()
    max_avg = models.FloatField()

    def __str__(self):
        return f"{self.label} ({self.min_avg}-{self.max_avg})"


class Settings(models.Model):
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)
    scale_max = models.FloatField(default=20)
    rounding = models.PositiveIntegerField(default=2)
    min_pass_avg = models.FloatField(default=10)
    localization = models.CharField(max_length=10, default='FR')
    enable_ai = models.BooleanField(default=False)



# ---------------------------
# Archivage
# ---------------------------
class ArchivedGrade(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    school_year = models.ForeignKey(SchoolYear, on_delete=models.CASCADE)
    archived_at = models.DateTimeField(auto_now_add=True)


class ArchivedBulletin(models.Model):
    bulletin = models.ForeignKey(Bulletin, on_delete=models.CASCADE)
    archived_at = models.DateTimeField(auto_now_add=True)
