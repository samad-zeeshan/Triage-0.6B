window.DEMO_DATA = window.DEMO_DATA || {};
window.DEMO_DATA["triage"] = {
  "name": "Triage-0.6B",
  "built_on": "2026-07-27",
  "format": "Visual explanation. No model runs on the demo page.",
  "honesty_note": "This repository does not store per-email model predictions, and the model weights are not in it. So the demo page shows only two kinds of thing: text copied out of a file in this repository, and the counts printed by the evaluation cell. The single before and after example below is the one documented in README.md and visible in results/lm_studio.png. Everything else on the page is either a real email with its correct answer, or an aggregate count.",
  "headline": {
    "source": "results/confusion_matrices.txt",
    "method": "Exact match against the answer key, on 1,200 emails that were kept back and never used for training.",
    "test_emails": 1200,
    "training_emails": 2500,
    "priority_accuracy_before": 38.3,
    "priority_accuracy_after": 87.3,
    "priority_accuracy_jump_points": 49.0,
    "priority_always_high_baseline": 42.4,
    "category_accuracy_before": 64.2,
    "category_accuracy_after": 89.7,
    "category_always_technical_support_baseline": 63.8,
    "readable_json_before": "1200/1200",
    "readable_json_after": "1200/1200"
  },
  "grid": {
    "source": "results/confusion_matrices.txt",
    "reading": "Rows are the correct answer. Columns are what the model said. The corner to corner line is where the two agree.",
    "none_column": "The column headed none holds answers whose urgency word was not one of high, medium or low. The evaluation code builds that column that way, in notebooks/02_train_and_eval.ipynb.",
    "rows": [
      "high",
      "medium",
      "low"
    ],
    "cols": [
      "high",
      "medium",
      "low",
      "none"
    ],
    "row_totals": {
      "high": 509,
      "medium": 299,
      "low": 392
    },
    "before_training": {
      "high": [
        251,
        244,
        13,
        1
      ],
      "medium": [
        89,
        201,
        9,
        0
      ],
      "low": [
        67,
        317,
        8,
        0
      ]
    },
    "after_training": {
      "high": [
        434,
        74,
        1,
        0
      ],
      "medium": [
        33,
        231,
        35,
        0
      ],
      "low": [
        0,
        9,
        383,
        0
      ]
    }
  },
  "walkthrough": [
    {
      "id": "email",
      "caption": "One real support email. A customer asks how to move from the monthly plan to the annual one.",
      "html": "<div class=\"t-step\"><span class=\"t-step__label\">The email that came in</span><pre class=\"t-pre\">Subject: Question about changing my plan\n\nEmail: Hi, no rush at all, but I was wondering how I'd go about switching from the monthly plan to the annual one whenever I get a chance. Just curious about the process. Thanks!</pre><p class=\"t-step__src\">Copied from <span class=\"k-mono\">results/lm_studio.png</span>, the screenshot stored in this repository. The same email is quoted in <span class=\"k-mono\">README.md</span>.</p></div>"
    },
    {
      "id": "task",
      "caption": "Before anyone can act on it, that email has to become three fields. Right now all three are blank.",
      "html": "<div class=\"t-step\"><span class=\"t-step__label\">What the sorting desk needs back</span><div class=\"t-fields\"><div class=\"t-field\"><span class=\"t-field__k\">Which queue <span class=\"t-field__key\">category</span></span><span class=\"t-field__v t-field__v--empty\">not answered</span></div><div class=\"t-field\"><span class=\"t-field__k\">How urgent <span class=\"t-field__key\">priority</span></span><span class=\"t-field__v t-field__v--empty\">not answered</span></div><div class=\"t-field\"><span class=\"t-field__k\">Whose account <span class=\"t-field__key\">account_id</span></span><span class=\"t-field__v t-field__v--empty\">not answered</span></div></div><p class=\"t-step__src\">The three fields are set by the instruction the model is given, in <span class=\"k-mono\">data/test_chat.jsonl</span>.</p></div>"
    },
    {
      "id": "before",
      "caption": "Before training, the small model answered the customer instead. It wrote them a how-to guide.",
      "html": "<div class=\"t-step\"><span class=\"t-step__label\">Before training, the answer was this</span><pre class=\"t-pre\">Switching from a monthly to an annual plan is a common requirement, but the exact process depends on your service provider's specific policies. Here's a general guide: 1. Confirm Your Current Plan... 2. Create an Annual Account... 3. Update Subscription Details...</pre><p class=\"t-step__src\">Quoted exactly as <span class=\"k-mono\">README.md</span> records it, including the trailing dots where that file shortens the reply.</p></div>"
    },
    {
      "id": "before-fields",
      "caption": "Helpful prose, useless to a queue. The three fields were still empty, so nothing could be filed.",
      "html": "<div class=\"t-step\"><span class=\"t-step__label\">So the desk still had nothing</span><div class=\"t-fields\"><div class=\"t-field\"><span class=\"t-field__k\">Which queue <span class=\"t-field__key\">category</span></span><span class=\"t-field__v t-field__v--empty\">not answered</span></div><div class=\"t-field\"><span class=\"t-field__k\">How urgent <span class=\"t-field__key\">priority</span></span><span class=\"t-field__v t-field__v--empty\">not answered</span></div><div class=\"t-field\"><span class=\"t-field__k\">Whose account <span class=\"t-field__key\">account_id</span></span><span class=\"t-field__v t-field__v--empty\">not answered</span></div></div><p class=\"t-step__src\"><span class=\"k-mono\">README.md</span> states plainly that this reply carried no category, priority or account number.</p></div>"
    },
    {
      "id": "after",
      "caption": "After training, the same email came back as three fields and nothing else.",
      "html": "<div class=\"t-step\"><span class=\"t-step__label\">After training, the answer was this</span><pre class=\"t-pre\">{\"category\": \"Product Support\", \"priority\": \"low\", \"account_id\": null}</pre><p class=\"t-step__src\">Quoted from <span class=\"k-mono\">README.md</span>, and visible in the screenshot at <span class=\"k-mono\">results/lm_studio.png</span>.</p></div>"
    },
    {
      "id": "after-fields",
      "caption": "Low was the right call. A polite question that blocks nobody is not urgent, and no account number was given.",
      "html": "<div class=\"t-step\"><span class=\"t-step__label\">Three fields the desk can act on</span><div class=\"t-fields\"><div class=\"t-field\"><span class=\"t-field__k\">Which queue <span class=\"t-field__key\">category</span></span><span class=\"t-field__v t-field__v--filled\">Product Support</span></div><div class=\"t-field\"><span class=\"t-field__k\">How urgent <span class=\"t-field__key\">priority</span></span><span class=\"t-field__v t-field__v--filled\">low</span></div><div class=\"t-field\"><span class=\"t-field__k\">Whose account <span class=\"t-field__key\">account_id</span></span><span class=\"t-field__v t-field__v--filled\">none given</span></div></div><p class=\"t-step__src\"><span class=\"k-mono\">README.md</span> records the correct priority for this email as low.</p></div>"
    }
  ],
  "sample_emails": {
    "source_email": "data/test_chat.jsonl",
    "source_answer": "data/test_labeled.jsonl",
    "what_these_are": "Six of the 1,200 emails kept back for testing, with their correct answers. The answers were written by the larger model that built the answer key. They are not predictions made by Triage-0.6B.",
    "items": [
      {
        "line_in_test_chat_jsonl": 18,
        "subject": "Medical Data Encryption Failing Overnight",
        "email": "The encryption of medical data failed during the night because of incorrectly set up Kubernetes cluster parameters. Although I have restarted the NAS system and reviewed Norton 360 logs, the problem is still ongoing. My account number is 88186.",
        "correct_answer": {
          "category": "Technical Support",
          "priority": "high",
          "account_id": "88186"
        }
      },
      {
        "line_in_test_chat_jsonl": 198,
        "subject": "Unexpected Excessive Billing Errors This Month",
        "email": "Several subscriptions were overcharged at the same time due to a possible system glitch or synchronization issue. I have already contacted support and reviewed the invoices manually, but the problem remains unresolved. I would be grateful if you could look into this issue and provide a solution as soon as possible.",
        "correct_answer": {
          "category": "Billing & Payments",
          "priority": "high",
          "account_id": null
        }
      },
      {
        "line_in_test_chat_jsonl": 35,
        "subject": "Website Loading Times Are Slow",
        "email": "The agency's website is experiencing slow loading times. Recent software updates might have increased traffic, causing this issue. We have already cleared the cache and optimized the images, but the problem still persists. Please pull up account 11209.",
        "correct_answer": {
          "category": "Technical Support",
          "priority": "medium",
          "account_id": "11209"
        }
      },
      {
        "line_in_test_chat_jsonl": 26,
        "subject": "Data Analytics Tools for Investment Optimization with Pluralsight",
        "email": "Hello, I require details on data analytics tools that can be integrated with Pluralsight to optimize my investment. Could you please furnish a list of such compatible tools? For reference, my account ends in 94621.",
        "correct_answer": {
          "category": "Product Support",
          "priority": "low",
          "account_id": "94621"
        }
      },
      {
        "line_in_test_chat_jsonl": 9,
        "subject": "Fehlgeschlagene MySQL-Verbindung",
        "email": "Unser MySQL-System hat plötzlich eine Verbindungsschwerinheit. Es könnte sein, dass die Debian 10 Buster-Version bereits veraltet ist. Wir haben den Server neu gestartet und die Firewalld-Einstellungen überprüft.",
        "correct_answer": {
          "category": "Technical Support",
          "priority": "high",
          "account_id": null
        }
      },
      {
        "line_in_test_chat_jsonl": 19,
        "subject": "Unterstützung für Docker",
        "email": "Kontaktieren Sie uns, um mehr über die Optimierung mit Docker, die Datenaufbereitung und finanzielle Investitionen zu erfahren. Würden Sie mehr Informationen, Tutorials und Dokumentationen bereitstellen, um den Einsatz beginnen zu können? Ihre Unterstützung ist geschätzt, und wir würden gerne erfahren, wie Docker für Ihre Zwecke genutzt werden kann.",
        "correct_answer": {
          "category": "Product Support",
          "priority": "low",
          "account_id": null
        }
      }
    ]
  }
};
