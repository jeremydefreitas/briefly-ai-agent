# Instructional prompt log

Record substantive user instructions chronologically for the assignment documentation.
Preserve the user's wording, redact any credentials, and keep assignment source requirements separate from user requests.

## 2026-10-12 - Workspace and API setup

**User request (verbatim):**

> Lets work on this assignment. Set up the workspace. We will use the OpenAI Agents SDK with my OpenAI API key. Create a .env for me to put my keys into as well. Lets start by setting up the repo, installing the sdk and trying to hit the OpenAI API to confirm if my key works. Store all main instructional prompts like this in a prompts.md file for later so we can include in the assignment documentation.

**Scope:** Initial Python repository setup, dependency installation, local credentials template, and a real API smoke check. The attached assignment describes future deliverables; it is not a request to deploy or complete them during this setup step.

**Smoke-check prompts:**

- Agent instructions: `Reply with exactly OPENAI_API_OK and nothing else.`
- Agent input: `Confirm this connection works.`

## 2026-10-12 - Review assignment and current workspace

**User request (verbatim):**

> We're working on Assignment 1 (see the pdf in the directory). The prompt has already been completed. Read the assignement discription, examine the current directory state and let me know your understanding.
>
> Prompt already executed:
> Lets work on this assignment. Set up the workspace. We will use the OpenAI Agents SDK with my OpenAI API key. Create a .env for me to put my keys into as well. Lets start by setting up the repo, installing the sdk and trying to hit the OpenAI API to confirm if my key works. Store all main instructional prompts like this in a prompts.md file for later so we can include in the assignment documentation.

**Scope:** Read the assignment requirements and inspect existing setup; report understanding without implementing later milestones or sending a new API request.

## 2026-10-12 - Keep Python and test configured API key

**User request (verbatim):**

> ok no lets stick to python and follow how things are done in the assignment doc. i put my api key in .env, how can we test it?

**Scope:** Continue with the existing Python setup and run the existing Agents SDK smoke check using local credentials.

## 2026-10-12 - Switch model backend to NVIDIA NIM

**User request (verbatim):**

> ok we will use NVIDIA Nim then with OpenAI agents sdk, make the code changes

**Follow-up instruction (verbatim):**

> we will remove the old open ai key, no need for a check

**Scope:** Retain Python and the OpenAI Agents SDK; configure the assignment's NVIDIA endpoint and Nemotron 3.5 Lightning model through the Chat Completions adapter. Remove the previous local key and leave its field blank for the NVIDIA key; do not add a provider-specific key-format check.

**Updated smoke-check prompts:**

- Agent instructions: `Reply with exactly NVIDIA_NIM_API_OK and nothing else.`
- Agent input: `Confirm this connection works.`

## 2026-10-12 - Set up the client and chat route

**User request (verbatim):**

> Ok it works, let remove the test script now and start setting up the client and /chat route. Keep the code clean and efficient

**Scope:** Remove the standalone smoke-check script, add a reusable NVIDIA-backed OpenAI Agents SDK client, and implement the assignment's POST /chat contract with framework-native session memory. The user reported that their connection test worked; this is user-reported verification.

## 2026-10-12 - Browser chat interface at root

**User request (verbatim):**

> create a simple UI on the the apps root that allows for interacting with the agent through the frontend

**Scope:** Serve a simple browser chat interface at GET / using the existing POST /chat API. Include conversation session IDs, a new-chat action, pending/error feedback, and responsive layout.

## 2026-10-12 - Install and integrate MCP servers

**User request (verbatim):**

> Ok good, lets continue working on the backend, lets move on to installing the MCPs

**Scope:** Install the assignment-recommended filesystem and Tavily MCP servers, configure real SDK discovery/invocation, manage connections in the app lifespan, and verify integration. Filesystem access is limited to data/. Tavily can use limited keyless search/extract while its optional local API key is unset.

## 2026-10-12 - MCP status indicators and live activity

**User request (verbatim):**

> on the frontend chat interface, add indicators for the MCPs status and add live logs of whats going on so it indicates to the user when a tool is used

**Scope:** Display live MCP connection status and request-scoped operational activity, including real tool starts, completions, and failures. Keep the assignment's POST /chat JSON contract and add a streaming endpoint for the frontend.

## 2026-10-12 - Assignment progress check

**User request (verbatim):**

> Ok progress check. What is left to do in this assignment?

**Scope:** Compare current implementation and recorded verification with the assignment requirements; report outstanding work without implementing further milestones.

## 2026-10-12 - First live behavior verification checks

**User request (verbatim):**

> Ok proceed with this step

**Context and scope:** Execute the proposed first two live /chat checks: no-tool arithmetic and filesystem reading/summarization. Save real responses and operational tool events, assess outcomes, and update the process log. The exact test prompts are recorded in docs/verification/core-checks.json.

## 2026-10-12 - Verify Tavily selection and multi-step tool use

**User request (verbatim):**

> go

**Context and scope:** Continue with the next two proposed live checks: Tavily selection and a multi-step search-and-save workflow. Observe real tool calls, inspect the resulting file, and record actual outcomes.

## 2026-10-12 - Verify live memory, isolation, and recovery

**User request (verbatim):**

> yes

**Context and scope:** Proceed with the proposed memory recall, session isolation, and recovery-after-tool-error checks using live /chat requests and record actual outcomes.

## 2026-10-12 - Controlled MCP fault verification

**User request (verbatim):**

> ok go

**Context and scope:** Execute the proposed transport-interruption and malformed-response checks using a temporary fault-injection MCP server. Verify graceful handling and a successful follow-up request, record actual evidence, and fix any demonstrated backend issue.

## 2026-10-13 - Review user-added Open-Meteo integration

**User request (verbatim):**

> im trying to add open-meteo myself, look at my work so far and tell me whats missing

**Scope:** Review the user's changes and identify blockers and remaining integration work. Do not install packages or change implementation on the user's behalf.

## 2026-10-13 - Complete Open-Meteo integration

**User request (verbatim):**

> do whats needed

**Context and scope:** Complete the reviewed Open-Meteo MCP integration: reliable local launch, pinned dependency, updated tests/docs, real discovery/invocation, and live weather selection through /chat. Preserve the user's work and use the existing MCP/status/activity architecture.

## 2026-10-13 - Redesign frontend as a briefing generator

**User request (verbatim):**

> Ok do it. Redesign the look of the front end and make it explanitory to the user on how they can use this tool in a useful way

**Context and scope:** Build a guided briefing frontend using the existing /chat/stream API, session memory, and MCP status/activity. Include briefing categories, region/timeframe/focus, explanatory examples, readable results, follow-ups, and export actions. Keep assignment backend contracts and MCP implementation intact.


## 2026-10-13 — Briefing failure investigation

> failing before response


## 2026-10-13 — Frontend refinement

> Ok it works, tighten the UI, add text formatting, may sectioning for weather with icons etc and make the overall look of the page look less AI generated


## 2026-10-14 — Docker packaging

Context: Proceed with the next assignment step: multi-stage Docker packaging and container verification.

> ok lets do the next step


## 2026-10-14 — Cloud Run deployment

Context: Proceed from the verified Docker packaging to Cloud Run deployment.

> ok lets move to next step

> i want to use a different gcloud account, also i dont have a project configred on gcp yet

Selected project after account setup:

> jd-assignment1-599

## 2026-10-13 — Briefing-generator direction (recorded during final review on 2026-10-14)

> Ok lets work on the frontend now. I want this to be a useful agent tool. I am thinking to make the frontend a breifing genterator so a user can ask for different type of breifings for ex: Give me a breifing of Today's global political news. The agent will use the MCPs to put together a relevant briefing. Can we do this without affecting the core assignment code?

## 2026-10-14 — Portfolio frontend redesign

> can we make the frontend look better? it looks really slapped together and vibe coded. also the briefing output doesnt look great. use your design skill and moden design language. a potential employer looking at this page should be able to understand the project fully and the value of the tool and be impressed by the output. add the reaearch activities to the bottom of the text field as well as live updating tags like other ai sites do it. use like a green color for that


## 2026-10-14 — Single-chat workspace refinement

> Looks good but lets refine more. there is some white space in the breifing section that can be removed. Lets remove the left brief generator section, instead lets add description on how the tool works in the main chat section with some buttons for example breifs that will prefil the text area with a prompt that asks for a brief. The main call to action text should be something like Ask a question or ask for a brief. Dont add too much instructions or irrelevant details. Clear, inutive design.


## 2026-10-14 — Switch to Lightning

Context: Use Nemotron Lightning instead of Ultra locally and on the deployed app.

> change to lightning.


## 2026-10-14 — Verify tool reliability and model choice

> fix the tool reliability issue and update docs that stated ultra to lightning. if the reliability issue is fixed by changing to ultra lets change back


## 2026-10-14 — Assignment deployment URL

> from the assignment doc its seem that our deployment url should conform to this: https://csci599-a1-xxxxxxxxxx-uw.a.run.app. Can you change ours to https://csci599-a1-briefly-uw.a.run.app ?


## 2026-10-14 — Match assignment service name exactly

> lets stick to what the assignment wants actually, https://csci599-a1-xxxxxxxxxx-uw.a.run.app


## 2026-10-14 — GitHub and final submission preparation

> clean up repo to prepare for github push. also finalize everything for assignment submission
