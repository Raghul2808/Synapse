from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables' / 'Synapse_Research_Paper.pdf'
FONT_DIR = Path('/usr/share/fonts/noto')
pdfmetrics.registerFont(TTFont('DejaVu', str(FONT_DIR / 'NotoSerif-Regular.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuBold', str(FONT_DIR / 'NotoSerif-Bold.ttf')))
pdfmetrics.registerFont(TTFont('DejaVuItalic', str(FONT_DIR / 'NotoSerif-Italic.ttf')))
pdfmetrics.registerFont(TTFont('NotoMath', str(FONT_DIR / 'NotoSansMath-Regular.ttf')))

def esc(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def page_decor(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setStrokeColor(colors.HexColor('#777777'))
    canvas.setLineWidth(0.45)
    canvas.rect(0.38*inch, 0.38*inch, w-0.76*inch, h-0.76*inch)
    canvas.setFont('DejaVu', 8)
    canvas.setFillColor(colors.HexColor('#444444'))
    canvas.drawString(0.70*inch, h-0.53*inch, 'Synapse: Constraint-Based Hackathon Matchmaking')
    canvas.drawRightString(w-0.70*inch, 0.54*inch, str(doc.page))
    canvas.restoreState()

styles = getSampleStyleSheet()
title = ParagraphStyle('TitlePaper', parent=styles['Title'], fontName='DejaVuBold', fontSize=16, leading=20, alignment=TA_CENTER, spaceAfter=8)
authors = ParagraphStyle('Authors', parent=styles['Normal'], fontName='DejaVu', fontSize=10, leading=13, alignment=TA_CENTER, spaceAfter=9)
abstract_label = ParagraphStyle('AbsLabel', parent=styles['Normal'], fontName='DejaVuBold', fontSize=10, leading=12, alignment=TA_LEFT, spaceAfter=2)
body = ParagraphStyle('BodyPaper', parent=styles['Normal'], fontName='DejaVu', fontSize=9.25, leading=13.0, alignment=TA_JUSTIFY, spaceAfter=6)
section = ParagraphStyle('Section', parent=styles['Heading2'], fontName='DejaVuBold', fontSize=11.2, leading=14, spaceBefore=7, spaceAfter=4)
subsection = ParagraphStyle('Subsection', parent=styles['Heading3'], fontName='DejaVuBold', fontSize=9.8, leading=12, spaceBefore=5, spaceAfter=2)
equation = ParagraphStyle('Equation', parent=body, fontName='NotoMath', fontSize=10, leading=14, alignment=TA_CENTER, spaceBefore=2, spaceAfter=5)
small = ParagraphStyle('Small', parent=body, fontSize=8.1, leading=10.2, spaceAfter=3)

def P(text, style=body):
    return Paragraph(esc(text), style)

def H(text, level=2):
    return Paragraph(esc(text), section if level == 2 else subsection)

def Eq(text):
    return Paragraph(esc(text), equation)

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=0.72*inch, leftMargin=0.72*inch, topMargin=0.78*inch, bottomMargin=0.72*inch)
    story=[]
    story += [Paragraph('Synapse: A Constraint-Based Matchmaking Platform for Hackathon Team Formation', title),
              Paragraph('Raghul M and Rithesh Madhav S<br/>Rajalakshmi Engineering College', authors),
              Paragraph('Abstract', abstract_label),
              P('Hackathon team formation is commonly supported by free-text directories in which participants describe skills, roles, experience, and preferences through unconstrained language. Equivalent concepts may be entered inconsistently, increasing normalization cost, lowering match precision, and forcing manual comparison. This design paper specifies Synapse, a constraint-based matchmaking platform that models human-capital allocation as a Constraint Satisfaction Problem. Critical matching attributes are represented through finite database domains, including enumerated project roles and experience levels, while technology stacks are retained as structured sets. A two-phase pipeline is proposed. Hard constraints first eliminate infeasible candidates through role parity, minimum experience, availability, and environment compatibility. Feasible candidates are then ranked through Jaccard technology-stack similarity and weighted contextual preferences. The architecture combines Next.js 14 App Router, React Server Components, PostgreSQL through Supabase and PgBouncer, Prisma ORM, NextAuth.js v5, and Vercel serverless deployment. The design supports constant-time categorical verification, linear candidate filtration, and explainable match decisions. This paper presents the specified system architecture and algorithmic model; it distinguishes the proposed CSP engine from any separate implementation-verification exercise.'),
              H('1. Introduction'),
              P('Hackathons impose an unusual team-formation problem. Participants must identify complementary abilities, assess constraints, and organize collaboration within a limited time window. Conventional directories provide profile lists, but a free-text representation does not establish a stable computational basis for matching. A user may describe a frontend capability as React, ReactJS, React.js, UI development, or web engineering. Similar ambiguity occurs for roles, experience, location, event mode, and technology preferences.'),
              P('If N profiles are repeatedly compared through unnormalized text attributes, manual or pairwise comparison can approach O(N^2) work. Synapse instead defines a finite candidate domain and evaluates explicit predicates. The resulting design separates feasibility from desirability: a candidate must first satisfy absolute constraints, then may be ranked among feasible alternatives.'),
              H('2. Contributions'),
              P('The proposed system contributes: (i) finite-domain modeling for roles and experience, (ii) deterministic hard-constraint filtering, (iii) Jaccard-based technology scoring, (iv) environment-aware ranking, and (v) a serverless, type-safe architecture that supports explainable decisions.')]
    story.append(PageBreak())
    story += [H('3. System Architecture'),
              P('Synapse follows a decoupled full-stack topology. Next.js 14 supplies App Router routing, layouts, React Server Components, and trusted route handlers. Interactive controls such as filters and forms are implemented as client components, while data retrieval and protected matching operations are placed in server-side contexts. Prisma constructs type-safe relational queries. Supabase provides PostgreSQL persistence, and PgBouncer on port 6543 pools database connections for short-lived Vercel functions.'),
              Eq('Browser → Next.js Route or Server Action → Session Verification → Prisma → PgBouncer:6543 → Supabase PostgreSQL'),
              P('Vercel distributes static assets through its edge network and executes dynamic application logic in serverless functions. This separation avoids exposing database credentials to browser clients and permits authentication checks before profile, application, favorite, and team-requirement mutations are executed.'),
              H('4. Data Modeling and Finite Domains'),
              P('Algorithmic matching requires comparable data. A finite domain prevents semantically equivalent values from being treated as unrelated text. ProjectRole may include FRONTEND_ENGINEER, BACKEND_ENGINEER, FULL_STACK_ENGINEER, AI_ML_ENGINEER, UI_UX_DESIGNER, DEVOPS_ENGINEER, BLOCKCHAIN_ENGINEER, and PRODUCT_MANAGER. ExperienceLevel may include BEGINNER, INTERMEDIATE, ADVANCED, and EXPERT.'),
              P('Let the experience domain be E = {BEGINNER, INTERMEDIATE, ADVANCED, EXPERT}. An ordinal mapping phi assigns the values 1 through 4. The required experience predicate is therefore evaluated without natural-language interpretation.'),
              Eq('ExperienceMatch(u,t) = 1 if φ(u.experience) ≥ φ(t.requiredExperience); otherwise 0'),
              P('The central entities are User, TeamRequirement, Application, Skill, Favorite, Account, and Session. A User may own team requirements and applications. An Application connects one candidate with one requirement, and a uniqueness rule UNIQUE(candidateId, teamRequirementId) prevents duplicate applications. A TeamRequirement stores the required role, experience floor, structured technology set, event mode, location, availability information, and open positions.'),
              H('5. Security and Implementation'),
              P('NextAuth.js v5 enforces zero-trust access using server-validated sessions and OAuth 2.0 providers. A JWT represents authenticated state, but authorization for sensitive operations must be derived from the verified server session rather than from a client-submitted user identifier. This boundary is essential for profile mutation, application creation, and favorite management. Deployment must use locked dependencies, generated Prisma artifacts, verified environment variables, and a PgBouncer-compatible database URL.')]
    story.append(PageBreak())
    story += [H('6. Matchmaking Algorithm as a CSP'),
              P('A Constraint Satisfaction Problem is represented as P = (X, D, C), where X denotes variables, D denotes finite domains, and C denotes constraints. For an open team position, the candidate variable x is selected from the domain of user profiles. Each candidate is evaluated against role, experience, availability, and environmental constraints.'),
              Eq('F = {u ∈ U | C_role(u,t) ∧ C_experience(u,t) ∧ C_environment(u,t) ∧ C_availability(u,t)}'),
              H('6.1 Phase 1: Hard Constraints', 3),
              P('Hard constraints are non-negotiable. Role parity is evaluated by direct enum equality. Experience compatibility is evaluated through the ordered finite experience domain. A candidate failing any predicate is excluded before similarity ranking occurs.'),
              Eq('C_role(u,t) = 1 if u.role = t.requiredRole; otherwise 0'),
              Eq('H(u,t) = C_role(u,t) · C_experience(u,t) · C_environment(u,t) · C_availability(u,t)'),
              P('Each candidate is evaluated once. Since role and experience checks are constant-time predicates, full hard filtering across N candidate profiles is O(N). The procedure is deterministic: identical data and constraints produce the same feasible set. A rejection can be explained through an explicit failed predicate rather than an opaque score.'),
              H('6.2 Phase 2: Soft Constraints', 3),
              P('Feasible candidates are ranked using structured technology stacks. Let S_u denote a candidate stack and S_t the required stack. Jaccard similarity rewards overlap while penalizing excess unrelated technologies only through the union term.'),
              Eq('J(S_u,S_t) = |S_u ∩ S_t| / |S_u ∪ S_t|'),
              P('Event mode and location may be represented by an environment weight. For online events, remote compatibility is assigned full weight. For offline events, a candidate must satisfy a location requirement. Hybrid events may permit remote participation when explicitly authorized.'),
              Eq('Score(u,t) = αJ(S_u,S_t) + βW_environment(u,t) + γW_availability(u,t) + δW_preference(u,t)'),
              P('The parameters satisfy α + β + γ + δ = 1. Technology overlap may receive the highest weight, while environmental compatibility, schedule compatibility, and optional preferences refine the ranking. If K candidates survive hard filtering and m is the bounded average stack size, scoring is O(K·m) and ordering is O(K log K).')]
    story.append(PageBreak())
    story += [H('7. Discussion'),
              P('Finite domains reduce ambiguity and permit O(1) categorical verification. The complete hard-filter pass remains O(N), avoiding unnecessary comparison of users who cannot satisfy mandatory requirements. The two-phase pipeline preserves an important distinction: high technology similarity cannot compensate for a missing mandatory role or insufficient experience. This improves transparency for both organizers and candidates.'),
              P('The model has limitations. Enumerations improve consistency but can be rigid when new specializations emerge. Controlled schema migrations are required to introduce new roles without creating uncontrolled synonyms. Jaccard similarity also treats skills uniformly unless domain-specific weights are introduced. Finally, self-reported skills do not constitute independently verified competence.'),
              H('8. Conclusion and Future Work'),
              P('Synapse specifies an explainable foundation for hackathon matchmaking through finite-domain data modeling, deterministic eligibility filtering, and heuristic ranking. Enumerated roles and experience levels turn ambiguous input into comparable state, while Jaccard similarity ranks feasible candidates by technology overlap. The proposed architecture combines Next.js, React Server Components, Supabase PostgreSQL, PgBouncer, Prisma, NextAuth.js, and Vercel to support secure, scalable execution.'),
              P('Future work should introduce natural-language classification during onboarding, with user confirmation before a free-text description is mapped to a finite role or skill category. GitHub API integration may provide live public metrics such as repository activity, language distributions, and project history. The next algorithmic extension is multi-member combinatorial optimization, in which a team is selected jointly to maximize role coverage, skill diversity, availability overlap, and contextual compatibility under explicit constraints.'),
              H('References'),
              P('[1] R. Dechter, Constraint Processing. Morgan Kaufmann, 2003.', small),
              P('[2] T. Lappas, K. Liu, and E. Terzi, “Finding a team of experts in social networks,” Proceedings of KDD, 2009.', small),
              P('[3] Next.js, “Next.js 14 App Router Documentation,” 2024.', small),
              P('[4] Prisma, “PostgreSQL Database Connector Documentation,” 2026.', small),
              P('[5] Auth.js, “NextAuth.js Documentation,” 2026.', small)]
    doc.build(story, onFirstPage=page_decor, onLaterPages=page_decor)
    print(OUT)

if __name__ == '__main__':
    main()
