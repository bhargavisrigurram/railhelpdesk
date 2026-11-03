# Sources

All seven files are the original files from official Indian Railways, IRCTC and PIB websites, saved byte for byte (only the file names were changed). They were fetched on 30 Oct 2026 between 04:52 and 05:07 IST (29 Oct 2026, 23:22 to 23:37 UTC).

| File | Title | Issued by | Date | Pages and format |
|---|---|---|---|---|
| `indianrail_refund_rules_2015.html` | Revised Refund Rules w.e.f. 12.11.2015 | Indian Railways (indianrail.gov.in) | rules from 12 Nov 2015; page last modified 14 Sep 2023 | HTML, one page, a table of pre-revised vs revised rules |
| `irctc_refund_rules_jan2026.pdf` | Refund Rules and TDR Filing w.e.f. 12-NOVEMBER-2015 (updated version, PDF created 19 Jan 2026) | IRCTC | 19 Jan 2026 | PDF, 11 pages, text |
| `rb_cc10_2024_advance_reservation.pdf` | Commercial Circular No. 10 of 2024: Time limit for Advance Reservations | Railway Board, Ministry of Railways | 16 Oct 2024 | PDF, 2 pages, scanned (no text layer). Page 1 English, page 2 Hindi |
| `rb_cc08_2025_tatkal.pdf` | Commercial Circular No. 08 of 2025: Modification in Tatkal scheme | Railway Board, Ministry of Railways | 10 Jun 2025 | PDF, 6 pages. Pages 1-2 English with text; pages 3-6 Hindi, scanned |
| `rb_cc10_2025_reservation_charts.pdf` | Commercial Circular No. 10 of 2025: Preparation of first reservation charts | Railway Board, Ministry of Railways | 2 Jul 2025 | PDF, 2 pages, scanned (no text layer). Page 1 Hindi, page 2 English |
| `rb_cc08_2026_vande_bharat_sleeper_refund.pdf` | Commercial Circular No. 08 of 2026: Introduction of Vande Bharat Sleeper Express and Amrit Bharat II Express with rationalised refund provision. Encloses the Gazette notification G.S.R. 41(E) of 16 Jan 2026 (Railway Passengers (Cancellation of Ticket and Refund of Fare) Amendment Rules, 2026) | Railway Board, Ministry of Railways | 19 Jan 2026 (rules in force from 16 Jan 2026) | PDF, 5 pages, text. Pages 1-2 circular, pages 3-4 gazette in Hindi, page 5 gazette in English |
| `pib_2026-03-24_reform_express.html` | Indian Railways Announces Five New Reforms Under 'Reform Express' (Release ID 2244597) | Ministry of Railways, via Press Information Bureau (PIB Delhi) | 24 Mar 2026 | HTML, the full PIB web page. The ticketing part is under "Ticket cancellation and refund" |

## Source URLs and fetch times

| File | URL | Fetched (UTC) |
|---|---|---|
| `indianrail_refund_rules_2015.html` | https://www.indianrail.gov.in/refund_Rules.html | 2026-10-29 23:22:19 (fetched again at 23:38:56, identical) |
| `irctc_refund_rules_jan2026.pdf` | https://contents.irctc.co.in/en/REFUND%20RULES%20wef%2012-Nov-15.pdf (the same file is also at https://contents.irctc.co.in/en/RefundCancellationRules.pdf) | 2026-10-29 23:26:20 |
| `rb_cc10_2024_advance_reservation.pdf` | https://ir.indianrailways.gov.in/railwayboard/uploads/directorate/traffic_comm/Comm_Cir_2024/2024-%20CC%20No_%2010%20of%202024-%20Change%20of%20Advance%20Reservation%20Period-ARP.pdf | 2026-10-29 23:35:02 |
| `rb_cc08_2025_tatkal.pdf` | https://ir.indianrailways.gov.in/railwayboard/uploads/directorate/traffic_comm/Comm_Cir_2025/CC%2008%20of%202025.pdf | 2026-10-29 23:35:01 |
| `rb_cc10_2025_reservation_charts.pdf` | https://ir.indianrailways.gov.in/railwayboard/uploads/directorate/traffic_comm/Comm_Cir_2025/MX-M453N_20250708_161959.pdf | 2026-10-29 23:36:37 |
| `rb_cc08_2026_vande_bharat_sleeper_refund.pdf` | https://ir.indianrailways.gov.in/railwayboard/uploads/directorate/traffic_comm/Comm_Cir_2026/CC%208%20of%202026.pdf | 2026-10-29 23:36:37 |
| `pib_2026-03-24_reform_express.html` | https://www.pib.gov.in/PressReleasePage.aspx?PRID=2244597 | 2026-10-29 23:29:09 |

The Railway Board circulars are listed on the Railway Board "Commercial Circulars" pages (Traffic Commercial directorate) at https://ir.indianrailways.gov.in/railwayboard/view_section.jsp?lang=0&id=0,1,304,366,555,737.

## Timetable data (database/)

`database/rail_timetable.db` is built from the datameet "Indian Railways Data" repository, https://github.com/datameet/railways (files `trains.json`, `stations.json`, `schedules.json`, last changed 8 Aug 2016). Its README puts the data under the CC0 licence. Fetched 2026-10-29 at about 23:20 UTC. See `database/schema.md` for what the snapshot covers.
