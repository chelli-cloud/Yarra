"""
Generates the Yarra Consortium User Manual as a PDF.

Documents the platform AS IMPLEMENTED TODAY -- every module, who can access
it, how it actually works, user stories, and acceptance expectations --
not an aspirational spec. Regenerate after any major module change:

    python scripts/generate_user_manual.py

Output: Yarra_User_Manual.pdf in the project root.
"""

import os

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGO_PATH = os.path.join(BASE_DIR, 'static', 'images', 'yarra-logo.jpeg')
OUTPUT_PATH = os.path.join(BASE_DIR, 'Yarra_User_Manual.pdf')

PRIMARY = colors.HexColor('#1F6F76')
PRIMARY_DARK = colors.HexColor('#154F54')
LIGHT_BG = colors.HexColor('#E3F5F3')
TEXT = colors.HexColor('#10282A')
MUTED = colors.HexColor('#5C7A7A')
BORDER = colors.HexColor('#D7EBE9')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle('Cover', parent=styles['Title'], fontSize=26, textColor=PRIMARY, alignment=TA_CENTER, spaceAfter=6))
styles.add(ParagraphStyle('CoverSub', parent=styles['Normal'], fontSize=12, textColor=MUTED, alignment=TA_CENTER, spaceAfter=4))
styles.add(ParagraphStyle('H1', parent=styles['Heading1'], textColor=PRIMARY, fontSize=18, spaceBefore=4, spaceAfter=10))
styles.add(ParagraphStyle('H2', parent=styles['Heading2'], textColor=PRIMARY_DARK, fontSize=14, spaceBefore=14, spaceAfter=6))
styles.add(ParagraphStyle('H3', parent=styles['Heading3'], textColor=TEXT, fontSize=11.5, spaceBefore=8, spaceAfter=4))
styles.add(ParagraphStyle('Body', parent=styles['Normal'], fontSize=9.5, textColor=TEXT, leading=13))
styles.add(ParagraphStyle('Muted', parent=styles['Normal'], fontSize=9, textColor=MUTED, leading=12))
styles.add(ParagraphStyle('BulletBody', parent=styles['Normal'], fontSize=9.5, textColor=TEXT, leading=13))
styles.add(ParagraphStyle('TOC', parent=styles['Normal'], fontSize=11, textColor=TEXT, leading=20))


# ---------------------------------------------------------------------------
# Content data -- edit this when modules change, then rerun the script.
# ---------------------------------------------------------------------------

ROLES = ['Super Admin', 'School Admin', 'Teacher', 'Yarra Evaluator', 'Vendor']

ROLE_MATRIX = [
    ['Module', 'Super Admin', 'School Admin', 'Teacher', 'Yarra Evaluator', 'Vendor'],
    ['Dashboard', 'Full', 'Own school', 'Limited', 'No', 'No'],
    ['User Management', 'Full (all schools)', 'Own school (max 2 admins, 5 teachers)', 'No', 'No', 'No'],
    ['School Onboarding', 'Creates (basic data)', 'Completes extended profile', 'No', 'No', 'No'],
    ['School Profile / Dashboard', 'Full', 'Own school (edit)', 'View', 'No', 'No'],
    ['Payments & Invoices', 'Full (any school)', 'Own school', 'No', 'No', 'No'],
    ['Events', 'Create / edit / delete', 'Register participants, manage', 'Register participants, manage', 'No', 'No'],
    ['Student Exchange', 'Oversight', 'Create / manage', 'View & apply', 'No', 'No'],
    ['Content Library', 'Approve / reject', 'Submit', 'View / comment', 'No', 'No'],
    ['Vendor Sign-up', 'Approves', 'No', 'No', 'No', 'Applies (no login needed)'],
    ['Vendor Marketplace', 'Approve promotions', 'Enquire / request', 'Enquire / request', 'No', 'Managed via Admin'],
    ['Vendor Event Interest', 'Notified', 'No', 'No', 'No', 'Applies'],
    ['School Network', 'View', 'View & contact', 'View only', 'No', 'No'],
    ['School Review', 'View', 'Edit (Leader/Admin)', 'View', 'View Self Study + ask questions', 'No'],
    ['Leadership Connect', 'No', 'Yes (Leader/Admin only)', 'No', 'No', 'No'],
    ['Notifications & Activity', 'Sees all activity', 'Own', 'Own', 'Own', 'No'],
    ['Consortium Analytics', 'Yes (direct URL)', 'No', 'No', 'No', 'No'],
    ['Role Preview (testing)', 'Yes', 'No', 'No', 'No', 'No'],
]

ROLE_STORIES = {
    'Super Admin': [
        'Create a school with just its name, state/country, Yarra Coordinator contact, and membership tier, and let the invite handle the rest.',
        'See total schools, revenue (manual payments + verified event fees), and pending approvals in one dashboard.',
        'Export schools, payments, or vendors as CSV for offline reporting.',
        'Broadcast an announcement to every school, or just one membership tier.',
        'Cap every school at 2 admins and 5 teachers so accounts stay under control.',
        'Create, edit, and delete Yarra-wide events, with registrations and results cleaned up automatically on delete.',
        'Review and approve school-submitted content before it reaches other schools.',
        'Approve vendors and their promotions before they appear in the marketplace.',
        'Get notified the moment any meaningful activity happens anywhere on the platform.',
        'Preview the platform as any other role, to test modules or help a school troubleshoot.',
    ],
    'School Admin': [
        'Invite teachers and a second admin by email, without needing an upload template.',
        'See our own school\'s membership, payments, and dashboard data -- never another school\'s.',
        'Record a payment (including cheque) if the bank transfer confirmation is still pending, and download its invoice.',
        'Review our full payment history in one place.',
        'Post a teacher/student exchange listing with an exact start and end date.',
        'Submit content for the library and know it stays private until Yarra approves it.',
        'Contact another school\'s Yarra Coordinator directly from the School Network.',
        'Showcase our achievements and leadership team on our school profile.',
        'Register our students for a Yarra event by name, without them needing their own login.',
        'Answer a Yarra Evaluator\'s question about our Self Study Questionnaire, with an optional document attached.',
    ],
    'Teacher': [
        'View events, exchanges, content, vendors, and the school network without needing edit access.',
        'Register a participant for an active event and pay online via Razorpay, or upload proof if online payment isn\'t configured.',
        'Mark attendance, download a certificate, and record feedback on a participant\'s behalf once they\'ve attended.',
        'View Open, Applied, Under Review, and Matched exchanges, and apply to open ones.',
        'Browse the content library, filter by type, save items for later, and like or report a comment.',
        'Browse the school network for collaboration ideas, without being able to contact other schools directly.',
    ],
    'Yarra Evaluator': [
        'View any school\'s Self Study Questionnaire without needing a School Admin to send it separately.',
        'Ask a follow-up question about a school\'s self study submission and have the School Admin notified immediately.',
        'See the School Admin\'s answer (text and/or an attached document) once they respond, right on the same page.',
    ],
    'Vendor': [
        'Sign up for the marketplace directly from the login page, with no Yarra account needed first.',
        'Submit our brochure and catalog alongside our profile, and wait for Super Admin approval.',
        'Send enquiries to schools and track their status once approved.',
        'Apply to support an upcoming Yarra event and know the Super Admin will see the request.',
    ],
}

MODULES = [
    {
        'name': '1. Login & Sessions',
        'purpose': 'Authenticate every user and route them into their role-scoped workspace.',
        'roles': 'All users.',
        'workflow': [
            'User opens the home page and clicks Login.',
            'Signs in with username or email + password, or via Google/Microsoft SSO if configured for the site.',
            'A session is created; the sidebar shows only the modules the user\'s role can access.',
            'User logs out to clear the session.',
        ],
        'stories': [
            'As any user, I want to log in with either my username or email so I don\'t need to remember which one I registered with.',
            'As a Super Admin, I want a Master Dashboard link so I can manage every school from one console.',
        ],
        'acceptance': [
            'Invalid credentials show a clear inline error, not a generic failure.',
            'SSO buttons only render when a provider is actually configured.',
            'Navigation hides links the current role cannot use.',
        ],
    },
    {
        'name': '2. Super Admin Dashboard',
        'purpose': 'Give the Super Admin a live snapshot of the whole consortium.',
        'roles': 'Super Admin.',
        'workflow': [
            'Log in as a superuser; the Command Centre dashboard loads automatically.',
            'Metrics (total/active schools, expiring memberships, revenue, pending vendors, flagged comments) are computed live from current data -- nothing is hand-entered.',
            'Drill into pending vendor approvals or flagged content directly from the same screen.',
            'Export schools, payments, or vendors as a CSV file for offline reporting.',
            'Send a broadcast announcement to every school, or filter to a single membership tier.',
        ],
        'stories': [
            'As a Super Admin, I want schools, revenue, and pending approvals visible in one place so I don\'t have to check every module separately.',
            'As a Super Admin, I want to export platform data as CSV so I can analyze it outside the app.',
            'As a Super Admin, I want to broadcast an announcement so every school (or a specific tier) hears about it at once.',
        ],
        'acceptance': [
            'Revenue = sum of verified event registration fees + every manually recorded Payment, not a flat estimate.',
            'Metrics recalculate automatically as schools/events/payments are added -- no manual refresh step.',
            'CSV exports and the broadcast tool are Super-Admin-only.',
        ],
    },
    {
        'name': '3. Master Dashboard / School Directory',
        'purpose': 'Let the Super Admin browse and jump into any member school.',
        'roles': 'Super Admin only.',
        'workflow': [
            'Open Master Dashboard from the sidebar.',
            'See every school with membership tier, user count, and event count.',
            'Use the school-selector dropdown, or "Add New School", to act on a specific school.',
        ],
        'stories': [
            'As a Super Admin, I want to open any school\'s profile directly from a dropdown instead of hunting through a list.',
        ],
        'acceptance': [
            'The selector navigates straight to that school\'s profile page.',
        ],
    },
    {
        'name': '4. User Management',
        'purpose': 'Give schools and the Super Admin a controlled way to add staff logins.',
        'roles': 'Super Admin (all schools). School Admin / School Leader (own school only).',
        'workflow': [
            'Admin or School Leader opens Invite User and enters an email + role.',
            'The system checks the school hasn\'t hit its cap -- max 2 admins, max 5 teachers, counting pending invitations as well as active accounts.',
            'An invitation link is generated (shown on screen; no email sending is wired up yet).',
            'The invitee opens the link and sets a password; their account email is locked to the address that was invited.',
            'Super Admin can additionally browse every school\'s users, each one\'s last sign-in, and their recent activity.',
        ],
        'stories': [
            'As a School Admin, I want to invite a teacher by email without setting a password for them myself.',
            'As a School Admin, I want to be blocked from exceeding 5 teachers so I don\'t over-provision by accident.',
            'As a Super Admin, I want to see every school\'s users, last sign-in, and recent actions in one place.',
        ],
        'acceptance': [
            'Caps count pending (unaccepted) invitations, not just accepted ones -- re-inviting past the limit is rejected.',
            'The created account\'s email always matches the invited address, never whatever the invitee types at signup.',
            'There is no bulk/Excel upload by design -- invitations are one at a time.',
        ],
    },
    {
        'name': '5. School Onboarding / Registration',
        'purpose': 'Create a new member school in two stages -- Super Admin fills the minimum, the school fills the rest.',
        'roles': 'Super Admin (creates). School Admin (completes).',
        'workflow': [
            'Super Admin enters school name, state, country, membership tier, and the Yarra Coordinator\'s name/email/phone.',
            'An invitation (role = Admin) is sent to the coordinator\'s email.',
            'The coordinator accepts and sets a password; their login email is locked to the invited address.',
            'The school profile shows a "Complete Your Profile" banner until the extended profile -- curriculum/board, learner count, principal contact, vision, infrastructure, and up to 10 supporting documents -- is submitted.',
        ],
        'stories': [
            'As a Super Admin, I want to onboard a school in seconds and let the school fill in the detail later.',
            'As a School Admin, I want a clear prompt telling me exactly what\'s still missing from our profile.',
        ],
        'acceptance': [
            'The profile-completed flag only flips once the extended form is actually submitted.',
            'A public self-registration form also exists as a fallback path outside the Super-Admin-initiated flow.',
        ],
    },
    {
        'name': '6. School Profile / School Dashboard',
        'purpose': 'The school\'s home base -- branding, membership status, and a structured registration profile.',
        'roles': 'Super Admin (any school). School Admin / School Leader (own school, editable). Others (view own school).',
        'workflow': [
            'View logo, location, contact person, membership tier, social links, achievements/highlights, leadership team, and (for the school\'s own staff) the assigned Yarra Coordinator\'s contact details.',
            'School Admin edits branding, contact details, and social links; uploads a logo.',
            'The extended registration profile is organized into 5 sections: School Details (address, state, Grades & Number of Students table covering Toddler through Grade 12, fee range, principal contact), Curriculum Details (board dropdown with a "specify" field for Mixed/Other, annual planning description, assessment practices), Infrastructure Details, Teacher Professional Development, and School Vision (5-year vision, 2-5 year focus areas, key strengths).',
            'Every grade level in the Grades & Number of Students table is mandatory -- the form will not save until all 16 counts are filled in.',
            'Achievements and leadership team are entered as part of the extended profile and displayed on the school\'s page.',
            'Admin panel links out to Complete Extended Profile, Invite Staff, User Management, and Payment History.',
        ],
        'stories': [
            'As a School Admin, I want to update our logo and social links myself.',
            'As a School Admin, I want a single structured form for our school\'s registration details, grouped the way Yarra reviews them.',
            'As a School Admin, I want to see our assigned Yarra Coordinator\'s contact details without having to ask Super Admin.',
            'As a Super Admin, I want to open and, if needed, edit any school\'s profile from the Master Dashboard.',
        ],
        'acceptance': [
            'Only School Leader/Admin roles can edit; everyone else gets a read-only view.',
            'State is selected from a fixed list of Indian states/UTs, not free text.',
        ],
    },
    {
        'name': '7. Payments & Invoices',
        'purpose': 'Record and track membership and event payments.',
        'roles': 'Super Admin (any school). School Admin / Teacher (own school).',
        'workflow': [
            'Open Record Payment; Super Admin chooses which school, School Admin is auto-scoped to their own.',
            'Enter amount, method (online / cheque / bank transfer / cash / other), notes, and an optional receipt file.',
            'Payment History lists every payment (Super Admin sees all schools, School Admin their own), each with a downloadable PDF invoice.',
            'For event registrations, staff separately download a PDF invoice for a participant once that registration\'s payment is verified.',
        ],
        'stories': [
            'As a Super Admin, I want to record a cheque payment on a school\'s behalf if their admin can\'t.',
            'As a School Admin, I want to see our full payment history and download an invoice for any past payment.',
            'As a School Admin, I want an invoice for a participant\'s event registration once their payment clears.',
        ],
        'acceptance': [
            'Cheque is a supported payment method, per the explicit requirement.',
            'Dashboard revenue includes every manually recorded payment, not just online ones.',
            'Payment History is scoped the same way Record Payment already is -- no new access rule introduced.',
        ],
    },
    {
        'name': '8. Events',
        'purpose': 'Run Yarra-wide events -- competitions, workshops, and activities -- with participants registered directly by school staff.',
        'roles': 'Super Admin (create/edit/delete). School Admin & Teacher (register participants, manage own school\'s participation).',
        'workflow': [
            'Super Admin creates an event: category, format, capacity, Pro-Bono or Paid fee type, registration link, brochure.',
            'Every school sees the event -- it is not scoped to one school.',
            'School Admin or Teacher registers a participant by name on the event page; Razorpay checkout runs if configured, otherwise a manual payment-proof upload is accepted.',
            'School staff mark attendance, log competition results, and record feedback for their own school\'s registered participants.',
            'After the event, a recording link, presentation file, and a photo gallery can be attached.',
            'Once a participant is marked attended, staff can download their PDF certificate of participation.',
            'Staff can export an event\'s attendee list as CSV from the Participant Records page.',
            'Deleting an event cascades its registrations and results -- no orphan records are left behind.',
        ],
        'stories': [
            'As a Super Admin, I want to create Yarra events so every member school can take part.',
            'As a School Admin, I want to register our students for an event by name, without them needing a login of their own.',
            'As a Teacher, I want to mark attendance and download a certificate on a participant\'s behalf once they\'ve attended.',
        ],
        'acceptance': [
            'Create, edit, and delete permissions exist only for Super Admin.',
            'Participant Records (grouped by school) are reached from the event page, not the main dashboard.',
            'A certificate is only downloadable once attendance is actually marked.',
            'There is no student self-service login for events -- registration, payment, attendance, certificates, invoices, and feedback are all handled by school staff on the participant\'s behalf.',
        ],
    },
    {
        'name': '9. Student Exchange Programs',
        'purpose': 'Match one school\'s teacher/student exchange offer with another school.',
        'roles': 'School Admin (create/manage). Teacher (view/apply, message).',
        'workflow': [
            'School Admin posts a listing: type, subject/grade, exact start and end dates, objectives.',
            'Other schools browse open listings and apply with a message.',
            'The listing owner reviews applications (Pending -> Under Review -> Approved/Rejected); approving one auto-rejects the rest and marks the listing Matched.',
            'Matched schools exchange messages through the application thread.',
            'The owner marks the exchange Completed; both sides submit a rating and comments.',
        ],
        'stories': [
            'As a School Admin, I want to post a listing so another school can apply.',
            'As a Teacher, I want to see Open, Applied, Under Review, and Matched exchanges and apply to open ones.',
        ],
        'acceptance': [
            'Visibility is role-filtered: School Admin sees Open/Applied/Matched; Teacher additionally sees Under Review.',
            'Messages are scoped to the specific matched application, not visible platform-wide.',
        ],
    },
    {
        'name': '10. Content Library',
        'purpose': 'Share Yarra-curated learning resources, gated by Super Admin approval.',
        'roles': 'Super Admin (approve/reject). School Admin (submit). Teacher & all staff (view/search/filter/comment).',
        'workflow': [
            'School Admin submits an article, podcast, video, or announcement, optionally scheduled for a future publish date.',
            'It saves as Pending Yarra Verification -- invisible to every other school until approved.',
            'Super Admin reviews the queue and approves (publishes) or rejects (returns to draft, submitter notified).',
            'Approved content is searchable/filterable by type and category, gated by Early-Years membership and any target-school list, and only actually visible once its scheduled publish date has passed.',
            'Any viewer can save an item to My Bookmarks, see related content in the same category, and like or report a comment.',
        ],
        'stories': [
            'As a School Admin, I want to submit a workshop recording and know it stays private until Yarra approves it.',
            'As a Super Admin, I want to curate the library before anything goes live.',
            'As a Teacher, I want to browse and filter content, save items for later, and like or report a comment, without being able to create or edit posts.',
        ],
        'acceptance': [
            'Pending content never appears to other schools.',
            'A future-scheduled post never appears before its publish date, even once approved.',
            'Only School Admin roles can submit; comments, likes, bookmarks, and the report action are open to any authenticated viewer.',
            'A reported comment appears in the Super Admin moderation queue.',
        ],
    },
    {
        'name': '11. School Network',
        'purpose': 'A directory of every member school, for collaboration discovery.',
        'roles': 'Super Admin, School Admin, Teacher (all view-only except own school).',
        'workflow': [
            'Browse school cards: name, location, state/country, curriculum/board, learner count, specialties.',
            'Own school links to its profile.',
            'Other schools show a "Contact via Yarra Coordinator" action for School Admin roles only, or a locked placeholder for everyone else.',
        ],
        'stories': [
            'As a Teacher, I want to browse the network for collaboration ideas, even though I can\'t contact schools directly.',
            'As a School Admin, I want to reach out to another school\'s Yarra Coordinator directly from their card.',
        ],
        'acceptance': [
            'The Contact action only renders for School Admin / School Leader roles.',
        ],
    },
    {
        'name': '12. Vendor Sign-up',
        'purpose': 'Let prospective vendors apply to join the marketplace, with no Yarra account required first.',
        'roles': 'Vendor applicant (public -- no login required). Super Admin (approves).',
        'workflow': [
            'A "Sign up as a Vendor" link on the public login page opens Vendor Sign-up, reachable without an existing account.',
            'Submit name, category, description, contact details, website, logo, brochure, and catalog.',
            'The application saves as unapproved.',
            'Super Admin approves via Django Admin, which unlocks marketplace visibility.',
        ],
        'stories': [
            'As a vendor, I want to sign up without first needing a Yarra login I have no way of getting.',
            'As a vendor, I want to submit our brochure and catalog alongside our profile so schools can properly evaluate us.',
        ],
        'acceptance': [
            'Unapproved vendors never appear in the public marketplace listing.',
            'The sign-up page works for both a signed-out visitor and an already logged-in user.',
        ],
    },
    {
        'name': '13. Vendor Marketplace',
        'purpose': 'Let schools discover approved vendors and send enquiries; let vendors run promotional campaigns.',
        'roles': 'Super Admin (approve vendors/promotions). School Admin & Teacher (browse, enquire).',
        'workflow': [
            'Browse/search/filter approved vendors by category.',
            'Open a vendor profile and send a subject + message enquiry.',
            'Track sent enquiries under My Requests, with an Open/Responded status.',
            'Super Admin separately approves promotional banners before they surface on the marketplace.',
        ],
        'stories': [
            'As a School Admin, I want to send a procurement enquiry and track whether the vendor has responded.',
            'As a Super Admin, I want to control which promotions actually surface.',
        ],
        'acceptance': [
            'Enquiries are scoped to the sender\'s own school under My Requests.',
        ],
    },
    {
        'name': '14. Vendor Event Interest',
        'purpose': 'Let approved vendors flag interest in supporting a specific Yarra event.',
        'roles': 'Vendor (any logged-in user acting for an approved vendor). Super Admin (notified).',
        'workflow': [
            'From an event\'s page, choose an approved vendor and submit an interest message.',
            'Every Super Admin is notified immediately.',
        ],
        'stories': [
            'As a vendor, I want to apply to be part of an upcoming Yarra event and know the Super Admin will see it.',
        ],
        'acceptance': [
            'Only approved vendors are selectable in the form.',
        ],
    },
    {
        'name': '15. School Review',
        'purpose': 'Track a school\'s self-study, review visit, School Improvement Plan, and recommendations cycle.',
        'roles': 'School Leader, Admin (edit). All staff (view). Yarra Evaluator (view Self Study + ask questions, see Module 20).',
        'workflow': [
            'Create a review cycle.',
            'Update status, dates, and a supporting document for each of the four stages.',
            'School Leader/Admin fills out the full Yarra School Self-Evaluation Record in-app (see Module 21) -- not available to Teachers.',
            'Any open Yarra Evaluator questions about the Self Study Questionnaire appear on this page for School Leader/Admin to answer.',
            'Browse previously archived cycles.',
        ],
        'stories': [
            'As a School Leader, I want to log our self-study progress and attach the supporting document.',
            'As a School Admin, I want to see and answer a Yarra Evaluator\'s question right here, without a separate email thread.',
        ],
        'acceptance': [
            'Only the active cycle is editable; archived cycles are read-only.',
        ],
    },
    {
        'name': '16. Leadership Connect',
        'purpose': 'A private discussion forum for School Leaders and Admins across the consortium.',
        'roles': 'School Leader / Admin only.',
        'workflow': [
            'Start a thread.',
            'Other leaders reply.',
            'The thread creator can lock it with a summary of key takeaways.',
        ],
        'stories': [
            'As a School Leader, I want to discuss policy questions with peers at other schools.',
        ],
        'acceptance': [
            'Teachers and students cannot open this module.',
        ],
    },
    {
        'name': '17. Notifications & Activity Log',
        'purpose': 'Keep every role aware of state changes relevant to them, and give Super Admin visibility into all platform activity.',
        'roles': 'All (own notifications). Super Admin (sees an activity feed of everyone\'s actions).',
        'workflow': [
            'A badge shows the unread count; opening a notification marks it read and deep-links to the relevant record.',
            'Nearly every state-changing action -- invites, payments, event registration, exchange applications, content submission, vendor enquiries -- also writes an Activity Log entry, visible on the User Management page.',
        ],
        'stories': [
            'As a Super Admin, I want any activity on the app to trigger a notification that lands here.',
        ],
        'acceptance': [
            'Notifications never grant access beyond what the recipient\'s role already has.',
        ],
    },
    {
        'name': '18. Consortium Analytics Dashboard',
        'purpose': 'A secondary, consortium-wide metrics view -- schools, students, teachers, events, exchanges, vendors, and a school engagement ranking.',
        'roles': 'Super Admin / Admin.',
        'workflow': [
            'Open the dashboard directly at /analytics/dashboard/.',
        ],
        'stories': [
            'As a Super Admin, I want to rank schools by engagement across registrations, enquiries, and exchange listings.',
        ],
        'acceptance': [
            'Note: this module is currently reachable only by direct URL -- it is not yet linked from the sidebar navigation.',
        ],
    },
    {
        'name': '19. Role Preview (Super Admin Testing Tool)',
        'purpose': 'Let the Super Admin click through the app exactly as another role sees it, for testing and support -- without a second login.',
        'roles': 'Super Admin only.',
        'workflow': [
            'A "Preview as role" dropdown in the top bar (visible only to a real Super Admin, or someone already mid-preview) lists School Leader, Admin, and Teacher.',
            'Selecting a role logs the Super Admin in as a representative account of that role.',
            'A persistent banner shows who is being previewed, with a one-click "Return to Super Admin".',
        ],
        'stories': [
            'As a Super Admin, I want to preview the app as a Teacher so I can verify a module works correctly for that role, or help a school troubleshoot.',
        ],
        'acceptance': [
            'Only a real Super Admin can start a preview; an ordinary user has no way to trigger it, even by guessing the URL.',
            'Vendor and Yarra Evaluator aren\'t in the list -- neither is a school-scoped Profile role, so there\'s no representative account to preview as.',
            'There is no student self-service login, so Student was removed from the previewable roles.',
        ],
    },
    {
        'name': '20. Yarra Evaluator & Self Study Q&A',
        'purpose': 'Give Yarra a cross-school reviewer role that can read Self Study Questionnaires and ask schools follow-up questions.',
        'roles': 'Yarra Evaluator (view + ask). School Leader / Admin (answer).',
        'workflow': [
            'Super Admin provisions a Yarra Evaluator account via Django Admin -- it is not a school-scoped Profile role, so it is created separately from the usual invite flow.',
            'The Evaluator opens their dashboard and sees every school\'s latest review cycle and Self Study status.',
            'Opening a school shows its Self Study Questionnaire document and a form to ask a question.',
            'Submitting a question notifies that school\'s Leader/Admin and creates an entry they can see on School Review.',
            'The school answers with text and/or an attached document; the Evaluator is notified and sees the answer on the same page.',
        ],
        'stories': [
            'As a Yarra Evaluator, I want to review a school\'s Self Study Questionnaire without waiting for it to be emailed to me.',
            'As a Yarra Evaluator, I want to ask a clarifying question and know the right person at the school will see it.',
            'As a School Admin, I want to answer an Evaluator\'s question in the same place I manage our review cycle.',
        ],
        'acceptance': [
            'Only a user with a Yarra Evaluator account can access this area; it is not reachable via the normal school-scoped nav.',
            'A question always notifies the school\'s Leader/Admin, never a broader audience.',
        ],
    },
    {
        'name': '21. Yarra School Self-Evaluation Record',
        'purpose': 'Reproduce Ms Chelli\'s official Self-Evaluation Record in-app -- ~170 questions across School Profile & Data, Institutional Capability Review (5 capability areas), Supporting Evidence, and School Priorities -- so a school\'s answers are visible to their Yarra Evaluator without a separate document.',
        'roles': 'School Leader, Admin (fill out). Yarra Evaluator (view, read-only). Not available to Teachers.',
        'workflow': [
            'Open Self-Evaluation Record from the School Review page.',
            'Answer questions grouped by Part -> Section -> Sub-area, matching the original form exactly: short answer, paragraph, single/multi-choice, 1-4 ratings, and evidence file uploads.',
            'Save at any time -- partial progress is kept and the form reopens pre-filled.',
            'The Yarra Evaluator sees the same record read-only (with any uploaded evidence files) from their school view.',
        ],
        'stories': [
            'As a School Admin, I want to fill out our Self-Evaluation Record over several sessions without losing progress.',
            'As a Yarra Evaluator, I want to see a school\'s full self-evaluation answers and evidence in one place.',
        ],
        'acceptance': [
            'Teachers cannot open this page even by URL -- only School Leader/Admin.',
            'The question set lives in one file (tenants/self_evaluation.py) so it can be updated without touching the view or template.',
        ],
    },
]

LIFECYCLES = [
    {
        'name': 'School Onboarding',
        'steps': [
            'Super Admin creates the school with basic data',
            'Invitation sent to the Yarra Coordinator email',
            'Coordinator accepts and sets a password (email locked to invite)',
            '"Complete Your Profile" banner shown',
            'Extended profile + documents submitted',
            'profile_completed flag set to True',
        ],
    },
    {
        'name': 'Event Management',
        'steps': [
            'Super Admin creates the event',
            'Every school views it; School Admin/Teacher registers participants by name (+ pay)',
            'Staff mark attendance and log results for their own school\'s participants',
            'Once a participant is marked attended, staff can download their certificate; staff can export the attendee list as CSV',
            'Recording link, presentation, and photo gallery attached post-event',
            '(Optional) Super Admin deletes -- registrations and results cascade-delete',
        ],
    },
    {
        'name': 'Exchange Program',
        'steps': [
            'Listing posted -- Open',
            'Application submitted -- Pending',
            'Owner reviews -- Under Review',
            'Owner approves -- Approved, listing becomes Matched, other applications auto-Rejected',
            'Exchange runs, then marked Completed',
            'Both sides submit rating + comments',
        ],
    },
    {
        'name': 'Content Publishing',
        'steps': [
            'School Admin submits post (optionally with a future publish date)',
            'Saved as Pending Yarra Verification',
            'Super Admin reviews',
            'Approved -> Published, but stays hidden until its publish date OR Rejected -> back to Draft, submitter notified',
            'Once visible: viewers can bookmark it, see related items, and like/report comments',
        ],
    },
    {
        'name': 'Vendor Approval',
        'steps': [
            'Vendor submits sign-up (with brochure/catalog)',
            'Status: unapproved',
            'Super Admin reviews via Django Admin',
            'Approved -- vendor appears in the marketplace and can receive/apply to event interest',
        ],
    },
    {
        'name': 'Payment (Event Registration)',
        'steps': [
            'School Admin/Teacher registers a participant for a paid event',
            'Razorpay order created (if configured) or manual proof uploaded',
            'Payment verified or failed',
            'Invoice PDF downloadable once verified',
        ],
    },
    {
        'name': 'Yarra Evaluator Q&A',
        'steps': [
            'Super Admin provisions a Yarra Evaluator account via Django Admin',
            'Evaluator opens a school\'s Self Study Questionnaire from the Evaluator dashboard',
            'Evaluator asks a question -- the school\'s Leader/Admin is notified',
            'School answers with text and/or an attached document, from the School Review page',
            'Evaluator is notified and sees the answer on the same page',
        ],
    },
]

CHECKLIST = [
    'Confirm each new school\'s Yarra Coordinator email is correct before sending the invite -- their login is permanently locked to it.',
    'Enforce the 2-admin / 5-teacher caps by removing an inactive user before approving a new invite past the limit.',
    'Review the Content Review queue regularly so submissions don\'t sit pending indefinitely; check for reported comments there too.',
    'Approve vendors via Django Admin before they can appear in the marketplace or receive event-interest applications.',
    'Delete an event only when certain -- it permanently removes every registration and result tied to it.',
    'Schedule check_membership_expiry to run daily (e.g. PythonAnywhere Tasks tab) so renewal reminders and auto-suspension actually fire.',
    'Use Broadcast Announcement sparingly -- it notifies every matching user immediately, with no undo.',
    'Provision Yarra Evaluator accounts via Django Admin only -- there is no self-signup or invite flow for this role.',
    'Regenerate this PDF after major module changes by running python scripts/generate_user_manual.py.',
]


# ---------------------------------------------------------------------------
# PDF assembly
# ---------------------------------------------------------------------------

def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PATH, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
        title='Yarra Consortium User Manual',
    )
    story = []

    # --- Cover page ---
    if os.path.exists(LOGO_PATH):
        story.append(Spacer(1, 3 * cm))
        img = Image(LOGO_PATH, width=8 * cm, height=8 * cm * (410 / 1280))
        img.hAlign = 'CENTER'
        story.append(img)
        story.append(Spacer(1, 1.5 * cm))
    else:
        story.append(Spacer(1, 6 * cm))

    story.append(Paragraph('Yarra Consortium User Manual', styles['Cover']))
    story.append(Paragraph('Role-based operating guide, generated from the live application', styles['CoverSub']))
    story.append(Paragraph('Covers every module as currently implemented, for Super Admins, School Admins, Teachers, Yarra Evaluators, and Vendors.', styles['CoverSub']))
    story.append(Spacer(1, 1 * cm))
    story.append(Paragraph('Regenerate with: python scripts/generate_user_manual.py', styles['Muted']))
    story.append(PageBreak())

    # --- Table of contents ---
    story.append(Paragraph('Table of Contents', styles['H1']))
    toc_entries = [
        '1. Role Access Matrix',
        '2. Role-Based User Stories',
        '3. Module Manuals',
        '4. Key Operating Lifecycles',
        '5. Administration Checklist',
    ]
    for entry in toc_entries:
        story.append(Paragraph(entry, styles['TOC']))
    story.append(PageBreak())

    # --- Role Access Matrix ---
    story.append(Paragraph('1. Role Access Matrix', styles['H1']))
    table_data = [[Paragraph(f'<b>{cell}</b>' if r == 0 else cell, styles['Body']) for cell in row] for r, row in enumerate(ROLE_MATRIX)]
    col_widths = [4.2 * cm, 2.9 * cm, 3.2 * cm, 2.4 * cm, 1.8 * cm, 2.2 * cm]
    t = Table(table_data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_DARK),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(PageBreak())

    # --- Role-based user stories ---
    story.append(Paragraph('2. Role-Based User Stories', styles['H1']))
    for role in ROLES:
        story.append(Paragraph(role, styles['H2']))
        items = [ListItem(Paragraph(s, styles['BulletBody']), leftIndent=8) for s in ROLE_STORIES[role]]
        story.append(ListFlowable(items, bulletType='bullet', start='circle'))
    story.append(PageBreak())

    # --- Module manuals ---
    story.append(Paragraph('3. Module Manuals', styles['H1']))
    for i, m in enumerate(MODULES):
        story.append(Paragraph(m['name'], styles['H2']))
        story.append(Paragraph(f"<b>Purpose:</b> {m['purpose']}", styles['Body']))
        story.append(Paragraph(f"<b>Roles:</b> {m['roles']}", styles['Body']))
        story.append(Spacer(1, 4))
        story.append(Paragraph('Workflow', styles['H3']))
        wf_items = [ListItem(Paragraph(step, styles['BulletBody']), leftIndent=8, value=n + 1) for n, step in enumerate(m['workflow'])]
        story.append(ListFlowable(wf_items, bulletType='1'))
        story.append(Paragraph('User Stories', styles['H3']))
        st_items = [ListItem(Paragraph(s, styles['BulletBody']), leftIndent=8) for s in m['stories']]
        story.append(ListFlowable(st_items, bulletType='bullet', start='circle'))
        story.append(Paragraph('Acceptance Expectations', styles['H3']))
        ac_items = [ListItem(Paragraph(a, styles['BulletBody']), leftIndent=8) for a in m['acceptance']]
        story.append(ListFlowable(ac_items, bulletType='bullet', start='circle'))
        if i < len(MODULES) - 1:
            story.append(Spacer(1, 10))
    story.append(PageBreak())

    # --- Lifecycles ---
    story.append(Paragraph('4. Key Operating Lifecycles', styles['H1']))
    for lc in LIFECYCLES:
        story.append(Paragraph(lc['name'], styles['H2']))
        items = [ListItem(Paragraph(step, styles['BulletBody']), leftIndent=8, value=n + 1) for n, step in enumerate(lc['steps'])]
        story.append(ListFlowable(items, bulletType='1'))
    story.append(PageBreak())

    # --- Administration checklist ---
    story.append(Paragraph('5. Administration Checklist', styles['H1']))
    items = [ListItem(Paragraph(c, styles['BulletBody']), leftIndent=8) for c in CHECKLIST]
    story.append(ListFlowable(items, bulletType='bullet', start='circle'))

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(2 * cm, 1.3 * cm, 'Yarra Consortium User Manual')
        canvas.drawRightString(A4[0] - 2 * cm, 1.3 * cm, f'Page {doc_.page}')
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


if __name__ == '__main__':
    build_pdf()
    print(f'Generated {OUTPUT_PATH}')
