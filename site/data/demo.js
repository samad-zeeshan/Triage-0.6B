window.DEMO_DATA = window.DEMO_DATA || {};
window.DEMO_DATA["triage"] = {
 "level": "q6_k",
 "threshold": 0.885,
 "temperatures": {
  "category": 1.234,
  "priority": 1.382
 },
 "teacher": {
  "served": [
   "deepseek-flash"
  ],
  "cost_per_ticket": 0.00010513949999999999
 },
 "cost_per_1000": {
  "small": 0.0,
  "cascade": 0.07079393,
  "teacher": 0.1051395
 },
 "escalated_share": 0.6733333333333333,
 "headline": {
  "base_priority": 38.3,
  "tuned_priority": 87.2,
  "tuned_priority_ci": [
   85.3,
   89.1
  ],
  "trivial_priority": 42.4,
  "v1_priority": 87.3
 },
 "cascade": {
  "student": {
   "category_acc": 0.8958333333333334,
   "priority_acc": 0.8725,
   "acc": 0.7875,
   "cost_per_1000": 0.0
  },
  "chosen": {
   "threshold": 0.885,
   "escalated": 0.6733333333333333,
   "acc": 0.8283333333333334,
   "kept_acc": 0.9795918367346939,
   "category_acc": 0.9066666666666666,
   "priority_acc": 0.9141666666666667,
   "cost_per_1000": 0.07079393
  },
  "teacher": {
   "category_acc": 0.905,
   "priority_acc": 0.9133333333333333,
   "acc": 0.8258333333333333,
   "cost_per_1000": 0.1051395
  }
 },
 "featured": {
  "easy": {
   "kind": "ticket",
   "id": "test-1105",
   "email": "Subject: Ungeduldete Unterstützung erforderlich\n\nEmail: Ein unerlaubter Zugangsbereich wurde in der IT-Infrastruktur des Krankenhauses entdeckt, was die Sicherheit medizinischer Daten potenziell gefährden könnte. Ausgetretene Software-Vulnerabilitäten und fehlerhafte Zugriffssteuerungen könnten die Ursache sein. Vorübergehende Zugriffsbeschränkungen wurden eingeführt und Passwörter aktualisiert, jedoch besteht die Bedrohung weiterhin. Sofortige Unterstützung ist erforderlich, um weitere Verletzungen zu verhindern und die Schutzmaßnahmen für Patientendaten zu gewährleisten.",
   "pred": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.9985,
      "Product Support": 0.0009,
      "Customer Service": 0.0006,
      "Billing & Payments": 0.0,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9985
    },
    "priority": {
     "probs": {
      "high": 0.9965,
      "medium": 0.0033,
      "low": 0.0002
     },
     "chosen": 0.9965
    }
   },
   "account_confidence": 0.9999,
   "ticket_confidence": 0.9965,
   "escalate": false,
   "gold": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "note": null
  },
  "ambiguous": {
   "kind": "ticket",
   "id": "test-0558",
   "email": "Subject: Support Required for Billing Issue\n\nEmail: I am reaching out to address a billing concern related to my data analytics services. I've been charged twice on my recent statement, and I believe this might be due to a synchronization problem between Puppet and Firebase. I've reviewed my invoices and contacted support, but the issue remains unresolved. Could you please investigate and rectify the billing discrepancy? If you need more details, please inform me, and I will provide them. Thanks for your help. Same account I always use, the one ending 60405.",
   "pred": {
    "category": "Billing & Payments",
    "priority": "medium",
    "account_id": "60405"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.0001,
      "Product Support": 0.0002,
      "Customer Service": 0.0,
      "Billing & Payments": 0.9997,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9997
    },
    "priority": {
     "probs": {
      "high": 0.0926,
      "medium": 0.8861,
      "low": 0.0213
     },
     "chosen": 0.8861
    }
   },
   "account_confidence": 0.9513,
   "ticket_confidence": 0.8861,
   "escalate": false,
   "gold": {
    "category": "Billing & Payments",
    "priority": "medium",
    "account_id": "60405"
   },
   "teacher": {
    "category": "Billing & Payments",
    "priority": "medium",
    "account_id": "60405"
   },
   "note": null
  },
  "escalated": {
   "kind": "ticket",
   "id": "test-0960",
   "email": "Subject: Umsetzung robuster Verschlüsselung für medizinische Daten\n\nEmail: Implementieren Sie eine sichere Verschlüsselungsmethode für die Übertragung und Speicherung medizinischer Daten in den IT-Systemen der Krankenhäuser, um die Daten Sicherheit zu gewährleisten. Zur Info, mein Konto endet auf 12930.",
   "pred": {
    "category": "Technical Support",
    "priority": "low",
    "account_id": "12930"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.748,
      "Product Support": 0.2456,
      "Customer Service": 0.0055,
      "Billing & Payments": 0.0009,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.748
    },
    "priority": {
     "probs": {
      "high": 0.2325,
      "medium": 0.3958,
      "low": 0.3717
     },
     "chosen": 0.3717
    }
   },
   "account_confidence": 0.9564,
   "ticket_confidence": 0.3717,
   "escalate": true,
   "gold": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": "12930"
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": null
   },
   "note": null
  },
  "off_task": {
   "kind": "off-task",
   "id": "off-04",
   "email": "Translate 'good morning' into Spanish.",
   "pred": {
    "category": "Customer Service",
    "priority": "low",
    "account_id": null
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.0011,
      "Product Support": 0.0037,
      "Customer Service": 0.9949,
      "Billing & Payments": 0.0003,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9949
    },
    "priority": {
     "probs": {
      "high": 0.0008,
      "medium": 0.012,
      "low": 0.9871
     },
     "chosen": 0.9871
    }
   },
   "account_confidence": 0.9999,
   "ticket_confidence": 0.9871,
   "escalate": false,
   "gold": null,
   "teacher": null,
   "note": "Not a support email. The model still answers in the ticket format, and is sure enough that the cascade keeps it."
  }
 },
 "tickets": [
  {
   "kind": "ticket",
   "id": "test-0026",
   "email": "Subject: Concern About Patient Billing Access\n\nEmail: An unauthorized attempt to access patient billing data was detected. This might have happened due to a phishing attack. We have reinforced employee training and updated firewall settings. We need your assistance to ensure the security of patient data. Please provide details of the incident, including the date and time it occurred. We would like to schedule a call at your convenience to discuss the necessary steps to secure the patient's data. Please let us know a suitable time for the call at <tel_num>. For reference, my account ends in 86124.",
   "pred": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "86124"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.974,
      "Product Support": 0.0073,
      "Customer Service": 0.0145,
      "Billing & Payments": 0.0042,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.974
    },
    "priority": {
     "probs": {
      "high": 0.7464,
      "medium": 0.2446,
      "low": 0.009
     },
     "chosen": 0.7464
    }
   },
   "account_confidence": 0.9451,
   "ticket_confidence": 0.7464,
   "escalate": true,
   "gold": {
    "category": "Customer Service",
    "priority": "high",
    "account_id": "86124"
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0031",
   "email": "Subject: Elasticsearch-Konfiguration für Datenauswertung\n\nEmail: Bitte leistet mir Unterstützung bei der Einstellung von Elasticsearch zur Verbesserung der Datenauswertung für Anlegedaten. Meine Kontonummer ist 28294.",
   "pred": {
    "category": "Technical Support",
    "priority": "low",
    "account_id": "28294"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.7833,
      "Product Support": 0.2148,
      "Customer Service": 0.0018,
      "Billing & Payments": 0.0001,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.7833
    },
    "priority": {
     "probs": {
      "high": 0.0019,
      "medium": 0.1495,
      "low": 0.8486
     },
     "chosen": 0.8486
    }
   },
   "account_confidence": 0.9837,
   "ticket_confidence": 0.7833,
   "escalate": true,
   "gold": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": "28294"
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": "28294"
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0134",
   "email": "Subject: Assistance with Downtime Problems\n\nEmail: went through unforeseen downtime with various products, such as Twitch Studio Beta and MATLAB. outage possibly due to recent software updates or network troubles. so far, restarted involved applications and verified server connections, but to no avail. team is diligently working to resolve the issue and prevent future occurrences. thank you for your patience and understanding. should you have any questions or concerns, please do not hesitate to contact us. Same account I always use, the one ending 78874.",
   "pred": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "78874"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.9996,
      "Product Support": 0.0003,
      "Customer Service": 0.0,
      "Billing & Payments": 0.0,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9996
    },
    "priority": {
     "probs": {
      "high": 0.8921,
      "medium": 0.1056,
      "low": 0.0023
     },
     "chosen": 0.8921
    }
   },
   "account_confidence": 0.9459,
   "ticket_confidence": 0.8921,
   "escalate": false,
   "gold": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "78874"
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "78874"
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0267",
   "email": "Subject: PrestaShop Data Analytics\n\nEmail: Could you provide more details on integrating data analytics into PrestaShop for investment optimization strategies? I need help with this matter. Dasselbe Konto wie immer, endet auf 63061.",
   "pred": {
    "category": "Product Support",
    "priority": "low",
    "account_id": "63061"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.1406,
      "Product Support": 0.8023,
      "Customer Service": 0.057,
      "Billing & Payments": 0.0001,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.8023
    },
    "priority": {
     "probs": {
      "high": 0.0003,
      "medium": 0.0106,
      "low": 0.9891
     },
     "chosen": 0.9891
    }
   },
   "account_confidence": 0.9753,
   "ticket_confidence": 0.8023,
   "escalate": true,
   "gold": {
    "category": "Technical Support",
    "priority": "low",
    "account_id": "63061"
   },
   "teacher": {
    "category": "Product Support",
    "priority": "low",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0308",
   "email": "Subject: IBM SPSS Statistics Hilfe\n\nEmail: Können Sie detaillierte Informationen zur Einbindung von IBM SPSS Statistics 28 im Bereich Anlagenanalyse für optimierte Entscheidungsfindung liefern? Ich möchte mehr über die Funktionalitäten und Kapazitäten erfahren. Dasselbe Konto wie immer, endet auf 86070.",
   "pred": {
    "category": "Product Support",
    "priority": "low",
    "account_id": "86070"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.1406,
      "Product Support": 0.844,
      "Customer Service": 0.0153,
      "Billing & Payments": 0.0001,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.844
    },
    "priority": {
     "probs": {
      "high": 0.0002,
      "medium": 0.0083,
      "low": 0.9914
     },
     "chosen": 0.9914
    }
   },
   "account_confidence": 0.949,
   "ticket_confidence": 0.844,
   "escalate": true,
   "gold": {
    "category": "Product Support",
    "priority": "low",
    "account_id": null
   },
   "teacher": {
    "category": "Product Support",
    "priority": "low",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0310",
   "email": "Subject: Anfrage an Kundendienst\n\nEmail: Die Projekttermine aktualisieren sich nicht, da ein unerwarteter Serverneustart aufgetreten ist. Mangelnde Wiederherstellungslogik verursachte ein Synchronisationsproblem. Ich habe den Dienst neu gestartet und die Logdateien überprüft, aber das Problem besteht weiterhin.",
   "pred": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.9999,
      "Product Support": 0.0001,
      "Customer Service": 0.0,
      "Billing & Payments": 0.0,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9999
    },
    "priority": {
     "probs": {
      "high": 0.9751,
      "medium": 0.0242,
      "low": 0.0006
     },
     "chosen": 0.9751
    }
   },
   "account_confidence": 0.9997,
   "ticket_confidence": 0.9751,
   "escalate": false,
   "gold": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0392",
   "email": "Subject: Mögliche Verletzung der Datensperreregelung bei den Krankenhausauftritten des IT-Systems\n\nEmail: Es wurde festgestellt, dass potenziell Datensperrerverletzungen bei den IT-Systemen des Krankenhauses bestehen, was die Vertraulichkeit der Patientendaten gefährdet. Die veralteten Sicherheitsprotokolle sind der Rückgriff für unautorisierten Zugriff. Um die Systeme zu schützen, sind Software-aktualisierungen und interne Audits erforderlich. Bitte untersuchen Sie die Angelegenheit und geben Sie Anweisungen für weitere Maßnahmen, um das Datensicherheitskonzept der Patienten zu sichern. Zur Info, mein Konto endet auf 65302.",
   "pred": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "65302"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.9636,
      "Product Support": 0.03,
      "Customer Service": 0.0055,
      "Billing & Payments": 0.0009,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9636
    },
    "priority": {
     "probs": {
      "high": 0.9607,
      "medium": 0.0382,
      "low": 0.0012
     },
     "chosen": 0.9607
    }
   },
   "account_confidence": 0.9537,
   "ticket_confidence": 0.9607,
   "escalate": false,
   "gold": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0474",
   "email": "Subject: Probleme mit Projektrevisionsaktualisierungen\n\nEmail: Der Benutzer hat Schwierigkeiten bei der Synchronisierung von Projektrevisionsaktualisierungen für seine Smart-Thermometer-Chef-Anwendungen auf mehreren Geräten. Nach der Durchführung neuer Softwarepatches hat der Benutzer versucht, das App-Cache zu löschen und die Anwendungen neu zu installieren, aber das Problem blieb bestehen. Der Benutzer hat mehrere Schritte zur Problemlösung durchgeführt, trotzdem behält sich das Problem bestehen. Zur Info, mein Konto endet auf 59190.",
   "pred": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": "59190"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.9861,
      "Product Support": 0.0134,
      "Customer Service": 0.0004,
      "Billing & Payments": 0.0,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9861
    },
    "priority": {
     "probs": {
      "high": 0.4181,
      "medium": 0.5768,
      "low": 0.0051
     },
     "chosen": 0.5768
    }
   },
   "account_confidence": 0.9906,
   "ticket_confidence": 0.5768,
   "escalate": true,
   "gold": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": "59190"
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0479",
   "email": "Subject: Alert for Unauthorized Access to Medical Server\n\nEmail: There has been an unauthorized access to the medical data server. Please pull up account 52952.",
   "pred": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "52952"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.9976,
      "Product Support": 0.0008,
      "Customer Service": 0.0015,
      "Billing & Payments": 0.0,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9976
    },
    "priority": {
     "probs": {
      "high": 0.9879,
      "medium": 0.0112,
      "low": 0.0009
     },
     "chosen": 0.9879
    }
   },
   "account_confidence": 0.9951,
   "ticket_confidence": 0.9879,
   "escalate": false,
   "gold": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "52952"
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "52952"
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0487",
   "email": "Subject: Einbinden Bitdefender Antivirus Plus\n\nEmail: Geben Sie detaillierte Informationen über die Integration von Bitdefender Antivirus Plus in unsere Projektmanagement-Software-as-a-Service-Plattform? Was müssen Sie wissen, um eine erfolgreiche Integration zu gewährleisten?",
   "pred": {
    "category": "Product Support",
    "priority": "low",
    "account_id": null
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.3646,
      "Product Support": 0.6199,
      "Customer Service": 0.0155,
      "Billing & Payments": 0.0,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.6199
    },
    "priority": {
     "probs": {
      "high": 0.0002,
      "medium": 0.0063,
      "low": 0.9935
     },
     "chosen": 0.9935
    }
   },
   "account_confidence": 0.9999,
   "ticket_confidence": 0.6199,
   "escalate": true,
   "gold": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": null
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0531",
   "email": "Subject: Support for Hospital Systems\n\nEmail: There is an unexpected security alert when accessing secured medical data on hospital systems. The issue might be due to an expired security certificate on the WLAN-Router. Steps taken include rebooting the WLAN-Router and updating the software, but the problem still persists. We would greatly appreciate your prompt assistance in resolving this matter. Please let us know any additional steps you need to troubleshoot and fix the issue. Available for discussion.",
   "pred": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.9982,
      "Product Support": 0.0015,
      "Customer Service": 0.0003,
      "Billing & Payments": 0.0,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9982
    },
    "priority": {
     "probs": {
      "high": 0.8211,
      "medium": 0.174,
      "low": 0.0049
     },
     "chosen": 0.8211
    }
   },
   "account_confidence": 0.9999,
   "ticket_confidence": 0.8211,
   "escalate": true,
   "gold": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0757",
   "email": "Subject: Issue with Connectivity of Digital Tools\n\nEmail: Our agency is experiencing connection problems with various digital tools, which are hindering brand growth strategies. Network instability and software compatibility issues have been repeatedly reported. We have tried router restarts and software updates, but the problems persist. We need help to quickly resolve the issue and prevent further disruptions. Meine Kontonummer ist 6910.",
   "pred": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "6910"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.9993,
      "Product Support": 0.0006,
      "Customer Service": 0.0,
      "Billing & Payments": 0.0,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9993
    },
    "priority": {
     "probs": {
      "high": 0.6937,
      "medium": 0.3022,
      "low": 0.0041
     },
     "chosen": 0.6937
    }
   },
   "account_confidence": 0.9915,
   "ticket_confidence": 0.6937,
   "escalate": true,
   "gold": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "6910"
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "6910"
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0798",
   "email": "Subject: Challenge with Access to Medical Data\n\nEmail: There has been an unexpected denial of access to medical data for authorized personnel. This could be due to network configuration or firewall issues. Despite restarting the servers and verifying user credentials, the problem continues. We need your help to address this promptly.",
   "pred": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.9985,
      "Product Support": 0.0011,
      "Customer Service": 0.0004,
      "Billing & Payments": 0.0,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9985
    },
    "priority": {
     "probs": {
      "high": 0.9482,
      "medium": 0.0504,
      "low": 0.0014
     },
     "chosen": 0.9482
    }
   },
   "account_confidence": 0.9999,
   "ticket_confidence": 0.9482,
   "escalate": false,
   "gold": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0813",
   "email": "Subject: Enhancing Investment Analytics Tools\n\nEmail: aiming to enhance investment analysis through data analytics. Specifically, interested in understanding the role of Kaspersky QuickBooks Online. Seeking insights and recommendations on how to integrate these tools for better investment analysis.",
   "pred": {
    "category": "Product Support",
    "priority": "low",
    "account_id": null
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.0742,
      "Product Support": 0.8904,
      "Customer Service": 0.0344,
      "Billing & Payments": 0.001,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.8904
    },
    "priority": {
     "probs": {
      "high": 0.0002,
      "medium": 0.0052,
      "low": 0.9946
     },
     "chosen": 0.9946
    }
   },
   "account_confidence": 0.9999,
   "ticket_confidence": 0.8904,
   "escalate": false,
   "gold": {
    "category": "Product Support",
    "priority": "low",
    "account_id": null
   },
   "teacher": {
    "category": "Product Support",
    "priority": "low",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0960",
   "email": "Subject: Umsetzung robuster Verschlüsselung für medizinische Daten\n\nEmail: Implementieren Sie eine sichere Verschlüsselungsmethode für die Übertragung und Speicherung medizinischer Daten in den IT-Systemen der Krankenhäuser, um die Daten Sicherheit zu gewährleisten. Zur Info, mein Konto endet auf 12930.",
   "pred": {
    "category": "Technical Support",
    "priority": "low",
    "account_id": "12930"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.748,
      "Product Support": 0.2456,
      "Customer Service": 0.0055,
      "Billing & Payments": 0.0009,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.748
    },
    "priority": {
     "probs": {
      "high": 0.2325,
      "medium": 0.3958,
      "low": 0.3717
     },
     "chosen": 0.3717
    }
   },
   "account_confidence": 0.9564,
   "ticket_confidence": 0.3717,
   "escalate": true,
   "gold": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": "12930"
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0963",
   "email": "Subject: Investment Portfolio Not Updating Correctly Today\n\nEmail: The portfolio is not updating. I tried restarting and reviewing the settings. Same account I always use, the one ending 12747.",
   "pred": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": "12747"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.9326,
      "Product Support": 0.0666,
      "Customer Service": 0.0006,
      "Billing & Payments": 0.0002,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9326
    },
    "priority": {
     "probs": {
      "high": 0.4258,
      "medium": 0.5253,
      "low": 0.049
     },
     "chosen": 0.5253
    }
   },
   "account_confidence": 0.9513,
   "ticket_confidence": 0.5253,
   "escalate": true,
   "gold": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "12747"
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "12747"
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0970",
   "email": "Subject: identified lag in data visualization process\n\nEmail: I am encountering issues with data visualization delays. The problem appeared due to intensive Elasticsearch queries. I have already tried restarting Elasticsearch and updating the RAM, but the issue persists. I would appreciate it if you could provide a solution. These delays are affecting my work and I need this problem resolved as soon as possible. Please let me know if there are further steps I can take to investigate the issue. Meine Kontonummer ist 99583.",
   "pred": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": "99583"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.9985,
      "Product Support": 0.0015,
      "Customer Service": 0.0,
      "Billing & Payments": 0.0,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9985
    },
    "priority": {
     "probs": {
      "high": 0.555,
      "medium": 0.4391,
      "low": 0.0059
     },
     "chosen": 0.4391
    }
   },
   "account_confidence": 0.992,
   "ticket_confidence": 0.4391,
   "escalate": true,
   "gold": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": "99583"
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "99583"
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-0975",
   "email": "Subject: Problem with Investment Efficiency\n\nEmail: Investments are failing to optimize due to data inconsistencies, which might be due to an outdated data analysis model. Despite restarting the system and verifying data origins, the issue remains unresolved. Same account I always use, the one ending 84039.",
   "pred": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "84039"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.9323,
      "Product Support": 0.0674,
      "Customer Service": 0.0002,
      "Billing & Payments": 0.0,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9323
    },
    "priority": {
     "probs": {
      "high": 0.5292,
      "medium": 0.4631,
      "low": 0.0078
     },
     "chosen": 0.5292
    }
   },
   "account_confidence": 0.9519,
   "ticket_confidence": 0.5292,
   "escalate": true,
   "gold": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": "84039"
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-1071",
   "email": "Subject: Fehler-Bericht\n\nEmail: Die verwendeten Werkzeuge sind fehlerhaft ausgefallen Dasselbe Konto wie immer, endet auf 81911.",
   "pred": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "81911"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.9943,
      "Product Support": 0.0057,
      "Customer Service": 0.0,
      "Billing & Payments": 0.0,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.9943
    },
    "priority": {
     "probs": {
      "high": 0.9432,
      "medium": 0.0551,
      "low": 0.0017
     },
     "chosen": 0.9432
    }
   },
   "account_confidence": 0.9708,
   "ticket_confidence": 0.9432,
   "escalate": false,
   "gold": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "81911"
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": "81911"
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-1107",
   "email": "Subject: Problems with Social Media Campaign\n\nEmail: Subpar audience interaction For reference, my account ends in 73704.",
   "pred": {
    "category": "Product Support",
    "priority": "medium",
    "account_id": "73704"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.0872,
      "Product Support": 0.7145,
      "Customer Service": 0.1983,
      "Billing & Payments": 0.0001,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.7145
    },
    "priority": {
     "probs": {
      "high": 0.0737,
      "medium": 0.7666,
      "low": 0.1597
     },
     "chosen": 0.7666
    }
   },
   "account_confidence": 0.9761,
   "ticket_confidence": 0.7145,
   "escalate": true,
   "gold": {
    "category": "Product Support",
    "priority": "medium",
    "account_id": "73704"
   },
   "teacher": {
    "category": "Product Support",
    "priority": "low",
    "account_id": "73704"
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-1114",
   "email": "Subject: Medical Data Security Practices\n\nEmail: I would like to seek advice on the security measures that should be implemented for safeguarding medical data on SD-Karte devices. Could you provide details on the recommended protocols? Same account I always use, the one ending 3817.",
   "pred": {
    "category": "Technical Support",
    "priority": "low",
    "account_id": "3817"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.6613,
      "Product Support": 0.3034,
      "Customer Service": 0.027,
      "Billing & Payments": 0.0084,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.6613
    },
    "priority": {
     "probs": {
      "high": 0.0012,
      "medium": 0.0451,
      "low": 0.9537
     },
     "chosen": 0.9537
    }
   },
   "account_confidence": 0.6777,
   "ticket_confidence": 0.6613,
   "escalate": true,
   "gold": {
    "category": "Product Support",
    "priority": "low",
    "account_id": null
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "low",
    "account_id": "3817"
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-1125",
   "email": "Subject: Medizinische Datenschutzverhohlen\n\nEmail: müssen erweiterte Sicherheitsmaßnahmen zur Schutzmedizinischer Daten für betroffene Produkte umgesetzt werden. IT-Systeme müssen integriert werden, um eine bessere Einhaltung zu gewährleisten und die Vertraulichkeit sowie die Integrität sensibler medizinischer Informationen zu sichern.",
   "pred": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.6573,
      "Product Support": 0.334,
      "Customer Service": 0.008,
      "Billing & Payments": 0.0007,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.6573
    },
    "priority": {
     "probs": {
      "high": 0.9353,
      "medium": 0.0582,
      "low": 0.0065
     },
     "chosen": 0.9353
    }
   },
   "account_confidence": 0.9999,
   "ticket_confidence": 0.6573,
   "escalate": true,
   "gold": {
    "category": "Technical Support",
    "priority": "high",
    "account_id": null
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-1128",
   "email": "Subject: Marketing Campaigns Performing Poorly Lately\n\nEmail: Marketing campaigns are performing poorly, impacting brand growth. Despite adjusting ad spend, results have remained unchanged.",
   "pred": {
    "category": "Product Support",
    "priority": "medium",
    "account_id": null
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.0467,
      "Product Support": 0.8973,
      "Customer Service": 0.0558,
      "Billing & Payments": 0.0002,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.8973
    },
    "priority": {
     "probs": {
      "high": 0.0316,
      "medium": 0.9047,
      "low": 0.0636
     },
     "chosen": 0.9047
    }
   },
   "account_confidence": 0.9999,
   "ticket_confidence": 0.8973,
   "escalate": false,
   "gold": {
    "category": "Product Support",
    "priority": "medium",
    "account_id": null
   },
   "teacher": {
    "category": "Product Support",
    "priority": "medium",
    "account_id": null
   },
   "note": null
  },
  {
   "kind": "ticket",
   "id": "test-1189",
   "email": "Subject: Unanticipated Drop in Investment Gains\n\nEmail: The returns on our investment have dropped unexpectedly. Potential reasons may include inaccurate data modeling or algorithmic errors. Despite reviewing the data sources and updating the system, the issue continues. I require your assistance to address this and avoid similar problems in the future. For reference, my account ends in 97705.",
   "pred": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": "97705"
   },
   "confidence": {
    "category": {
     "probs": {
      "Technical Support": 0.8021,
      "Product Support": 0.1965,
      "Customer Service": 0.0009,
      "Billing & Payments": 0.0005,
      "Returns & Exchanges": 0.0
     },
     "chosen": 0.8021
    },
    "priority": {
     "probs": {
      "high": 0.5096,
      "medium": 0.4733,
      "low": 0.0172
     },
     "chosen": 0.4733
    }
   },
   "account_confidence": 0.9917,
   "ticket_confidence": 0.4733,
   "escalate": true,
   "gold": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": "97705"
   },
   "teacher": {
    "category": "Technical Support",
    "priority": "medium",
    "account_id": null
   },
   "note": null
  }
 ]
};
