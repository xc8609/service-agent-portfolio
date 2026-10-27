# Recorded walkthrough

`walkthrough.spec.ts` drives one synthetic enquiry through the working application
and records a captioned video: first contact, facts, handling rule, Agent draft,
reviewed note, linked handoff, specialist finding, verified callback and closure
check. It is a presentation script, not a regression test; the suites in `../tests`
remain the acceptance evidence.

Record against a **fresh** disposable demo, because the script continues the seeded
`DEMO-CASE-001` enquiry. The API accepts browser origins on ports 8000 and 5173 only;
use 5173 when 8000 is already serving your own demo.

```bash
npm run build
BANK_TEST_ADMIN_URL=postgresql://... BANK_DEMO_PORT=5173 python ../../services/api/ci_serve.py
BANK_BASE_URL=http://127.0.0.1:5173 npx playwright test -c demo/playwright.config.ts --output /tmp/walkthrough
```

`BANK_TEST_ADMIN_URL` must point at an empty, disposable PostgreSQL database; the
server migrates, seeds and freezes the clock exactly as the CI browser server does.
Set `WALKTHROUGH_SHOTS=<folder>` to also save one still per caption for review.

The published files in `docs/media/` were encoded with ffmpeg from the recorded WebM:

```bash
ffmpeg -i video.webm -c:v libx264 -preset slow -crf 30 -pix_fmt yuv420p -movflags +faststart -an bank-walkthrough.mp4
ffmpeg -i video.webm -vf "fps=2,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=64:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle" bank-walkthrough.gif
```
