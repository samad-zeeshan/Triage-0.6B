# Notes for the demo page

Working notes behind `docs/index.html`. Written before the page, kept as the record of
what is provable from this repository and what is not.

---

## What this actually does, in one sentence a 12 year old understands

It reads a customer's email and fills in three boxes: which team should handle it, how
urgent it is, and the customer's account number.

## Who has the problem, and the moment they are stuck

The person who opens the support inbox on Monday morning. The inbox is full. Nobody can
start fixing anything until somebody has opened each email and decided three things: which
team owns it, whether it can wait, and which customer it is. That sorting is slower than
the answering, so the queue backs up behind it, and an email saying the payment system is
down waits behind a polite question about invoices.

## What people did before this existed

Two options, both bad in different ways.

1. A person reads and sorts every email by hand.
2. A large model in the cloud does it, which works well but charges per email and requires
   sending customer messages off your own machines. `README.md` states this trade off
   directly in its "The problem" section.

## What numbers exist, where they came from, and how they were measured

Every number is from `results/confusion_matrices.txt`, which is the verbatim printout of
the evaluation cell in `notebooks/02_train_and_eval.ipynb`. Two figures come from
`README.md`. Line counts were checked directly against the data files.

| Number | Meaning | Where it is | Cross-check |
| --- | --- | --- | --- |
| 1,200 | emails kept back and never used for training | confusion_matrices.txt line 1 | `data/test_chat.jsonl` and `data/test_labeled.jsonl` are both 1,200 lines |
| 2,500 | emails used for training | README.md "Split: 2,500 train" | `data/train_chat.jsonl` is 2,500 lines |
| 42.4% | score for ignoring the email and always saying "high" | line 4 | 509 of 1,200 gold labels are high, in `data/test_labeled.jsonl`. 509/1200 = 42.4% |
| 38.3% | urgency accuracy before training | line 7 | matches its confusion matrix: (251+201+8)/1200 = 38.3% |
| 64.2% | team accuracy before training | line 7 | no per-cell matrix for category exists in the repo |
| 87.3% | urgency accuracy after training | line 15 | matches its matrix: (434+231+383)/1200 = 87.3% |
| 89.7% | team accuracy after training | line 15 | no per-cell matrix for category exists in the repo |
| +49.0 points | the urgency jump | line 22 | 87.3 minus 38.3 |
| 1200/1200 | answers that parsed, before and after | lines 7 and 15 | |
| 63.8% | score for always saying "Technical Support" | README.md headline table only | 766 of 1,200 gold categories are Technical Support, in `data/test_labeled.jsonl`. 766/1200 = 63.8% |
| the 24 grid cells | the two urgency confusion matrices | lines 8 to 12 and 16 to 20 | row totals 509, 299 and 392 match the gold label counts in `data/test_labeled.jsonl` exactly |
| 600 million | the model's size | README.md line 3 | |
| about 7 in 10 | share of emails given an account number sentence | `p_has_id=0.7` in `notebooks/01_label_with_teacher.ipynb` | |
| twice over | training passes over the 2,500 examples | `num_train_epochs=2` in `notebooks/02_train_and_eval.ipynb` | |

**How it was measured.** Both models were asked the same 1,200 questions with greedy
decoding. An answer counted as right only when it matched the answer key exactly. The
answer key is what a larger model (DeepSeek, at temperature 0) wrote when it was shown the
same emails. That is the correct measurement for a project whose whole aim is to copy a
larger model, and it is not the same as human-checked accuracy.

## What it does not do

- It only knows five teams and three urgency levels. That list is fixed in the instruction
  text, visible in `data/test_chat.jsonl`.
- The answer key is a larger model's opinion, not a support team's. 87.3% is agreement
  with that model.
- Account number extraction is **not** covered by the headline figure. The scoring code in
  `notebooks/02_train_and_eval.ipynb` scores urgency and team only, and a comment in that
  notebook warns that its rebuilt split must not be used to score `account_id` because the
  injected account sentences are not byte identical to the ones the answer key saw.
- The emails are synthetic. One training run, one seed, no variance bars. All stated in
  `README.md` under "What this does not prove".
- "medium" is the weak class. 231 of 299 after training, from the grid.

---

## The integrity constraint, and how the page respects it

**This repository contains no per-email model predictions, and no model weights.** There is
no way to produce one here. So the page never shows a prediction that is not literally
written in a file:

- The one before and after example (base model writes an essay, trained model returns three
  fields) is documented in `README.md` and is visible in `results/lm_studio.png`. It is the
  only model output shown anywhere on the page, and every step naming it cites the file.
- The six sample emails are real held-out rows from `data/test_chat.jsonl`, shown with the
  **answer key** from `data/test_labeled.jsonl`. The page says in two places that this is
  the correct answer, not a prediction.
- The two confusion matrices are per-cell counts, which is what the repository does have.
  They are used verbatim.
- No stored-run badge is used. The format badge reads "Visual explanation", because that is
  what it is. A standing note under the demo says the model is not in this repository and
  nothing runs while you read.

Nothing was added to the page that could not be pointed at in a file. Where a number would
have been needed and did not exist (a per-cell matrix for team accuracy, an accuracy figure
for account numbers), the claim was left out rather than estimated.

---

## Signature element

**The diagonal.** The two urgency confusion matrices drawn as one instrument at one scale:
a four column grid where each cell holds a square whose *area* is the number of emails in
it, the three cells where the answer and the truth agree are washed in brass, and a single
heavy brass rule is threaded corner to corner over the top of the ink through those three
cells.

It fits because this project's entire claim is a classifier learning to agree with the
truth, and the repository's strongest asset is exactly the per-cell counts that make that
visible. Before training the ink pools in a vertical stripe down the "medium" column,
nowhere near the line: the model has no read on urgency and picks the safe middle. After
training the ink is strung along the brass line like beads. Same emails, same scale, one
picture, no commentary needed. It is a matrix of counts, not bars measured against a value
rule (Tally's zero line) and not intervals plotted on a time axis (Change-Gate's freeze
band).

---

## Verification performed (Chrome, Windows 11)

- **Served from a subpath** at `http://localhost:PORT/Triage-0.6B/`: all six requests
  resolved under `/Triage-0.6B/`, nothing leaked to the origin root, zero console messages.
- **`file://`**: opened `docs/index.html` directly. Data resolved from `window.DEMO_DATA`,
  the walkthrough played all six steps and stopped at the last one, zero console messages.
- **No network at runtime**: the only requests are `index.html`, `kit.css`, `kit.js`,
  `data/triage.js`, `data/triage.json` and `lm-studio.png`, all same origin. The favicon is
  an inline 1 by 1 image, so the browser makes no extra request for one.
- **360px wide**: document scroll width 360, no horizontal page scroll. The only element
  wider than the viewport is the counts table, which sits inside `.k-scroll-x` and scrolls
  in its own box.
- **No layout shift**: cumulative layout shift 0.000 with zero shift entries, measured
  across load and all six walkthrough steps.
- **Stage reserve**: tallest step measured at 360, 545, 745 and 1265 pixels wide
  (314px and 272px). `--k-player-stage-min` set to 20rem and 17rem accordingly. Stage box
  height is constant across all six steps at both widths.
- **Caption reserve**: longest caption is 108 characters and still fits the kit's three
  line reserve at 360px (98px content in a 99px box).
- **Demo timing**: pressing Play flips the button to Pause immediately and the first step
  change lands at 1.9 seconds. The whole run is 11 seconds and stops at step 6.
- **Keyboard**: tab order is document order, no positive `tabindex` anywhere, focus ring is
  the kit's 3px brass outline at 2px offset (checked on a real Tab press).
- **Headings**: one `h1`, then `h2` per section with an `h3` nested where needed, no skipped
  levels.
- **Reduced motion**: the page's own stylesheet contains no `transition`, `animation`,
  `@keyframes` or `scroll-behavior`. The only animated properties on the whole page are the
  kit's own button and tick colour transitions, which the kit's reduced motion block
  neutralises, and the hero wash, which `kit.js` detaches entirely under
  `prefers-reduced-motion: reduce`. Verified by inspecting every element's computed
  `animation-name` and `transition-property`.
- **Contrast**: no new colours were introduced, so the kit's measured ratios hold. The one
  new pairing is the signature grid. Computed with the WCAG 2.1 formula: brass rule on the
  brass wash 5.49 light and 7.78 dark, blue ink on the brass wash 7.27 and 7.34, grey count
  text on the brass wash 6.35 and 7.23. All pass. The grid's own hairlines are drawn in
  `--k-edge` and are decorative: the cells are also delimited by the brass wash, the
  labels and the printed counts, and the same counts are available as a table.
- **Dashes**: zero U+2014 and zero U+2013 in every file written here.
- **Weight**: 201 KB of page assets in total, of which the screenshot is 92 KB.
