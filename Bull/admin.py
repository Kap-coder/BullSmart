from django.contrib import admin
from .models import (
	Sanction, User, SchoolYear, Term, Sequence, Classroom, Teacher, Student,
	Subject, ClassSubject, Grade, Discipline, MentionRule,
	Settings, Bulletin, ArchivedGrade, ArchivedBulletin, StudentSubject
)

@admin.register(Sanction)
class SanctionAdmin(admin.ModelAdmin):
	list_display = ('texte', 'min_heures_absence')
	search_fields = ('texte',)


@admin.register(StudentSubject)
class StudentSubjectAdmin(admin.ModelAdmin):
	list_display = ('student', 'subject', 'is_optional')
	search_fields = ('student__matricule', 'student__first_name', 'student__last_name', 'subject__name')

admin.site.register(User)
admin.site.register(SchoolYear)
admin.site.register(Term)
admin.site.register(Sequence)
admin.site.register(Classroom)
admin.site.register(Teacher)
admin.site.register(Student)
admin.site.register(Subject)
admin.site.register(ClassSubject)
admin.site.register(Grade)
admin.site.register(Discipline)
admin.site.register(MentionRule)
admin.site.register(Settings)
admin.site.register(Bulletin)
admin.site.register(ArchivedGrade)
admin.site.register(ArchivedBulletin)
