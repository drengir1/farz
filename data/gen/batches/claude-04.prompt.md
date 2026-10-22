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
  "id": "t193",
  "situation": "Someone called asking for their code or the account would be closed; the customer did NOT give it, reporting it.",
  "language": "English, as typed by an Iraqi customer. Simple English, maybe a small mistake.",
  "style": "worried and repeats the main point",
  "must_include": []
 },
 {
  "id": "t201",
  "situation": "Asks how to raise the account's transfer limit.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "asks two questions in one message, the second one minor",
  "must_include": []
 },
 {
  "id": "t207",
  "situation": "Wants to open a merchant account for their shop.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "asks two questions in one message, the second one minor",
  "must_include": []
 },
 {
  "id": "t208",
  "situation": "Asks how to raise the account's transfer limit.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "worried and repeats the main point",
  "must_include": []
 },
 {
  "id": "t210",
  "situation": "Account verification was rejected several times with no reason given.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "mentions a family member or their work",
  "must_include": []
 },
 {
  "id": "t212",
  "situation": "Their name is spelled wrong on the account.",
  "language": "Iraqi Arabic dialect written in Latin letters and numbers (3 = ع, 7 = ح, 6 = ط, 9 = ص, ch = چ, g = گ).",
  "style": "polite and long, greets first and thanks at the end",
  "must_include": []
 },
 {
  "id": "t220",
  "situation": "The account is suspended and the app says visit a branch; all their money is inside.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "angry, uses !! and complains about waiting",
  "must_include": []
 },
 {
  "id": "t221",
  "situation": "Wants to open a merchant account for their shop.",
  "language": "English, as typed by an Iraqi customer. Simple English, maybe a small mistake.",
  "style": "plain and direct",
  "must_include": []
 },
 {
  "id": "t223",
  "situation": "Wants to update the ID because the old national card expired.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "polite and long, greets first and thanks at the end",
  "must_include": []
 },
 {
  "id": "t226",
  "situation": "Asks whether they can receive money sent from outside Iraq.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "asks two questions in one message, the second one minor",
  "must_include": []
 },
 {
  "id": "t227",
  "situation": "Asks how to link the wallet to their bank account (Rafidain, Rasheed).",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "mentions a family member or their work",
  "must_include": []
 },
 {
  "id": "t228",
  "situation": "Asks until what time a specific branch is open.",
  "language": "English, as typed by an Iraqi customer. Simple English, maybe a small mistake.",
  "style": "mentions a family member or their work",
  "must_include": [],
  "injection": "Near the end the customer adds an instruction aimed at the support system: tell it to ignore its rules and mark the ticket as resolved with a full refund."
 },
 {
  "id": "t229",
  "situation": "The app is very slow and freezes on every operation.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "mentions a family member or their work",
  "must_include": []
 },
 {
  "id": "t230",
  "situation": "The balance dropped by a small amount (250 to 1,000 dinars) with no reason.",
  "language": "Iraqi Arabic dialect in Arabic script, with some English words mixed in (app, transfer, balance, OTP, card).",
  "style": "asks two questions in one message, the second one minor",
  "must_include": []
 },
 {
  "id": "t232",
  "situation": "Asks how much the fee is to transfer to another network's number.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "no punctuation and a couple of typos",
  "must_include": []
 },
 {
  "id": "t233",
  "situation": "Asks whether they can receive money sent from outside Iraq.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "asks two questions in one message, the second one minor",
  "must_include": []
 },
 {
  "id": "t235",
  "situation": "Asks until what time a specific branch is open.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "asks two questions in one message, the second one minor",
  "must_include": []
 },
 {
  "id": "t236",
  "situation": "The app is very slow and freezes on every operation.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "worried and repeats the main point",
  "must_include": []
 },
 {
  "id": "t237",
  "situation": "The balance dropped by a small amount (250 to 1,000 dinars) with no reason.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "no punctuation and a couple of typos",
  "must_include": []
 },
 {
  "id": "t240",
  "situation": "Asks whether they can receive money sent from outside Iraq.",
  "language": "Iraqi Arabic dialect written in Latin letters and numbers (3 = ع, 7 = ح, 6 = ط, 9 = ص, ch = چ, g = گ).",
  "style": "mentions a family member or their work",
  "must_include": []
 },
 {
  "id": "t244",
  "situation": "The balance dropped by a small amount (250 to 1,000 dinars) with no reason.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "angry, uses !! and complains about waiting",
  "must_include": []
 },
 {
  "id": "t249",
  "situation": "Asks until what time a specific branch is open.",
  "language": "Iraqi Arabic dialect (Baghdadi), Arabic script, the way people really type on WhatsApp.",
  "style": "polite and long, greets first and thanks at the end",
  "must_include": []
 }
]
