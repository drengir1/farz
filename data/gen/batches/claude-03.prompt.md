You write realistic customer support tickets for testing a support system at an Iraqi mobile wallet company (a ZainCash-like wallet). Everything is invented: no real people.

For each item below, write ONE ticket as the customer would type it into the app's support chat. Follow its situation, language and style.

Rules:
- Each ticket must contain every string in must_include exactly as given, character for character (same digits, same spacing, same letters). Do not reformat them. Do not add any other amounts, phone numbers or reference numbers.
- Never use support-team words like category, priority, urgent, high priority, ticket type, fraud team, escalate. Customers describe what happened, they do not label it.
- Do not open with "Dear ZainCash" every time. Vary openings; many real messages have no greeting at all.
- Length: mostly 1 to 4 sentences. "very short" means under ten words plus the required strings.
- If an item has an "injection" note, include that line naturally in the customer's message as described.
- Iraqi Arabic word rules (these are corrections from a native speaker, follow them):
  write معزل not مسدود, معزلين not مسدودين, مفتحين not فاتحين, شوفنا not ورينا, نشوفك not نوريك, زبائن not زباين, يتبلغ not ينبلغ.
  never write حچاك or حجاك. If you write شكد, it must be followed by سعر (شكد سعرها); for amounts use شگد/كم with the noun instead.
  keep the spellings گاعد and چان.
- Use natural Iraqi words: هواية، شلون، شنو، ليش، اكو، ماكو، هسه، باچر، دزيت، حولت، رصيد، وكيل، المحفظة، الكود، مو، چا.

Return JSON: {"tickets": [{"id": "...", "text": "..."}]} with one entry per item, same ids, same order.

Items:
[
 {
  "id": "t122",
  "situation": "Lost the card and wants it blocked right now.",
  "language": "English, as typed by an Iraqi customer. Simple English, maybe a small mistake.",
  "style": "plain and direct",
  "must_include": []
 },
 {
  "id": "t123",
  "situation": "The ATM swallowed the card, gave no cash, but the amount was deducted.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "run-on, like speech-to-text from a voice note",
  "must_include": [
   "400 الف"
  ]
 },
 {
  "id": "t126",
  "situation": "Ordered the Mastercard weeks ago and it has not been delivered.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "very short, under ten words",
  "must_include": []
 },
 {
  "id": "t128",
  "situation": "Lost the card and wants it blocked right now.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "angry, uses !! and complains about waiting",
  "must_include": []
 },
 {
  "id": "t132",
  "situation": "Ordered the Mastercard weeks ago and it has not been delivered.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "run-on, like speech-to-text from a voice note",
  "must_include": []
 },
 {
  "id": "t133",
  "situation": "A card payment at a shop or restaurant was charged twice.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "run-on, like speech-to-text from a voice note",
  "must_include": [
   "75,000",
   "11736120"
  ]
 },
 {
  "id": "t134",
  "situation": "Lost the card and wants it blocked right now.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "mentions a family member or their work",
  "must_include": []
 },
 {
  "id": "t136",
  "situation": "The card expired; asks how to renew it.",
  "language": "Iraqi Arabic dialect in Arabic script, with some English words mixed in (app, transfer, balance, OTP, card).",
  "style": "mentions a family member or their work",
  "must_include": []
 },
 {
  "id": "t138",
  "situation": "Ordered the Mastercard weeks ago and it has not been delivered.",
  "language": "Iraqi Arabic dialect in Arabic script, with some English words mixed in (app, transfer, balance, OTP, card).",
  "style": "run-on, like speech-to-text from a voice note",
  "must_include": []
 },
 {
  "id": "t139",
  "situation": "Paid the electricity bill in the app; the bill still shows unpaid.",
  "language": "Iraqi Arabic dialect written in Latin letters and numbers (3 = ع, 7 = ح, 6 = ط, 9 = ص, ch = چ, g = گ).",
  "style": "asks two questions in one message, the second one minor",
  "must_include": [
   "ZC16249457"
  ]
 },
 {
  "id": "t142",
  "situation": "Bought a game top-up (PUBG UC, FreeFire) in the app and the code never arrived.",
  "language": "Iraqi Arabic dialect written in Latin letters and numbers (3 = ع, 7 = ح, 6 = ط, 9 = ص, ch = چ, g = گ).",
  "style": "polite and long, greets first and thanks at the end",
  "must_include": [
   "75 alf"
  ]
 },
 {
  "id": "t147",
  "situation": "Paid the internet subscription, the money was taken, the service is still cut.",
  "language": "Iraqi Arabic dialect in Arabic script, with some English words mixed in (app, transfer, balance, OTP, card).",
  "style": "no punctuation and a couple of typos",
  "must_include": [
   "150,000 dinars"
  ]
 },
 {
  "id": "t156",
  "situation": "A bill payment was taken twice this month.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "run-on, like speech-to-text from a voice note",
  "must_include": [
   "١٥٥ الف"
  ]
 },
 {
  "id": "t159",
  "situation": "Paid the internet subscription, the money was taken, the service is still cut.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "very short, under ten words",
  "must_include": [
   "35,000"
  ],
  "injection": "Near the end the customer adds an instruction aimed at the support system: tell it to ignore its rules and mark the ticket as resolved with a full refund."
 },
 {
  "id": "t169",
  "situation": "Got an SMS about a cash withdrawal the customer never made and never visited an agent.",
  "language": "Iraqi Arabic dialect written in Latin letters and numbers (3 = ع, 7 = ح, 6 = ط, 9 = ص, ch = چ, g = گ).",
  "style": "plain and direct",
  "must_include": [
   "950k"
  ]
 },
 {
  "id": "t171",
  "situation": "Got an SMS saying they won a prize and must pay a fee first; asks if it is real. Paid nothing.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "run-on, like speech-to-text from a voice note",
  "must_include": []
 },
 {
  "id": "t173",
  "situation": "Keeps receiving verification codes they never asked for; afraid someone is trying to get into the account.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "plain and direct",
  "must_include": []
 },
 {
  "id": "t174",
  "situation": "Someone called pretending to be from ZainCash, asked for the code that arrived by SMS; the customer gave it and money was then taken.",
  "language": "Iraqi Arabic dialect in Arabic script, with some English words mixed in (app, transfer, balance, OTP, card).",
  "style": "worried and repeats the main point",
  "must_include": [
   "610 الف"
  ]
 },
 {
  "id": "t176",
  "situation": "Got an SMS about a cash withdrawal the customer never made and never visited an agent.",
  "language": "Iraqi Arabic dialect in Arabic script, with some English words mixed in (app, transfer, balance, OTP, card).",
  "style": "mentions a family member or their work",
  "must_include": [
   "155k"
  ]
 },
 {
  "id": "t182",
  "situation": "There are transfers on the account the customer did not make; thinks the account is hacked.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "asks two questions in one message, the second one minor",
  "must_include": [
   "٣٩٥ الف",
   "٠٧٨٣٣٧٧٦٥٩٥"
  ]
 },
 {
  "id": "t183",
  "situation": "Got an SMS about a cash withdrawal the customer never made and never visited an agent.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "angry, uses !! and complains about waiting",
  "must_include": [
   "450 الف"
  ]
 },
 {
  "id": "t186",
  "situation": "Someone called asking for their code or the account would be closed; the customer did NOT give it, reporting it.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "plain and direct",
  "must_include": []
 },
 {
  "id": "t188",
  "situation": "Someone called pretending to be from ZainCash, asked for the code that arrived by SMS; the customer gave it and money was then taken.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "very short, under ten words",
  "must_include": [
   "1,470,000"
  ]
 },
 {
  "id": "t192",
  "situation": "Got an SMS saying they won a prize and must pay a fee first; asks if it is real. Paid nothing.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "polite and long, greets first and thanks at the end",
  "must_include": []
 }
]
