<div align="center">

# 🧭 Pathfinda

**Find your path — before you have to choose it.**

A career path-finding app that helps South African high-school students match their
subjects, marks, and interests to real degrees, careers, and the bursaries that fund them.

![Flutter](https://img.shields.io/badge/Flutter-02569B?style=flat&logo=flutter&logoColor=white)
![Dart](https://img.shields.io/badge/Dart-0175C2?style=flat&logo=dart&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Android-3DDC84?style=flat&logo=android&logoColor=white)
![Status](https://img.shields.io/badge/Status-Closed%20Testing-orange?style=flat)
![License](https://img.shields.io/badge/License-MIT-black?style=flat)

</div>

---

## 📖 Overview

Most South African students pick a university degree with almost no structured guidance —
and the cost of guessing wrong is a wasted year and a lot of money. **Pathfinda** turns that
guesswork into a guided flow: tell it your subjects, marks and interests, and it maps you to
degrees you actually qualify for, the careers they lead to, and where to study them.

Built solo with **Flutter/Dart**, currently in **closed testing on the Google Play Store**.

## ✨ Features

- 🎯 **Subject & interest matching** — turns Grade 10–12 subject choices + interests into a shortlist of degree paths
- 🏛️ **Degree & university explorer** — what you can study, and where
- 💼 **Career outcomes** — where each path actually leads
- 📊 **Requirements check** — APS / subject-minimum awareness so students target realistically
- 📱 **Mobile-first** — designed for the phone every SA student already has

> **Roadmap:** bursary matching (link students to funding they qualify for), NBT/APS calculator, and offline mode.

## 🖼️ Demo & Screenshots

> _Add 3–4 screenshots + a 30-second screen recording here — this is the single highest-impact
> thing you can do for the repo. Suggested shots: onboarding, the matching flow, a results screen._

```
docs/
  ├── screenshot-onboarding.png
  ├── screenshot-matching.png
  ├── screenshot-results.png
  └── demo.gif
```

Embed once added:

```markdown
<p align="center">
  <img src="docs/screenshot-onboarding.png" width="230"/>
  <img src="docs/screenshot-matching.png" width="230"/>
  <img src="docs/screenshot-results.png" width="230"/>
</p>
```

## 🛠️ Tech Stack

| Layer | Choice |
|---|---|
| Framework | Flutter |
| Language | Dart |
| Target | Android (iOS-ready via Flutter) |
| Distribution | Google Play (closed testing) |

## 🚀 Getting Started

```bash
# Prerequisites: Flutter SDK installed (flutter doctor should pass)

git clone https://github.com/thandofrans28-ship-it/pathfinda.git
cd pathfinda

flutter pub get        # install dependencies
flutter run            # run on an emulator or connected device
```

Build a release APK:

```bash
flutter build apk --release
```

## 📂 Project Structure

```
lib/
  ├── main.dart          # app entry point
  ├── screens/           # UI screens (onboarding, matching, results)
  ├── models/            # data models (subjects, degrees, careers)
  ├── data/              # matching logic + datasets
  └── widgets/           # reusable UI components
```

## 🧑‍💻 About the Author

Built by **Thando Frans** — a Grade 12 (IEB) student in East London, South Africa, heading into
**Electrical Engineering**. Pathfinda started from a simple observation: my classmates were making
massive decisions with almost no data. So I built the tool I wished we had.

- 💼 [LinkedIn](https://www.linkedin.com/in/thando-frans)
- ✉️ thandofrans28@gmail.com

## 📄 License

Released under the **MIT License** — see [`LICENSE`](LICENSE).

---

<div align="center"><sub>Made in East London 🇿🇦 · Building at the maths × code intersection</sub></div>
