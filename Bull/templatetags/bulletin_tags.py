from django import template
register = template.Library()

@register.filter
def get_grade(grades, key):
    try:
        student_id, subject_id = [int(x) for x in key.split(',')]
    except Exception:
        return None
    for g in grades:
        if g.student_id == student_id and g.class_subject.subject_id == subject_id:
            return g
    return None

@register.filter
def get_all_ok(grades, student_id):
    student_grades = [g for g in grades if g.student_id == student_id]
    return all(g.value is not None for g in student_grades)

@register.filter
def get_bulletin(bulletins, student_id):
    for b in bulletins:
        if b.student_id == student_id:
            return b
    return None


@register.filter
def get_bulletin_for_student(bulletins, student):
    """
    Returns the bulletin object for the given student from a queryset or list of bulletins.
    """
    for bulletin in bulletins:
        if hasattr(bulletin, 'student_id') and bulletin.student_id == student.id:
            return bulletin
        if hasattr(bulletin, 'student') and getattr(bulletin.student, 'id', None) == student.id:
            return bulletin
    return None


@register.filter
def get_grade_for_subject(grades, subject_id):
    for g in grades:
        if hasattr(g, 'class_subject') and getattr(g.class_subject, 'subject_id', None) == subject_id:
            return g
    return None


@register.filter
def get_sequence_bulletins(bulletins_by_student, student):
    bulletins = bulletins_by_student.get(student.id, [])
    return [b for b in bulletins if hasattr(b, 'sequence') and b.sequence is not None and not hasattr(b, 'is_trimester') and not hasattr(b, 'is_annual')]

@register.filter
def get_trimester_bulletins(bulletins_by_student, student):
    bulletins = bulletins_by_student.get(student.id, [])
    return [b for b in bulletins if hasattr(b, 'is_trimester') and b.is_trimester]

@register.filter
def get_annual_bulletins(bulletins_by_student, student):
    bulletins = bulletins_by_student.get(student.id, [])
    return [b for b in bulletins if hasattr(b, 'is_annual') and b.is_annual]
