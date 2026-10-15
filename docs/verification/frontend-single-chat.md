# Single-chat frontend verification

Verified on 2026-10-14 (America/Los_Angeles).

## Interface

Removed the sidebar generator, its form state and event handlers, and the large
illustrative preview. The chat contains the requested question/brief CTA, a short
explanation, and three example briefing buttons. Examples prefill editable text
without sending. The message area grows with content instead of reserving a fixed
height, and report content uses its available width. Project details are collapsed;
tool connectivity is a compact row. Green activity remains under the composer.

Freeform request guidance retains current date/time, bounded research, source
handling and weather formatting. The agent still chooses tools; no application
keyword router was introduced. No backend, model, secret, or resource change.

## Local verification

Expanded Node frontend checks passed for example prefill, no automatic request,
editing before sending, all example prompts, empty input, research instructions,
safe report rendering, session reuse/reset, exports, and progress/failure states.

Real Chrome checks with intercepted fixtures passed at 1440px desktop and
390/768px mobile widths, without horizontal overflow or script errors. The checks
confirmed no generator form, a compact initial message area under 400px, editable
prefills without submission, report/source navigation, activity tags, and reset.
Desktop/report/mobile screenshots were inspected. Those fixtures are UI tests,
not live model or weather evidence. A missing project-link ID found by the first
browser run was corrected before the passing runs.

## Deployed browser verification

- URL: https://briefly-2ez6etscva-uw.a.run.app
- Revision: briefly-00003-2xl; serving all traffic.
- Actual Chrome clicked the Los Angeles weather example, verified no automatic
  request, appended a request for fewer than 200 words, and explicitly sent it.
- Real geocoding and weather_forecast completed; a structured final report arrived.
  The Conditions, Rain & Wind, Travel Notes, and Sources sections were present.
- Terminal tags were completed, no running tag remained, and there were no browser
  script errors. No requests/responses were intercepted in this check.
- Exact prompt, events, response, headings and tag states are in
  [live evidence](frontend-single-chat-live.json). This is a UI/tool flow check;
  it does not independently validate every generated weather assertion.

[Compact desktop layout](images/single-chat-desktop.png) uses intercepted fixtures.
[Actual deployed weather result](images/single-chat-live-weather.png) is a live run.
Earlier portfolio/cloud reports retain their original revision context.
