# IBM Bob — Task Contributions

This document lists the tasks IBM Bob completed during development of the astrophotography engine, with a short summary of each and a link to the full task transcript.

> **Disclaimer:** Not all tasks are listed here. Some tasks were deleted during development to keep the record focused — specifically tasks that were split into smaller pieces, superseded by a follow-up task, or were purely exploratory with no lasting output. Every task listed below represents a distinct, self-contained unit of work.

---

## May 1, 2026

### [Initial Project Planning](bob-contributions/bob_task_may-1-2026_3-20-17-pm.md)
*3:20 PM*

Clarified requirements for the astrophotography target suggestion engine through a structured Q&A. Established the core stack — Astro frontend, Python FastAPI backend, Messier Catalogue (110 objects), beginner-friendly focus, weather and moon phase integration — and produced the initial `ASTROPHOTOGRAPHY_ENGINE_PLAN.md`.

---

### [Frontend & .gitignore Review](bob-contributions/bob_task_may-1-2026_3-30-26-pm.md)
*3:30 PM*

Reviewed the Astro frontend scaffold and `.gitignore`. Identified two issues: the `@astrojs/react` integration was installed but not registered in `astro.config.mjs`, and the CSS import path in `index.astro` pointed to a non-existent file name.

---

### [Python Setup Troubleshooting](bob-contributions/bob_task_may-1-2026_3-42-31-pm.md)
*3:42 PM*

Diagnosed a "command not found: python / python3" error on macOS. Confirmed Python was not on the system PATH and recommended installing it via Homebrew (`brew install python3`).

---

### [Development Roadmap Check](bob-contributions/bob_task_may-1-2026_4-45-18-pm.md)
*4:45 PM*

Reviewed the outstanding todo list and summarised what was next up for implementation, helping prioritise the next phase of development.

---

## May 2, 2026

### [Backend Server Diagnosis](bob-contributions/bob_task_may-2-2026_7-50-50-pm.md)
*7:50 PM*

Investigated why the backend server could not start despite two `./start.sh` terminals running. Checked for a port 8000 conflict using `lsof`, reviewed the `start.sh` script, and verified backend dependencies were installed.

---

### [Location Search Investigation](bob-contributions/bob_task_may-2-2026_7-52-57-pm.md)
*7:52 PM*

Read and analysed the geocoding pipeline — `location.py`, `LocationInput.astro`, and `api.ts` — to diagnose why location searches were failing. Found both a Nominatim user-agent compliance issue and a frontend/backend endpoint mismatch.

---

### [Nominatim User-Agent Fix](bob-contributions/bob_task_may-2-2026_7-53-48-pm.md)
*7:53 PM*

Updated the Nominatim geocoder user-agent string in `backend/app/api/location.py` to include contact information (`astrophotography-target-finder/2.0 (contact@example.com)`), bringing it into compliance with Nominatim's usage policy.

---

### [Location 404 Diagnosis](bob-contributions/bob_task_may-2-2026_7-56-20-pm.md)
*7:56 PM*

Investigated a `404 Not Found` on `POST /api/location/search`. Traced the issue to a route mismatch: the frontend was calling an endpoint that did not exist; the backend's actual route was `GET /api/v1/location/geocode`.

---

### [Frontend API Endpoint Fix](bob-contributions/bob_task_may-2-2026_7-57-09-pm.md)
*7:57 PM*

Updated `frontend/src/lib/api.ts` to call the correct `GET /api/v1/location/geocode` endpoint, switching from a POST body to a query parameter (`address`).

---

### [Nominatim 403 Comprehensive Fix](bob-contributions/bob_task_may-2-2026_7-59-13-pm.md)
*7:59 PM*

Applied deeper fixes to the persistent Nominatim 403 error: added a mandatory 1-second delay between requests, improved the user-agent header, added a `Referer` header, and implemented retry logic with exponential backoff.

---

### [Switch to ArcGIS Geocoding](bob-contributions/bob_task_may-2-2026_8-04-41-pm.md)
*8:04 PM*

Replaced Nominatim with the ArcGIS geocoding service in `location.py`. ArcGIS requires no API key, has more generous rate limits, and no strict user-agent requirements — resolving the recurring 403 issues definitively.

---

### [Equipment Validation Investigation](bob-contributions/bob_task_may-2-2026_8-06-46-pm.md)
*8:06 PM*

Diagnosed a spurious "please enter equipment details" error that appeared even when all fields were filled in. Traced it to an overly strict validation check that only looked for `aperture_mm` and ignored the alternative `f_number` input mode.

---

### [Equipment Validation Fix](bob-contributions/bob_task_may-2-2026_8-07-08-pm.md)
*8:07 PM*

Fixed the validation logic in `frontend/src/pages/index.astro` to accept either `aperture_mm` or `f_number`, and to also validate the required sensor dimension fields.

---

### [SkyMap Component Creation](bob-contributions/bob_task_may-2-2026_8-13-14-pm.md)
*8:13 PM*

Created `frontend/src/components/SkyMap.tsx` — an interactive React component rendering a polar plot of the night sky using Chart.js. Features include target markers colour-coded by difficulty, moon position, altitude circles (30°/60°/90°), cardinal direction labels, and a time slider to animate target movement across the observation window.

---

### [Development Stage Review](bob-contributions/bob_task_may-2-2026_8-16-38-pm.md)
*8:16 PM*

Reviewed the current state of the project against the original plan, confirming which phases were complete and identifying what work remained.

---

### [SkyMap Debug & Fix](bob-contributions/bob_task_may-2-2026_8-34-06-pm.md)
*8:34 PM*

Debugged the SkyMap component not rendering on the `/skymap-demo` page. Investigated Chart.js registration, the `client:load` Astro island directive, required prop passing, and TypeScript compilation errors, then implemented the fix.

---

### [Next Steps Planning](bob-contributions/bob_task_may-2-2026_8-54-09-pm.md)
*8:54 PM*

Reviewed the application's completed features and outstanding gaps, then recommended and prioritised the next set of features to implement.
