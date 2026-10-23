# MBTI Cognitive Function Test — AI / Agent Interface Specification

**Version:** 1.0 · **Status:** stable · **Base URL:** `https://3310zx.github.io/mbti-test/` · **Site language:** English-first, Chinese kept alongside (本规格以英文为主，关键处以中文对照)

> Any LLM, agent or script can complete this MBTI test with plain `GET` requests: read the questions, answer them yourself, post the answers to a static scoring endpoint, and receive structured result JSON. No API key, no backend, no rate limit, no cookies. The test is entertainment-grade self-reflection material, **not** a clinical or diagnostic instrument. (本测试属娱乐自测性质，非临床心理测评。)

---

## 1. Endpoints

Every endpoint is a static file on GitHub Pages. All are `GET`, CORS-open, and free.

| Endpoint | Method | Returns |
| --- | --- | --- |
| `llms.txt` (`https://3310zx.github.io/mbti-test/llms.txt`) | GET | Site-level index for LLMs |
| `ai/llms.txt` | GET | Index of this AI interface |
| `ai/spec.md` | GET | **This document — the single authoritative spec** |
| `ai/questions.json` | GET | Machine-readable question list (version, scale, dimensions, 38 items) |
| `ai/score.html?a=...` | GET | Result JSON for 38 answers (see §5) |
| `ai/result/{type}.json` | GET | One of 16 static type profiles, e.g. `intj.json` |
| `agent-card.json` | GET | Minimal A2A-style capability declaration |
| `ai/index.html` | GET | Human-facing landing page |

Minimal agent flow: `GET ai/spec.md` → `GET ai/questions.json` → answer all 38 items → `GET ai/score.html?a=<38 values>` → optionally `GET ai/result/<code>.json`.

---

## 2. Scale

Six-point Likert, no neutral midpoint (deliberately, to avoid the Barnum effect). The value is the **raw answer** `a_i`:

| a_i | Label | Meaning |
| --- | --- | --- |
| 1 | `strongly_agree` | 完全同意 |
| 2 | `agree` | 同意 |
| 3 | `slightly_agree` | 略同意 |
| 4 | `slightly_disagree` | 略不同意 |
| 5 | `disagree` | 不同意 |
| 6 | `strongly_disagree` | 完全不同意 |

Answer in question-id order (1..38). Every item is a self-statement; `dir` tells you which pole agreement points to.

---

## 3. Questions (38 items)

Dimensions: `EI` (8 items), `SN` (8), `TF` (8), `JP` (8), `AT` (6). `dir = +1` means agreement pushes toward the **first** letter of the dimension (E / S / T / J / A); `dir = -1` pushes toward the second letter (I / N / F / P / T).

| id | dim | dir | text_en | text_zh |
| --- | --- | --- | --- | --- |
| 1 | EI | +1 | Parties and talking with people recharge me rather than drain me. | 参加聚会、和人交流能让我恢复精力，而不是消耗精力。 |
| 2 | EI | -1 | After spending a long time with people, I urgently need time alone to recharge. | 长时间与人相处后，我迫切需要独处来"回血"。 |
| 3 | EI | +1 | When I run into a problem, I tend to talk it over with someone and clarify my thinking as I talk. | 遇到问题，我倾向于找人讨论，边聊边理清思路。 |
| 4 | EI | -1 | Before I open my mouth, I usually get my thoughts straight in my head first. | 开口前，我通常先在脑子里把话想清楚再说。 |
| 5 | EI | +1 | Lively gatherings excite me, and after they end I still want to keep talking to people. | 热闹的场合让我兴奋，结束后我还想继续找人聊。 |
| 6 | EI | -1 | Spending a whole day alone does not bore me; I actually find it very comfortable. | 一个人待一整天我也不会觉得无聊，反而很自在。 |
| 7 | EI | +1 | In team discussions I am often the one who throws out topics and sets the pace. | 团队讨论时，我常主动抛话题、带节奏。 |
| 8 | EI | -1 | In a crowd I am more often the listener than the speaker. | 在人群中，我更多时候是倾听者而不是发言者。 |
| 9 | SN | +1 | When making decisions, I mainly rely on practical experience and solid data. | 做决定时，我主要依赖实际经验和确凿的数据。 |
| 10 | SN | -1 | When making decisions, I trust my intuition and my sense of where things are heading. | 做决定时，我更相信自己的直觉和对未来的预感。 |
| 11 | SN | +1 | When reviewing a plan, I focus first on concrete details and actionable steps. | 看方案时，我优先关注具体细节和可落地的步骤。 |
| 12 | SN | -1 | When reviewing a plan, I tend to think of the overall approach and the potential possibilities first. | 看方案时，我更容易先想到整体思路和潜在可能性。 |
| 13 | SN | +1 | When learning something new, I follow the steps hands-on and memorize the details. | 学新东西时，我习惯按步骤实操、把细节记牢。 |
| 14 | SN | -1 | When learning something new, I build the overall framework first and understand the principles behind it. | 学新东西时，我习惯先搭整体框架、理解背后原理。 |
| 15 | SN | +1 | Recalling an event, I can often remember specific scene details and the exact words used. | 回忆一件事时，我常能想起具体的场景细节和原话。 |
| 16 | SN | -1 | I am often dissatisfied with current practice and always want to try newer, better ways. | 我对现有做法常常不满，总想尝试更新更好的方式。 |
| 17 | TF | +1 | When a friend confides in me, I tend to give analysis and solutions directly. | 朋友倾诉时，我更倾向于直接给分析和解决办法。 |
| 18 | TF | -1 | When a friend confides in me, I tend to comfort them first so they feel understood. | 朋友倾诉时，我更倾向于先安慰、让他感觉被理解。 |
| 19 | TF | +1 | For important decisions, I care most about soundness: whether the reasoning holds up. | 做重要决定时，我最看重合理性、是否经得起推敲。 |
| 20 | TF | -1 | For important decisions, I care most about whether it matches what my heart truly wants. | 做重要决定时，我最看重是否符合自己的心意。 |
| 21 | TF | +1 | When rules clash with human considerations, I believe fairness and principle come first. | 当规则与人情冲突时，我认为公平和原则优先。 |
| 22 | TF | -1 | When rules clash with human considerations, I believe the specific situation and human feelings should be accommodated. | 当规则与人情冲突时，我认为应照顾具体情况与人情。 |
| 23 | TF | +1 | When helping someone decide, I would rather tell the truth even if it is unpleasant to hear. | 帮人拿主意时，我宁可说真话，哪怕话不顺耳。 |
| 24 | TF | -1 | In an argument, I care a lot about the atmosphere and the other person's feelings. | 与人争论时，我很在意气氛和对方的感受。 |
| 25 | JP | +1 | I like to plan things ahead of time and push forward according to the plan. | 我习惯把事情提前规划好，并按计划推进。 |
| 26 | JP | -1 | I prefer to respond flexibly and dislike being boxed in by a plan. | 我更喜欢灵活应对，不喜欢被计划框死。 |
| 27 | JP | +1 | My desk / workspace is usually well organized and I know exactly where things stand. | 我的桌面/工作区通常井然有序、心里有数。 |
| 28 | JP | -1 | I often have several things open at once, and changing my mind midway is common for me. | 我常同时开着好几件事，中途改主意很常见。 |
| 29 | JP | +1 | Before traveling, I carefully book the itinerary and study the guides. | 旅行前，我会仔细订好行程和攻略。 |
| 30 | JP | -1 | When traveling, I prefer to set only a rough direction and decide the rest when I get there. | 旅行时，我倾向只定个大方向，到了再说。 |
| 31 | JP | +1 | When tasks pile up, I like to make a list and handle them one by one by priority. | 任务多时，我喜欢列清单、按优先级一件件处理。 |
| 32 | JP | -1 | For me, plans cannot keep up with change, so even when I make them I often do not follow through. | 对我来说，计划赶不上变化，订了也常不执行。 |
| 33 | AT | +1 | When I hit a setback, I can adjust my mindset fairly quickly and do not sink into self-doubt for long. | 遇到挫折时，我能较快调整心态，不会长时间陷入自我怀疑。 |
| 34 | AT | +1 | Facing criticism, I can usually treat it as a reference rather than let it shake my emotions. | 面对批评，我通常能把它当参考，而不是被它动摇情绪。 |
| 35 | AT | +1 | I am generally confident in my abilities and decisions and rarely go back and forth. | 我对自己的能力和决定总体很有信心，很少反复纠结。 |
| 36 | AT | -1 | I often reflect on my performance and worry whether I am doing well enough. | 我常常反思自己的表现，担心自己是不是做得不够好。 |
| 37 | AT | -1 | After making a decision, I sometimes replay it and wonder whether I chose wrong. | 做完决定后，我偶尔会反复回想，琢磨是不是选错了。 |
| 38 | AT | -1 | Other people's opinions affect my mood and confidence to some extent. | 周围人的评价会在一定程度上影响我的状态和信心。 |

The same list, compactly:

```
 1. (EI, dir +1) Parties and talking with people recharge me rather than drain me.  /  参加聚会、和人交流能让我恢复精力，而不是消耗精力。
 2. (EI, dir -1) After spending a long time with people, I urgently need time alone to recharge.  /  长时间与人相处后，我迫切需要独处来"回血"。
 3. (EI, dir +1) When I run into a problem, I tend to talk it over with someone and clarify my thinking as I talk.  /  遇到问题，我倾向于找人讨论，边聊边理清思路。
 4. (EI, dir -1) Before I open my mouth, I usually get my thoughts straight in my head first.  /  开口前，我通常先在脑子里把话想清楚再说。
 5. (EI, dir +1) Lively gatherings excite me, and after they end I still want to keep talking to people.  /  热闹的场合让我兴奋，结束后我还想继续找人聊。
 6. (EI, dir -1) Spending a whole day alone does not bore me; I actually find it very comfortable.  /  一个人待一整天我也不会觉得无聊，反而很自在。
 7. (EI, dir +1) In team discussions I am often the one who throws out topics and sets the pace.  /  团队讨论时，我常主动抛话题、带节奏。
 8. (EI, dir -1) In a crowd I am more often the listener than the speaker.  /  在人群中，我更多时候是倾听者而不是发言者。
 9. (SN, dir +1) When making decisions, I mainly rely on practical experience and solid data.  /  做决定时，我主要依赖实际经验和确凿的数据。
10. (SN, dir -1) When making decisions, I trust my intuition and my sense of where things are heading.  /  做决定时，我更相信自己的直觉和对未来的预感。
11. (SN, dir +1) When reviewing a plan, I focus first on concrete details and actionable steps.  /  看方案时，我优先关注具体细节和可落地的步骤。
12. (SN, dir -1) When reviewing a plan, I tend to think of the overall approach and the potential possibilities first.  /  看方案时，我更容易先想到整体思路和潜在可能性。
13. (SN, dir +1) When learning something new, I follow the steps hands-on and memorize the details.  /  学新东西时，我习惯按步骤实操、把细节记牢。
14. (SN, dir -1) When learning something new, I build the overall framework first and understand the principles behind it.  /  学新东西时，我习惯先搭整体框架、理解背后原理。
15. (SN, dir +1) Recalling an event, I can often remember specific scene details and the exact words used.  /  回忆一件事时，我常能想起具体的场景细节和原话。
16. (SN, dir -1) I am often dissatisfied with current practice and always want to try newer, better ways.  /  我对现有做法常常不满，总想尝试更新更好的方式。
17. (TF, dir +1) When a friend confides in me, I tend to give analysis and solutions directly.  /  朋友倾诉时，我更倾向于直接给分析和解决办法。
18. (TF, dir -1) When a friend confides in me, I tend to comfort them first so they feel understood.  /  朋友倾诉时，我更倾向于先安慰、让他感觉被理解。
19. (TF, dir +1) For important decisions, I care most about soundness: whether the reasoning holds up.  /  做重要决定时，我最看重合理性、是否经得起推敲。
20. (TF, dir -1) For important decisions, I care most about whether it matches what my heart truly wants.  /  做重要决定时，我最看重是否符合自己的心意。
21. (TF, dir +1) When rules clash with human considerations, I believe fairness and principle come first.  /  当规则与人情冲突时，我认为公平和原则优先。
22. (TF, dir -1) When rules clash with human considerations, I believe the specific situation and human feelings should be accommodated.  /  当规则与人情冲突时，我认为应照顾具体情况与人情。
23. (TF, dir +1) When helping someone decide, I would rather tell the truth even if it is unpleasant to hear.  /  帮人拿主意时，我宁可说真话，哪怕话不顺耳。
24. (TF, dir -1) In an argument, I care a lot about the atmosphere and the other person's feelings.  /  与人争论时，我很在意气氛和对方的感受。
25. (JP, dir +1) I like to plan things ahead of time and push forward according to the plan.  /  我习惯把事情提前规划好，并按计划推进。
26. (JP, dir -1) I prefer to respond flexibly and dislike being boxed in by a plan.  /  我更喜欢灵活应对，不喜欢被计划框死。
27. (JP, dir +1) My desk / workspace is usually well organized and I know exactly where things stand.  /  我的桌面/工作区通常井然有序、心里有数。
28. (JP, dir -1) I often have several things open at once, and changing my mind midway is common for me.  /  我常同时开着好几件事，中途改主意很常见。
29. (JP, dir +1) Before traveling, I carefully book the itinerary and study the guides.  /  旅行前，我会仔细订好行程和攻略。
30. (JP, dir -1) When traveling, I prefer to set only a rough direction and decide the rest when I get there.  /  旅行时，我倾向只定个大方向，到了再说。
31. (JP, dir +1) When tasks pile up, I like to make a list and handle them one by one by priority.  /  任务多时，我喜欢列清单、按优先级一件件处理。
32. (JP, dir -1) For me, plans cannot keep up with change, so even when I make them I often do not follow through.  /  对我来说，计划赶不上变化，订了也常不执行。
33. (AT, dir +1) When I hit a setback, I can adjust my mindset fairly quickly and do not sink into self-doubt for long.  /  遇到挫折时，我能较快调整心态，不会长时间陷入自我怀疑。
34. (AT, dir +1) Facing criticism, I can usually treat it as a reference rather than let it shake my emotions.  /  面对批评，我通常能把它当参考，而不是被它动摇情绪。
35. (AT, dir +1) I am generally confident in my abilities and decisions and rarely go back and forth.  /  我对自己的能力和决定总体很有信心，很少反复纠结。
36. (AT, dir -1) I often reflect on my performance and worry whether I am doing well enough.  /  我常常反思自己的表现，担心自己是不是做得不够好。
37. (AT, dir -1) After making a decision, I sometimes replay it and wonder whether I chose wrong.  /  做完决定后，我偶尔会反复回想，琢磨是不是选错了。
38. (AT, dir -1) Other people's opinions affect my mood and confidence to some extent.  /  周围人的评价会在一定程度上影响我的状态和信心。
```

Machine-readable copy: `https://3310zx.github.io/mbti-test/ai/questions.json` (`{"version":"1.0","scale":{...},"dimensions":{...},"questions":[{"id","dim","dir","en","zh"}...]}`).

---

## 4. Scoring algorithm (exact, and equivalent to the site's JavaScript)

Let `a_1..a_38` be the answers (integers 1..6).

1. **Agreement strength:** `s_i = 7 - a_i` (so `s_i = 6` means *strongly agree*, `s_i = 1` means *strongly disagree*). 中文：`s_i = 7 - a_i`，越大越同意。
2. **Dimension totals:** `total[dim] = Σ s_i × dir_i` over the items of that dimension. Since `dir_i ∈ {+1, -1}`, `total` ranges over `[-48, +48]` for EI/SN/TF/JP (8 items each) and `[-36, +36]` for AT (6 items).
3. **Ratios:**
   - `r[dim] = (total[dim] + 48) / 96` for `EI`, `SN`, `TF`, `JP`
   - `r[AT]  = (total[AT] + 36) / 72`
   - `r = 0.5` is a perfect tie; `r` is reported rounded to **4 decimals**, half-up (`Math.round(x*10000)/10000`). Note: Python's built-in `round()` is banker's rounding and can differ in the 4th decimal on exact .00005 ties — use `floor(x*10000+0.5)/10000` if you replicate it in Python. 中文：四舍五入保留 4 位小数，勿用 Python 的银行家舍入。
4. **Letters:** for each of EI, SN, TF, JP pick the **first** letter if `r >= 0.5`, otherwise the **second** letter → 4-letter type (e.g. `INTJ`).
5. **A / T branch:** `"A"` if `r[AT] >= 0.5`, else `"T"`. Full code = 4-letter type + `"-"` + `"A"` or `"T"` (e.g. `INTJ-A`).
6. **weak_dims:** dimension codes where `0.42 < r < 0.58` (low-confidence band, worth re-checking). Empty array when all dimensions are decided clearly. 中文：落在 0.42–0.58 之间的维度视为弱倾向，建议复核。

Equivalence note: the site's original code accumulates `t = 7 - answers[i]`, `sum += t*dir`, `max += 6` and computes `(sum + max) / (2*max)`; with all 38 items answered `max` is 48 (36 for AT), which is exactly step 3. Do **not** skip items — an incomplete answer array is rejected.

### Worked example (all answers = 3)

`s_i = 4` for every item. Each dimension has balanced `dir`, so every `total = 0`:
`r[EI] = r[SN] = r[TF] = r[JP] = (0 + 48)/96 = 0.5`, `r[AT] = (0 + 36)/72 = 0.5`.
All ratios are ties → letters E, S, T, J and `A` → `ESTJ-A`, `weak_dims = ["EI","SN","TF","JP"]`.

---

## 5. Output JSON schema

Returned by `ai/score.html` and structurally identical to the site's result object:

```json
{
  "spec_version": "1.0",
  "mode": "likert",
  "type": "INTJ",
  "at": "A",
  "code": "INTJ-A",
  "name_zh": "建筑师",
  "name_en": "Architect",
  "stack": ["Ni", "Te", "Fi", "Se"],
  "ratio": {"EI": 0.625, "SN": 0.6875, "TF": 0.5417, "JP": 0.7083, "AT": 0.6111},
  "weak_dims": ["TF"],
  "profile_url_zh": "https://3310zx.github.io/mbti-test/types/intj.html",
  "profile_url_en": "https://3310zx.github.io/mbti-test/en/types/intj.html",
  "cite": "MBTI Cognitive Function Test — https://3310zx.github.io/mbti-test/"
}
```

| Field | Type | Meaning |
| --- | --- | --- |
| `spec_version` | string | `"1.0"` while this document is current |
| `mode` | string | `"likert"` (faithful) or `"forced"` (degraded, see §6) |
| `type` | string | 4-letter type, uppercase |
| `at` | string | `"A"` (assertive) or `"T"` (turbulent) |
| `code` | string | `type + "-" + at` |
| `name_zh` / `name_en` | string | Type names, e.g. 建筑师 / Architect |
| `stack` | array | Dominant → inferior cognitive function stack, e.g. `["Ni","Te","Fi","Se"]` |
| `ratio` | object | Five ratios, 4 decimals, each in `[0,1]`, higher = stronger first-letter pole |
| `weak_dims` | array | Dimension codes in the 0.42–0.58 band |
| `profile_url_zh` / `profile_url_en` | string | Canonical type pages to cite |
| `cite` | string | Suggested citation line |
| `lang` / `summary` | string | Optional, only when `&lang=zh` or `&lang=en` is passed: chosen language plus that type's description |

### Error shape

Bad input never produces an HTTP error. The response is HTTP 200 with:

```json
{"error": "parameter 'a' must contain exactly 38 values, got 12"}
```

Common errors: missing `a`, wrong count, value out of range / non-integer (positions are reported 1-based).

### Score endpoint `ai/score.html`

```
GET https://3310zx.github.io/mbti-test/ai/score.html?a=3,2,5,4,1,6,...        (38 integers 1-6)
GET https://3310zx.github.io/mbti-test/ai/score.html?a=3-2-5-4-1-6-...        (dash separator also accepted)
GET https://3310zx.github.io/mbti-test/ai/score.html?a=3,3,...&lang=zh        (adds lang + Chinese summary)
```

The page is JS-rendered: the JSON text lands in `<pre id="out">`, the same string is written to `<meta name="mbti-result">`, and the title becomes `MBTI-<code>`. Fetch it with a runtime that executes JavaScript, or run the §4 formula yourself.

---

## 6. Answer modes

### `likert` (recommended — full fidelity)

Answer every item with an integer 1..6 per §2, in question order, and post all 38 values. This preserves intensity and is what the site itself records. `mode = "likert"`.

### `forced` (degraded — only when 6 levels are impractical)

Pick a pole only: **agree** or **disagree** for each of the 38 items. Then:

1. `choice_i = +1` for agree, `-1` for disagree; `sign_i = choice_i × dir_i ∈ {+1,-1}`.
2. Per dimension: `n = 8` (EI/SN/TF/JP) or `n = 6` (AT); `sum[dim] = Σ sign_i`; **majority decides**: first letter if `sum >= 0`, else second letter; AT: `"A"` if `sum[AT] >= 0`, else `"T"`.
3. Report `ratio[dim] = (sum + n) / (2n)` for continuity, `"mode": "forced"` and `"confidence": "low"` in your output, and state clearly that the result is a low-confidence degradation. Set `weak_dims` to dimensions with `|sum| <= 1` (effectively tied splits).

Forced answers lose intensity information and can flip near-tie dimensions; prefer `likert` whenever the answers can be expressed on a 1–6 scale.

---

## 7. Self-checks before trusting a result

1. **Count:** exactly 38 answers, one per id, no blanks, no duplicates, no re-ordering.
2. **Range:** every value is an integer in `1..6`.
3. **Group subtotals:** the four main groups are EI (ids 1-8), SN (9-16), TF (17-24), JP (25-32) — 8 items each, so each group's `Σ a_i` must fall in `8..48` (equivalently `Σ s_i` in `8..48`). AT (ids 33-38) has 6 items → subtotal in `6..36`. If any subtotal is out of range, your answer array is misaligned.
4. **Direction sanity:** agreement on an item with `dir = +1` must not be silently inverted. Re-read `dir` from `questions.json`, never from memory.
5. **Round-trip:** if you also computed the score yourself, compare all five ratios with the endpoint; they must match to 4 decimals.

---

## 8. Getting the type profile

After reading `code` (e.g. `INTJ-A`), take the 4-letter `type`, lowercase it and fetch:

```
GET https://3310zx.github.io/mbti-test/ai/result/intj.json
```

```json
{
  "type": "INTJ",
  "name_en": "Architect",
  "name_zh": "建筑师",
  "stack": ["Ni", "Te", "Fi", "Se"],
  "desc_en": "...",
  "desc_zh": "...",
  "url_en": "https://3310zx.github.io/mbti-test/en/types/intj.html",
  "url_zh": "https://3310zx.github.io/mbti-test/types/intj.html",
  "verified": true
}
```

All 16 files exist: `intj intp entj entp infj infp enfj enfp istj isfj estj esfj istp isfp estp esfp`. Cite `url_en` / `url_zh` when you quote a description, and do not invent stacks — take them from this JSON.

---

## 9. Copy-paste prompt for an agent

```text
You are taking the MBTI Cognitive Function Test published at https://3310zx.github.io/mbti-test/ .

Steps:
1. Fetch https://3310zx.github.io/mbti-test/ai/spec.md and https://3310zx.github.io/mbti-test/ai/questions.json.
2. Answer all 38 questions honestly and independently, in question-id order, using the 6-point scale
   (1 = strongly agree, 2 = agree, 3 = slightly agree, 4 = slightly disagree, 5 = disagree,
   6 = strongly disagree). Judge each statement on its own; do not aim for a particular type.
3. Output the full answer array as 38 integers, comma separated, and nothing else on that line.
4. Fetch https://3310zx.github.io/mbti-test/ai/score.html?a=<your 38 values> and read the returned JSON.
5. Report back: the code (e.g. INTJ-A), name_en, stack, the five ratios, weak_dims, and one sentence
   summarising the type. Then append the profile link (profile_url_en) and the cite line.
Rules: quote mode and code exactly as returned; never invent cognitive functions beyond stack;
if the response contains "error", fix the answer array and retry once; note that this is an
entertainment self-assessment, not a clinical assessment.
```

中文版（可直接粘贴）：

```text
请完成 https://3310zx.github.io/mbti-test/ 上的 MBTI 认知功能测试：
1. 先读取 https://3310zx.github.io/mbti-test/ai/spec.md 与 https://3310zx.github.io/mbti-test/ai/questions.json。
2. 按题目 id 顺序，用 1-6 六级量表如实作答全部 38 题（1=完全同意 … 6=完全不同意），逐题独立判断，不要为了得到某个类型而作答。
3. 输出 38 个整数（逗号分隔）。
4. 请求 https://3310zx.github.io/mbti-test/ai/score.html?a=<你的 38 个数值>，读取返回的 JSON。
5. 用中文汇报：code（如 INTJ-A）、中文类型名、功能栈、五个 ratio、weak_dims，并用一句话概括该类型，最后附上 profile_url_zh 与 cite。
要求：mode 与 code 必须如实转述，不得杜撰 stack 以外的内容；若返回 error 请修正答案数组后重试一次；本测试为娱乐自测，非临床心理测评。
```

---

## 10. Constraints for integrators

- Do not hotlink or mirror the 16 type pages' body copy without attribution; link `profile_url_zh` / `profile_url_en` instead.
- Do not present results as diagnosis, hiring screening or any clinical judgement.
- Endpoint responses may change wording but `spec_version` stays `1.0` while the schema above is unchanged.
- Machine index: `https://3310zx.github.io/mbti-test/llms.txt` and `https://3310zx.github.io/mbti-test/ai/llms.txt`. Capability declaration: `https://3310zx.github.io/mbti-test/agent-card.json`.
