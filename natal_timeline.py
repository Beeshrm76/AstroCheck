#!/usr/bin/env python3
"""
natal_timeline.py - deterministic cycle ledger for the corrected natal dossier.

Computes (no hand-typed placeholders):
  * Vimshottari Mahadasha / Antardasha windows (Rahu MD, Jupiter MD, Saturn MD)
  * Hellenistic annual profections (house, sign, lord of the year)
  * BaZi annual pillar, Ten God vs Day Master 乙, branch interactions
  * Maya Long Count / Tzolk'in / Haab' (GMT 584283)

Interpretation text lives in the CAREER/LOVE/FINANCE/HEALTH dicts below;
edit those, re-run, and the markdown tables regenerate.

Usage:  python natal_timeline.py > section4.md
        python natal_timeline.py --test
"""
import sys
from datetime import date

BIRTH = date(2004, 4, 6)

# ------------------------------------------------------------------ Vimshottari
VIM = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
       "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
MD_WINDOWS = {  # from the dossier: Moon in Chitra -> Mars balance -> Rahu -> Jupiter
    "Rahu": (date(2006, 5, 10), date(2024, 5, 10)),
    "Jupiter": (date(2024, 5, 10), date(2040, 5, 10)),
}


def antardashas(md):
    s, e = MD_WINDOWS[md]
    total = (e - s).days
    i = ORDER.index(md)
    out, cur = [], s
    for k in range(9):
        lord = ORDER[(i + k) % 9]
        days = round(total * VIM[lord] / 120)
        nxt = e if k == 8 else date.fromordinal(cur.toordinal() + days)
        out.append((lord, cur, nxt))
        cur = nxt
    return out


ALL_AD = [(md, ad, s, e) for md in MD_WINDOWS for ad, s, e in antardashas(md)]
ALL_AD.sort(key=lambda t: t[2])


def dasha_label(year):
    ys, ye = date(year, 1, 1), date(year, 12, 31)
    parts = []
    for md, ad, s, e in ALL_AD:
        if s <= ye and e > ys:
            tag = f"{md[:3]}-{ad[:3]}"
            if s > ys:
                tag += f" (from {s.strftime('%b')})"
            parts.append(tag)
    if year == 2040:
        parts.append("Saturn MD (from May)")
    return " → ".join(parts)


# ------------------------------------------------------------------ Profections
SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra",
         "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORD = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus",
             "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
ASC_SIGN = 3  # Cancer (tropical whole sign)


def profection(age):
    h = age % 12 + 1
    s = (ASC_SIGN + age) % 12
    return h, SIGNS[s], SIGN_LORD[s]


# ------------------------------------------------------------------ BaZi
STEMS = "甲乙丙丁戊己庚辛壬癸"
BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
DM = 1  # 乙
NATAL = {"Y": "申", "M": "辰", "D": "卯", "H": "巳"}


def year_pillar(y):
    return STEMS[(y - 4) % 10], BRANCHES[(y - 4) % 12]


def ten_god(stem_idx, dm=DM):
    e, d = stem_idx // 2, dm // 2          # element index: wood,fire,earth,metal,water
    same = (stem_idx % 2) == (dm % 2)
    if e == d:
        return "比肩" if same else "劫财"
    if e == (d + 1) % 5:
        return "食神" if same else "伤官"   # output
    if e == (d + 2) % 5:
        return "偏财" if same else "正财"   # wealth
    if e == (d + 3) % 5:
        return "七杀" if same else "正官"   # officer / killings
    return "偏印" if same else "正印"       # resource


PAIRS = lambda s: {frozenset(p) for p in s.split()}  # noqa: E731
HARMONY = PAIRS("子丑 寅亥 卯戌 辰酉 巳申 午未")
HARM = PAIRS("子未 丑午 寅巳 卯辰 申亥 酉戌")
BREAK = PAIRS("子酉 丑辰 寅亥 卯午 巳申 未戌")
PUNISH = PAIRS("子卯")
SELF = set("辰午酉亥")
TRINES = ["申子辰", "亥卯未", "寅午戌", "巳酉丑"]


def interactions(branch):
    out = []
    bi = BRANCHES.index(branch)
    for pos, nb in NATAL.items():
        pair = frozenset((branch, nb))
        if (bi - BRANCHES.index(nb)) % 12 == 6:
            out.append(f"clash {nb}({pos})")
        if pair in HARMONY:
            out.append(f"combine {nb}({pos})")
        if pair in HARM:
            out.append(f"harm {nb}({pos})")
        if pair in BREAK:
            out.append(f"break {nb}({pos})")
        if pair in PUNISH:
            out.append(f"punish {nb}({pos})")
        if branch == nb and branch in SELF:
            out.append(f"self-punish {nb}({pos})")
        elif branch == nb:
            out.append(f"repeat {nb}({pos})")
    for t in TRINES:
        if branch in t:
            others = [b for b in t if b != branch]
            present = [b for b in others if b in NATAL.values()]
            if len(present) == 2:
                out.append(f"full trine {t} completed")
            else:
                for pos, nb in NATAL.items():
                    if nb in present:
                        out.append(f"half-trine {nb}({pos})")
    if branch in "寅巳申" and set("寅巳申") - {branch} <= set(NATAL.values()):
        out.append("triple punishment 寅巳申 completed")
    return out


# ------------------------------------------------------------------ Maya
TZ_NAMES = ["Imix", "Ik", "Akbal", "Kan", "Chicchan", "Cimi", "Manik", "Lamat",
            "Muluc", "Oc", "Chuen", "Eb", "Ben", "Ix", "Men", "Cib", "Caban",
            "Etznab", "Cauac", "Ahau"]
HAAB = ["Pop", "Uo", "Zip", "Zotz", "Tzec", "Xul", "Yaxkin", "Mol", "Chen", "Yax",
        "Zac", "Ceh", "Mac", "Kankin", "Muan", "Pax", "Kayab", "Cumku", "Wayeb"]


def maya(d, corr=584283):
    jdn = d.toordinal() + 1721425
    n = jdn - corr
    lc = [n // 144000, n % 144000 // 7200, n % 7200 // 360, n % 360 // 20, n % 20]
    off = n - 1872000                      # 13.0.0.0.0 = 4 Ahau 8 Cumku
    tz = f"{(3 + off) % 13 + 1} {TZ_NAMES[(19 + off) % 20]}"
    pos = (348 + off) % 365
    hb = f"{pos % 20} {HAAB[pos // 20]}"
    return ".".join(map(str, lc)), tz, hb


# ------------------------------------------------------------------ Interpretation text with Inspiration & Actions
CAREER = {
 2026: {
     'pred': "Gains come through networks and allies. Output year (伤官) rewards visible skill, but the 午–卯 break warns of friction with seniors or abrupt role changes.",
     'action': "Launch visible portfolio projects; leverage peer mastermind groups; avoid overt confrontation with entrenched authority."
 },
 2027: {
     'pred': "Behind-the-scenes year: Saturn sub-period favors patient skill-building, research and remote work. Low visibility, steady output.",
     'action': "Commit to deep technical mastery or certification; work without craving immediate recognition; build internal software/systems."
 },
 2028: {
     'pred': "Profection returns to the Ascendant (Saturn). Direct Wealth: a clearly defined role and recognition for reliability.",
     'action': "Step into an explicit title or executive responsibility; monetize established competence; negotiate compensation based on verifiable output."
 },
 2029: {
     'pred': "Sun-lorded year (Sun in the 10th): pay follows status. 酉 clashes the Day Branch, so a job or direction change is likely; Mercury sub-period from January favors analytical work.",
     'action': "Pivot toward high-leverage analytical roles; welcome structural repositioning; draft contracts with meticulous scrutiny."
 },
 2030: {
     'pred': "Best year for credentials, publishing and technical mastery (Mercury is Lagna lord and year lord). Direct Officer brings formal titles or approval; 戌 clashes 辰, so expect procedural friction.",
     'action': "Publish intellectual property; apply for institutional licensure; navigate bureaucratic delays with methodical patience."
 },
 2031: {
     'pred': "Foundations: relocation, home-office or property-linked decisions. Seven Killings plus the 亥–巳 clash raise pressure; avoid impulsive exits. Ketu sub-period turns attention inward from April.",
     'action': "Solidify operational base or international remote hub; resist rage-quitting under high stress; seek quiet strategic counsel."
 },
 2032: {
     'pred': "Creative or entrepreneurial initiative (Mars year lord). Resource star favors learning and mentorship, and 子 completes the 申子辰 water trine (Resource for a Wood Day Master). Venus sub-period from March supports creative, client-facing or foreign work.",
     'action': "Inaugurate independent venture or flagship creative product; partner with experienced mentors; engage international clients."
 },
 2033: {
     'pred': "Service and operations (Jupiter-lorded 6th). Good year to systematize and delegate; unconventional learning pays; watch overwork.",
     'action': "Document workflows and hire support; automate repetitive tasks; acquire specialized analytical skillsets."
 },
 2034: {
     'pred': "Contracts, partnerships and public roles. 寅 completes the 寅巳申 punishment trio with natal 巳 and 申: read agreements, vet partners. Sun sub-period begins in November.",
     'action': "Conduct exhaustive legal due diligence on all joint ventures; require dual signatures on operational funds; lead with transparent integrity."
 },
 2035: {
     'pred': "Shared resources, restructuring, deep research. Friend star: peer collaboration or competition. Moon sub-period from September shifts focus to family and security.",
     'action': "Restructure corporate equity or debt; audit shared accounts; focus on organizational consolidation."
 },
 2036: {
     'pred': "Higher learning, teaching, travel, publishing. Pisces is also the MC sign, so reputation builds through ideas.",
     'action': "Deliver keynote addresses or publish broad treatises; initiate cross-border partnerships; mentor rising talent."
 },
 2037: {
     'pred': "Profection peak in Aries (the Sun's exaltation sign). Mars sub-period from January brings competitive drive; Rahu sub-period from December starts an ambition-heavy phase.",
     'action': "Seize top executive post or industry leadership; campaign boldly for major mandates; temper aggression with strategic poise."
 },
 2038: {
     'pred': "Rahu sub-period meets the 11th-house profection: strong year for network leverage and income growth. Avoid shortcuts and overpromising.",
     'action': "Scale high-impact network alliances; enforce the 6-month liquid reserve rule; reject speculative get-rich-quick gambits."
 },
 2039: {
     'pred': "Consolidation and strategy, possibly remote or foreign work. Preparation for the Saturn Mahadasha.",
     'action': "Tidy operational loose ends; conduct quiet behind-the-scenes research; transition from hyper-expansion to institutional stability."
 },
 2040: {
     'pred': "Threshold: Saturn Mahadasha begins in May and a new profection cycle starts. Direct Officer favors formal authority and responsibility.",
     'action': "Embrace long-term institutional governance; anchor personal legacy; establish 20-year structural objectives."
 }
}

LOVE = {
 2026: {
     'pred': "Venus-lorded year: romance grows from friendships and shared circles. Saturn sub-period (from late June) favors seriousness over casual contact.",
     'action': "Explore romantic potential within existing community; set clear mutual intentions early; favor emotional maturity over ephemeral excitement."
 },
 2027: {
     'pred': "Private, inward bonding; the 卯–未 half-trine (亥卯未) supports a quiet, loyal connection. Watch secrecy and unspoken expectations.",
     'action': "Protect couple intimacy from outside noise; establish shared domestic rituals; communicate unspoken vulnerable needs openly."
 },
 2028: {
     'pred': "Self-focus and clearer standards; you are more visible. Moon-lorded year puts emotional needs in front.",
     'action': "Articulate core relationship standards without compromise; ensure your personal identity is not submerged in partnership."
 },
 2029: {
     'pred': "Strongest tension signal: 酉 clashes the Day Branch (spouse palace). Expect disagreement, a breakup or changed living arrangements. Communicate directly.",
     'action': "Address lingering friction calmly and without vindictiveness; seek couples mediation if needed; avoid stonewalling during conflict."
 },
 2030: {
     'pred': "Connection through conversation, study, friends or siblings; the 卯–戌 combine is supportive.",
     'action': "Bond over intellectual projects, travel, or shared learning; introduce partner to close sibling/peer network."
 },
 2031: {
     'pred': "Domestic anchoring (Venus year lord); 亥–卯 half-combine supports commitment or cohabitation. Ketu sub-period from April can bring withdrawal.",
     'action': "Invest in comfortable home life or cohabitation; provide partner breathing room for solitude; maintain patient tenderness."
 },
 2032: {
     'pred': "Peak romance window: 5th-house profection, Venus sub-period from March, and natal Moon+Ketu in the 5th. The 子–卯 punishment adds intensity: aim for honesty over drama.",
     'action': "Plan romantic adventures and creative dates; choose direct honesty over emotional games; celebrate relational milestones."
 },
 2033: {
     'pred': "Everyday partnership built on routine and practical care. Fewer fireworks, more proof of reliability.",
     'action': "Demonstrate love through practical service; share domestic chores fairly; establish soothing weekly date nights."
 },
 2034: {
     'pred': "7th-house profection (Saturn-lorded): commitment themes strongest, Venus sub-period active. Mature, slower unions suggested. 寅 clashes 申 and completes the punishment trio: test and clarify first.",
     'action': "Formalize long-term commitment or marriage; clarify financial agreements in advance; communicate transparently during family tensions."
 },
 2035: {
     'pred': "Deep intimacy, vulnerability and joint finances. A peer-like partner or rivalry is possible. Do the emotional work.",
     'action': "Have fearless conversations about shared assets and emotional wounds; embrace authentic vulnerability over guarded stoicism."
 },
 2036: {
     'pred': "Shared growth through travel or learning; a partner from a different culture is possible. Jupiter (7th lord) is year lord.",
     'action': "Travel abroad together; explore philosophical or spiritual dimensions; celebrate diverse cultural horizons."
 },
 2037: {
     'pred': "Career dominates; Mars sub-period can bring impatience at home. Balance is the lesson.",
     'action': "Schedule non-negotiable couple time despite intense work demands; avoid bringing workplace aggression home."
 },
 2038: {
     'pred': "Social and aspirational bonds favored; Rahu may tempt toward an idealized or unconventional partner. Check for substance.",
     'action': "Evaluate new connections on real-world character rather than idealized allure; protect established loyal relationships."
 },
 2039: {
     'pred': "Private, restorative year for repair and long-term trust.",
     'action': "Take a restorative retreat together; forgive old missteps; reaffirm foundational emotional vows."
 },
 2040: {
     'pred': "Identity and needs reset before the Saturn era; choose on long-term compatibility.",
     'action': "Align on life goals for the next two decades; prioritize partners who value steady mutual devotion and integrity."
 }
}

FINANCE = {
 2026: {
     'pred': "11th-house profection (gains) with Mercury/Rahu already in the sidereal 11th: income through connections. Saturn sub-period asks for disciplined saving.",
     'action': "Monetize professional network; save 30%+ of windfall income; set up automated capital accumulation channels."
 },
 2027: {
     'pred': "Expenses and hidden costs rise (12th profection; Venus and Mars in the sidereal 12th). Preserve capital; avoid lending and speculation.",
     'action': "Refuse unsecured personal loans; audit hidden subscriptions and leaks; maintain a conservative, defensive portfolio."
 },
 2028: {
     'pred': "Direct Wealth: steadier income tied to your own effort and name. Good year to build a base.",
     'action': "Negotiate baseline salary or core retainer fees; acquire reliable tangible assets; eliminate lingering consumer debt."
 },
 2029: {
     'pred': "2nd-house (money) profection with Indirect Wealth: side or variable income. The Day-Branch clash warns against hasty financial changes.",
     'action': "Build diversified income streams; avoid impulsive changes to investment allocations; keep emergency cash accessible."
 },
 2030: {
     'pred': "Skills, IP and trade-based income. Good year to invest in education or tools.",
     'action': "Invest capital into proprietary tools, hardware, and accredited training; protect copyrighted assets."
 },
 2031: {
     'pred': "Property, housing and family finances in focus. The 亥–巳 clash and Ketu sub-period argue against impulse purchases.",
     'action': "Conduct thorough structural inspections before real estate purchases; lock in fixed-rate financing; avoid speculative property flips."
 },
 2032: {
     'pred': "Speculation tempts (5th profection, Mars lord). Apply the overextension warning; Venus sub-period raises discretionary spending.",
     'action': "Set strict limits on speculative trading (max 5% portfolio); cap luxury entertainment budgets; reinvest windfalls safely."
 },
 2033: {
     'pred': "Steady earnings through work and service; clear debts, tidy systems.",
     'action': "Pay down principal mortgages/loans; optimize tax deductions with a certified advisor; streamline billing workflows."
 },
 2034: {
     'pred': "Rob-Wealth (劫财) is a classic caution on shared money: keep partnership and contract finances documented and separate.",
     'action': "Separate business capital from personal funds; obtain notarized contracts for joint investments; reject informal money pledges."
 },
 2035: {
     'pred': "8th house: joint finances, loans, taxes, inheritance. Peer-related spending is possible. Insure and document.",
     'action': "Update estate plans, wills, and insurance policies; resolve lingering tax audits or shared liabilities promptly."
 },
 2036: {
     'pred': "Growth through knowledge, international work, publishing. Moderate expansion favored.",
     'action': "Deploy capital into global opportunities or education ventures; diversify currency holdings cautiously."
 },
 2037: {
     'pred': "Income tied to position and authority. Mars sub-period supports gains but also risk-taking.",
     'action': "Leverage senior title for equity participation; avoid leveraged bets during high-confidence periods."
 },
 2038: {
     'pred': "Likely a high-gain year: 11th profection, Rahu sub-period, Direct Wealth. Enforce the 6-month liquid reserve rule; Rahu rewards boldness and punishes overreach.",
     'action': "Capitalize on major commercial contracts; immediately bank a non-negotiable 6-month living reserve; do not over-leverage."
 },
 2039: {
     'pred': "Slower cash flow; spending on health, travel, retreat. Consolidate.",
     'action': "Prune speculative investments; allocate resources to health and sabbatical wellness; preserve liquid liquidity."
 },
 2040: {
     'pred': "Shift from expansion to structure. Saturn Mahadasha rewards long-term, unglamorous wealth habits.",
     'action': "Lock in defensive, index-based wealth preservation; prioritize high-dividend, cash-flow-positive assets for the 19-year Saturn cycle."
 }
}

HEALTH = {
 2026: {
     'pred': "High social stimulation and Fire energy. Protect sleep; avoid burnout from commitments.",
     'action': "Set a strict 10:30 PM screen curfew; drink electrolytes to balance fire/heat; practice calming parasympathetic breathwork."
 },
 2027: {
     'pred': "Saturn-on-Ascendant theme meets the retreat house. Prioritize rest, sleep hygiene and stress release; nervous fatigue is the main risk.",
     'action': "Schedule quarterly digital detox retreats; optimize bedroom darkness and temperature; consult a sleep specialist if insomnia flares."
 },
 2028: {
     'pred': "The body is the focus. Build durable routines (training, diet) suited to slow, consistent, structured effort.",
     'action': "Adopt progressive strength training 3x/week; prioritize high-protein whole foods; focus on posture and spine alignment."
 },
 2029: {
     'pred': "Stress-prone transition year (Day-Branch clash). Watch tension and sleep.",
     'action': "Incorporate daily somatic stretching; reduce stimulants and caffeine; monitor gastrointestinal and pelvic tension."
 },
 2030: {
     'pred': "High mental load (Mercury). Schedule screen-free time; avoid over-scheduling.",
     'action': "Take daily 30-minute nature walks without headphones; practice eye strain relief exercises; protect mental bandwidth."
 },
 2031: {
     'pred': "Wellbeing tied to the home environment. Ketu sub-period argues for quiet recovery.",
     'action': "Improve domestic air and water filtration; establish a quiet meditation/reading nook; enjoy nourishing home-cooked meals."
 },
 2032: {
     'pred': "High-energy year for sport, creativity and play. Mars lord gives drive; avoid overtraining.",
     'action': "Engage in competitive sports or martial arts; include deload weeks to prevent joint injuries; stay hydrated."
 },
 2033: {
     'pred': "Health-house profection: check-ups and routines matter. Work stress is the likeliest imbalance.",
     'action': "Schedule comprehensive blood work and annual preventative check-ups; enforce strict finish times on the workday."
 },
 2034: {
     'pred': "Relationship and legal stress may show in the body. Keep boundaries and recovery habits.",
     'action': "Seek massage or somatic therapy for neck/shoulder tension; practice daily boundary-setting; avoid stress-eating."
 },
 2035: {
     'pred': "Depth year. Emotional processing with a trusted person or professional supports wellbeing.",
     'action': "Work through unprocessed grief or emotional weight with a therapist; explore journaling; prioritize deep sleep."
 },
 2036: {
     'pred': "Generally supportive; travel and meaning-making improve mood.",
     'action': "Plan active outdoor excursions in nature; maintain regular daily rhythms while traveling; nourish mental optimism."
 },
 2037: {
     'pred': "High ambition and Fire tension. Guard against overwork and heat-type stress.",
     'action': "Monitor blood pressure and cardiac workload; take scheduled breaks during work crunches; prioritize cooling foods."
 },
 2038: {
     'pred': "Busy calendar; maintain routines so the pace doesn't erode sleep.",
     'action': "Guard evening wind-down rituals fiercely; decline non-essential social events; delegate administrative logistics."
 },
 2039: {
     'pred': "Rest and recovery priority; nervous-system regulation.",
     'action': "Engage in restorative yoga, sauna, or hydrotherapy; simplify daily calendar commitments; rebuild adrenal reserves."
 },
 2040: {
     'pred': "New baseline of habits before the Saturn era: regular sleep, strength work, sustainable pacing.",
     'action': "Establish permanent, sustainable lifestyle anchors: bone-density exercises, joint mobility, consistent sleep schedule."
 }
}

HOUSE_THEME = {1: "Self", 2: "Wealth", 3: "Skills", 4: "Home", 5: "Creativity/Romance",
               6: "Routine/Service/Health", 7: "Partnership", 8: "Transformation/Shared resources",
               9: "Wisdom/Travel", 10: "Career/Status", 11: "Networks/Gains", 12: "Retreat/Hidden"}


def cycle_cell(y):
    age = y - BIRTH.year
    h, sign, lord = profection(age)
    st, br = year_pillar(y)
    tg = ten_god(STEMS.index(st))
    ix = ", ".join(interactions(br)) or "none"
    return (f"{dasha_label(y)} · H{h} {sign} ({HOUSE_THEME[h]}), lord {lord} · "
            f"BaZi {st}{br} {tg} · {ix}")


def ledger(y0, y1):
    rows = ["| Year | Age | Dasha (MD-AD) | Profection | BaZi year | Ten God | Branch interactions |",
            "|---|---|---|---|---|---|---|"]
    for y in range(y0, y1 + 1):
        age = y - BIRTH.year
        h, sign, lord = profection(age)
        st, br = year_pillar(y)
        rows.append(f"| {y} | {age} | {dasha_label(y)} | H{h} {sign} / {lord} | {st}{br} | "
                    f"{ten_god(STEMS.index(st))} | {', '.join(interactions(br)) or '-'} |")
    return "\n".join(rows)


def domain_table(title, data):
    rows = [f"### {title}", "",
            "| Time Period | Positions & Cycles | Precise Prediction & Explanation | What to Do (Inspiration & Action) |",
            "|---|---|---|---|"]
    for y in range(2026, 2041):
        rows.append(f"| {y} (Age {y - BIRTH.year}) | {cycle_cell(y)} | {data[y]['pred']} | {data[y]['action']} |")
    return "\n".join(rows) + "\n"


def self_test():
    assert maya(BIRTH) == ("12.19.11.2.19", "8 Cauac", "7 Tzec"), maya(BIRTH)
    assert year_pillar(2004) == ("甲", "申")
    assert year_pillar(2026) == ("丙", "午")
    assert ten_god(STEMS.index("辛")) == "七杀"
    assert ten_god(STEMS.index("戊")) == "正财"
    assert profection(22)[:2] == (11, "Taurus")
    assert profection(6)[0] == 7            # ages 6-8 -> H7-H9
    assert antardashas("Jupiter")[0][0] == "Jupiter"
    print("All natal_timeline tests passed successfully!")


if __name__ == "__main__":
    if "--test" in sys.argv:
        self_test()
        sys.exit()
    print("## 5. CYCLE LEDGER AND MASTER PREDICTIVE TIMELINE (2026-2040)\n")
    print("### 5.0 Computed ledger, 2010-2040\n")
    print(ledger(2010, 2040) + "\n")
    print("### Antardasha windows (computed)\n")
    print("| Mahadasha | Antardasha | Start | End |\n|---|---|---|---|")
    for md, ad, s, e in ALL_AD:
        print(f"| {md} | {ad} | {s} | {e} |")
    print()
    print(domain_table("5A. Career & Professional Development", CAREER))
    print(domain_table("5B. Love Life & Partnerships", LOVE))
    print(domain_table("5C. Finance & Wealth Accumulation", FINANCE))
    print(domain_table("5D. Health & Internal Vitality (symbolic, not medical advice)", HEALTH))

