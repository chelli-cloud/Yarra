"""
The Yarra School Self-Evaluation Record, reproduced in-app from the official
Google Form so School Leader/Admin can fill it out (and a Yarra Evaluator can
review it) without leaving Yarra. Edit this file and rerun migrations/tests if
Ms Chelli's form changes -- it is the single source of truth for the schema.

Each question is a flat dict with:
  id          unique key (matches the form's own numbering, e.g. 'B-1.1a')
  part        'A' | 'B' | 'C' | 'D'
  section     top-level heading within the part
  subsection  optional sub-heading (Part B capability sub-areas)
  label       the question text
  type        'text' | 'textarea' | 'radio' | 'checkbox' | 'scale' | 'file'
  choices     list of (value, label) for radio/checkbox
  scale_labels (left_label, right_label) for scale-type questions
  required    bool
"""

PURPOSE_TEXT = (
    "This process is not about proving that your school is good. It is about helping "
    "your leadership team answer questions such as: What are we doing well? Where are "
    "we inconsistent? What should we focus on next? What will make the biggest "
    "difference over the next five years? The more honest your reflections, the more "
    "useful the evaluation will be."
)

SCORING_GUIDE = [
    '1 - Rarely Seen', '2 - Seen in Some Areas', '3 - Seen in most Areas',
    '4 - Seen consistently across the School',
]

BOARD_CHOICES = [
    ('matric_state', 'Matric/State'), ('cbse', 'CBSE'), ('icse', 'ICSE'),
    ('ed_excel', 'Ed Excel'), ('cambridge', 'Cambridge'), ('ib', 'IB'), ('other', 'Other'),
]

GRADE_CHOICES = [
    ('toddler', 'Toddler'), ('pre_kg', 'Pre KG'), ('lkg', 'LKG'), ('ukg', 'UKG'),
] + [(f'grade_{i}', f'Grade {i}') for i in range(1, 13)]

CAPABILITY_AREA_CHOICES = [
    ('learning_teaching', 'Learning & Teaching'), ('people_talent', 'People & Talent'),
    ('leadership_culture', 'Leadership & Culture'), ('operations_support', 'Operations & Support'),
    ('admissions_family', 'Admissions & Family Partnerships'),
]

SUPPORT_CHOICES = [
    ('professional_learning', 'Professional Learning'), ('leadership_support', 'Leadership & Support'),
    ('systems_processes', 'Systems and Processes'), ('coaching_mentoring', 'Coaching and Mentoring'),
    ('school_visits', 'School visits and collaboration'), ('review_feedback', 'Review and feedback'),
    ('improvement_planning', 'Improvement planning'), ('other', 'Other'),
]

ACTION_PLAN_GROUP_CHOICES = [
    ('school_leadership', 'School Leadership'), ('teachers', 'Teachers'), ('coordinators', 'Coordinators'),
    ('administrative_staff', 'Administrative Staff'), ('parents', 'Parents'), ('students', 'Students'),
]


QUESTIONS = []

# ---------------------------------------------------------------------------
# PART A: SCHOOL PROFILE & DATA
# ---------------------------------------------------------------------------
QUESTIONS += [
    {'id': 'A-1.1', 'part': 'A', 'section': '1. School Information', 'label': 'School Name', 'type': 'text', 'required': True},
    {'id': 'A-1.2', 'part': 'A', 'section': '1. School Information', 'label': 'Location', 'type': 'text', 'required': True},
    {'id': 'A-1.3', 'part': 'A', 'section': '1. School Information', 'label': 'Board / Curriculum', 'type': 'checkbox', 'choices': BOARD_CHOICES, 'required': True},
    {'id': 'A-1.4', 'part': 'A', 'section': '1. School Information', 'label': 'Year Established', 'type': 'text', 'required': True},
    {'id': 'A-1.5', 'part': 'A', 'section': '1. School Information', 'label': 'Trust/Society', 'type': 'text', 'required': True},
    {'id': 'A-1.6', 'part': 'A', 'section': '1. School Information', 'label': 'Head of School/ Principal', 'type': 'text', 'required': True},
    {'id': 'A-1.7', 'part': 'A', 'section': '1. School Information', 'label': 'Evaluation Coordinator', 'type': 'text', 'required': True},
    {'id': 'A-1.8', 'part': 'A', 'section': '1. School Information', 'label': 'Contact Email', 'type': 'text', 'required': True},
    {'id': 'A-1.9', 'part': 'A', 'section': '1. School Information', 'label': 'Contact Number', 'type': 'text', 'required': True},

    {'id': 'A-2.1', 'part': 'A', 'section': '2. School Structure', 'label': 'Grades Offered', 'type': 'checkbox', 'choices': GRADE_CHOICES, 'required': True},
    {'id': 'A-2.2-upload', 'part': 'A', 'section': '2. School Structure', 'label': 'Please upload Grade-wise Distribution (Grade / Number of Sections / Number of Students / Average Class Size, Early Years through Grade 12) in Word / Excel / Typed down and save as Pdf or Image', 'type': 'file', 'required': True},
    {'id': 'A-2.3', 'part': 'A', 'section': '2. School Structure', 'label': 'Total Student Strength', 'type': 'text', 'required': False},
    {'id': 'A-2.4', 'part': 'A', 'section': '2. School Structure', 'label': 'Total No. teaching Staff', 'type': 'text', 'required': True},
    {'id': 'A-2.5', 'part': 'A', 'section': '2. School Structure', 'label': 'Total No. of Non Teaching Staff', 'type': 'text', 'required': True},
    {'id': 'A-2.6', 'part': 'A', 'section': '2. School Structure', 'label': 'Number of Academic Leaders / Coordinators', 'type': 'text', 'required': False},

    {'id': 'A-3.1', 'part': 'A', 'section': '3. Staff Profile', 'label': 'Total Number of Teachers in Early Learning', 'type': 'text', 'required': True},
    {'id': 'A-3.2', 'part': 'A', 'section': '3. Staff Profile', 'label': 'Total Number of Teachers in Primary School', 'type': 'text', 'required': True},
    {'id': 'A-3.3', 'part': 'A', 'section': '3. Staff Profile', 'label': 'Total Number of Teachers in High School', 'type': 'text', 'required': True},
    {'id': 'A-3.4', 'part': 'A', 'section': '3. Staff Profile', 'label': '% of Teacher attrition in the past 2 Academic Years', 'type': 'text', 'required': True},
    {'id': 'A-3.5', 'part': 'A', 'section': '3. Staff Profile', 'label': 'Number of teachers who joined this Academic year', 'type': 'text', 'required': True},
    {'id': 'A-3.6', 'part': 'A', 'section': '3. Staff Profile', 'label': 'Total Number of Non Teaching Staff', 'type': 'text', 'required': True},
    {'id': 'A-3.7', 'part': 'A', 'section': '3. Staff Profile', 'label': '% of Non Teaching staff attrition in the past 2 Academic Years', 'type': 'text', 'required': True},

    {'id': 'A-4.1', 'part': 'A', 'section': '4. Student Data', 'label': 'Average Student attendance (%) in the past one year', 'type': 'text', 'required': True},
    {'id': 'A-4.2', 'part': 'A', 'section': '4. Student Data', 'label': 'Student attrition (%) in the past two years', 'type': 'text', 'required': True},
    {'id': 'A-4.3', 'part': 'A', 'section': '4. Student Data', 'label': 'Students requiring additional support (No. of students across grade - briefly describe the nature of support required)', 'type': 'textarea', 'required': True},
    {'id': 'A-4.4', 'part': 'A', 'section': '4. Student Data', 'label': 'Any major student discipline incidents in the past two years', 'type': 'textarea', 'required': True},
    {'id': 'A-4.5', 'part': 'A', 'section': '4. Student Data', 'label': 'Briefly describe student leadership opportunities available', 'type': 'textarea', 'required': True},

    {'id': 'A-5.1', 'part': 'A', 'section': '5. Professional Learning & School Systems', 'label': 'Briefly describe your Classroom observations process', 'type': 'textarea', 'required': True},
    {'id': 'A-5.2', 'part': 'A', 'section': '5. Professional Learning & School Systems', 'label': 'Teachers observed at least once (%) in the past year', 'type': 'text', 'required': True},
    {'id': 'A-5.3', 'part': 'A', 'section': '5. Professional Learning & School Systems', 'label': 'Professional development sessions conducted. Briefly describe the no. of sessions conducted and the topics on which Professional development sessions have been held', 'type': 'textarea', 'required': True},
    {'id': 'A-5.4', 'part': 'A', 'section': '5. Professional Learning & School Systems', 'label': 'Average PD hours per teacher', 'type': 'text', 'required': True},
    {'id': 'A-5.5', 'part': 'A', 'section': '5. Professional Learning & School Systems', 'label': 'Briefly describe your Induction programme for new teachers', 'type': 'textarea', 'required': True},
    {'id': 'A-5.6', 'part': 'A', 'section': '5. Professional Learning & School Systems', 'label': 'Briefly describe your Teacher mentoring system', 'type': 'textarea', 'required': True},
    {'id': 'A-5.7', 'part': 'A', 'section': '5. Professional Learning & School Systems', 'label': 'Briefly describe your Student wellbeing programme', 'type': 'radio', 'choices': [('yes', 'Yes'), ('no', 'No')], 'required': True},
    {'id': 'A-5.8', 'part': 'A', 'section': '5. Professional Learning & School Systems', 'label': 'Briefly describe your Student council or student leadership programme', 'type': 'textarea', 'required': True},
    {'id': 'A-5.9', 'part': 'A', 'section': '5. Professional Learning & School Systems', 'label': 'Parent satisfaction survey conducted', 'type': 'radio', 'choices': [('yes', 'Yes'), ('no', 'No')], 'required': True},
]

# ---------------------------------------------------------------------------
# PART B: INSTITUTIONAL CAPABILITY REVIEW
# ---------------------------------------------------------------------------
_SCALE = ('1 - Rarely Seen', '4 - Seen consistently across the school')


def _scale_q(qid, section, subsection, label):
    return {'id': qid, 'part': 'B', 'section': section, 'subsection': subsection, 'label': label, 'type': 'scale', 'required': True, 'scale_labels': _SCALE}


def _overall_q(qid, section, subsection):
    return {'id': qid, 'part': 'B', 'section': section, 'subsection': subsection, 'label': f'Overall Rating ({subsection})', 'type': 'scale', 'required': True, 'scale_labels': ('1', '4')}


CAPABILITY_AREAS = [
    ('CAPABILITY AREA 1: LEARNING & TEACHING', 'Teaching & Learning', [
        ('B-1.1 Student Engagement', [
            ('a', 'Students participate actively in learning'),
            ('b', 'Students ask questions and think critically.'),
            ('c', 'Students collaborate to support learning.'),
            ('d', 'Students take ownership of their learning.'),
        ]),
        ('B-1.2 Teaching Practice', [
            ('a', 'Teachers use a variety of teaching strategies.'),
            ('b', 'Learning goes beyond content coverage'),
            ('c', 'Students apply learning in meaningful ways'),
            ('d', 'Teaching is adapted to meet learner needs.'),
        ]),
        ('B-1.3 Assessment & Feedback', [
            ('a', 'Assessment measures student understanding'),
            ('b', 'A variety of assessment methods are used.'),
            ('c', 'Students receive timely and useful feedback'),
            ('d', 'Assessment evidence is used to plan next steps.'),
        ]),
        ('B-1.4 Learning Environment', [
            ('a', 'Students feel safe and included'),
            ('b', 'Participation is encouraged.'),
            ('c', 'Relationships are respectful and positive.'),
            ('d', 'Learning spaces support engagement'),
        ]),
    ], 'B-1.5'),
    ('CAPABILITY AREA 2: PEOPLE & TALENT', 'People & Talent', [
        ('B-2.1 Teacher Growth', [
            ('a', 'Teachers receive regular feedback on their teaching practices.'),
            ('b', 'Professional learning is planned and relevant.'),
            ('c', 'Teachers receive coaching and support to improve'),
            ('d', 'Teachers have opportunities to grow professionally'),
        ]),
        ('B-2.2 Collaboration', [
            ('a', 'Teams plan and review learning together'),
            ('b', 'Good practices are shared across teams'),
            ('c', 'Staff collaborate regularly to improve learning'),
        ]),
        ('B-2.3 Staff Support', [
            ('a', 'New staff are supported during induction'),
            ('b', 'Staff wellbeing is actively considered'),
            ('c', 'Staff feel valued and supported'),
        ]),
    ], 'B-2.4'),
    ('CAPABILITY AREA 3: LEADERSHIP & CULTURE', 'Leadership & Culture', [
        ('B-3.1 Direction & Priorities', [
            ('a', 'School priorities are clearly communicated by the Leadership'),
            ('b', 'Expectations are understood across the school'),
            ('c', "Staff understand the school's goals"),
        ]),
        ('B-3.2 Leadership', [
            ('a', 'Leaders support staff and students'),
            ('b', 'Roles and responsibilities are clear'),
            ('c', 'Staff have opportunities to lead initiatives'),
        ]),
        ('B-3.3 Culture', [
            ('a', 'Shared values are visible in daily practice'),
            ('b', 'Staff contribute ideas and feedback'),
            ('c', 'Relationships are respectful and collaborative'),
        ]),
        ('B-3.4 Review and Improvement', [
            ('a', 'Progress towards goals is reviewed regularly'),
            ('b', 'School improvement priorities are discussed'),
            ('c', 'Decisions are followed by clear actions'),
        ]),
    ], 'B-3.5'),
    ('CAPABILITY AREA 4: OPERATIONS & SUPPORT', 'Administration and Operations', [
        ('B-4.1 Administration', [
            ('a', 'Administrative processes are efficient'),
            ('b', 'Staff can easily access the information they need'),
            ('c', 'School procedures are followed consistently'),
        ]),
        ('B-4.2 Operations', [
            ('a', 'Daily school operations run smoothly'),
            ('b', 'Resources are available when needed'),
            ('c', 'Facilities are safe and support learning'),
        ]),
        ('B-4.3 Student Support', [
            ('a', 'Students receive support when needed'),
            ('b', 'Safety procedures are consistently followed'),
            ('c', 'Student wellbeing is actively supported'),
        ]),
    ], 'B-4.4'),
    ('CAPABILITY AREA 5: ADMISSIONS & FAMILY PARTNERSHIPS', 'Admissions & Family Partnerships', [
        ('B-5.1 Admissions', [
            ('a', 'Admissions processes are timely and well organised'),
            ('b', 'Families receive clear and timely information'),
            ('c', 'Prospective families have a positive admissions experience'),
        ]),
        ('B-5.2 Student Transition', [
            ('a', 'New students settle into the school successfully'),
            ('b', 'Families are supported during key transitions'),
        ]),
        ('B-5.3 Parent Communication', [
            ('a', 'Communication with families is clear and timely'),
            ('b', 'Parents know whom to contact when they need support'),
        ]),
        ('B-5.4 Family Engagement', [
            ('a', 'Families have opportunities to participate in school life'),
            ('b', 'Parent feedback is regularly sought'),
            ('c', 'Families feel welcomed and valued'),
        ]),
        ('B-5.5 Community Relationships', [
            ('a', 'The school builds positive relationships with the wider community'),
            ('b', 'Partnerships create meaningful learning opportunities'),
        ]),
    ], 'B-5.6'),
]

for area_title, final_label, subsections, final_prefix in CAPABILITY_AREAS:
    for sub_title, items in subsections:
        prefix = sub_title.split(' ', 1)[0]  # e.g. 'B-1.1'
        for suffix, label in items:
            QUESTIONS.append(_scale_q(f'{prefix}{suffix}', area_title, sub_title, label))
        QUESTIONS.append(_overall_q(f'{prefix}-overall', area_title, sub_title))
    QUESTIONS.append({
        'id': f'{final_prefix}-final', 'part': 'B', 'section': area_title, 'subsection': 'Final Rating & Reflection',
        'label': f'Provide your final rating for the Capability Area of {final_label}',
        'type': 'scale', 'required': True,
        'scale_labels': ('Needs significant improvement', 'Highly matured and evolved'),
    })
    QUESTIONS.append({'id': f'{final_prefix}-working-well', 'part': 'B', 'section': area_title, 'subsection': 'Final Rating & Reflection', 'label': f'What is working well in {final_label}?', 'type': 'textarea', 'required': True})
    QUESTIONS.append({'id': f'{final_prefix}-challenging', 'part': 'B', 'section': area_title, 'subsection': 'Final Rating & Reflection', 'label': 'What remains challenging?', 'type': 'textarea', 'required': True})
    QUESTIONS.append({'id': f'{final_prefix}-evidence', 'part': 'B', 'section': area_title, 'subsection': 'Final Rating & Reflection', 'label': 'Evidence available', 'type': 'textarea', 'required': False})

# ---------------------------------------------------------------------------
# PART C: SUPPORTING EVIDENCE
# ---------------------------------------------------------------------------
EVIDENCE_SECTIONS = [
    ('C-1.1 Learning and Teaching', [
        ('a', 'Lesson Plans'), ('b', 'Student work'), ('c', 'Assessment Examples'),
        ('d', 'Classroom observation records'), ('e', 'Learning documentation'),
    ]),
    ('C-1.2 People & Talent', [
        ('a', 'Professional learning Plans'), ('b', 'Teacher induction processes'),
        ('c', 'Mentoring records'), ('d', 'Staff development Plans'), ('e', 'Teacher feedback processes'),
    ]),
    ('C-1.3 Leadership & Culture', [
        ('a', 'School goals and priorities'), ('b', 'Meeting records'),
        ('c', 'Improvement plans'), ('d', 'Leadership Structures'), ('e', 'Staff Surveys'),
    ]),
    ('C-1.4 Operations & Support', [
        ('a', 'School calendars'), ('b', 'Administrative processes'),
        ('c', 'Safety Procedures'), ('d', 'Student Support records'), ('e', 'Operational Manuals'),
    ]),
    ('C-1.5 Admissions and Family Partnerships', [
        ('a', 'Parent communication samples'), ('b', 'Admission Processes'),
        ('c', 'Parent Surveys'), ('d', 'Orientation Programs'), ('e', 'Community Initiatives'),
    ]),
]

for sub_title, items in EVIDENCE_SECTIONS:
    prefix = sub_title.split(' ', 1)[0]
    for suffix, label in items:
        QUESTIONS.append({'id': f'{prefix}{suffix}', 'part': 'C', 'section': 'Supporting Evidence', 'subsection': sub_title, 'label': label, 'type': 'file', 'required': True})

QUESTIONS += [
    {'id': 'C-1.6a', 'part': 'C', 'section': 'Supporting Evidence', 'subsection': 'C-1.6 Evidence Reflection', 'label': "What evidence best represents your school's strengths?", 'type': 'textarea', 'required': True},
    {'id': 'C-1.6b', 'part': 'C', 'section': 'Supporting Evidence', 'subsection': 'C-1.6 Evidence Reflection', 'label': 'Which evidence best illustrates your current challenges?', 'type': 'textarea', 'required': True},
]

# ---------------------------------------------------------------------------
# PART D: SCHOOL PRIORITIES & IMPROVEMENT
# ---------------------------------------------------------------------------
QUESTIONS += [
    {'id': 'D-1', 'part': 'D', 'section': 'School Priorities & Improvement', 'label': "What are your school's top three priorities for this year?", 'type': 'textarea', 'required': True},
    {'id': 'D-2', 'part': 'D', 'section': 'School Priorities & Improvement', 'label': "What are your school's greatest challenges?", 'type': 'textarea', 'required': True},
    {'id': 'D-3', 'part': 'D', 'section': 'School Priorities & Improvement', 'label': 'Which capability area would you most like to strengthen over the next 12 months?', 'type': 'checkbox', 'choices': CAPABILITY_AREA_CHOICES, 'required': True},
    {'id': 'D-4', 'part': 'D', 'section': 'School Priorities & Improvement', 'label': 'Why have you selected this area', 'type': 'textarea', 'required': True},
    {'id': 'D-5', 'part': 'D', 'section': 'School Priorities & Improvement', 'label': 'What would success look like one year from now?', 'type': 'textarea', 'required': True},
    {'id': 'D-6', 'part': 'D', 'section': 'School Priorities & Improvement', 'label': 'What support would be most valuable?', 'type': 'radio', 'choices': SUPPORT_CHOICES, 'required': False},
    {'id': 'D-7', 'part': 'D', 'section': 'School Priorities & Improvement', 'label': 'Which groups will be involved in working on your Action Plan and implementation of the same?', 'type': 'checkbox', 'choices': ACTION_PLAN_GROUP_CHOICES, 'required': True},
    {'id': 'D-8', 'part': 'D', 'section': 'School Priorities & Improvement', 'label': 'If your school could make one meaningful improvement this year, what would it be', 'type': 'textarea', 'required': True},
]

PART_TITLES = {
    'A': 'PART A: SCHOOL PROFILE & DATA',
    'B': 'PART B: INSTITUTIONAL CAPABILITY REVIEW',
    'C': 'PART C: SUPPORTING EVIDENCE',
    'D': 'PART D: SCHOOL PRIORITIES & IMPROVEMENT',
}

QUESTIONS_BY_ID = {q['id']: q for q in QUESTIONS}


def grouped_questions():
    """Groups QUESTIONS into Part -> Section -> Subsection -> [questions], preserving order."""
    parts = []
    part_index = {}
    for q in QUESTIONS:
        part_key = q['part']
        if part_key not in part_index:
            part_index[part_key] = {'key': part_key, 'title': PART_TITLES[part_key], 'sections': [], '_section_index': {}}
            parts.append(part_index[part_key])
        part = part_index[part_key]
        section_key = q.get('section') or q.get('subsection') or part['title']
        if section_key not in part['_section_index']:
            part['_section_index'][section_key] = {'title': section_key, 'subsections': [], '_sub_index': {}}
            part['sections'].append(part['_section_index'][section_key])
        section = part['_section_index'][section_key]
        sub_key = q.get('subsection') if q.get('section') else None
        if sub_key:
            if sub_key not in section['_sub_index']:
                section['_sub_index'][sub_key] = {'title': sub_key, 'questions': []}
                section['subsections'].append(section['_sub_index'][sub_key])
            section['_sub_index'][sub_key]['questions'].append(q)
        else:
            if '_flat' not in section:
                section['_flat'] = {'title': None, 'questions': []}
                section['subsections'].append(section['_flat'])
            section['_flat']['questions'].append(q)
    return parts
