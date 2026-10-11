# Synapse FOAI Project Report QA Summary

## Final artifacts

- `Synapse_FOAI_Project_Report.docx`
- `Synapse_FOAI_Project_Report.pdf`
- `Synapse_FOAI_Report_Package.zip`

## Document checks

- Final PDF page count: 35 pages, within the required 30-40 page range.
- Page size: A4 (595.304 x 841.89 points).
- General body format: Times New Roman 14 pt with 1.5 line spacing; margins are 1.25 inches left and 1 inch on the remaining sides. The abstract is one page with double line spacing.
- Student details checked: RAGHUL M (2116240701409) and RITHESH MADHAV S (2116240701428).
- The supplied architecture image is included as Figure 3.1. Verified implementation diagrams and 13 genuine user-supplied Synapse UI captures are included separately.
- The final PDF was rendered to 35 PNG pages and every page was visually inspected in grouped raster reviews. No clipped text, overlap, broken table, malformed image, or blank page was found.
- The only contents page is the supplied-format Table of Contents on PDF page 4. No List of Figures, List of Tables, abbreviations list, or additional contents page is present.
- The Table of Contents has an outer border and spaced columns; it is the only contents structure.
- Footer numbering is a plain Arabic number on every page (1 through 35), with no "Page" prefix. A thin page border is applied on every page.
- Chapter start pages in the final PDF: 1 at page 5, 2 at page 7, 3 at page 9, 4 at page 16, 5 at page 23, 6 at page 30, and 7 at page 35. The static table of contents reflects these pages.

## Website and screenshot evidence

- Source-discovered routes: 21 page routes plus 10 route handlers. The screenshot manifest records 13 user-supplied captured UI states plus source-discovered route status.
- HTTP-inspected deployed routes: public and protected routes were checked where safely accessible. Public routes returned their inspected page responses; protected routes redirected to `/login` without an authenticated session.
- Captured screenshots: 13 genuine user-supplied deployed-interface captures are embedded as Figures 4.1 to 4.13. They cover dark and light landing states, sign-up, support widget, profile, dashboard navigation, external directory, team filtering, team request form, account menu, application status, collaboration content, and workflow/FAQ content.
- DOCX media audit: 22 inline images total - college logo, supplied architecture, verified diagrams, and the 13 captured UI screenshots.
- No mock, synthetic, or substitute application screenshots were created. Browser automation remained unavailable, so the captures are evidence of the shown states rather than a controlled form-interaction or multi-viewport test.
- Important observed states: public landing page, public team page, public hackathon page, sign-up, authenticated profile/navigation, team request form, application status, password routes, protected-route redirects, external-directory API responses, unauthenticated favorites API response, and the failed team-list API response.

## Tests and results

| Check | Actual result | Status |
|---|---|---|
| `npm test -- --runInBand` | 1 suite and 2 tests passed | PASS |
| Deployed `/` | HTTP 200 | PASS |
| Deployed `/api/teams` | HTTP 500 | FAIL |
| Deployed Unstop, Devpost, Devfolio handlers | HTTP 200 for each | PASS |
| Protected dashboard route | Redirected to `/login` | PASS |
| Unauthenticated favorites API | HTTP 401 | PASS |
| Authenticated workflows and form interaction | No authorized session; browser runtime unavailable | BLOCKED |
| User-interface state evidence | 13 genuine user-supplied deployed captures embedded | PASS |

## Material implementation findings

- The current Prisma schema uses PostgreSQL, not MongoDB Atlas. The supplied architecture image is treated as proposed architecture, not verified deployment fact.
- The code implements client-side conjunctive filtering of team records. No Match API, CSP search, heuristic ranking, automatic recommendation, machine-learning model, or GitHub portfolio API integration was found.
- The deployed team-list endpoint returned HTTP 500 during inspection. The report does not claim team-card data was successfully demonstrated.
- The current schema uses `requiredRole` and `requiredExperience`, while visible client components read legacy `role` and `experience` names. This is documented as a risk.
- The source contains Nodemailer helpers and AWS S3 upload code, but email delivery and S3 upload were not exercised.

## Package contents

The ZIP contains the final PDF and DOCX, QA summary, 13 captured PNG screenshots, screenshot manifest, route inventory, original supplied architecture image, and editable SVG plus PNG versions of all verified diagrams. It excludes temporary renders, working files, and application source code.
