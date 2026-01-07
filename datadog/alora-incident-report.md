---
title: Alora Incident Report
author: Adedoyinsola Ogungbesan
modified: 2026-01-05T13:51:50.358Z
tags: []
metadata:
  type: Report
time:
  live_span: 1w
template_variables: []
---


# Summary

A total of 3 incidents were declared in this reporting period dating \[January 1, 2026 to January 7, 2026\]. Of these incidents, 2 had customer impact with a mean impact duration of 42 minutes. The most common severity of incident during this period was **SEV-2 (High)** (Median Severity), incidents of this severity are defined as incidents that **re major issues affecting customers and users, often degrading a core feature (like Audio) without taking down the entire platform**. The end of this section visualizes of the number of incidents per week as well as the mean customer impact duration, each broken down by the severity of the incident.

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/ftp-im2-uza](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/ftp-im2-uza.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/ftp-im2-uza)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/f8h-2qx-hu4](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/f8h-2qx-hu4.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/f8h-2qx-hu4)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/c4t-7ws-6ai](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/c4t-7ws-6ai.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/c4t-7ws-6ai)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/c3d-hjk-rtk](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/c3d-hjk-rtk.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/c3d-hjk-rtk)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/2r3-cmp-9qz](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/2r3-cmp-9qz.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/2r3-cmp-9qz)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/28t-g59-gr8](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/28t-g59-gr8.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/28t-g59-gr8)

# Outage Tracking

During this reporting period, **2** incidents were classified as an outage (a SEV-1 or SEV-2 incident). SEV-1 incidents are defined as **critical functionality unavailable for all users (e.g., API 500 errors)**, while SEV-2 incidents are defined as **significant degradation of a core feature (e.g., Audio failing)**. Over the course of this reporting period, the portion of incidents considered to be outages has trended **upward** reaching a weekly **maximum** percentage of **66%**. The mean customer impact of these outages was **42 minutes**, reaching a weekly maximum value of **60 minutes**.

Analyzing these outages reveals the following patterns:

1. **Tight Coupling to External APIs**: Both outages (API Crash & Audio Failure) stemmed from synchronous dependencies on Vertex AI and ElevenLabs. When they hiccuped, the app crashed.

2. **Lack of Client-Side Resilience**: The frontend had no "retry logic" or "offline mode", turning minor backend errors into full user-facing outages.

To reduce the number of outages, it is recommended that the following steps are taken:

1. **Implement Circuit Breakers**: Wrap external calls in a circuit breaker to fail fast and serve cached/default content instead of crashing.

2. **Asynchronous Audio**: Move TTS generation to a background queue so it doesn't block the main analysis flow.

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/cxb-nai-95n](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/cxb-nai-95n.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/cxb-nai-95n)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/76h-bvj-28j](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/76h-bvj-28j.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/76h-bvj-28j)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/bny-jkf-2tz](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/bny-jkf-2tz.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/bny-jkf-2tz)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/6b3-d6d-pr8](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/6b3-d6d-pr8.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/6b3-d6d-pr8)

# Response Breakdown

---

### Detection & Resolution Metrics

Incidents were mostly commonly detected by **Automated Datadog Monitors (APM via `ddtrace`)**.

For all incidents during this period:

* **Mean Time to Repair (MTTR)** was **45 minutes**.

* **Mean Time to Resolve (MTTRe)** was **2 hours 15 minutes**.

_Definitions:_

* _Time to Repair_: Time between incident creation and end of customer impact.

* _Time to Resolve_: Time between incident creation and full resolution/closure.

Over the course of this reporting period:

* **Mean Time to Repair** trended **\[downward\]** with a weekly **minimum** value of **15 minutes**.

* **Mean Time to Resolve** trended **\[downward\]** with a weekly **minimum** value of **2 hours**.

### Response Improvements

Investigating the response characteristics further, it is recommended that the following action items are prioritized to improve the response process:

1. **Automated Rollback**: The "Backend API Outage" took 30 mins to diagnose. An automated "Bad Deployment" monitor could have rolled it back in 5 mins.

2. **Shared Dashboards**: The Audio team struggled to see Backend logs. All teams should have access to the **"Alora Pilot - Executive Health"** dashboard in Datadog.

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/md9-5pw-qqw](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/md9-5pw-qqw.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/md9-5pw-qqw)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/kp6-v9e-g52](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/kp6-v9e-g52.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/kp6-v9e-g52)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/d7e-86b-32e](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/d7e-86b-32e.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/d7e-86b-32e)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/fy7-aij-rgd](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/fy7-aij-rgd.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/fy7-aij-rgd)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/hwp-8x8-jwk](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/hwp-8x8-jwk.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/hwp-8x8-jwk)

# Organizational & Service Breakdown

Investigating the response characteristics further, it is recommended that the following action items are prioritized to improve the response process:

During this reporting period, **Team Backend (Pilot)** responded to the most incidents (API Outage + Latency), while **Team Integration** responded to incidents with the largest mean customer impact (Audio Service Failure).

Upon reviewing with these teams, they reported facing the following challenges:

1. **Vertex AI Quota Limits**: Unpredictable rate limiting caused latency spikes (SEV-3) that were hard to reproduce in staging.

2. **Third-Party API Instability**: ElevenLabs timeouts (SEV-2) lacked robust retry logic in the initial code, causing immediate user-facing failures.

3. **Missing "Circuit Breakers"**: The frontend kept retrying failed requests, exacerbating the API Outage (SEV-1).

It is recommended that more resources are allocated to **Team Integration (Frontend/Audio)** to ensure they receive adequate support in meeting reliability goals. The proposed changes would include:

* Implementing **Exponential Backoff** for all external API calls (ElevenLabs/Gemini).

* Adding a **"Graceful Degradation"** mode (e.g., if Audio fails, just show text without erroring).

Comparatively, service **`pilot-backend`** experienced the most incidents, while service **`audio-synthesizer`** experienced incidents with the largest mean customer impact (due to long investigation times).

Additional review of these services reveals the following action items that should be taken to prevent future incidents involving these services:

1. **Implement Region Failover**: Configure Vertex AI to failover from `us-central1` to `us-east1` if latency > 5s (SEV-3 Mitigation).

2. **Add Health Checks**: Ensure

0. **Background3D** assets are cached or proxied to prevent loading timeouts (Proactive SEV-2 Prevention).

2. 

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/kmn-cei-29b](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/kmn-cei-29b.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/kmn-cei-29b)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/s6v-h5s-mk6](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/s6v-h5s-mk6.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/s6v-h5s-mk6)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/r2u-k5b-3zw](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/r2u-k5b-3zw.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/r2u-k5b-3zw)

[![https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/db9-pqj-2ws](https://p.us5.datadoghq.com/s/image/e022494b-d508-11f0-be9a-8a035bedc65e/db9-pqj-2ws.png)](https://us5.datadoghq.com/s/e022494b-d508-11f0-be9a-8a035bedc65e/db9-pqj-2ws)

<!--Some widget snapshots failed to export, so we’ve included their JSON definitions instead. If you reimport this markdown file to Datadog, widgets will display as expected.-->

```dd-widget
{
  "id": "tehk28f8",
  "type": "notebook_cells",
  "attributes": {
    "definition": {
      "query": {
        "data_source": "logs",
        "storage": "hot",
        "name": "datasource_1",
        "columns": [
          {
            "column": "timestamp",
            "type": "timestamp"
          },
          {
            "column": "host",
            "type": "string"
          },
          {
            "column": "service",
            "type": "string"
          },
          {
            "column": "message",
            "type": "string"
          }
        ],
        "time_window": {
          "from": 1767009575792,
          "to": 1767614375792
        }
      },
      "type": "analysis_data_source"
    }
  }
}
```