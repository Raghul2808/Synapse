from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    FrameBreak, NextPageTemplate, KeepTogether, Flowable,
)

ROOT = Path('/home/fykern/WebstormProjects/DevMatchups')
OUT = ROOT / 'deliverables' / 'Synapse_IEEE_Conference_Paper.pdf'
FONT_DIR = Path('/usr/share/fonts/liberation')
MATH_FONT = Path('/usr/share/fonts/noto/NotoSansMath-Regular.ttf')
pdfmetrics.registerFont(TTFont('TNR', str(FONT_DIR / 'LiberationSerif-Regular.ttf')))
pdfmetrics.registerFont(TTFont('TNRB', str(FONT_DIR / 'LiberationSerif-Bold.ttf')))
pdfmetrics.registerFont(TTFont('TNRI', str(FONT_DIR / 'LiberationSerif-Italic.ttf')))
pdfmetrics.registerFont(TTFont('TNRBI', str(FONT_DIR / 'LiberationSerif-BoldItalic.ttf')))
pdfmetrics.registerFont(TTFont('Math', str(MATH_FONT)))

PAGE_W, PAGE_H = A4
MARGIN_X = 0.68 * inch
MARGIN_Y = 0.62 * inch
GAP = 0.25 * inch
CONTENT_W = PAGE_W - 2 * MARGIN_X
COL_W = (CONTENT_W - GAP) / 2

styles = getSampleStyleSheet()
body = ParagraphStyle('Body', parent=styles['BodyText'], fontName='TNR', fontSize=8.45,
    leading=9.95, alignment=TA_JUSTIFY, firstLineIndent=0.17*inch, spaceAfter=3.25)
body0 = ParagraphStyle('Body0', parent=body, firstLineIndent=0, spaceAfter=4.1)
abstract = ParagraphStyle('Abstract', parent=body, fontSize=8.6, leading=10.05,
    firstLineIndent=0, spaceAfter=4.4)
keywords = ParagraphStyle('Keywords', parent=abstract, fontName='TNRI', spaceAfter=5.1)
title = ParagraphStyle('Title', parent=styles['Title'], fontName='TNR', fontSize=20.5,
    leading=23, alignment=TA_CENTER, spaceAfter=8)
author = ParagraphStyle('Author', parent=styles['Normal'], fontName='TNR', fontSize=10.0,
    leading=11.25, alignment=TA_CENTER)
section = ParagraphStyle('Section', parent=styles['Heading1'], fontName='TNR', fontSize=10,
    leading=11.3, alignment=TA_CENTER, spaceBefore=5.3, spaceAfter=3.5)
subsection = ParagraphStyle('Subsection', parent=styles['Heading2'], fontName='TNRI', fontSize=9.25,
    leading=10.5, alignment=TA_LEFT, spaceBefore=3.8, spaceAfter=2.0)
caption = ParagraphStyle('Caption', parent=styles['Normal'], fontName='TNR', fontSize=7.6,
    leading=8.7, alignment=TA_LEFT, spaceBefore=2, spaceAfter=5)
tablehead = ParagraphStyle('TableHead', parent=caption, fontName='TNR', fontSize=7.6,
    leading=8.7, alignment=TA_CENTER, spaceBefore=5.5, spaceAfter=2)
reference = ParagraphStyle('References', parent=styles['Normal'], fontName='TNR', fontSize=7.4,
    leading=8.25, alignment=TA_JUSTIFY, leftIndent=0.18*inch, firstLineIndent=-0.18*inch, spaceAfter=1.5)
equation_style = ParagraphStyle('Equation', parent=styles['Normal'], fontName='TNR', fontSize=9.1,
    leading=11, alignment=TA_CENTER)

def P(text, style=body):
    return Paragraph(escape(text), style)

def R(text):
    return Paragraph(escape(text), reference)

class FigurePlaceholder(Flowable):
    def __init__(self, width, height, label):
        super().__init__()
        self.width, self.height, self.label = width, height, label
    def wrap(self, availW, availH):
        return self.width, self.height
    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(colors.black)
        c.setLineWidth(0.55)
        c.rect(0, 0, self.width, self.height)
        c.setFont('TNR', 7.8)
        lines = self.label.split('\n')
        y = self.height / 2 + (len(lines)-1) * 4.5
        for line in lines:
            c.drawCentredString(self.width/2, y, line)
            y -= 10
        c.restoreState()

class Equation(Flowable):
    def __init__(self, equation, n):
        super().__init__()
        self.equation = equation
        self.n = n
        self.width = COL_W
        self.height = 20
    def wrap(self, availW, availH):
        self.width = availW
        return availW, self.height
    def draw(self):
        c = self.canv
        c.saveState()
        c.setFont('Math', 9.2)
        c.drawCentredString(self.width/2, 6.5, self.equation)
        c.drawRightString(self.width, 6.5, f'({self.n})')
        c.restoreState()

def heading(roman, text):
    return Paragraph(f'{roman}. {escape(text.upper())}', section)

def sub(letter, text):
    return Paragraph(f'{letter}. {escape(text)}', subsection)

def author_cell(name, email):
    lines = [
        name,
        'Department of Computer Science and Engineering',
        'Rajalakshmi Engineering College',
        'Chennai, Tamil Nadu, India',
        email,
    ]
    return Paragraph('<br/>'.join(escape(x) for x in lines), author)

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setTitle('Synapse Constraint Based Hackathon Matchmaking')
    canvas.setAuthor('Raghul M; Rithesh Madhav S')
    canvas.setSubject('IEEE Conference Paper')
    canvas.restoreState()

def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(OUT), pagesize=A4, leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_Y, bottomMargin=MARGIN_Y, title='Synapse Constraint Based Hackathon Matchmaking')
    first_header_h = 270
    col_h_first = PAGE_H - MARGIN_Y - (MARGIN_Y + first_header_h + 7)
    first_frames = [
        Frame(MARGIN_X, PAGE_H - MARGIN_Y - first_header_h, CONTENT_W, first_header_h,
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id='first_header'),
        Frame(MARGIN_X, MARGIN_Y, COL_W, col_h_first,
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id='first_left'),
        Frame(MARGIN_X + COL_W + GAP, MARGIN_Y, COL_W, col_h_first,
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id='first_right'),
    ]
    later_h = PAGE_H - 2*MARGIN_Y
    later_frames = [
        Frame(MARGIN_X, MARGIN_Y, COL_W, later_h,
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id='later_left'),
        Frame(MARGIN_X + COL_W + GAP, MARGIN_Y, COL_W, later_h,
              leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id='later_right'),
    ]
    doc.addPageTemplates([
        PageTemplate(id='First', frames=first_frames, onPage=on_page),
        PageTemplate(id='Later', frames=later_frames, onPage=on_page),
    ])

    story = []
    story += [
        P('Synapse Constraint Based Matchmaking for Hackathon Team Formation', title),
        Table([[author_cell('Raghul M', 'raghul.m.2024.cse@rajalakshmi.edu.in'),
                author_cell('Rithesh Madhav S', 'rithesh.m.2024.cse@rajalakshmi.edu.in')]],
              colWidths=[CONTENT_W/2, CONTENT_W/2], style=TableStyle([
                  ('VALIGN',(0,0),(-1,-1),'TOP'), ('LEFTPADDING',(0,0),(-1,-1),0),
                  ('RIGHTPADDING',(0,0),(-1,-1),0), ('TOPPADDING',(0,0),(-1,-1),0),
                  ('BOTTOMPADDING',(0,0),(-1,-1),0),
              ])),
        Spacer(1, 7),
        Paragraph('<b><i>Abstract—</i></b>' + escape(
            'Hackathon platforms frequently expose participant profiles as free-text directories. '
            'Equivalent technical capabilities can therefore be represented by incompatible strings, '
            'which increases normalization effort and weakens the precision of team formation. This '
            'paper presents Synapse, a constraint-based matchmaking architecture that treats candidate '
            'selection as a Constraint Satisfaction Problem. The design uses finite database domains for '
            'project roles and experience levels, followed by a two-phase decision pipeline. First, role '
            'parity, experience floor, availability, and event compatibility are evaluated as deterministic '
            'hard constraints. Second, the feasible candidates are ranked using Jaccard similarity over '
            'structured technology sets and weighted contextual preferences. The platform is organized as '
            'a Next.js application with React Server Components, Prisma, PostgreSQL through Supabase '
            'and PgBouncer, NextAuth.js version five, and Vercel serverless deployment. The resulting '
            'model offers explainable rejection reasons, bounded categorical verification, and linear '
            'candidate filtering. The paper also identifies the limitations of rigid enumerations and '
            'outlines natural-language classification and GitHub-derived evidence as future extensions.'), abstract),
        Paragraph('<b><i>Keywords—</i></b>' + escape('constraint satisfaction, team formation, hackathons, finite domains, Jaccard similarity, Next.js, Prisma'), keywords),
        NextPageTemplate('Later'), FrameBreak(),
    ]

    story += [
        heading('I', 'Introduction'),
        P('Hackathons impose a short and highly constrained team-formation interval. Participants must identify complementary roles, compatible experience levels, and a practical collaboration context before the event begins. Conventional portals make this task a directory search problem: a participant enters an arbitrary description, reviews many profiles, and infers whether a candidate can fill a team requirement. Such a process is inconsistent because React, React.js, react, and frontend development may denote related capability while remaining distinct database values.'),
        P('The resulting ambiguity produces two costs. First, a system must repeatedly normalize or compare unbounded text representations. Second, users must perform manual pairwise screening, which can approach O(N^2) work when N profiles are repeatedly compared. Synapse reframes this activity as constrained allocation. It distinguishes feasibility from desirability: a candidate is admitted to the feasible set only when mandatory predicates hold, and is ranked only after that decision.'),
        P('The principal contributions are a finite-domain data model, a deterministic hard-constraint filter, a set-based soft ranking function, and a server-side architecture that retains matching decisions behind authenticated application boundaries. The work draws on constraint-processing principles [1] and team-formation research [2].'),

        heading('II', 'System Architecture'),
        sub('A', 'Decoupled Application Topology'),
        P('Synapse uses Next.js 14 as the application boundary. The App Router coordinates route segments and layouts, while React Server Components (RSCs) execute data-dependent rendering on the server. Client components are reserved for interactive filters, form controls, and stateful interface behavior. This separation keeps database credentials and matching predicates out of the browser while preserving a responsive search experience [3].'),
        P('Route handlers and server actions receive requests, verify session state, validate payloads, and invoke Prisma. Prisma translates typed application operations to PostgreSQL queries. In the intended hosted configuration, Supabase provides PostgreSQL persistence and PgBouncer supplies connection pooling on port 6543. The pooled URL is appropriate for short-lived serverless invocations, whereas administrative tasks use a direct connection when required.'),
        FigurePlaceholder(COL_W, 76, 'FIGURE PLACEHOLDER\nBrowser and Next.js request boundary\nAuthenticated route handler and Prisma\nPgBouncer port 6543 and PostgreSQL'),
        Paragraph('Fig. 1. Proposed Synapse deployment and data-access topology.', caption),
        sub('B', 'Serverless Execution Path'),
        P('Vercel distributes static assets through its edge network and invokes dynamic code in isolated serverless executions. A request flows from a browser to a protected Next.js route, then to session verification, Prisma, the pooled database connection, and the database. This path centralizes authorization and prevents the client from issuing privileged persistence operations directly.'),

        heading('III', 'Data Modeling and Finite Domains'),
        P('A finite domain makes a comparison meaningful before it is executed. The Prisma schema defines ProjectRole and ExperienceLevel as enumerations. The role domain includes FRONTEND, BACKEND, FULLSTACK, UI_UX_DESIGNER, DATA_SCIENTIST, AI_ML_ENGINEER, APP_DEVELOPER, and DEVOPS. The ordered experience domain contains BEGINNER, INTERMEDIATE, ADVANCED, and EXPERT. A user stores a primary role, experience level, technology-set array, and time-zone information; a hackathon requirement stores a required role, minimum experience, structured skill array, event mode, location, and open positions.'),
        Paragraph('TABLE I<br/>FINITE DOMAINS USED BY THE MATCHER', tablehead),
        Table([
            [P('Attribute', caption), P('Domain representation', caption), P('Decision use', caption)],
            [P('ProjectRole', caption), P('Closed enum', caption), P('Role parity', caption)],
            [P('ExperienceLevel', caption), P('Ordered enum', caption), P('Minimum floor', caption)],
            [P('Skills', caption), P('Structured set', caption), P('Jaccard ranking', caption)],
        ], colWidths=[0.82*inch, 1.08*inch, 1.05*inch], style=TableStyle([
            ('GRID',(0,0),(-1,-1),0.35,colors.black), ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E8E8E8')),
            ('LEFTPADDING',(0,0),(-1,-1),3), ('RIGHTPADDING',(0,0),(-1,-1),3),
            ('TOPPADDING',(0,0),(-1,-1),2), ('BOTTOMPADDING',(0,0),(-1,-1),2),
        ])),
        Spacer(1, 4),
        P('Enumerations prevent a value such as “AI/ML engineer” from silently becoming a distinct category from AI_ML_ENGINEER. They do not eliminate all semantic work: technology labels remain a structured but extensible set because the long tail of frameworks evolves more quickly than the core role taxonomy. A uniqueness constraint on candidate and post identifiers additionally prevents duplicate applications.'),

        heading('IV', 'The Matchmaking Algorithm'),
        sub('A', 'Constraint Satisfaction Formulation'),
        P('Let U be the set of candidate profiles and let t denote a team requirement. The matching state is expressed as P equals X, D, C, where X contains candidate variables, D contains their finite domains, and C contains the mandatory predicates. The hard-filtered feasible set is formed by role equality, an ordinal experience comparison, environment compatibility, and availability compatibility. Each predicate is evaluated once per candidate. With indexed retrieval and constant-time categorical checks, the scan is O(N).'),
        P('Role parity is evaluated as candidate role equals required role. Experience is mapped to the ordinal function phi, where phi(BEGINNER) is less than phi(INTERMEDIATE), phi(ADVANCED), and phi(EXPERT). A candidate is feasible only when phi(candidate experience) is greater than or equal to phi(required experience). This ordering turns a vague statement such as “senior enough” into a deterministic predicate and permits an explicit explanation when a candidate is excluded.'),
        sub('B', 'Soft Constraint Ranking'),
        P('For each feasible candidate, Synapse compares the candidate technology set A with the requirement set B. Jaccard similarity measures the shared portion of the union and returns a value in the closed interval from zero to one [7].'),
        Equation('J(A,B) = |A ∩ B| / |A ∪ B|,', 1),
        P('The score is then combined with environment, availability, and optional-preference weights. An online event receives full remote-environment credit. An offline event requires compatible location, and a hybrid event may permit remote participation only when explicitly enabled. The weights alpha, beta, gamma, and delta are nonnegative and sum to one.'),
        Equation('Score(u,t) = αJ(A,B) + βE(u,t) + γV(u,t) + δP(u,t).', 2),
        P('If K candidates remain after hard filtering and m is the bounded average technology-set size, the scoring stage is O(Km); ordering the result is O(K log K). The two-phase design prevents high technology overlap from compensating for a missing mandatory role or insufficient experience.'),

        heading('V', 'Implementation and Security'),
        P('Authentication is implemented with NextAuth.js version five and OAuth 2.0 providers. The application uses JSON Web Token sessions, but a token is treated as evidence of authenticated state rather than as unrestricted authority. Middleware distinguishes public, authentication, and protected routes; unauthenticated requests to protected paths are redirected to login. Server-side handlers must still derive identity from the verified session and validate every mutation, because client-submitted identifiers are not authorization evidence [5].'),
        P('Prisma is used as the typed persistence boundary and is paired with validation before data is committed. Environment variables hold provider credentials and database URLs; they are not exposed to client components. The deployment includes a custom .npmrc setting for legacy peer-dependency resolution, allowing Vercel builds to install the project dependency graph consistently. Locked versions, generated Prisma artifacts, and separate pooled versus direct database URLs are deployment controls rather than algorithmic assumptions.'),

        heading('VI', 'Discussion and Limitations'),
        P('Finite domains permit O(1) categorical verification and make the filter explainable: a candidate can be told whether role, experience, location, or availability prevented a match. Database-side predicates also avoid loading a whole profile directory into the browser. The model is especially suitable for hackathons because mandatory team coverage is often more important than a globally optimized social score.'),
        P('The same structure introduces rigidity. New specializations require a controlled schema migration, and a self-reported technology set is not independent evidence of competence. Jaccard similarity also treats skill labels uniformly unless domain-specific weights are introduced. Further, the current pairwise ranking does not solve the multi-member assignment problem, where several vacancies and candidates must be selected jointly. These limitations motivate human confirmation and later optimization stages rather than hidden automated rejection.'),

        heading('VII', 'Conclusion and Future Work'),
        P('Synapse defines a practical algorithmic basis for hackathon team formation. Finite roles and experience levels convert ambiguous input into comparable state; deterministic filtering identifies feasible candidates; and Jaccard-based ranking orders feasible alternatives without obscuring mandatory requirements. The architecture combines Next.js, RSCs, Prisma, PostgreSQL, NextAuth.js, and Vercel deployment so that data access and authorization remain server controlled.'),
        P('Future work will use natural-language classification during onboarding, followed by user confirmation before any text is mapped to an enum or skill set. GitHub API integration may add opt-in public indicators such as language distribution and repository activity. The longer-term optimization problem is multi-member team assembly with role coverage, diversity, schedule overlap, and participant preference under explicit constraints.'),

        Paragraph('ACKNOWLEDGMENT', section),
        P('The authors thank the Department of Computer Science and Engineering, Rajalakshmi Engineering College, for academic guidance and infrastructure support.', body0),
        Paragraph('REFERENCES', section),
        R('[1] R. Dechter, Constraint Processing. San Francisco, CA, USA: Morgan Kaufmann, 2003.'),
        R('[2] T. Lappas, K. Liu, and E. Terzi, “Finding a team of experts in social networks,” in Proceedings of the 15th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2009, pp. 467–476.'),
        R('[3] Vercel, “Next.js documentation,” 2026. [Online]. Available: https://nextjs.org/docs'),
        R('[4] Prisma, “Prisma ORM documentation,” 2026. [Online]. Available: https://www.prisma.io/docs'),
        R('[5] Auth.js, “Auth.js documentation,” 2026. [Online]. Available: https://authjs.dev'),
        R('[6] Supabase, “Supabase database documentation,” 2026. [Online]. Available: https://supabase.com/docs'),
        R('[7] P. Jaccard, “Etude comparative de la distribution florale dans une portion des Alpes et des Jura,” Bulletin de la Societe Vaudoise des Sciences Naturelles, vol. 37, pp. 547–579, 1901.'),
    ]
    doc.build(story)
    print(OUT)

if __name__ == '__main__':
    build()
