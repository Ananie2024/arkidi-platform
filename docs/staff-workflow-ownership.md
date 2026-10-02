# Staff Workflow Ownership

The screens and API permissions in this document define the current operational owners. All parish-owned records are constrained to the authenticated user's parish or deanery by the API; the active parish selector is a UI convenience and is not an authorization boundary.

| Workflow | Operational owner | Read / submit roles | Scope |
| --- | --- | --- | --- |
| Parish ministries and lay groups | Parish priest | Auditors can read; parish priest creates; archdiocesan IT and Chancellor administer | Required parish |
| Councils and commissions | Parish priest or Chancellor | Auditors can read; priest/Chancellor create and maintain | Parish, deanery, or archdiocese as assigned; parish UI creates parish bodies |
| Meeting schedule and minutes | Parish secretary or ministry leader | Auditors can read; secretary/leader schedule, update, and record minutes | Meeting's parish; linked council/commission must agree with the meeting parish |
| Pastoral survey design and lifecycle | Parish priest or Chancellor | Auditors can read; secretary submits scoped parish response; priest/Chancellor create, activate, and close | Parish UI creates parish surveys; parish and deanery users can see applicable broader-scope surveys in their jurisdiction |
| Clergy appointment and decree record | Chancellor | Auditors can read; Chancellor or Super Admin records appointments | Appointment parish is checked; readers see assignments only for parishes in their jurisdiction |

Records created or amended through these workflows use the existing audit log events in the domain services. The pilot should name the parish priest, secretary, and ministry lead who own day-to-day updates before enabling these write roles for production accounts.
