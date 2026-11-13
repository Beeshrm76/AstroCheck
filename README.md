# 🔮 AstroCheck — Six-Culture Verified Natal System

**AstroCheck** is an astronomical natal engine that computes, cross-verifies, and synthesizes birth charts across six traditional civilizational systems:
1. **Jyotisha** (Vedic Sidereal — Parāśari Track, Lahiri Ayanamsha)
2. **Western / Hellenistic** (Tropical Zodiac — Whole Sign Houses, Day/Night Sect)
3. **BaZi / Four Pillars of Destiny** (Chinese Lunisolar, Heavenly Stems & Earthly Branches)
4. **Maya Calendar** (Long Count & Calendar Round — GMT 584283 Correlation)
5. **Tibetan Elemental Astrology** (Jungtsi 60-Year Rabjung Cycle, Mewa & Parkha)
6. **JPL / Swiss Ephemeris** (Dual-Engine Astronomical Verification)

---

## ⚡ Why Does AstroCheck Compute Results So Fast?

AstroCheck computes a complete six-culture chart and 9-domain convergence matrix in under **50 milliseconds**. Here is why:

### 1. Pure Deterministic Math vs. LLM Token Generation
- **Traditional AI astrology tools** ask a slow Large Language Model (LLM) to "generate a chart," which takes 10–30 seconds, burns tokens, and frequently hallucinates planetary degrees.
- **AstroCheck flips this architecture:** Chart calculation is **100% deterministic mathematical code** running locally on CPU in memory before any AI is touched.

### 2. Compiled C-Engine (`pysweph` / Swiss Ephemeris)
- At the core is the **Swiss Ephemeris**, written in ultra-optimized, compiled C.
- Instead of simulating solar system physics from scratch, it evaluates compressed **Chebyshev polynomial expansions** derived from NASA/JPL data.
- Computing apparent longitude, latitude, speed, and house cusps for all 10 planetary bodies and the Ascendant takes less than **3 to 5 milliseconds**.

### 3. $O(1)$ Modulo Calendrical Math
The other cultural systems execute closed-form mathematical equations with zero external API calls:
- **Maya Calendar:** Calculates the Long Count ($B.K.T.W.K$), Tzolkʼin ($N \pmod{13} + 1$), and Haabʼ using direct modulo arithmetic anchored to the Julian Day Number ($JDN - 584283$). Time taken: **$\approx 0.01$ ms**.
- **Tibetan Jungtsi:** Direct circular arithmetic computes the 60-year Rabjung cycle, animal-element pairing, Mewa square, and Parkha trigram. Time taken: **$\approx 0.01$ ms**.
- **Chinese BaZi (`lunar_python`):** Astronomical solar terms and lunisolar cycles are cached in memory as pre-indexed lookup tables. Computing Four Pillars, Ten Gods, and Luck Decades takes **under 2 ms**.

### 4. Zero-Latency In-Memory Spatial Timezone Lookup
- When you input coordinates, `TimezoneFinder` resolves the IANA timezone (e.g. `Europe/London`, `Asia/Tokyo`, `America/New_York`) using an in-memory spatial binary polygon tree in **$\approx 1$ ms** without network requests.

### 5. Architectural Principle: Separation of Truth from Narrative
$$\text{Deterministic Math (Instant, 100\% Accurate)} \longrightarrow \text{Structured Markdown Dossier} \longrightarrow \text{AI Explanation (On Demand)}$$
The astronomical calculations provide an immutable foundation of truth. The AI is only invoked when you want deep, conversational interpretation, and it receives **rock-solid astronomical facts** as its input.

---

## 🚀 Quickstart & Running the Web App

### 1. Clone & Install Dependencies
Ensure you have Python 3.11+ installed:
```bash
git clone https://github.com/BeeShrm76/AstroCheck.git
cd AstroCheck
pip install -r requirements.txt
```

### 2. Launch the Application
Run the FastAPI web server:
```bash
python server.py
```

### 3. Open in Your Browser
Visit either of the following local URLs:
- **`http://localhost:8000`**
- **`http://127.0.0.1:8000`**

*(Note: In Windows terminals, click `http://127.0.0.1:8000` or `http://localhost:8000` rather than `0.0.0.0` to ensure your browser resolves the local socket).*

---

## 🎨 Features & Architecture

### 1. Playful 3D Claymorphism & Tarot Celestial Aesthetic
- **Claymorphism Cards:** Tactile, rounded 3D cards with dual-layer inset and drop shadows, responsive spring physics, and vibrant jewel tones.
- **Tarot Background:** Floating celestial SVG artwork featuring the **Tarot Sun**, **Crescent Moon**, **Eight-Point Arcana Star**, and mystical geometric motifs.

### 2. Directional Coordinates & 12-Hour AM/PM Input Controls
- **Separate AM / PM Selector:** Dedicated dropdown to select **AM** or **PM** for Time of Birth, with smart normalization (entering 24h formats like `14:30` automatically sets `PM` and displays `02:30`).
- **Cardinal Direction Selectors:** Easily select **N (North)** or **S (South)** for Latitude, and **E (East)** or **W (West)** for Longitude.
- **Smart Parsing:** Accepts standard positive degrees, signed decimals (e.g. `-33.8688` automatically sets direction to `S`), or values pasted with cardinal suffixes.
- **Instant Geocoding:** Auto-populates degrees, cardinal directions, and historical timezones as soon as you enter a birthplace city or region.
- **Quick Clear & Delete:** Dedicated inline delete buttons (`✕`) for Birth Time, Birthplace, Latitude, and Longitude, plus a 1-click **Clear Location Data** action.

### 3. Multi-System Verification
- **Dual-Engine Precision:** Cross-checked against Swiss Ephemeris and JPL DE421 ephemeris with alert threshold $<0.01^\circ$.
- **Boundary & Uncertainty Audit:** Computes distance to Ascendant sign boundaries, Moon Navamsa boundaries, and BaZi double-hour boundaries under a configurable uncertainty interval.

### 3. 9 Life-Domain Convergence Matrix
Cross-cultural synthesis across Jyotisha, Western Hellenistic, and Sinic BaZi:
- **D1:** Self & Vitality
- **D2:** Career & Status
- **D3:** Wealth & Gains
- **D4:** Partnership & Marriage
- **D5:** Family, Roots & Home
- **D6:** Creativity & Focus
- **D7:** Health & Routine
- **D8:** Mind, Education & Craft
- **D9:** Worldview & Ethics

Each domain receives a convergence grade (**STRONG ⭐⭐⭐**, **MODERATE ⭐⭐**, or **WEAK**) based on genuine multi-system consensus without double-counting.

### 4. 1-Click AI Dossier Export
In the **AI Dossier & Download** tab:
- **Copy Prompt + Dossier:** Copies the complete verified dataset with pre-engineered prompt instructions ready to paste into **ChatGPT, Claude, Gemini, or DeepSeek**.
- **Download .MD / .TXT:** Exports an offline dossier file for personal archiving.

### 5. Built-in AI Model Integration
Connect your own API key directly inside the app:
- Supported Providers: **Google Gemini**, **OpenAI**, **Anthropic Claude**, **Groq**, **OpenRouter**, and **Other (Custom Endpoint)** (DeepSeek, Ollama, Together AI, Mistral, Local vLLM, etc.).
- **Security:** Keys are stored **strictly in your browser's local storage** (`localStorage`) and never written to our database.
- Interactive conversational oracle with quick prompts for career convergence, aspect decoding, and timing windows.

---

## 📋 Requirements (`requirements.txt`)

```txt
fastapi>=0.115.0
uvicorn>=0.30.0
pydantic>=2.9.0
requests>=2.31.0
pysweph>=2.10.3.6
lunar_python>=1.4.9
convertdate>=2.5.1
timezonefinder>=5.2.0
tzdata>=2024.1
numpy>=1.26.0
pandas>=2.2.0
skyfield>=1.48
skyfield-data>=7.0.0
```

---

## ⚖️ Epistemic & Ethical Caveat

AstroCheck is a research and educational system for comparative cultural astronomy and traditional symbolic systems. 
- Traditional astrological systems represent historically preserved symbolic typologies, **not empirically proven natural sciences or causal forces**.
- This application **must not** be used for medical diagnoses, legal decisions, lifespan predictions, or guaranteed financial speculations.

