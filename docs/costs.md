# Cost disclosure

Checked 2026-10-14. Currency: USD. This is a resource-cost explanation, not a
measured billing total or a promise that the project is free.

- **NVIDIA NIM:** the app uses the user's NVIDIA developer endpoint/key, not paid
  OpenAI inference. The assignment lists NIM developer keys as its zero-cost
  alternative. Actual entitlement, credits, quotas, and provider terms are
  account-specific; no NVIDIA billing statement was inspected.
- **Tavily:** the deployed server is in capped keyless mode. No authenticated
  Tavily paid plan is configured. Keyless calls can be rate-limited or unavailable.
- **Open-Meteo:** no key or paid plan is configured for this coursework use.
- **Cloud Run:** one vCPU, 512 MiB, request-based CPU allocation, zero minimum
  instances and a maximum of one instance for the revision. Idle scale-to-zero
  avoids a permanently provisioned instance; startup, requests, and networking
  can still incur usage. Instance limits are scaling settings, not spending caps.
- **Artifact Registry and Secret Manager:** image storage, active secret versions,
  secret access, and applicable network transfer can incur charges after their
  free allowances. Repeated preparation adds image tags and secret versions.
- **Cloud Build:** the API is enabled to match the assignment prerequisites;
  the submitted image was built locally with Docker and pushed directly. No
  Cloud Build job was submitted by this workflow.

For illustration, Google's published request-based list rates are $0.000024 per
active vCPU-second, $0.0000025 per GiB-second, and $0.40 per million requests
(before free tier/credits and other charges). At those rates, a hypothetical
600-second request using 1 vCPU and 0.5 GiB is about $0.0152 for compute and its
single request. This is an estimate, excludes startup boost/network/storage/
secrets/model usage, and is not the measured price of a verification run.
The shared monthly Cloud Run free tier lists 180,000 vCPU-seconds, 360,000
GiB-seconds, and two million requests. Eligibility/usage is aggregated by billing
account; education-credit status and remaining credit were not verified.

Sources: [Cloud Run pricing](https://cloud.google.com/run/pricing),
[Artifact Registry pricing](https://cloud.google.com/artifact-registry/pricing),
[Secret Manager pricing](https://cloud.google.com/secret-manager/pricing).
Check Billing Reports for project jd-assignment1-599 for the actual total and
retain the deployed service until grading is complete, as the assignment requires.
