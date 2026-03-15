# Security Engineer Study Research

## Purpose

This memo is for deciding whether security-engineer-related study should be added to the current 24-month plan.

This memo started as a separate decision note from `data/project-seed.yaml`.
As of `2026-03-15`, the selected `OT / ICS security mini-track` has been added to the live seed as:

- `E-SEC`
- `ISS-043`
- `ISS-044`
- `ISS-045`
- `ISS-046`

The rest of this file remains useful as background and rationale.

## Bottom line first

If you add security study to the current plan, the best fit is:

1. `OT / ICS security` as a small sub-track
2. `情報処理安全確保支援士（SC）` as a later optional exam track
3. `Web Security Academy` as a lightweight appsec side track

The strongest fit with your existing plan is not generic web pentesting.
It is `OT / ICS security`, because it connects directly to:

- 制御基礎
- 図面読解
- PLC / シーケンス制御
- 発電機盤・ポンプ盤理解
- 実務証拠づくり
- AI 活用による保守・記録・分析

## Why OT / ICS security fits best

Your current plan is already close to the technical surface where OT security becomes valuable.

You are building around:
- electrical work
- control logic
- drawings
- PLC
- plant / panel understanding

That means security study can become:
- a differentiation point in interviews
- a way to explain control knowledge in higher-value language
- a bridge from "I can read and build" to "I can operate more safely"

This is much more aligned than jumping straight into generic bug bounty or cloud security.

## Official data points

### 1. IPA 情報処理安全確保支援士試験（SC）

IPA says the SC exam is for people aiming to become security engineers or security consultants, and that the role includes planning, designing, developing, operating, and evaluating secure systems, plus incident management and advice to organizations.

Source:
- [IPA: 情報処理安全確保支援士試験](https://www.ipa.go.jp/shiken/kubun/sc.html)

Important current points:
- As of the page updated on `2026-02-02`, IPA says SC is scheduled to move to `CBT` in `2026年度`.
- IPA also says the scope of knowledge/skills itself does not change, and the format/count/time remain the same.

Source:
- [IPA: CBT方式での実施について](https://www.ipa.go.jp/shiken/2026/ap_koudo_sc-cbt.html)

IPA’s stated role/skill areas include:
- security policy / risk assessment / risk response
- secure procurement and secure development
- crypto, authentication, filtering, logging
- incident management
- legal, audit, and evidence handling

That means SC is broad and recognized, but not narrow.
It is a serious "security generalist / upper-intermediate" track.

### 2. 登録セキスペの制度負荷

IPA’s 2025制度資料 shows:
- registration is updated every `3 years`
- annual online training is required
- one practical course every `3 years` is required
- the annual online course is about `6 hours`

The same IPA material also shows that recent lecture examples included:
- AI use and AI regulation trends
- security management points for AI use
- threat intelligence
- ransomware response
- compliance and governance

Source:
- [IPA: 国家資格「情報処理安全確保支援士」制度の仕組みについて](https://www.ipa.go.jp/jinzai/riss/ps6vr70000019c29-att/ps6vr70000019c2i.pdf)

This matters because:
- passing SC is one thing
- maintaining the registered qualification is another

If you only want "security literacy + career narrative", you may not need to commit to full registration immediately.

### 3. 登録者数の参考

IPA published that, as of `2025-04-01`, registered specialists totaled `23,751`, with average age `44.2`.

Source:
- [IPA: 情報処理安全確保支援士登録者について（2025年4月1日時点）](https://www.ipa.go.jp/jinzai/riss/reports/data/20250401allriss.html)

Interpretation:
- the credential is clearly recognized
- it is not "rare", but it is still strong enough to signal seriousness
- for your path, the differentiator would be `SC + OT/control/PLC + practical evidence`, not SC alone

### 4. NIST SP 800-82 Rev. 3

NIST says SP 800-82 Rev. 3 gives guidance on securing `OT` while respecting performance, reliability, and safety requirements.
It explicitly covers:
- ICS
- PLC
- SCADA
- OT topologies
- common threats and vulnerabilities
- recommended countermeasures

The final publication date shown is `2023-09-28`.

Source:
- [NIST SP 800-82 Rev. 3](https://csrc.nist.gov/pubs/sp/800/82/r3/final)

This is the single strongest source for why OT security fits your plan.

### 5. CISA ICS training

CISA’s official training pages show:
- `Introduction to Control Systems in Cybersecurity (101)` is a `4-hour` course
- there is `no tuition cost`
- it covers ICS architecture, IT vs ICS differences, risk, vulnerabilities, and mitigation

Source:
- [CISA: Introduction to Control Systems in Cybersecurity (101)](https://www.cisa.gov/resources-tools/training/introduction-control-systems-cybersecurity-101)

CISA also lists stronger OT security training:
- `ICS300`
- virtual / online
- expected completion time `12-20 hours`
- no tuition cost

Source:
- [CISA: Advanced Cybersecurity for Industrial Control Systems (ICS300)](https://www.cisa.gov/resources-tools/training/advanced-cybersecurity-industrial-control-systems-ics300)

CISA’s broader training page also says:
- ICS training is free
- available virtually
- and there is a cybersecurity workforce training guide

Source:
- [CISA: Cybersecurity Training & Exercises](https://www.cisa.gov/cybersecurity-training-exercises)

### 6. PortSwigger Web Security Academy

PortSwigger states that Web Security Academy is:
- free
- online
- interactive
- safe and legal to use
- continuously updated

The current page also shows learning areas including:
- SQL injection
- XSS
- CSRF
- API testing
- web LLM attacks

Source:
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)

This is excellent if you want appsec fundamentals without spending money, but it is less directly connected to your PLC / control path than OT security.

### 7. NIST CSF 2.0

NIST says CSF 2.0 was published on `2024-02-26` and is a high-level taxonomy of cybersecurity outcomes that organizations of any size or maturity can use to understand, assess, prioritize, and communicate cybersecurity efforts.

Source:
- [NIST CSF 2.0](https://csrc.nist.gov/pubs/cswp/29/the-nist-cybersecurity-framework-csf-20/final)

This is useful if you want a management / risk language layer to explain security in interviews or improvement proposals.

## Best-fit options for your current plan

### Option A: OT / ICS security mini-track

Best overall fit.

Why:
- directly overlaps with control, drawings, PLC, plant/panel understanding
- creates a stronger story for equipment, control, maintenance, and reliability jobs
- can become evidence / proposal / memo output without derailing the main exam path

Recommended size:
- `2-4 hours per month`
- deferred until `2026-07-05`
- then run as a small side track in phase-2 and phase-3

Candidate outputs:
- OT security reading note
- PLC / panel risk checklist
- “IT と OT の違い” one-page memo
- incident / safety / availability viewpoint memo

### Option B: SC exam exploration

Good, but heavier.

Why:
- nationally recognized in Japan
- broadens your range beyond purely electrical/control work
- strong interview signal if combined with practical OT evidence

Why not now:
- your mainline until `2026-07-04` is clearly 第一種電気工事士
- SC is too broad to add as a main exam in the short term without dilution
- registered qualification also has ongoing maintenance obligations

Recommended size:
- do not make it a mainline before `2027`
- if added earlier, limit to “exploration only”, not exam prep

### Option C: Web app security fundamentals

Useful but lowest fit with current plan.

Why:
- good for general cyber literacy
- good for learning attacker thinking
- useful if AI / automation work starts touching internal tools or web apps

Why it ranks lower:
- weaker connection to your electrical / control / PLC identity
- easier to drift into an unrelated sub-career

Recommended size:
- very small side track only
- one lab block every few weeks at most

## Suggested decision rules

Add security study if you want one of these:
- stronger differentiation around `OT / PLC / control + security`
- a better story for “I understand not only operation, but also risk and resilience”
- practical evidence that links plant/control knowledge with modern cyber concerns

Defer it if:
- the current exam mainline already feels tight
- it would reduce 第一種電気工事士 or control-foundation time
- you are tempted to make it a second major exam too early

## Recommended insertion points if you decide to add it

### Safe insertion point

After `2026-07-04`.

Reason:
- before that, it competes with the explicit exam mainline
- after that, it can reinforce control / PLC learning instead of distracting from it

### Best phase fit

1. `phase-2`
- add very small OT/ICS reading and note-making

2. `phase-3`
- add OT/ICS security around PLC and drawings

3. `phase-5`
- if desired, add one security-flavored AI / automation deliverable

## Minimal plan candidate

If you want the lightest, highest-fit version, add only this:

1. `OTセキュリティ入門メモ`
- Read selected sections of NIST SP 800-82 Rev. 3
- Output: 1 memo on “IT と OT の違い / PLC を含む OT の守り方の基本”

2. `CISA ICS 101 or equivalent note`
- Output: 1 memo on ICS architecture / consequence-based risk / mitigation basics

3. `月1件の実務証跡にセキュリティ観点を1行加える`
- Example: safety, availability, network separation, account control, logging, change control

This is enough to test fit without breaking the main plan.

## Moderate plan candidate

If the light version feels good, then add:

1. OT/ICS basics
2. one PLC/OT risk checklist
3. one security-oriented internal improvement memo
4. optional SC exploration note

Still do not make SC a primary exam until the main exam priorities are clear.

## My recommendation

If you add anything now, add:
- `OT / ICS security mini-track only`

Do not add:
- full SC exam prep
- broad web pentest study

Why:
- OT security multiplies the value of what you are already learning
- it creates better differentiation for your current career story
- it has the lowest risk of derailing the mainline

## Sources

- [IPA: 情報処理安全確保支援士試験](https://www.ipa.go.jp/shiken/kubun/sc.html)
- [IPA: CBT方式での実施について](https://www.ipa.go.jp/shiken/2026/ap_koudo_sc-cbt.html)
- [IPA: 国家資格「情報処理安全確保支援士」制度の仕組みについて](https://www.ipa.go.jp/jinzai/riss/ps6vr70000019c29-att/ps6vr70000019c2i.pdf)
- [IPA: 情報処理安全確保支援士登録者について（2025年4月1日時点）](https://www.ipa.go.jp/jinzai/riss/reports/data/20250401allriss.html)
- [NIST SP 800-82 Rev. 3](https://csrc.nist.gov/pubs/sp/800/82/r3/final)
- [NIST CSF 2.0](https://csrc.nist.gov/pubs/cswp/29/the-nist-cybersecurity-framework-csf-20/final)
- [CISA: Introduction to Control Systems in Cybersecurity (101)](https://www.cisa.gov/resources-tools/training/introduction-control-systems-cybersecurity-101)
- [CISA: Advanced Cybersecurity for Industrial Control Systems (ICS300)](https://www.cisa.gov/resources-tools/training/advanced-cybersecurity-industrial-control-systems-ics300)
- [CISA: Cybersecurity Training & Exercises](https://www.cisa.gov/cybersecurity-training-exercises)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
