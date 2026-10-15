# Portfolio frontend verification

Verified locally and on Cloud Run on 2026-10-14 (America/Los_Angeles).

## Changes

Forest-green research workspace, an explanatory product introduction, capability
summary, report reader, guided setup, and a project/API overview. Briefings use
editorial typography, summary/development/implication/source sections, weather
tables, numbered reference links, source navigation, and reading-time metadata.
The composer contains live running/completed green tags and an expandable activity
log. Retry/failure states have distinct styling; failed tools are not relabeled as
successful when the model returns a response. The initial report is explicitly
an illustrative format preview, not fabricated live research.

## Deterministic verification

- All 23 Python backend tests passed in 17.937 seconds.
- Expanded Node frontend tests passed for streaming, safe formatting, numbered
  reference links, report hierarchy, progress/failure tags, session behavior,
  copy/download, and explicit workspace saving.
- Headless Chrome checks passed at 1440px desktop and 390/768px mobile widths,
  with no horizontal overflow or page script errors. Guided submission, sources
  navigation, report/source sections, running/failure/completed tags, weather
  formatting, and reset were exercised using intercepted fixtures. These browser
  fixtures do not demonstrate live model reasoning or reference weather values.
- Inspected desktop, rendered report, and mobile screenshots; refined mobile
  project-label wrapping and preserved the generate button icon after completion.
- Formatter and browser tooling were installed only under ignored tmp/. No
  browser libraries or other frontend runtime dependencies were added.

## Actual deployed browser check

- Service: https://briefly-2ez6etscva-uw.a.run.app
- Ready revision: briefly-00002-ds6, serving all traffic.
- Submitted the Weather & travel guided form in actual Chrome with Los Angeles,
  Today, quick depth, and a focus on conditions/rain/wind/outdoor advice.
- No HTTP requests or responses were intercepted in this check. Real activity
  recorded successful geocoding and weather_forecast calls followed by a final
  structured response. The displayed response contained Conditions, Rain & wind,
  Travel notes, and Sources sections.
- Live tags showed Location resolved, Forecast retrieved, and Response ready;
  no running tag remained after completion. The page reported 35 seconds and
  178 words for this request. No page script errors were recorded.
- Actual events, final output, headings, visible tag states, and browser-error
  results are in [live browser evidence](frontend-portfolio-live.json). This
  establishes the browser/tool/formatting path, not independent verification of
  every generated weather claim or source URL.

[Desktop layout reference](images/portfolio-desktop.png) (intercepted UI fixtures)
and [actual deployed weather result](images/portfolio-live-weather.png).

The backend API, MCP configuration, deployed model, secret versions, and resource
settings were preserved. The previous deployment result is retained under
`docs/deployment/revisions/`; earlier cloud verification reports describe their
original revision and remain historical evidence.
