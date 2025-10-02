from django import forms
from ckeditor.widgets import CKEditorWidget
from Bull.models import Student, Classroom, Teacher, User, Subject, ClassSubject, BulletinTemplate, SchoolYear

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['matricule', 'last_name', 'first_name', 'gender', 'birth_date', 'birth_place', 'photo', 'classroom', 'repeater']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=[('M', 'Masculin'), ('F', 'Féminin')]),
            'repeater': forms.CheckboxInput(),
        }

class ImportStudentsForm(forms.Form):
    excel_file = forms.FileField(label='Fichier Excel (.xlsx)')

class ExportStudentsForm(forms.Form):
    classroom = forms.ModelChoiceField(queryset=Classroom.objects.all(), label='Classe à exporter')

class UserForm(forms.ModelForm):
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput, required=False)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['phone', 'is_active']

# Formulaire pour lier une classe à un enseignant
from Bull.models import ClassSubject, Classroom, Subject
class TeacherClassSubjectForm(forms.Form):
    classroom = forms.ModelChoiceField(queryset=Classroom.objects.all(), label='Classe')
    subject = forms.ModelChoiceField(queryset=Subject.objects.none(), label='Matière')

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super().__init__(*args, **kwargs)
        self.fields['classroom'].queryset = Classroom.objects.all()
        if 'classroom' in self.data:
            try:
                classroom_id = int(self.data.get('classroom'))
                subjects = ClassSubject.objects.filter(classroom_id=classroom_id).values_list('subject', flat=True)
                self.fields['subject'].queryset = Subject.objects.filter(id__in=subjects)
            except (ValueError, TypeError):
                self.fields['subject'].queryset = Subject.objects.none()
        else:
            self.fields['subject'].queryset = Subject.objects.none()

class BulletinTemplateForm(forms.ModelForm):
    class Meta:
        model = BulletinTemplate
        fields = ['school_year', 'name', 'header_docx', 'footer_docx', 'html_canvas', 'active']
        widgets = {
            'school_year': forms.Select(),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'header_docx': forms.ClearableFileInput(attrs={'accept': '.docx'}),
            'footer_docx': forms.ClearableFileInput(attrs={'accept': '.docx'}),
            'html_canvas': CKEditorWidget(),
            'active': forms.CheckboxInput(),
        }