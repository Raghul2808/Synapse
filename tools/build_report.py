from pathlib import Path
import json, shutil, subprocess, textwrap, re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / 'references' / 'FORMAT FOR PREPARATION OF PROJECT REPORT .docx'
OUT = ROOT / 'deliverables' / 'Synapse_FOAI_Project_Report.docx'
ASSETS = ROOT / 'report_assets'
DIAG = ASSETS / 'diagrams'
ARCH = ROOT / 'references' / 'ARCHITECTURE DIAGRAM.jpeg'
LOGO = ASSETS / 'college_logo.png'
SHOT_DIR = ASSETS / 'screenshots'
USER_SHOT_DIR = Path('/home/fykern/Pictures/Screenshots')

def set_cell_shading(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd'); shd.set(qn('w:fill'), fill); tcPr.append(shd)

def set_cell_margins(cell, top=90, start=90, bottom=90, end=90):
    tc = cell._tc; tcPr = tc.get_or_add_tcPr(); mar = tcPr.first_child_found_in('w:tcMar')
    if mar is None: mar = OxmlElement('w:tcMar'); tcPr.append(mar)
    for side, val in [('top', top), ('start', start), ('bottom', bottom), ('end', end)]:
        n = mar.find(qn(f'w:{side}'))
        if n is None: n = OxmlElement(f'w:{side}'); mar.append(n)
        n.set(qn('w:w'), str(val)); n.set(qn('w:type'), 'dxa')

def font(run, size=14, bold=False, name='Times New Roman'):
    run.font.name = name; run._element.rPr.rFonts.set(qn('w:ascii'), name); run._element.rPr.rFonts.set(qn('w:hAnsi'), name)
    run.font.size = Pt(size); run.font.bold = bold; run.font.color.rgb = RGBColor(0,0,0)

def svg_diagram(name, title, columns, arrows):
    # Editable SVG source retained alongside the report raster used in DOCX.
    width, height = 1280, 780
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<defs><marker id="a" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="black"/></marker></defs>',
           f'<text x="640" y="42" text-anchor="middle" font-family="Times New Roman" font-size="25" font-weight="bold">{title}</text>']
    positions={}
    for x, y, w, h, label, key in columns:
        positions[key]=(x,y,w,h)
        out += [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="white" stroke="black" stroke-width="2"/>']
        lines = label.split('\n'); base = y+h/2-(len(lines)-1)*14
        for i,line in enumerate(lines): out.append(f'<text x="{x+w/2}" y="{base+i*28}" text-anchor="middle" font-family="Times New Roman" font-size="20">{line}</text>')
    for a,b,label in arrows:
        x,y,w,h=positions[a]; x2,y2,w2,h2=positions[b]
        sx=x+w/2; sy=y+h/2; ex=x2+w2/2; ey=y2+h2/2
        if abs(ex-sx)>abs(ey-sy): sx=x+w if ex>sx else x; ex=x2 if ex>sx else x2+w
        else: sy=y+h if ey>sy else y; ey=y2 if ey>sy else y2+h
        out.append(f'<line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" stroke="black" stroke-width="2" marker-end="url(#a)"/>')
        if label: out.append(f'<text x="{(sx+ex)/2}" y="{(sy+ey)/2-8}" text-anchor="middle" font-family="Times New Roman" font-size="15" fill="black">{label}</text>')
    out.append('</svg>')
    svg = DIAG / f'{name}.svg'; png=DIAG / f'{name}.png'; svg.write_text('\n'.join(out), encoding='utf-8')
    subprocess.run(['rsvg-convert','-w','1600','-o',str(png),str(svg)], check=True)
    return png

def build_diagrams():
    DIAG.mkdir(parents=True, exist_ok=True)
    d={}
    d['verified_architecture']=svg_diagram('verified_architecture','Verified Synapse Implementation Architecture',[
        (45,220,190,95,'Browser\nReact client','browser'),(285,100,220,95,'Next.js App Router\nPages and layouts','next'),
        (285,350,220,95,'Route handlers\nServer actions','api'),(575,100,210,95,'NextAuth v5\nCredentials Google GitHub','auth'),
        (575,350,210,95,'Prisma Client\nType-safe queries','prisma'),(875,350,210,95,'PostgreSQL\nUser Hackathon Application','db'),
        (875,100,210,95,'External directory APIs\nUnstop Devpost Devfolio','external'),(1085,590,150,90,'Vercel\nDeployment','vercel')],
        [('browser','next','HTTP'),('next','api','API request'),('api','auth','session'),('api','prisma','query'),('prisma','db','SQL'),('api','external','directory fetch'),('next','vercel','deploy')])
    d['use_case']=svg_diagram('use_case','User Workflow Supported by Source and Deployment Evidence',[
        (60,270,170,90,'Visitor','visitor'),(330,100,210,80,'Browse teams\nand hackathons','browse'),(330,250,210,80,'Register or\nlog in','login'),(330,400,210,80,'View directory\nresults','directory'),(670,100,220,80,'Create profile\nand team request','profile'),(670,250,220,80,'Apply to a\nteam request','apply'),(670,400,220,80,'Favorite external\nhackathons','fav'),(990,250,200,80,'Authentication\nrequired','gate')],
        [('visitor','browse','public'),('visitor','login','public'),('browse','directory','data'),('login','profile','session'),('login','apply','session'),('login','fav','session'),('profile','gate','protected'),('apply','gate','protected'),('fav','gate','protected')])
    d['matching_flow']=svg_diagram('matching_flow','Implemented Team Discovery and Filtering Flow',[
        (45,275,180,80,'GET /api/teams','get'),(300,275,180,80,'Redux post store','store'),(555,90,190,80,'Text search\nteam event location','search'),(555,250,190,80,'Mode filter\nOnline Offline Hybrid','mode'),(555,410,190,80,'Experience filter\nclient label match','exp'),(555,570,190,80,'Skill overlap\nsubstring match','skill'),(1000,275,190,90,'All predicates true\nrender cards\notherwise empty state','result')],
        [('get','store','response'),('store','search','records'),('store','mode','records'),('store','exp','records'),('store','skill','records'),('search','result','AND'),('mode','result','AND'),('exp','result','AND'),('skill','result','AND')])
    d['dataflow']=svg_diagram('dataflow','Verified Data Flow for Team Request and Application',[
        (55,115,195,85,'Find Member form\nReact Hook Form Zod','form'),(55,365,195,85,'Team detail\napplication dialog','dialog'),(360,115,210,85,'POST /api/post\nauth check','post'),(360,365,210,85,'POST /api/apply\nFormData','apply'),(680,115,210,85,'Prisma Hackathon\ncreate','hc'),(680,365,210,85,'S3 upload optional\nApplication create','ac'),(1000,235,190,85,'PostgreSQL\nHackathon User\nApplication','pg')],
        [('form','post','JSON'),('post','hc','validated fields'),('hc','pg','insert'),('dialog','apply','multipart'),('apply','ac','metadata'),('ac','pg','insert/update')])
    d['erd']=svg_diagram('erd','Database Entities Confirmed by Prisma Schema',[
        (55,110,230,150,'User\nid email username\nskills primaryRole experience\napplications hackathons accounts','user'),(390,80,230,125,'Hackathon\nid teamName event\nrequiredRole skills\nuserId','hack'),(390,330,230,125,'Application\ncandidateId postId\nstatus resume URLs','app'),(720,80,230,125,'Account\nprovider providerAccountId\nuserId','acct'),(720,330,230,125,'ExternalHackathonFavorite\nuserId externalId platform','fav'),(1000,210,200,110,'PasswordResetToken\nVerificationToken\nemail token expires','token')],
        [('user','hack','1 to many'),('user','app','1 to many'),('hack','app','1 to many'),('user','acct','1 to many'),('user','fav','1 to many'),('user','token','email keyed')])
    d['auth_sequence']=svg_diagram('auth_sequence','Authentication and Session Sequence',[
        (50,320,170,80,'Browser','browser'),(310,120,210,80,'Login form\nZod validation','login'),(310,400,210,80,'OAuth providers\nGoogle GitHub','oauth'),(620,120,210,80,'NextAuth\nCredentials authorize','nextauth'),(620,400,210,80,'Prisma Adapter\nAccount and User','adapter'),(960,250,210,80,'JWT session\nprotected route gate','jwt')],
        [('browser','login','credentials'),('login','nextauth','signIn'),('browser','oauth','OAuth choice'),('oauth','nextauth','callback'),('nextauth','adapter','read/write'),('nextauth','jwt','issue session'),('jwt','browser','redirect')])
    return d

def clear_body(doc):
    body=doc._element.body
    for child in list(body):
        if child.tag != qn('w:sectPr'): body.remove(child)

def add_field(p, instr):
    r=p.add_run(); fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),instr); r._r.addnext(fld)

def set_styles(doc):
    normal=doc.styles['Normal']; normal.font.name='Times New Roman'; normal._element.rPr.rFonts.set(qn('w:ascii'),'Times New Roman'); normal._element.rPr.rFonts.set(qn('w:hAnsi'),'Times New Roman'); normal.font.size=Pt(14); normal.font.color.rgb=RGBColor(0,0,0)
    normal.paragraph_format.line_spacing=1.5; normal.paragraph_format.space_after=Pt(4); normal.paragraph_format.first_line_indent=Inches(.28); normal.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.JUSTIFY
    for st, size in [('Heading 1',16),('Heading 2',14),('Heading 3',14)]:
        try: s=doc.styles[st]
        except KeyError: s=doc.styles.add_style(st, WD_STYLE_TYPE.PARAGRAPH)
        s.font.name='Times New Roman'; s._element.rPr.rFonts.set(qn('w:ascii'),'Times New Roman'); s._element.rPr.rFonts.set(qn('w:hAnsi'),'Times New Roman'); s.font.size=Pt(size); s.font.bold=True; s.font.color.rgb=RGBColor(0,0,0); s.paragraph_format.space_before=Pt(9); s.paragraph_format.space_after=Pt(5); s.paragraph_format.keep_with_next=True
    sec=doc.sections[0]; sec.page_width=Inches(8.27); sec.page_height=Inches(11.69); sec.top_margin=Inches(1.0); sec.bottom_margin=Inches(1.0); sec.left_margin=Inches(1.25); sec.right_margin=Inches(1.0)
    # A restrained academic page frame is applied inside every physical page.
    sectPr=sec._sectPr; old=sectPr.first_child_found_in('w:pgBorders')
    if old is not None: sectPr.remove(old)
    borders=OxmlElement('w:pgBorders'); borders.set(qn('w:offsetFrom'),'page')
    for side in ('top','left','bottom','right'):
        edge=OxmlElement(f'w:{side}'); edge.set(qn('w:val'),'single'); edge.set(qn('w:sz'),'8'); edge.set(qn('w:space'),'18'); edge.set(qn('w:color'),'808080'); borders.append(edge)
    sectPr.append(borders)
    footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER; footer.paragraph_format.space_before=Pt(0); footer.paragraph_format.space_after=Pt(0); add_field(footer,'PAGE')

def p(doc, text='', align=None, size=14, bold=False, first=True, line=1.5, after=4, before=0):
    para=doc.add_paragraph(); para.paragraph_format.line_spacing=line; para.paragraph_format.space_after=Pt(after); para.paragraph_format.space_before=Pt(before); para.paragraph_format.first_line_indent=Inches(.28) if first else Inches(0); para.alignment=align or WD_ALIGN_PARAGRAPH.JUSTIFY
    run=para.add_run(text); font(run,size,bold); return para

def heading(doc, text, level=1):
    para=doc.add_paragraph(style=f'Heading {level}'); para.paragraph_format.first_line_indent=Inches(0); para.alignment=WD_ALIGN_PARAGRAPH.LEFT; r=para.add_run(text); font(r,16 if level==1 else 14,True); return para

def chapter(doc, no, title):
    doc.add_page_break(); h=heading(doc,f'CHAPTER {no}',1); h.alignment=WD_ALIGN_PARAGRAPH.CENTER
    h2=heading(doc,title,1); h2.alignment=WD_ALIGN_PARAGRAPH.CENTER; return h2

def figure(doc, path, caption, width=6.1):
    para=doc.add_paragraph(); para.alignment=WD_ALIGN_PARAGRAPH.CENTER; para.paragraph_format.space_after=Pt(2); para.add_run().add_picture(str(path),width=Inches(width))
    cap=doc.add_paragraph(); cap.alignment=WD_ALIGN_PARAGRAPH.CENTER; cap.paragraph_format.space_after=Pt(7); cap.paragraph_format.keep_with_next=False; r=cap.add_run(caption); font(r,11,False); return cap

def screenshot_pair(doc, left_path, left_caption, right_path, right_caption, left_width=2.78, right_width=2.78):
    """Two genuine UI captures per report row, retaining readable aspect ratios."""
    t=doc.add_table(rows=1, cols=2); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
    for cell, path, caption, width in ((t.cell(0,0),left_path,left_caption,left_width),(t.cell(0,1),right_path,right_caption,right_width)):
        set_cell_margins(cell,top=45,start=45,bottom=45,end=45); cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        q=cell.paragraphs[0]; q.alignment=WD_ALIGN_PARAGRAPH.CENTER; q.paragraph_format.space_after=Pt(2); q.add_run().add_picture(str(path),width=Inches(width))
        cap=cell.add_paragraph(); cap.alignment=WD_ALIGN_PARAGRAPH.CENTER; cap.paragraph_format.space_after=Pt(2); cap.paragraph_format.line_spacing=1.0
        r=cap.add_run(caption); font(r,9.5)
    doc.add_paragraph().paragraph_format.space_after=Pt(2)
    return t

def copy_user_screenshots():
    SHOT_DIR.mkdir(parents=True, exist_ok=True)
    sources={
        'landing_dark':'2026_10_09_09_27_46_screenshot.png',
        'signup':'2026_10_09_09_28_03_screenshot.png',
        'support_widget':'2026_10_09_09_28_12_screenshot.png',
        'profile':'2026_10_09_09_29_39_screenshot.png',
        'profile_navigation':'2026_10_09_09_29_47_screenshot.png',
        'hackathon_directory':'2026_10_09_09_30_01_screenshot.png',
        'team_filters':'2026_10_09_09_30_14_screenshot.png',
        'team_request_form':'2026_10_09_09_30_29_screenshot.png',
        'account_menu':'2026_10_09_09_30_40_screenshot.png',
        'application_status':'2026_10_09_09_30_51_screenshot.png',
        'landing_collaboration':'2026_10_09_09_31_11_screenshot.png',
        'landing_workflow':'2026_10_09_09_31_26_screenshot.png',
        'landing_light':'2026_10_09_09_33_37_screenshot.png'
    }
    copied={}
    for key, filename in sources.items():
        source=USER_SHOT_DIR/filename
        if not source.exists(): raise FileNotFoundError(source)
        target=SHOT_DIR/f'{key}.png'; shutil.copy2(source,target); copied[key]=target
    return copied

def table(doc, headers, rows, widths=None):
    t=doc.add_table(rows=1, cols=len(headers)); t.alignment=WD_TABLE_ALIGNMENT.CENTER
    tblPr=t._tbl.tblPr; borders=OxmlElement('w:tblBorders')
    for side in ('top','left','bottom','right','insideH','insideV'):
        edge=OxmlElement(f'w:{side}'); edge.set(qn('w:val'),'single'); edge.set(qn('w:sz'),'6'); edge.set(qn('w:space'),'0'); edge.set(qn('w:color'),'D9D9D9'); borders.append(edge)
    tblPr.append(borders)
    hdr=t.rows[0].cells
    for i,h in enumerate(headers):
        set_cell_shading(hdr[i],'D9D9D9'); set_cell_margins(hdr[i]); hdr[i].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
        q=hdr[i].paragraphs[0]; q.alignment=WD_ALIGN_PARAGRAPH.CENTER; q.paragraph_format.space_after=Pt(0); r=q.add_run(h); font(r,10,True)
        if widths: hdr[i].width=Inches(widths[i])
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for i,val in enumerate(row):
            set_cell_margins(cells[i]); cells[i].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            q=cells[i].paragraphs[0]; q.paragraph_format.space_after=Pt(0); q.paragraph_format.line_spacing=1.0; q.alignment=WD_ALIGN_PARAGRAPH.LEFT if len(str(val))>18 else WD_ALIGN_PARAGRAPH.CENTER
            r=q.add_run(str(val)); font(r,9.5)
            if widths: cells[i].width=Inches(widths[i])
    doc.add_paragraph().paragraph_format.space_after=Pt(2)
    return t

def toc_table(doc, rows):
    t=doc.add_table(rows=1, cols=3); t.alignment=WD_TABLE_ALIGNMENT.CENTER; t.autofit=False
    # Fix the Word table grid as well as the cells.  This prevents Word/LibreOffice
    # from redistributing the columns and wrapping otherwise single-line TOC entries.
    widths=[1.65,3.13,1.15]
    layout=OxmlElement('w:tblLayout'); layout.set(qn('w:type'),'fixed'); t._tbl.tblPr.append(layout)
    borders=OxmlElement('w:tblBorders')
    for side in ('top','left','bottom','right'):
        edge=OxmlElement(f'w:{side}'); edge.set(qn('w:val'),'single'); edge.set(qn('w:sz'),'10'); edge.set(qn('w:space'),'8'); edge.set(qn('w:color'),'000000'); borders.append(edge)
    t._tbl.tblPr.append(borders)
    for i,w in enumerate(widths):
        t._tbl.tblGrid.gridCol_lst[i].set(qn('w:w'),str(int(w*1440)))
    def set_width(cell, width):
        tcpr=cell._tc.get_or_add_tcPr(); tcw=tcpr.first_child_found_in('w:tcW')
        if tcw is None:
            tcw=OxmlElement('w:tcW'); tcpr.append(tcw)
        tcw.set(qn('w:w'),str(int(width*1440))); tcw.set(qn('w:type'),'dxa')
    for i,label in enumerate(['CHAPTER NO.','TITLE','PAGE NO.']):
        c=t.rows[0].cells[i]; c.width=Inches(widths[i]); set_width(c,widths[i]); set_cell_margins(c, top=70, start=30, bottom=70, end=30)
        q=c.paragraphs[0]; q.alignment=WD_ALIGN_PARAGRAPH.CENTER; q.paragraph_format.space_after=Pt(0); r=q.add_run(label); font(r,12,True)
    for row in rows:
        cells=t.add_row().cells
        for i,val in enumerate(row):
            cells[i].width=Inches(widths[i]); set_width(cells[i],widths[i]); set_cell_margins(cells[i], top=55, start=30, bottom=55, end=30)
            q=cells[i].paragraphs[0]; q.paragraph_format.line_spacing=1.0; q.paragraph_format.space_after=Pt(0); q.alignment=WD_ALIGN_PARAGRAPH.CENTER if i != 1 else WD_ALIGN_PARAGRAPH.LEFT
            r=q.add_run(val); font(r,12)
    return t

def code(doc, text):
    q=doc.add_paragraph(); q.paragraph_format.first_line_indent=Inches(0); q.paragraph_format.line_spacing=1.0; q.paragraph_format.space_after=Pt(5)
    shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),'F2F2F2'); q._p.get_or_add_pPr().append(shd)
    for line in text.split('\n'):
        r=q.add_run(line+'\n'); font(r,8.5,False,'Courier New')
    return q

def bullets(doc, items):
    for item in items:
        q=doc.add_paragraph(); q.paragraph_format.left_indent=Inches(.3); q.paragraph_format.first_line_indent=Inches(-.18); q.paragraph_format.line_spacing=1.3; q.paragraph_format.space_after=Pt(2); r=q.add_run('• ' + item); font(r,13)

def add_cover(doc):
    for _ in range(2): p(doc,'',align=WD_ALIGN_PARAGRAPH.CENTER,first=False,after=0)
    p(doc,'SYNAPSE',align=WD_ALIGN_PARAGRAPH.CENTER,size=22,bold=True,first=False,after=8)
    p(doc,'ADVANCED DEVELOPER MATCHMAKING AND HACKATHON COLLABORATION PLATFORM',align=WD_ALIGN_PARAGRAPH.CENTER,size=16,bold=True,first=False,line=1.2,after=18)
    p(doc,'A PROJECT REPORT',align=WD_ALIGN_PARAGRAPH.CENTER,size=14,bold=True,first=False,after=6)
    p(doc,'submitted in partial fulfillment of the requirements for the course',align=WD_ALIGN_PARAGRAPH.CENTER,size=14,first=False,after=5)
    p(doc,'FOUNDATIONS OF ARTIFICIAL INTELLIGENCE',align=WD_ALIGN_PARAGRAPH.CENTER,size=16,bold=True,first=False,after=18)
    p(doc,'Submitted by',align=WD_ALIGN_PARAGRAPH.CENTER,size=14,first=False,after=5)
    p(doc,'2116240701409 - RAGHUL M\n2116240701428 - RITHESH MADHAV S',align=WD_ALIGN_PARAGRAPH.CENTER,size=14,bold=True,first=False,line=1.5,after=15)
    pp=doc.add_paragraph(); pp.alignment=WD_ALIGN_PARAGRAPH.CENTER; pp.add_run().add_picture(str(LOGO),width=Inches(2.05)); pp.paragraph_format.space_after=Pt(12)
    p(doc,'DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING',align=WD_ALIGN_PARAGRAPH.CENTER,size=14,bold=True,first=False,after=5)
    p(doc,'RAJALAKSHMI ENGINEERING COLLEGE\nTHANDALAM, CHENNAI - 602 105',align=WD_ALIGN_PARAGRAPH.CENTER,size=14,bold=True,first=False,line=1.35,after=13)
    p(doc,'OCTOBER 2026',align=WD_ALIGN_PARAGRAPH.CENTER,size=14,bold=True,first=False)

def add_certificate(doc):
    doc.add_page_break(); p(doc,'BONAFIDE CERTIFICATE',align=WD_ALIGN_PARAGRAPH.CENTER,size=16,bold=True,first=False,after=24)
    p(doc,'Certified that this project report titled "SYNAPSE: ADVANCED DEVELOPER MATCHMAKING AND HACKATHON COLLABORATION PLATFORM" is the bonafide work of RAGHUL M (2116240701409) and RITHESH MADHAV S (2116240701428), carried out under my supervision for the course Foundations of Artificial Intelligence.',size=14,first=False,line=1.5,after=42)
    p(doc,'',first=False,after=22)
    p(doc,'SIGNATURE OF THE FACULTY INCHARGE',align=WD_ALIGN_PARAGRAPH.LEFT,size=12,bold=True,first=False,after=35)
    p(doc,'Submitted for the Practical Examination held on ________________________________',align=WD_ALIGN_PARAGRAPH.LEFT,size=12,first=False,after=50)
    p(doc,'SIGNATURE OF THE INTERNAL EXAMINER',align=WD_ALIGN_PARAGRAPH.LEFT,size=12,bold=True,first=False)

def add_front(doc):
    doc.add_page_break(); p(doc,'ABSTRACT',align=WD_ALIGN_PARAGRAPH.CENTER,size=16,bold=True,first=False,after=18)
    abstract=('Synapse is a full-stack web application for hackathon collaboration. It lets users discover team requests, publish member requirements, apply to a team, and browse external hackathon directories. The implementation uses Next.js 14, React, TypeScript, Tailwind CSS, NextAuth v5, Prisma, and a PostgreSQL schema. Its data model records profiles, skills, declared roles and experience, team requests represented as Hackathon records, applications, and user-specific external hackathon favorites. The deployed application is served by Vercel.\n\nThis report assesses the application as a Foundations of Artificial Intelligence project by separating the intended Constraint Satisfaction framing from the code that currently executes. The schema defines finite role and experience domains and stores skill arrays, which are suitable inputs for a future constraint-based matcher. The verified team-discovery code performs client-side conjunctive filtering over search text, event mode, experience label, and skills. No CSP search procedure, heuristic score, ranking model, machine-learning model, or automatic team recommendation engine was found in the inspected source.\n\nThe report documents the verified architecture, database relations, authentication, routes, API endpoints, external directory integrations, and test result.')
    for para in abstract.split('\n\n'): p(doc,para,size=14,first=True,line=2.0,after=9)
    p(doc,'TABLE OF CONTENTS',align=WD_ALIGN_PARAGRAPH.CENTER,size=16,bold=True,first=False,after=16)
    toc_table(doc,[
        ('','ABSTRACT','3'),('1','INTRODUCTION','5'),('2','LITERATURE REVIEW','7'),('3','PROPOSED SYSTEM','9'),('','3.1   ARCHITECTURE DIAGRAM','9'),('4','MODULES DESCRIPTION','16'),('','4.1   AUTHENTICATION AND ACCOUNT MODULE','16'),('','4.2   REGISTRATION VERIFICATION AND RESET','17'),('5','IMPLEMENTATION AND RESULTS','23'),('','5.1   EXPERIMENTAL SETUP','23'),('','5.2   RESULTS','25'),('6','CONCLUSION AND FUTURE WORK','30'),('7','REFERENCES','35')])

def add_ch1(doc):
    chapter(doc,1,'INTRODUCTION')
    heading(doc,'1.1 Background',2)
    p(doc,'Hackathons require people with complementary technical abilities to form a working team within a limited time. A participant may be able to build a user interface, train a model, write backend services, prepare a deployment pipeline, or present a prototype, but no single profile reliably covers every role. Informal discovery through social groups and event channels can be slow and can hide relevant candidates outside a participant’s immediate network. Synapse addresses this discovery problem through a web interface that holds user profiles and publishes team requirements.')
    p(doc,'The project is implemented as a Next.js web application. The public interface exposes a landing page, a team directory, an external hackathon directory, and authentication pages. Authenticated flows support profile updates, creating a team requirement, applying to a team request, and maintaining external hackathon favorites. The system therefore focuses on the practical sequence that precedes collaboration: discovery, eligibility information, contact, and application.')
    heading(doc,'1.2 Problem Statement',2)
    p(doc,'A potential hackathon participant needs to locate a suitable team request without reading every listing manually. A team organizer needs a way to express required skills, the intended role, experience level, event mode, location, and registration date. Conventional listing pages provide information but often leave the user to manually compare requirements against their own profile. The FOAI opportunity is to represent the comparison as constraints and use those constraints to reduce the search space.')
    heading(doc,'1.3 Objectives and Scope',2)
    table(doc,['OBJECTIVE','VERIFIED INTERPRETATION'],[
        ('Publish team requirements','Authenticated form posts a Hackathon record with team, event, role, skills, mode, location, and date.'),('Discover opportunities','Team cards are fetched from /api/teams and filtered in the client when data is available.'),('Browse external events','Hackathon page requests Unstop, Devpost, and Devfolio directory APIs.'),('Manage identity','NextAuth supports credentials plus Google and GitHub providers.'),('Support future intelligent matching','Schema stores finite role and experience domains and skill arrays, but no automatic matcher is implemented.')],[2.1,4.1])
    heading(doc,'1.4 Stakeholders and Assumptions',2)
    p(doc,'Primary stakeholders are hackathon participants, team organizers, event-focused student communities, and project supervisors reviewing the FOAI formulation. The system assumes that users enter accurate skills and contact links, that external directory APIs remain available, and that an organizer is able to evaluate applications after receiving them. The current user interface does not demonstrate a team-balance optimizer, automatic acceptance decision, reputation score, or conflict-resolution workflow.')
    heading(doc,'1.5 Contributions and Current Limitations',2)
    bullets(doc,['A full-stack evidence base with a relational schema, authentication routes, route handlers, and external directory aggregation.','A transparent client-side rule filter that can narrow a list by search text, mode, experience label, and skill substring.','A documented FOAI formulation that distinguishes stored candidate constraints from an unimplemented CSP solver.','A clear limitation report: deployed team retrieval returned HTTP 500 during inspection, and protected interfaces could not be evaluated without credentials.'])

def add_ch2(doc):
    chapter(doc,2,'LITERATURE REVIEW')
    heading(doc,'2.1 Constraint Reasoning and Team Formation',2)
    p(doc,'Constraint satisfaction represents a problem through variables, finite domains, and restrictions that define acceptable combinations. Dechter describes constraint processing as a general framework for reasoning about assignments subject to constraints [3]. In a team-formation context, a candidate selection variable may have a domain of users, while hard constraints can require a role, availability, or eligibility condition. Soft constraints can express preferred skill overlap, timezone compatibility, or team diversity. This framework is useful for Synapse because its schema already expresses role and experience as finite enumerations and skills as arrays.')
    p(doc,'Team formation has also been studied as a skill-coverage problem. Lappas, Liu, and Terzi formulate the problem of selecting experts who collectively cover task skills while considering social-network structure [5]. Synapse does not model an expert graph or communication cost, so that method cannot be claimed as implemented. Its value here is conceptual: a future Synapse matcher could combine skill coverage with a small number of explicit constraints and explain why each team is proposed.')
    heading(doc,'2.2 Recommendation and Multi-Criteria Selection',2)
    p(doc,'A recommender normally ranks alternatives by predicted utility, similarity, preferences, or a learned model. Multi-criteria decision procedures can combine several attributes, but the aggregation rule must be stated. The inspected code does not calculate a score, weight criteria, sort candidate matches, or train a model. It evaluates a Boolean conjunction over filtered records. The literature therefore informs a future extension rather than describing an existing recommendation component.')
    heading(doc,'2.3 Web Architecture and Persistent Data',2)
    p(doc,'Next.js 14 documents the App Router as a file-system routing model that uses current React features [6]. In Synapse, pages, layouts, route handlers, and client components follow that approach. Prisma documents a PostgreSQL datasource through a schema provider and connection URL [8]. The inspected Prisma schema uses provider = "postgresql" and relates User, Hackathon, Application, Account, and ExternalHackathonFavorite records. These sources support the technology discussion; they are not evidence that every architectural box in the supplied diagram is deployed.')
    table(doc,['SOURCE','RELEVANCE TO SYNAPSE','IMPLEMENTED OR CONCEPTUAL'],[
        ('Dechter [3]','Variables, domains, and constraints provide the FOAI vocabulary.','Conceptual formulation; finite domains stored.'),('Lappas et al. [5]','Skill coverage and team selection motivate future matching.','Conceptual only; no expert graph or solver.'),('Next.js [6]','App Router pages, layouts, and route handlers.','Implemented in app/ and app/api/.'),('Prisma [8]','Schema-driven PostgreSQL data access.','Implemented in prisma/schema.prisma.'),('NextAuth [1]','Credentials and OAuth session handling.','Implemented in auth.ts and auth.config.ts.')],[1.25,3.1,1.85])
    heading(doc,'2.4 Gap Addressed by the Project',2)
    p(doc,'The practical gap is not a lack of a general team-formation theory; it is the absence of a lightweight, accessible workflow that brings profile information, team requirements, and external event discovery into one application. Synapse supplies that workflow. The evidence also shows the gap between the product description and the present algorithm: a genuine intelligent matcher still needs candidate retrieval, explicit hard and soft constraints, a selection strategy, and an explanation mechanism.')

def add_ch3(doc, d):
    chapter(doc,3,'PROPOSED SYSTEM')
    heading(doc,'3.1 System Overview',2)
    p(doc,'Synapse combines a public discovery interface with authenticated creator and applicant flows. The landing page links to team and hackathon exploration. The team area retrieves organizer-created Hackathon records. The hackathon area aggregates remote listings from Unstop, Devpost, and Devfolio. Authentication is handled by NextAuth and a Prisma adapter. The currently verified persistent layer is PostgreSQL, not MongoDB Atlas.')
    figure(doc,ARCH,'Figure 3.1 Supplied proposed system architecture. This diagram is included as supplied; it depicts intended components that are not all verified in the repository.',6.1)
    heading(doc,'3.2 Architecture Comparison',2)
    table(doc,['SUPPLIED DIAGRAM CLAIM','SOURCE OR DEPLOYMENT EVIDENCE','ASSESSMENT'],[
        ('MongoDB Atlas data layer','prisma/schema.prisma specifies provider = postgresql; Docker Compose includes postgres-dev.','Not supported by current code.'),('Prisma ORM','lib/prisma.ts instantiates PrismaClient; route handlers call Prisma methods.','Supported.'),('Next.js 14 App Router','package.json uses next ^14.2.7; app/ contains pages, layouts, and route handlers.','Supported.'),('NextAuth','auth.ts and auth.config.ts configure NextAuth, credentials, Google, and GitHub.','Supported.'),('Match API and CSP algorithm','No /api/match route or solver function was found. Team filtering is in PostsTab.tsx.','Not supported as implemented.'),('GitHub portfolio API','Profile accepts a GitHub URL; no GitHub API call was found.','Not supported as an integration.'),('Email service','Nodemailer-based verification and reset helpers are present.','Supported in source; delivery not exercised.'),('Vercel/AWS','Response headers identify Vercel; AWS S3 code is present for optional resume upload.','Vercel verified; S3 source-only.')],[1.65,3.25,1.35])
    figure(doc,d['verified_architecture'],'Figure 3.2 Verified implementation architecture derived from the inspected source.',6.1)
    heading(doc,'3.3 User Roles and Requirements',2)
    figure(doc,d['use_case'],'Figure 3.3 User workflow supported by source and deployment evidence.',6.1)
    table(doc,['CATEGORY','REQUIREMENT'],[
        ('Functional','Visitors can reach public home, teams, hackathons, login, signup, reset, and verification routes.'),('Functional','Authenticated users can create team requirements, update profile information, apply to team posts, and store favorites.'),('Non-functional','The web client is responsive through Tailwind CSS class usage and has desktop/mobile navigation components.'),('Non-functional','Password comparisons use bcrypt; authentication state uses JWT sessions through NextAuth.'),('Constraint','No session may be bypassed; protected URLs redirect to /login in the deployed inspection.'),('Constraint','External directory content depends on remote provider APIs and may change independently of Synapse.')],[1.45,4.8])
    heading(doc,'3.4 FOAI Formulation and Actual Algorithm',2)
    p(doc,'An accurate future CSP for team matching can define candidate variables x1 ... xk, whose domains are eligible users, and hard constraints for role, event mode, application uniqueness, and required skills. A soft objective can reward skill coverage and compatible preferences. The present code does not instantiate these variables, enumerate domains, backtrack, propagate constraints, or optimize an objective. Instead, it retrieves a list of posts and evaluates direct predicates on each post.')
    figure(doc,d['matching_flow'],'Figure 3.4 Implemented team discovery and filtering flow. The logic is a client-side Boolean filter, not a CSP solver.',6.1)
    code(doc,"matchesSearch = fields.some(value => value.toLowerCase().includes(search))\nmatchesMode = selectedModes.length ? selectedModes.some(m => post.hackathonMode.includes(m)) : true\nmatchesExperience = selectedExperience.length ? selectedExperience.some(e => post.experience.includes(e)) : true\nmatchesSkills = selectedSkills.length ? selectedSkills.some(skill => post.skills.some(s => s.includes(skill))) : true\nreturn matchesSearch && matchesMode && matchesExperience && matchesSkills")
    p(doc,'The output is an unranked subset of listings in their existing order. When no listing satisfies every active predicate, the interface renders an empty-state message. Matching uses case-insensitive substring inclusion. There is no tie-breaker, no explicit score, and no indication that a required role is enforced in the evaluated code; moreover, the component reads legacy role and experience field names while the current schema defines requiredRole and requiredExperience. This inconsistency is a current limitation.')
    heading(doc,'3.5 Data Model and Data Flow',2)
    figure(doc,d['erd'],'Figure 3.5 Database entity relationship diagram based on prisma/schema.prisma.',6.1)
    p(doc,'The User record is the central identity entity. It owns account links, created hackathon records, submitted applications, and saved external favorites. A Hackathon record represents an organizer-created team requirement rather than a public event directory item. It stores the team and event names, mode, location, registration date, required role and experience fields, skills, and the organizer identifier. An Application joins one candidate to one team request and is constrained to be unique for that pair. This relation prevents one candidate from applying repeatedly to the same request.')
    p(doc,'The schema uses cascading deletion from User to accounts, applications, owned hackathons, and favorites. The Application to Hackathon relation is retained so an application cannot point to a missing post. These relationships support basic integrity but do not model a separate Team entity, team membership roster, recommendation history, or interaction graph. Consequently, the source currently supports individual requests and applications rather than a full multi-member team optimization model.')
    figure(doc,d['auth_sequence'],'Figure 3.6 Authentication and session sequence based on auth.ts and auth.config.ts.',6.1)
    p(doc,'A credentials sign-in begins with client validation and reaches NextAuth authorization, which retrieves the account record and compares the stored bcrypt hash. On success, NextAuth stores the user identifier in a JWT session. The middleware then distinguishes public routes, authentication routes, and protected routes. The session gate is therefore the primary control for dashboard pages and creation workflows. OAuth account links are stored through the Prisma adapter when Google or GitHub authentication is configured.')
    figure(doc,d['dataflow'],'Figure 3.7 Verified team request and application data flow.',6.1)
    p(doc,'The team request form sends JSON to the post route after the user submits event and role information. The route calls auth() before it creates a Hackathon record. The application path is different because it sends multipart FormData: optional resume bytes can be uploaded to S3, while link fields and identifiers are persisted through Prisma. A production-ready version should derive every mutable user identifier from the server session and validate the request body before database operations. The report identifies this as a recommended improvement rather than a demonstrated protection.')

def add_ch4(doc, s):
    chapter(doc,4,'MODULES DESCRIPTION')
    heading(doc,'4.1 Authentication and Account Module',2)
    p(doc,'The authentication module is defined in auth.ts and auth.config.ts. NextAuth is configured with a Prisma adapter and JWT sessions. The credentials provider validates email and password inputs with LoginSchema, looks up the user with GetUserByEmail, and compares a bcrypt hash. Google and GitHub providers are also configured through environment variables. The middleware treats auth URLs differently from public and protected routes; unauthenticated access to a protected page redirects to /login.')
    heading(doc,'4.2 Registration, Verification, and Password Reset',2)
    p(doc,'Actions/register.ts validates fields, hashes a password with bcrypt using ten rounds, checks for duplicate email or username values, creates the user, and generates a verification token. The mail helper uses Nodemailer to prepare verification and reset messages. Actions/login.ts blocks an unverified credentials account until a verification message is sent. Actions/newPassword.ts validates a reset token, checks expiry, hashes the replacement password, and deletes the used token. These paths are present in source but their end-to-end mail delivery was not exercised because no authorized test mailbox was supplied.')
    heading(doc,'4.3 Profile Module',2)
    p(doc,'The dashboard profile form retrieves and updates user data through /api/user. It exposes name, email, GitHub URL, LinkedIn URL, portfolio or resume link, profile image, skills, bio, and a role field. The route handler accepts an object containing user data, replaces the skills array with the submitted array, and performs prisma.user.update. The code does not show route-level authorization verifying that the submitted user.id belongs to the current session. This should be corrected before relying on the endpoint for production authorization.')
    heading(doc,'4.4 Team Request and Discovery Module',2)
    p(doc,'The Find Member page provides a React Hook Form containing team, hackathon, registration URL, event mode, member count, skills, experience, date, location, and description fields. It posts the data to /api/post. The route first calls auth() and rejects unauthenticated requests. It creates a Hackathon record with the current session user id. Team discovery calls GET /api/teams, stores its Hackathon array in Redux, and client-filters that array. During deployed inspection, GET /api/teams returned HTTP 500, so no current public data result can be asserted.')
    heading(doc,'4.5 Application Module',2)
    p(doc,'A team detail page calls POST /api/id to retrieve one Hackathon record and GET /api/user to retrieve its organizer data. Its application dialog collects LinkedIn, GitHub, and resume information. POST /api/apply detects a duplicate candidateId/postId pair, optionally uploads a selected resume to an AWS S3 bucket, updates profile links, and creates an Application record. The database itself enforces the candidateId/postId uniqueness constraint. The code should additionally verify the session user at the API boundary because candidateId is accepted from form data.')
    heading(doc,'4.6 External Hackathon and Favorites Module',2)
    p(doc,'The hackathons page requests the internal Unstop, Devpost, and Devfolio route handlers. Each handler fetches a remote provider endpoint with axios; the client normalizes selected fields and displays cards by platform. The favorites route requires auth(), then creates or deletes a user-specific ExternalHackathonFavorite using a composite unique key. Deployed requests to all three external directory handlers returned HTTP 200 during the inspection. The favorites endpoint returned HTTP 401 without a session, which is expected.')
    heading(doc,'4.7 Validation, Error Handling, and Observability',2)
    p(doc,'Zod schemas validate registration, login, reset, new password, and front-end team form input. Prisma operations are enclosed in try/catch blocks in the route handlers and usually return JSON error messages. Sentry configuration files and a Sentry example route are present. However, the post route imports a hackathonSchema but does not call parse or safeParse before using the request body. This leaves a gap between the intended validation contract and the executed server route.')
    table(doc,['MODULE','INPUTS','OUTPUTS','LIMITATIONS'],[
        ('Authentication','Credentials or OAuth callback','JWT session or error','No authorized browser session available for UI test.'),('Profiles','User form data','Updated User record','POST route trusts submitted user object.'),('Team requests','Form fields and session','Hackathon record','Live GET /api/teams returned 500.'),('Filtering','Search and selected filters','Unranked subset','No CSP, score, or ranking.'),('Applications','Links, resume, identifiers','Application record / S3 URL','API lacks visible session ownership check.'),('External events','Remote APIs','Normalized cards','Availability relies on third parties.')],[1.15,1.55,1.55,2.0])
    heading(doc,'4.8 Captured Interface Evidence',2)
    p(doc,'Figures 4.1 to 4.13 are genuine user-supplied captures of the deployed Synapse interface. They are included as interface evidence rather than as proof of every backend operation. In particular, they show rendered controls and displayed sample content; they do not override the separately reported HTTP 500 observation for the public team-list endpoint or the source-code findings about the present filtering algorithm.')
    heading(doc,'4.8.1 Landing, Theme, and Account Entry',3)
    p(doc,'The landing captures show the shared navigation, call-to-action buttons, theme treatment, and the collaboration message presented to a public visitor. The sign-up capture shows the three available account-entry choices: GitHub, Google, and email. The support-widget capture is identified as an embedded assistance interface and is not treated as a Synapse-authored matching module.')
    screenshot_pair(doc,s['landing_dark'],'Figure 4.1 Dark-theme landing hero with public navigation and team-discovery calls to action.',s['landing_light'],'Figure 4.2 Light-theme landing hero showing the same public entry points.',2.78,2.78)
    screenshot_pair(doc,s['signup'],'Figure 4.3 Registration screen with GitHub, Google, and email continuation choices.',s['support_widget'],'Figure 4.4 Embedded support-chat widget opened from the landing page.',2.78,1.72)
    heading(doc,'4.8.2 Profile and Navigation Controls',3)
    p(doc,'The profile capture displays contact-link controls, a skills area, an about-me area, and an Edit Profile action. The compact navigation capture provides Dashboard, Profile, Edit Profile, Application Status, Team Requests, GitHub, Support, and Logout controls. These screens correspond to the account and profile modules described above.')
    screenshot_pair(doc,s['profile'],'Figure 4.5 Authenticated profile view with links, skills, biography area, and Edit Profile control.',s['profile_navigation'],'Figure 4.6 Compact dashboard navigation with profile, request, support, and logout controls.',2.78,1.62)
    heading(doc,'4.8.3 Hackathon Discovery and Team Filtering',3)
    p(doc,'The hackathon directory capture visibly separates Unstop, Devpost, and Devfolio provider tabs and presents event cards with mode, live status, location, favorite, and visit controls. The team-discovery capture shows the actual search field and filter categories for mode, experience, and skills, alongside rendered team requirement cards. It supports the report’s description of a user-driven filter interface; it does not evidence automated ranking or a CSP solver.')
    screenshot_pair(doc,s['hackathon_directory'],'Figure 4.7 External hackathon directory showing platform tabs and event cards.',s['team_filters'],'Figure 4.8 Team discovery search, mode, experience, skill filters, and requirement cards.',2.78,2.78)
    heading(doc,'4.8.4 Team Request, Account Menu, and Applications',3)
    p(doc,'The team-request capture presents the organizer form fields for event details, member count, role, skills, experience, location, dates, and additional details. The account menu exposes quick links to profile and dashboard views. The application-status capture renders a status table for submitted, rejected, and accepted outcomes, with a visit-post action for each displayed entry.')
    screenshot_pair(doc,s['team_request_form'],'Figure 4.9 Find Member team-request form with event and team-member requirement fields.',s['account_menu'],'Figure 4.10 Account menu with profile, dashboard, report, and logout actions.',2.74,1.70)
    screenshot_pair(doc,s['application_status'],'Figure 4.11 Application-status table with team, hackathon, visit-post, and status columns.',s['landing_collaboration'],'Figure 4.12 Landing collaboration section with global-discovery messages and partner marks.',2.78,2.78)
    heading(doc,'4.8.5 Public Workflow and Help Content',3)
    p(doc,'The final landing-page capture describes the visible user journey: create a team, discover teams matching a skill set, explore upcoming hackathons, and upload a resume or connect GitHub. The lower part of the same view exposes frequently asked questions. These are public explanatory components, not an implementation of a skill-matching algorithm.')
    figure(doc,s['landing_workflow'],'Figure 4.13 Public How It Works and frequently asked questions sections of the landing page.',5.9)
    p(doc,'The workflow cards give a visitor a concise description of the intended sequence: establish a profile, publish or discover a team need, explore an event, and provide supporting profile material. The cards are useful interface guidance because they expose the system boundaries before sign-in. They should be read as product navigation, however, rather than as execution evidence for automatic teammate selection. The displayed phrase about teams matching a skill set is therefore interpreted in this report alongside the inspected client predicates, which implement direct user-selected filtering.')
    p(doc,'The FAQ area is a second public help surface. It groups questions about creating or joining a team, platform access, multiple teams, skill matching, event discovery, and featured event types. This grouping makes the public landing page more self-explanatory, while the answer content and any dynamic interactions were not separately exercised in this report. The capture documents the interface state supplied by the project team; it does not assert a test result for every FAQ interaction.')

def add_ch5(doc, d):
    chapter(doc,5,'IMPLEMENTATION AND RESULTS')
    heading(doc,'5.1 Experimental Setup',2)
    p(doc,'The codebase is a TypeScript Next.js project named devmatchups in package.json. Its dependency declarations identify Next.js 14.2.7, React 18.3.1, Prisma 5.22.0, NextAuth 5.0.0-beta.18, Tailwind CSS 3.4.1, Zod 3.23.8, React Hook Form, Redux Toolkit, axios, Nodemailer, AWS SDK, and Sentry. The relational schema declares PostgreSQL, while Docker Compose provisions a postgres-dev service. The deployment response headers identify Vercel as the serving platform.')
    table(doc,['COMPONENT','OBSERVED CONFIGURATION','EVIDENCE'],[
        ('Frontend','Next.js 14 App Router, React, TypeScript, Tailwind CSS, shadcn-style components.','package.json; app/; components/'),('Authentication','NextAuth v5, credentials, Google and GitHub providers, JWT session.','auth.ts; auth.config.ts'),('Database','Prisma 5.22.0 with PostgreSQL datasource.','prisma/schema.prisma'),('State and forms','Redux Toolkit, React Hook Form, Zod.','lib/store; team and auth forms'),('External data','Unstop, Devpost, Devfolio APIs; AWS S3 code for resumes.','app/api/*Hackathon; apply route'),('Deployment','Vercel response header; Sentry build configuration.','HTTP response; next.config.mjs')],[1.25,3.2,1.8])
    heading(doc,'5.2 Source Implementation Evidence',2)
    p(doc,'The public homepage composes Navbar, Hero, logos, globe, process flow, FAQ, call to action, and footer components. The application uses nested layouts to apply navigation and footer structure. Team listings and hackathon directory screens are client components because they use effect hooks, Redux, local state, and browser interaction. Route handlers are placed under app/api/ and return NextResponse JSON values.')
    code(doc,"export async function GET(req: Request) {\n  try {\n    const hackathon = await prisma.hackathon.findMany();\n    return NextResponse.json({ Hackathon: hackathon }, { status: 201 });\n  } catch (error) {\n    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });\n  }\n}")
    p(doc,'The excerpt above is the complete team-list handler in app/api/teams/route.ts. It reads all Hackathon records and returns them without pagination or an authorization requirement. Its deployed HTTP response was 500 at the time of inspection. The status code 201 for a successful GET is also semantically unusual; a successful retrieval should normally use 200. These observations are implementation findings, not assumptions about application intent.')
    heading(doc,'5.3 Route Inventory and Access Results',2)
    figure(doc,d['use_case'],'Figure 5.1 Route-access and observed-result summary. Genuine deployed-interface captures are documented separately in Chapter 4.',5.9)
    table(doc,['ROUTE','PURPOSE','HTTP OBSERVATION','ACCESS / LIMITATION'],[
        ('/','Landing page','200; title Synapse','Public; HTML inspected.'),('/teams','Team discovery','200; title Synapse','Public page; backing GET /api/teams was 500.'),('/hackathons','External event directory','200; title Synapse','Public; each external handler returned 200.'),('/login','Credentials/OAuth sign in','200; title Login | Synapse','Public; form interaction not executed.'),('/signup','Registration','200; title Signup | Synapse','Public; no account created.'),('/forgot-password, /reset','Recovery pages','200','Public; no email flow exercised.'),('/dashboard and child routes','Profile and requests','Redirected to /login','Protected without credentials.'),('/findmember, /favorites, /settings','Creator/favorite flows','Redirected to /login','Protected without credentials.'),('/verify-email','Source route exists','Redirected to /login','Deployed behavior differed from file route name.')],[1.45,1.55,1.65,1.7])
    heading(doc,'5.4 Responsive and Interaction Evidence',2)
    p(doc,'The source includes desktop navigation and a mobile Sheet navigation menu. Tailwind breakpoint classes such as md:flex, md:hidden, sm:grid-cols-2, and lg:grid-cols-3 define responsive layouts. The team filter has a drawer filter on smaller layouts and an inline filter panel on larger layouts. The hackathon page tracks a selected platform tab and conditionally directs an unauthenticated user to /login when Favorites is selected. These statements are verified by component source. Thirteen genuine user-supplied deployed-interface captures are embedded in Chapter 4, covering public landing, sign-up, profile, navigation, directory, filtering, request, menu, and application-status states. They document rendered states but are not a controlled tablet/mobile viewport test.')
    heading(doc,'5.5 Testing and Validation',2)
    p(doc,'The repository includes one Jest suite. It renders a locally defined sample Home component and asserts that a sample heading and paragraph exist. The command npm test -- --runInBand was executed successfully: one test suite passed with two tests. The suite validates the Jest setup but it does not render Synapse app/page.tsx, call a route handler, test authentication, or exercise the deployed service. Accordingly, no broader test success is inferred from it.')
    table(doc,['ID','MODULE','PROCEDURE','ACTUAL RESULT','STATUS'],[
        ('T01','Unit test setup','Run npm test -- --runInBand.','1 suite; 2 tests passed.','PASS'),('T02','Public landing route','GET deployed /.','HTTP 200; title Synapse.','PASS'),('T03','Public team route','GET deployed /teams and /api/teams.','Page 200; API 500.','FAIL'),('T04','External directories','GET three deployed API handlers.','Unstop, Devpost, Devfolio each 200.','PASS'),('T05','Protected dashboard','GET /dashboard with redirects.','Final URL /login.','PASS'),('T06','Favorites API','GET without session.','HTTP 401 Unauthorized.','PASS'),('T07','Registration validation','Browser form invalid-input interaction.','Browser runtime unavailable.','BLOCKED'),('T08','UI state evidence','Review supplied deployed captures.','13 genuine captures embedded in Chapter 4.','PASS'),('T09','Apply workflow','Authenticated submission.','No credentials supplied; no production records created.','BLOCKED')],[.45,1.05,1.65,1.85,.7])
    heading(doc,'5.6 Results and Discussion',2)
    p(doc,'The inspected code and HTTP responses demonstrate an operational public shell, authentication routing, external hackathon aggregation, and a database-backed model for profiles, team requests, and applications. The three external directory services were live during inspection. The project also provides a clear data structure for role, experience, and skills. These are practical prerequisites for future intelligent decision support.')
    p(doc,'The strongest FOAI conclusion is that Synapse currently implements a rule-based filtering interface, not an automated constraint solver. A selected search, mode, experience, and skill condition is applied as an AND combination. This is useful search refinement, but it does not select a team from candidates, maximize an objective, or produce recommendations. The present system should be described as constraint-ready rather than CSP-based until a solver or explicit scoring method is implemented and tested.')
    heading(doc,'5.7 Observed Limitations',2)
    table(doc,['LIMITATION','EVIDENCE','IMPACT'],[
        ('Team list service failure','Deployed GET /api/teams returned HTTP 500.','Team cards cannot be verified in the live environment.'),('No verified match algorithm','No Match API or solver; filtering resides in PostsTab.tsx.','AI claim must be limited to rule-based discovery.'),('Schema/UI naming drift','Schema uses requiredRole/requiredExperience while components use role/experience.','Filter and detail display may not align with current data model.'),('API authorization concerns','/api/user POST and /api/apply accept user identifiers from client input.','Server-side ownership validation should be added.'),('Automation limitation','Browser-control runtime could not initialize.','No controlled interactive or multi-viewport test.'),('Limited tests','Jest suite uses a sample component.','No direct integration or end-to-end coverage.')],[1.75,2.65,1.35])
    heading(doc,'5.8 Traceability from Claim to Evidence',2)
    p(doc,'The report uses three kinds of evidence. Source evidence establishes what the repository contains at the inspected revision. Deployment evidence establishes only what a non-authenticated HTTP request observed at the stated URL. Test evidence establishes only the command and assertions actually executed. This separation prevents a feature described in a README, architecture diagram, or planned schema comment from being reported as a completed and demonstrated capability.')
    p(doc,'For example, the README calls the system AI-driven and describes Constraint Satisfaction matching. The schema comments also use CSP language. The executable client filter is the stronger implementation evidence because it supplies the actual predicates and rendering outcome. The report therefore treats role and experience enumerations as constraint-ready fields, while classifying the running filter as a deterministic Boolean narrowing procedure. A future implementation should add a separate matcher module, unit tests with known candidate sets, and recorded decisions that can be checked against the stated constraints.')
    table(doc,['REPORT CLAIM','PRIMARY EVIDENCE','CONFIDENCE BOUNDARY'],[
        ('Uses PostgreSQL through Prisma','prisma/schema.prisma and lib/prisma.ts','Source-confirmed; provider not inferred from the old architecture image.'),('Public pages are reachable','HTTP 200 and HTML title observations','Only unauthenticated route reachability was checked.'),('External directories aggregate data','Three route-handler sources and three HTTP 200 responses','Provider payload freshness was not evaluated.'),('Team matching is not a CSP solver','Absence of match route/solver; PostsTab predicate implementation','Conclusion is limited to inspected source.'),('Protected pages require login','middleware.ts plus redirect observation','Authenticated behavior remains untested.')],[1.55,2.65,1.45])
    heading(doc,'5.9 User Interface Evidence Boundary',2)
    p(doc,'The report embeds thirteen genuine user-supplied captures of the deployed Synapse interface in Section 4.8. The capture manifest records their filenames, represented URL or state, viewport dimensions, and CAPTURED status. The report does not label these captures as end-to-end test results: no controlled browser session, form submission, tablet viewport run, or mobile viewport run was executed in this environment. The browser-control runtime was unavailable during the original capture attempt. This distinction preserves the difference between a real user-interface image, a source-derived diagram, and an automated interaction test.')
    p(doc,'Each retained image is paired with a caption that states the visible interface purpose rather than inferring unavailable hidden behavior. For example, the external-directory image establishes that provider tabs and event-card controls were rendered in the captured state; it does not establish the freshness of every external payload. Likewise, the application-status table establishes the displayed labels and columns, but it does not prove that the displayed values were produced by a new test submission. This evidence discipline keeps the visual record useful without expanding it beyond what the captured pixels show.')
    p(doc,'The report package preserves the original-resolution PNG copies in the screenshots folder, and the document includes print-scaled versions to maintain readable captions and balanced A4 pages. The capture manifest should be used with the report whenever a reviewer needs to distinguish a public page, an authenticated state, and a user-interface component such as the account menu or support widget. Future test evidence should add a controlled test account, stated viewport dimensions, scripted steps, expected result, and observed result for each interaction that needs to be claimed as verified.')

def add_ch6(doc):
    chapter(doc,6,'CONCLUSION AND FUTURE WORK')
    heading(doc,'6.1 Conclusion',2)
    p(doc,'Synapse provides a coherent web application structure for hackathon collaboration: public discovery pages, user authentication, a PostgreSQL-backed data model, team-request creation, applications, profile editing, and external hackathon aggregation. The implementation uses current Next.js App Router patterns, Prisma data access, NextAuth sessions, and a responsive component library. The deployed Vercel service returned public pages and live external directory results during inspection, showing that the external event discovery portion was reachable.')
    p(doc,'For FOAI, the report distinguishes the system’s stored constraints from a completed intelligent matcher. Role and experience enums and skill arrays give the system a useful representation for a future CSP. The implemented discovery function currently filters listings with Boolean conditions. It does not solve a CSP, score alternatives, rank matches, or apply machine learning. Presenting that limitation directly protects the technical credibility of the project and gives an achievable next implementation target.')
    heading(doc,'6.2 Recommended Future Work',2)
    bullets(doc,['Implement an explicit candidate-to-team matcher with declared variables, domains, hard constraints, soft preferences, and an explainable selection result.','Normalize profile and team requirement field names so client components use requiredRole and requiredExperience consistently.','Move filtering and pagination to the server when data volume grows, then expose stable query parameters and test the API contract.','Add session ownership checks to profile and application mutations; validate post bodies with the imported Zod schema.','Repair and monitor the deployed /api/teams service, including a useful 200 success response and graceful empty-state behavior.','Add integration tests for route handlers and end-to-end tests for authentication gates, invalid forms, filtering, favorite toggling, and responsive navigation.','Use a dedicated non-production test account for safe screenshot capture and protected workflow verification.'])
    heading(doc,'6.3 Future FOAI Matching Design',2)
    p(doc,'A next version can treat each open team position as a variable. Its candidate domain should include active profiles that meet basic eligibility criteria. Hard constraints can enforce the required role, skill coverage, availability, and one-application-per-post condition. Soft constraints can award extra relevant skills, compatible timezones, past collaboration preference, and balance across roles. A deterministic scoring formula should be published with every suggestion, while a CSP or branch-and-bound search can generate feasible combinations. The interface should explain the result in plain language, for example by identifying the fulfilled role, overlapping skills, and unmet preferences.')
    heading(doc,'6.4 Proposed Evaluation Plan',2)
    p(doc,'A future matcher should be evaluated with a controlled, non-production dataset rather than a claim of accuracy without ground truth. The dataset can contain profiles with declared roles, skills, experience, timezone, and availability, together with team requirements. Test cases should include an exact skill match, a role match with missing skills, multiple feasible candidates, an empty candidate domain, and conflicting hard constraints. Each case should record the input, generated feasible set, score or objective value where applicable, and the final explanation presented to the user.')
    p(doc,'The first implementation can remain explainable and deterministic. It can filter candidates by hard constraints, compute skill coverage as the count of required skills that overlap a candidate profile, apply documented bonuses for optional preferences, and sort by score with a stable secondary key. A subsequent team-level solver can select multiple users jointly and reject a combination when required roles are duplicated or a required role is absent. This staged approach makes the transition from a discovery filter to an FOAI matching module testable, reviewable, and appropriate for student project evidence.')
    heading(doc,'6.5 Acceptance Criteria for the Next Release',2)
    p(doc,'The next release should not claim intelligent matching until it satisfies a small, verifiable acceptance set. First, a request must identify its required role, experience level, and skills using the same field names as the database schema. Second, a profile candidate must be evaluated only after the server confirms that the candidate is eligible to view or apply to that request. Third, every generated recommendation must expose the hard constraints that passed, the optional preferences that influenced order, and the reason any candidate was excluded. Fourth, the deployed team endpoint must return either a documented empty collection or a successful collection response; an internal error must be observable through monitoring and test coverage.')
    p(doc,'A suitable test fixture can use five profiles and two team requirements. It should prove that a missing hard skill excludes a profile, a complete skill overlap ranks above a partial optional overlap, a duplicate application is rejected, and an empty domain produces a clear result. The test suite should run against a disposable PostgreSQL database and should assert the response body as well as status codes. A browser test can then verify that the explanation is visible to the participant without exposing another user’s private email, resume, or authentication token. These criteria connect the FOAI formulation to implementable software behavior.')
    heading(doc,'6.6 Implementation Milestones',2)
    p(doc,'The system can be improved in small, evidence-driven milestones. The first milestone is data-contract repair: use requiredRole and requiredExperience consistently in the Prisma model, create form, detail page, and filter logic. The second is service reliability: identify the root cause of the deployed team-list HTTP 500 response, add structured error logging, and cover the success, empty, and error cases with a route-handler test. The third is authorization hardening: derive mutable user identifiers from the current session rather than accepting them from the client. Each milestone reduces a concrete failure mode before the project adds a more complex matching algorithm.')
    p(doc,'The next milestone can introduce a pure matching function with no network dependency. Its inputs should be a normalized team requirement and a collection of candidate profiles; its output should be a stable array of result objects containing feasible status, matched skills, unmet hard constraints, optional-preference score, and explanation text. Unit tests can specify a small candidate fixture and assert exact result order. Only after this function is stable should it be exposed through a protected API route and added to the user interface. This sequence keeps the FOAI claim connected to executable, inspectable behavior.')
    table(doc,['MILESTONE','DELIVERABLE','EVIDENCE OF COMPLETION'],[
        ('Data contract repair','Shared role and experience field types','Form submission, API response, and filter tests use one name.'),('Team service reliability','GET /api/teams success and error handling','Deployment returns 200 or a documented empty array.'),('Authorization hardening','Session-derived ownership checks','Negative tests reject mismatched user identifiers.'),('Rule matcher','Pure deterministic matching function','Fixture tests show feasible set and stable ordering.'),('CSP extension','Constraint model and explanation UI','Integration tests demonstrate hard and soft constraints.')],[1.25,2.0,2.4])
    heading(doc,'6.7 Documentation and Deployment Checklist',2)
    p(doc,'The final stage of the project should verify that the deployed environment, source repository, and submitted documentation agree. The deployment should expose the same public routes that are described in the report, and every route handler should use the same schema fields named in the client forms. Public information may be indexed for discovery, but protected data such as resumes, account tokens, and private contact information must remain behind an authenticated session. A server error must be treated as a release issue and not as an empty result. This checklist gives the project a repeatable handoff process for future versions.')
    p(doc,'Before deployment, the team should run the unit suite, add route-handler tests for the team and application endpoints, and use a non-production account to complete safe browser tests. After deployment, the team should confirm the response code for the landing page, team directory, external hackathon directory, and protected dashboard redirect. The report should then be updated only with results that were actually observed. Keeping source evidence, deployment evidence, and user-interface evidence separate avoids overstating the work completed by the current version.')
    table(doc,['CHECK','EXPECTED EVIDENCE','CURRENT STATUS'],[
        ('Schema consistency','One shared role and experience naming contract','Needs implementation alignment.'),('Public routes','200 responses for intended public pages','Landing and external APIs observed.'),('Protected routes','Redirect or authorization result without data leak','Redirect behavior observed.'),('Team discovery','Successful list response or explicit empty state','Deployment returned HTTP 500.'),('UI evidence','Genuine deployed-interface captures with captions','13 captures embedded; no controlled multi-viewport test.')],[1.4,2.5,1.75])

def add_refs(doc):
    chapter(doc,7,'REFERENCES')
    p(doc,'',first=False,after=20)
    refs=[
        '[1] Auth.js, "NextAuth.js documentation," 2026. [Online]. Available: https://authjs.dev. Accessed: Oct. 2026.',
        '[2] R. Barták, "Constraint satisfaction problem," in Encyclopedia of Artificial Intelligence, 2nd ed., Wiley, 2009.',
        '[3] R. Dechter, Constraint Processing. San Francisco, CA: Morgan Kaufmann, 2003.',
        '[4] T. F. Gonzalez, Ed., Handbook of Approximation Algorithms and Metaheuristics. Boca Raton, FL: CRC Press, 2007.',
        '[5] T. Lappas, K. Liu, and E. Terzi, "Finding a team of experts in social networks," in Proceedings of the 15th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, 2009, pp. 467-476.',
        '[6] Next.js, "Next.js 14 App Router documentation," 2024. [Online]. Available: https://nextjs.org/docs/14/app. Accessed: Oct. 2026.',
        '[7] PostgreSQL Global Development Group, "PostgreSQL documentation," 2026. [Online]. Available: https://www.postgresql.org/docs/. Accessed: Oct. 2026.',
        '[8] Prisma, "PostgreSQL database connector," 2026. [Online]. Available: https://www.prisma.io/docs. Accessed: Oct. 2026.',
        '[9] Raghul2808, "Synapse source repository," GitHub. [Online]. Available: https://github.com/Raghul2808/Synapse. Accessed: Oct. 2026.',
        '[10] Synapse, "Deployed application," Vercel. [Online]. Available: https://synapse-livid-gamma-14.vercel.app/. Accessed: Oct. 2026.',
        '[11] Zod, "TypeScript-first schema validation," 2026. [Online]. Available: https://zod.dev. Accessed: Oct. 2026.'
    ]
    for ref in refs:
        q=doc.add_paragraph(); q.paragraph_format.first_line_indent=Inches(0); q.paragraph_format.line_spacing=1.0; q.paragraph_format.space_after=Pt(3); r=q.add_run(ref); font(r,11)

def write_manifests(s):
    ASSETS.mkdir(exist_ok=True); (ASSETS/'screenshots').mkdir(exist_ok=True)
    manifest='filename,URL,page title,viewport size,state,result,limitations\n'
    captured=[
        (s['landing_dark'].name,'https://synapse-livid-gamma-14.vercel.app/','Synapse','1920x1080','dark-theme landing hero','CAPTURED','User-supplied genuine deployed-interface capture.'),
        (s['landing_light'].name,'https://synapse-livid-gamma-14.vercel.app/','Synapse','1920x1080','light-theme landing hero','CAPTURED','User-supplied genuine deployed-interface capture.'),
        (s['landing_collaboration'].name,'https://synapse-livid-gamma-14.vercel.app/','Synapse','1899x858','landing collaboration section','CAPTURED','User-supplied genuine deployed-interface capture.'),
        (s['landing_workflow'].name,'https://synapse-livid-gamma-14.vercel.app/','Synapse','1770x1007','landing workflow and FAQ','CAPTURED','User-supplied genuine deployed-interface capture.'),
        (s['signup'].name,'https://synapse-livid-gamma-14.vercel.app/signup','Signup | Synapse','1912x1080','registration choices','CAPTURED','User-supplied genuine deployed-interface capture.'),
        (s['support_widget'].name,'https://synapse-livid-gamma-14.vercel.app/','Synapse','514x788','opened support widget','CAPTURED','User-supplied genuine deployed-interface capture.'),
        (s['profile'].name,'https://synapse-livid-gamma-14.vercel.app/dashboard/profile','Profile | Synapse','1505x991','authenticated profile','CAPTURED','User-supplied genuine deployed-interface capture.'),
        (s['profile_navigation'].name,'https://synapse-livid-gamma-14.vercel.app/dashboard/profile','Profile | Synapse','354x405','dashboard navigation','CAPTURED','User-supplied genuine deployed-interface capture.'),
        (s['hackathon_directory'].name,'https://synapse-livid-gamma-14.vercel.app/hackathons','Synapse','1920x1005','external directory cards','CAPTURED','User-supplied genuine deployed-interface capture.'),
        (s['team_filters'].name,'https://synapse-livid-gamma-14.vercel.app/teams','Synapse','1920x993','team filters and cards','CAPTURED','User-supplied genuine deployed-interface capture.'),
        (s['team_request_form'].name,'https://synapse-livid-gamma-14.vercel.app/findmember','Find Member | Synapse','1158x1026','team request form','CAPTURED','User-supplied genuine deployed-interface capture.'),
        (s['account_menu'].name,'https://synapse-livid-gamma-14.vercel.app/dashboard','Dashboard | Synapse','224x164','account menu','CAPTURED','User-supplied genuine deployed-interface capture.'),
        (s['application_status'].name,'https://synapse-livid-gamma-14.vercel.app/dashboard/requests','Dashboard | Synapse','1621x399','application status','CAPTURED','User-supplied genuine deployed-interface capture.')]
    rows=captured+[
        ('N/A','https://synapse-livid-gamma-14.vercel.app/','Synapse','1440/768/390','public landing','NOT CAPTURED','Browser-control runtime failed during initialization.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/teams','Synapse','1440/768/390','public team directory','NOT CAPTURED','Page HTTP 200; deployed /api/teams HTTP 500; browser capture unavailable.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/hackathons','Synapse','1440/768/390','public external directory','NOT CAPTURED','External endpoints HTTP 200; browser capture unavailable.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/login','Login | Synapse','1440/768/390','auth page','NOT CAPTURED','No login interaction performed; browser capture unavailable.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/signup','Signup | Synapse','1440/768/390','registration page','NOT CAPTURED','No production account created; browser capture unavailable.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/dashboard','Login | Synapse','1440/768/390','protected route redirect','NOT CAPTURED','Redirected to /login without session.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/findmember','Login | Synapse','1440/768/390','protected route redirect','NOT CAPTURED','Redirected to /login without session.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/favorites','Login | Synapse','1440/768/390','protected route redirect','NOT CAPTURED','Redirected to /login without session.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/dashboard/profile','Login | Synapse','1440/768/390','protected profile','NOT CAPTURED','Redirected to /login without session.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/dashboard/requests','Login | Synapse','1440/768/390','protected requests','NOT CAPTURED','Redirected to /login without session.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/settings','Login | Synapse','1440/768/390','protected settings','NOT CAPTURED','Redirected to /login without session.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/forgot-password','Forgot Password | Synapse','1440/768/390','password recovery','NOT CAPTURED','Public route; browser capture unavailable.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/reset','Reset | Synapse','1440/768/390','password reset','NOT CAPTURED','Public route; token workflow was not exercised.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/new-password','New Password | Synapse','1440/768/390','password reset','NOT CAPTURED','Public route; token workflow was not exercised.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/new-verification','New Verification | Synapse','1440/768/390','verification','NOT CAPTURED','Public route; browser capture unavailable.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/verify-email','Login | Synapse','1440/768/390','verification route','NOT CAPTURED','Redirected to /login in deployed observation.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/signup/onboarding','Signup | Synapse','1440/768/390','onboarding','NOT CAPTURED','No account created; browser capture unavailable.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/signup/verify','Signup | Synapse','1440/768/390','signup verification','NOT CAPTURED','No account created; browser capture unavailable.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/teams/[id]','Dynamic team detail','1440/768/390','dynamic team detail','NOT CAPTURED','Requires an existing record identifier; live list endpoint returned HTTP 500.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/error','Error | Synapse','1440/768/390','error page','NOT CAPTURED','Source-discovered route; browser capture unavailable.'),
        ('N/A','https://synapse-livid-gamma-14.vercel.app/sentry-example-page','Sentry Example | Synapse','1440/768/390','Sentry example','NOT CAPTURED','Source-discovered route; browser capture unavailable.')]
    for row in rows: manifest += ','.join('"'+str(x).replace('"','""')+'"' for x in row)+'\n'
    (ASSETS/'screenshot_manifest.csv').write_text(manifest,encoding='utf-8')
    (ASSETS/'route_inventory.csv').write_text(manifest,encoding='utf-8')
    (ASSETS/'screenshots'/'README.md').write_text('This folder contains 13 user-supplied genuine captures of the deployed Synapse interface. Browser automation remained unavailable in the report environment; no synthetic or substitute application screenshots were created. See screenshot_manifest.csv.\n',encoding='utf-8')

def main():
    d=build_diagrams(); s=copy_user_screenshots(); write_manifests(s)
    shutil.copy2(REF, OUT)
    doc=Document(OUT); clear_body(doc); set_styles(doc)
    add_cover(doc); add_certificate(doc); add_front(doc); add_ch1(doc); add_ch2(doc); add_ch3(doc,d); add_ch4(doc,s); add_ch5(doc,d); add_ch6(doc); add_refs(doc)
    # Word refreshes fields when opened; page field is preserved for native editing.
    settings=doc.settings.element; upd=OxmlElement('w:updateFields'); upd.set(qn('w:val'),'true'); settings.append(upd)
    doc.save(OUT)
    print(OUT)

if __name__=='__main__': main()
