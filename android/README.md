# AutoApply-Agent — Android App

Jetpack Compose + Material 3 Android dashboard that connects to the AutoApply-Agent FastAPI backend.

## Features

| Tab | Description |
|---|---|
| **Scraper** | Paste a job URL, submit, poll for status, then tap "Check" to view the parsed result |
| **Resume** | Upload a LaTeX resume and view it categorized into Education, Experience, Skills, Projects |
| **Jobs** | Browse scraped jobs in a scrollable list with match scores and missing skills |
| **Auto-Apply** | Toggle auto/manual submission, start/pause/stop the agent, handle uncertain fields |
| **Dashboard** | Overview cards showing total jobs scraped, applications sent, and pending actions |

## Tech Stack

- **Kotlin 2.0** + **Jetpack Compose**
- **Material 3** with dynamic color support
- **Retrofit + Moshi** — HTTP client for the FastAPI backend
- **Room** — Local SQLite cache for offline job access
- **Hilt** — Dependency injection
- **Navigation Compose** — Bottom tab navigation

## Quick Start

### Prerequisites

- Android Studio Jellyfish (2024.1) or later
- Android SDK 34
- JDK 17

### Build

```bash
cd android
./gradlew assembleDebug
```

The APK will be at `app/build/outputs/apk/debug/app-debug.apk`.

### Run Tests

```bash
# Kotlin unit tests (no emulator needed)
./gradlew test

# Python integration tests (requires backend running)
cd .. && source .venv/bin/activate
pytest tests/test_android_integration.py -v
```

### Backend Connection

The backend runs on **AWS EC2** on port `8000`. Before building, set your EC2 public IP in:
```
app/src/main/java/com/autoapply/agent/di/NetworkModule.kt
```

Find your IP with:
```bash
ssh autoapply "curl -s http://checkip.amazonaws.com"
```

Then update the `BASE_URL` constant, e.g. `http://54.x.x.x:8000/`.

## Project Structure

```
android/
├── build.gradle.kts                # Root build config
├── settings.gradle.kts             # Project settings
├── gradle.properties               # JVM / AndroidX flags
├── app/
│   ├── build.gradle.kts            # App dependencies
│   └── src/
│       ├── main/
│       │   ├── AndroidManifest.xml
│       │   ├── res/values/         # strings.xml, themes.xml
│       │   └── java/com/autoapply/agent/
│       │       ├── AutoApplyApp.kt         # @HiltAndroidApp
│       │       ├── MainActivity.kt         # @AndroidEntryPoint
│       │       ├── data/
│       │       │   ├── local/              # Room (JobEntity, JobDao, AppDatabase)
│       │       │   ├── remote/             # Retrofit (ApiService, ApiModels)
│       │       │   └── repository/         # JobRepository
│       │       ├── di/                     # Hilt modules
│       │       └── ui/
│       │           ├── navigation/         # AppNavigation (bottom tabs)
│       │           ├── screens/            # All screens + ViewModels
│       │           └── theme/              # Material 3 theme
│       └── test/                           # JUnit unit tests
```

## Backend-Pending Features

These screens have full UI but no backend wired yet:

- **Resume Modification** — "Modify Resume" button on job detail (Download/Cancel ready)
- **Profile Configuration** — Full form for personal info, skills, experience
- **Auto-Apply Agent** — State machine UI (Idle → Running → Paused → Needs Input)
