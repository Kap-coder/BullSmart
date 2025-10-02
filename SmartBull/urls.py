
from django.contrib import admin
from django.urls import path, include
# from rest_framework import routers
# from rest_framework_simplejwt.views import (
#     TokenObtainPairView,
#     TokenRefreshView,
# )
from Bull import views
# from Bull.views import RegisterView, StudentAnalysisView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions


from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

# router = routers.DefaultRouter()
# router.register(r'users', views.UserViewSet)
# router.register(r'schoolyears', views.SchoolYearViewSet)
# router.register(r'terms', views.TermViewSet)
# router.register(r'sequences', views.SequenceViewSet)
# router.register(r'classrooms', views.ClassroomViewSet)
# router.register(r'teachers', views.TeacherViewSet)
# router.register(r'students', views.StudentViewSet)
# router.register(r'subjects', views.SubjectViewSet)
# router.register(r'classsubjects', views.ClassSubjectViewSet)
# router.register(r'grades', views.GradeViewSet)
# router.register(r'disciplines', views.DisciplineViewSet)
# router.register(r'mentionrules', views.MentionRuleViewSet)
# router.register(r'settings', views.SettingsViewSet)
# router.register(r'bulletins', views.BulletinViewSet)
# router.register(r'archivedgrades', views.ArchivedGradeViewSet)
# router.register(r'archivedbulletins', views.ArchivedBulletinViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="SmartBull API",
        default_version='v1',
        description="API de gestion des bulletins scolaires Camerounais",
        contact=openapi.Contact(email="support@smartbull.local"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('parameters/sanctions-table/', views.sanctions_table, name='sanctions_table'),
    path('bulletin-templates/', views.bulletin_template_list, name='bulletin_template_list'),
    path('bulletin-templates/add/', views.bulletin_template_create, name='bulletin_template_create'),
    path('bulletin-templates/<int:template_id>/edit/', views.bulletin_template_edit, name='bulletin_template_edit'),
    path('teachers/<int:teacher_id>/unlink_class_subject/<int:classsubject_id>/', views.unlink_class_subject_teacher, name='unlink_class_subject_teacher'),
    path('ajax/get_subjects_for_class/', views.get_subjects_for_class, name='get_subjects_for_class'),
    path('teachers/', views.teachers_list_view, name='teachers_list'),
    path('teachers/add/', views.add_teacher_view, name='add_teacher'),
    path('teachers/<int:teacher_id>/edit/', views.edit_teacher_view, name='edit_teacher'),
    path('teachers/<int:teacher_id>/delete/', views.delete_teacher_view, name='delete_teacher'),
    path('teachers/<int:teacher_id>/', views.teacher_detail_view, name='teacher_detail'),
    path('students/<int:student_id>/delete/', views.delete_student_view, name='delete_student'),
    path('students/<int:student_id>/delete/', views.delete_student_view, name='delete_student'),
    path('students/add/', views.add_student_view, name='add_student'),
    path('students/import/', views.import_students_view, name='import_students'),
    path('students/export/', views.export_students_view, name='export_students'),
    path('parameters/add-term/', views.add_term, name='add_term'),
    path('parameters/edit-term/<int:term_id>/', views.edit_term, name='edit_term'),
    path('parameters/delete-term/<int:term_id>/', views.delete_term, name='delete_term'),
    path('parameters/edit-sequence/<int:seq_id>/', views.edit_sequence, name='edit_sequence'),
    path('parameters/delete-sequence/<int:seq_id>/', views.delete_sequence, name='delete_sequence'),
    path('parameters/add-schoolyear/', views.add_schoolyear, name='add_schoolyear'),
    path('parameters/edit-schoolyear/<int:sy_id>/', views.edit_schoolyear, name='edit_schoolyear'),
    path('parameters/delete-schoolyear/<int:sy_id>/', views.delete_schoolyear, name='delete_schoolyear'),
    path('parameters/', views.parameters_view, name='parameters'),
    path('parameters/edit-html-canvas/', views.edit_html_canvas, name='edit_html_canvas'),
    path('parameters/add-sanction/', views.add_sanction, name='add_sanction'),
    path('parameters/edit-sanction/', views.edit_sanction, name='edit_sanction'),
    path('parameters/delete-sanction/', views.delete_sanction, name='delete_sanction'),
    path('parameters/set-active-schoolyear/<int:sy_id>/', views.set_active_schoolyear, name='set_active_schoolyear'),
    path('parameters/set-active-sequence/<int:seq_id>/', views.set_active_sequence, name='set_active_sequence'),
    path('classsubject/<int:cs_id>/generate-grades/', views.generate_grades_view, name='generate_grades'),
    path('classsubject/<int:cs_id>/students/', views.classsubject_students_view, name='classsubject_students'),
    path('classsubject/<int:cs_id>/save-grades/', views.save_grades_view, name='save_grades'),
    path('classsubject/<int:cs_id>/download-pdf/', views.download_grades_pdf, name='download_grades_pdf'),
    path('classsubject/<int:cs_id>/validate/', views.validate_grades_view, name='validate_grades'),
    path('subjects/<int:subject_id>/class-cards/', views.subject_class_cards_view, name='subject_class_cards'),
    path('sequences/add/', views.add_sequence_view, name='add_sequence'),
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('students/', views.students_view, name='students'),
    path('students/<int:student_id>/', views.student_detail_view, name='student_detail'),
    path('students/<int:student_id>/edit/', views.student_edit_view, name='student_edit'),
    path('users/', views.users_view, name='users'),
    path('classes/', views.classes_view, name='classes'),
    path('classes/<int:class_id>/edit/', views.class_edit_view, name='class_edit'),
    path('classes/add/', views.class_add_view, name='class_add'),
    path('classes/<int:class_id>/', views.class_detail_view, name='class_detail'),
    path('subjects/', views.subjects_view, name='subjects'),
    path('subjects/add/', views.subject_add_view, name='subject_add'),
    path('subjects/<int:subject_id>/', views.subject_detail_view, name='subject_detail'),
    path('subjects/<int:subject_id>/edit/', views.subject_edit_view, name='subject_edit'),
    path('subjects/<int:subject_id>/classsubject/add/', views.classsubject_add_view, name='classsubject_add'),
    path('classsubject/<int:cs_id>/', views.classsubject_detail_page, name='classsubject_detail'),
    path('classsubject/<int:cs_id>/edit/', views.classsubject_edit_page, name='classsubject_edit'),
    path('classsubject/<int:cs_id>/delete/', views.classsubject_delete_page, name='classsubject_delete'),
    path('grades/', views.grades_view, name='grades'),
    path('bulletins/', views.bulletin_view, name='bulletins'),
    path('bulletins/<int:student_id>/<int:sequence_id>/', views.bulletin_detail_view, name='bulletin_detail'),
    path('my-bulletin/', views.my_bulletin_view, name='my_bulletin'),
    path('notes/', views.subject_card_list_view, name='subject_card_list'),
    path('bulletins/calculate/', views.calculate_bulletins, name='calculate_bulletins'),
    path('bulletins/export/pdf/', views.export_bulletins_pdf, name='export_bulletins_pdf'),
    path('bulletins/export/excel/', views.export_bulletins_excel, name='export_bulletins_excel'),
    path('bulletins/generate/', views.calculate_bulletins, name='generate_bulletins'),
    path('bulletins/stats/', views.bulletin_stats, name='bulletin_stats'),
    path('bulletins/<int:student_id>/<int:sequence_id>/pdf/', views.download_bulletin_pdf, name='download_bulletin_pdf'),
    path('bulletins/generate/trimester/', views.generate_bulletins_trimester, name='generate_bulletins_trimester'),
    path('bulletins/generate/annual/', views.generate_bulletins_annual, name='generate_bulletins_annual'),

    # # path('api/', include(router.urls)),
    # path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # # path('api/auth/register/', RegisterView.as_view(), name='auth_register'),
    # path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    # path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    # # path('api/ia/analyse/', StudentAnalysisView.as_view(), name='student-analysis'),
    # path('api/bulletins/<int:pk>/export_pdf/', views.BulletinViewSet.as_view({'get': 'export_pdf'}), name='bulletin-export-pdf'),
]

from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
