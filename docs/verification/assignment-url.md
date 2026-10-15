# Assignment-prefixed deployment URL (historical)

Superseded by the [exact assignment service name](assignment-exact-url.md).

Previously verified public URL: https://csci599-a1-briefly-2ez6etscva-uw.a.run.app

Service: `csci599-a1-briefly`; revision: `csci599-a1-briefly-00001-clb`; region: `us-west1`. Same immutable image, Ultra model, secret reference, runtime identity, and resource settings as the preceding deployment.

The assignment PDF uses `csci599-a1` in its sample deployment and labels the submission URL format an example. Its `xxxxxxxxxx` portion represents a generated Cloud Run identifier. Google assigns this identifier; the exact requested hostname `csci599-a1-briefly-uw.a.run.app` cannot be selected. See [Google Cloud service URL documentation](https://docs.cloud.google.com/run/docs/triggering/https-request#service_url).

Public checks passed: frontend HTTP 200, all three MCPs connected, direct arithmetic, and real filesystem read with the expected first line. Verified deployed Ultra setting, readiness, traffic, and public invoker policy. [Exact live evidence](assignment-url-live.json).

Updated README, deployment preparation, deployment plan/result/runtime metadata, submission checklist, and archive URL. Original `briefly` service remains available for existing links; historical verification records retain their actual original URLs. No service was deleted.
