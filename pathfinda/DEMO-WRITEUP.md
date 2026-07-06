# Pathfinda — Demo Write-Up

A short, reusable narrative you can drop into a Play Store description, a bursary
application, a university interview, or a LinkedIn post. Three lengths — pick by context.

---

## 🎬 30-second pitch (interviews / "tell me about a project")

> "Pathfinda is a mobile app I built to fix a real problem I watched happen around me:
> South African students choosing degrees almost blind. You enter your subjects, your
> marks and your interests, and it maps you to degrees you actually qualify for, the
> careers they lead to, and where to study them. I designed, built and shipped it solo
> in Flutter, and it's currently in closed testing on the Google Play Store. Next I'm
> adding bursary matching so students find the funding they qualify for too."

## 📱 Play Store / landing-page description (~100 words)

> **Choosing what to study shouldn't be a guess.**
>
> Pathfinda helps South African high-school students find their path. Tell it your
> subjects, your marks and what you enjoy, and Pathfinda matches you to degrees you
> qualify for, the careers they open up, and the universities that offer them — all from
> your phone.
>
> No more picking a degree based on a rumour or a single open day. Pathfinda gives you a
> shortlist built around *you*, so you walk into your application year knowing your
> options and your requirements.
>
> Built for SA students, by an SA student. **Find your path — before you have to choose it.**

## 📝 Full write-up (portfolio / bursary "tell us about something you built")

**The problem.** In my school and others around me, students were making one of the
biggest decisions of their lives — what degree to spend three-to-five years and a lot of
money on — with almost no structured information. Guidance was a rushed conversation and a
pile of prospectuses. Get it wrong and you lose a year and a lot of money.

**What I built.** Pathfinda is a Flutter/Dart Android app that turns that guesswork into a
guided flow. A student enters their Grade 10–12 subjects, marks and interests; Pathfinda
maps those to degree paths they realistically qualify for, shows the careers each path
leads to, and points to universities that offer them — with an awareness of APS and
subject-minimum requirements so the shortlist is realistic, not aspirational noise.

**How I did it.** I designed the flow, modelled the subject → degree → career data, built
the matching logic and the entire UI myself, and took it through Google Play's release
process to **closed testing** — the real, unglamorous work of shipping, not just coding.

**What's next.** Bursary matching (connecting students to funding they qualify for), an
NBT/APS calculator, and offline support for students with limited data.

**Why it matters to me.** I'm heading into electrical engineering — I like taking a messy,
real-world problem and building something that actually works. Pathfinda is that instinct applied
early: I saw people making high-stakes decisions with bad information, and I built the tool to fix it.

---

## ✅ Checklist to make this land (do before you share the repo widely)

- [ ] Record a **30-second screen capture** of the core flow → save as `docs/demo.gif`
- [ ] Add **3–4 screenshots** to `docs/` and embed them in the README
- [ ] Add a **LICENSE** file (MIT) so the repo looks finished
- [ ] Write a one-line repo **description** + topics on GitHub: `flutter`, `dart`, `edtech`, `south-africa`
- [ ] Make the repo **public** when you're ready for people to see it
- [ ] Add the **Play Store test link** once you can share it (huge credibility signal)
- [ ] Capture one **metric** you can quote later ("X testers", "Y degree paths mapped")
