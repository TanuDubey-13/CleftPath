# CleftPath — UI/UX Design System Specification

> **Platform:** CleftPath  
> **Tagline:** *“Every journey deserves a path forward.”*  
> **Document Version:** 1.0.0  
> **Status:** Approved Official Design System Baseline  
> **Target Implementer:** Cursor (Frontend Engineering) & UI Designers

---

## 1. Brand Identity, Emotion & Core Metaphor

CleftPath is an empathetic, privacy-first healthcare sanctuary for individuals and families navigating the longitudinal cleft lip and palate journey.

```
+-----------------------------------------------------------------------------------------+
|                                    BRAND ESSENCE                                        |
|                                                                                         |
|  * HOPE & WARMTH          Supportive, calming sanctuary; never a cold hospital portal.  |
|  * CONTINUITY & PROGRESS  The "Path" connects prenatal discovery to adulthood.         |
|  * TRUST & CLARITY        Evidence-based, accessible, high-contrast, low cognitive load.|
|  * COMMUNITY & BELONGING  Peer connection and shared victories across every milestone.  |
+-----------------------------------------------------------------------------------------+
```

### 1.1 The Visual Metaphor: "The Path"
The user interface is structured around the visual metaphor of an **organic, illuminated path**. Rather than rigid tables or sterile medical charts, milestones, appointments, and feeding logs are represented as waypoints along an interconnected, evolving trail.

---

## 2. Design Tokens & Foundations

### 2.1 Color Palette & Semantic Tokens

```
  Warm Ivory (Canvas)       Deep Teal (Primary)      Soft Sage (Success/Growth)    Warm Coral (Accent)
     #FAF7F2                   #0F4C5C                     #81B29A                   #E07A5F
  [bg-stone-50 / ivory]     [teal-900 / primary]        [sage-500 / secondary]     [coral-500 / accent]
```

#### Complete Color Token Matrix

| Token Name | Hex Code | RGB | Tailwind Class | Semantic Usage |
| :--- | :--- | :--- | :--- | :--- |
| **`ivory-50` (Canvas)** | `#FAF7F2` | `250, 247, 242` | `bg-ivory-50` | Primary application canvas / background |
| **`ivory-100` (Surface)**| `#F4EFE6` | `244, 239, 230` | `bg-ivory-100` | Secondary surface, subtle nested panels |
| **`surface-white`** | `#FFFFFF` | `255, 255, 255` | `bg-white` | Primary card background, dialog surfaces |
| **`teal-900` (Primary)**| `#0F4C5C` | `15, 76, 92` | `bg-teal-900`, `text-teal-900` | Primary brand color, headers, primary buttons |
| **`teal-800` (Hover)** | `#155D70` | `21, 93, 112` | `bg-teal-800` | Primary button hover state |
| **`teal-700` (Active)** | `#1C7289` | `28, 114, 137` | `bg-teal-700` | Interactive active states, focus rings |
| **`teal-100` (Subtle)** | `#E2EFF2` | `226, 239, 242` | `bg-teal-100` | Highlight badges, active sidebar items |
| **`sage-600` (Success)**| `#6A9B84` | `106, 155, 132` | `bg-sage-600` | Completed milestones, positive growth |
| **`sage-500` (Growth)** | `#81B29A` | `129, 178, 154` | `bg-sage-500`, `text-sage-700` | Secondary brand, health metrics, checklist checks |
| **`sage-100` (Subtle)** | `#EEF5F1` | `238, 245, 241` | `bg-sage-100` | Success badges, verified health tags |
| **`coral-500` (Accent)**| `#E07A5F` | `224, 122, 95` | `bg-coral-500`, `text-coral-600`| Warm milestone badges, active tabs, reminders |
| **`coral-600` (Hover)** | `#CC674C` | `204, 103, 76` | `bg-coral-600` | Accent button hover state |
| **`coral-100` (Subtle)**| `#FAECE8` | `250, 236, 232` | `bg-coral-100` | Milestone countdown pills, important notices |
| **`emergency-600` (Red)**| `#D9383A`| `217, 56, 58` | `bg-rose-600`, `text-rose-600` | Emergency triage banner, critical medical flags |
| **`charcoal-900` (Text)**| `#2D3748`| `45, 55, 72` | `text-charcoal-900` | High-contrast readable body and title text |
| **`charcoal-600` (Muted)**|`#5A6578`| `90, 101, 120` | `text-charcoal-600` | Subtitles, helper text, timestamps |
| **`border-subtle`** | `#E7E2DA` | `231, 226, 218` | `border-stone-200` | Card borders, table dividers, input borders |

---

### 2.2 Typography Hierarchy

* **Primary Font Family:** `Plus Jakarta Sans` or `Inter` (sans-serif) — Clean, rounded, empathetic, highly legible in pediatric/clinical contexts.
* **Secondary / Heading Family:** `Outfit` or `Plus Jakarta Sans` — Modern, warm geometric headers.
* **Monospace / Metric Font:** `JetBrains Mono` — For numerical medical records, feeding ml calculations, and timestamps.

```
Display 1    Plus Jakarta Sans 700   36px / 44px   tracking-tight   Hero titles, Milestone celebrations
Heading 1    Outfit 700             28px / 36px   tracking-tight   Page headers, Major stage banners
Heading 2    Outfit 600             22px / 28px   tracking-normal  Card headers, Section dividers
Heading 3    Plus Jakarta Sans 600   18px / 24px   tracking-normal  Module subheaders, Form group titles
Body-Lg      Inter 400/500          16px / 24px   tracking-normal  Lead paragraphs, PathGuide messages
Body-Md      Inter 400/500          14px / 20px   tracking-normal  Default body, table data, form labels
Body-Sm      Inter 400/500          12px / 16px   tracking-wide    Timestamps, metadata, badges
Overline     Plus Jakarta Sans 700   11px / 14px   tracking-widest  UPPERCASE section tags, stage markers
```

---

### 2.3 Spacing & 8-Point Layout Grid
* Baseline Grid: **4px / 8px** increment system.
* Standard Layout Gaps:
  * Micro (between icon & label): `gap-1.5` (6px) or `gap-2` (8px)
  * Component Interior: `p-4` (16px) or `p-6` (24px)
  * Card-to-Card Grid: `gap-6` (24px)
  * Page Section Spacing: `space-y-8` (32px) or `space-y-12` (48px)
  * Max Content Container: `max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`

---

### 2.4 Border Radius Scale
CleftPath eliminates harsh, intimidating clinical corners in favor of generous, welcoming curvatures:
* `rounded-sm`: **4px** (Checkboxes, small tags)
* `rounded-md`: **8px** (Input fields, dropdown menus)
* `rounded-lg`: **12px** (Standard buttons, small cards, tooltips)
* `rounded-xl`: **16px** (Medium cards, dialog boxes)
* `rounded-2xl`: **24px** (Standard dashboard cards, milestone nodes) — **Default for Cards**
* `rounded-3xl`: **32px** (Hero banners, PathGuide chat drawers)
* `rounded-full`: **9999px** (Pill badges, avatars, floating action triggers)

---

### 2.5 Elevation & Warm Shadows
Shadows use a warm umber/charcoal ambient occlusion tone (`rgba(45, 55, 72, ...)`) rather than harsh cold black:
* **`shadow-warm-sm`:** `0 1px 3px 0 rgba(45, 55, 72, 0.06), 0 1px 2px 0 rgba(45, 55, 72, 0.04)`
* **`shadow-warm-md`:** `0 4px 12px -2px rgba(45, 55, 72, 0.08), 0 2px 6px -1px rgba(45, 55, 72, 0.04)`
* **`shadow-warm-lg`:** `0 12px 24px -4px rgba(45, 55, 72, 0.10), 0 4px 8px -2px rgba(45, 55, 72, 0.05)`
* **`shadow-warm-xl`:** `0 20px 32px -6px rgba(45, 55, 72, 0.14), 0 8px 16px -4px rgba(45, 55, 72, 0.06)`

---

## 3. Navigation Architecture

### 3.1 Desktop Sidebar Navigation (`w-64` or `w-72`)
Fixed left-hand navigation panel styled with `bg-white border-r border-stone-200`:

```
+------------------------------------------+
|  [Logo Icon]  CleftPath                  |
|  "Every journey deserves a path forward" |
+------------------------------------------+
|  ACTIVE PATIENT SWITCHER                 |
|  [Avatar] Baby Leo (4m) [Cleft Lip/Pal] ▾|
+------------------------------------------+
|  MAIN NAVIGATION                         |
|  [Home]        Dashboard                 |
|  [Compass]     My Journey                |
|  [BookOpen]    Health Library            |
|  [Calendar]    Appointments              |
|  [HeartPulse]  Baby & Parent Care        |
|  [Mic]         Voice Journey             |
|  [Sparkles]    PathGuide (AI)            |
|  [Users]       The Village               |
+------------------------------------------+
|  USER & PREFERENCES                      |
|  [User]        Profile                   |
|  [Settings]    Settings                  |
+------------------------------------------+
|  [!] EMERGENCY CARE HELPLINE             |
+------------------------------------------+
```

* **Sidebar Item States:**
  * *Default:* `text-charcoal-600 hover:text-teal-900 hover:bg-teal-50/60 rounded-xl px-3 py-2.5 transition`
  * *Active:* `bg-teal-900 text-white font-medium rounded-xl px-3 py-2.5 shadow-warm-sm` (Active icon colored `text-coral-400` or `text-white`).

---

### 3.2 Mobile Bottom Navigation Bar (`h-16`)
Fixed bottom bar for mobile screens (`block md:hidden bg-white/95 backdrop-blur-md border-t border-stone-200`):

```
+-------------------------------------------------------------+
|  [Home]      [Compass]     [HeartPulse]    [Mic]    [Sparkle]|
| Dashboard     Journey       Baby Care      Voice    PathGuide|
+-------------------------------------------------------------+
```

---

## 4. Dashboard Grid & Reusable Card Blueprint

The central dashboard aggregates the 8 core operational domains into an actionable 12-column responsive layout:

```
+----------------------------------------------------------------------------------------+
|                                  DASHBOARD TOP BAR                                     |
|  "Welcome back, Sarah"  |  Stage 2: Primary Lip Repair (3-6 Months)  |  [Date / Actions]|
+----------------------------------------------------------------------------------------+
|                                    GRID (12-COL)                                       |
|                                                                                        |
|  [ CARD 1: MY JOURNEY (8-COL) ]              [ CARD 2: UPCOMING APPOINTMENT (4-COL) ]  |
|  - Active Stage: Lip Surgery (4 weeks away)   - Dr. Robert Sterling (Cleft Surgeon)    |
|  - Milestone Progress Ring (65%)              - Monday, Oct 14 at 10:00 AM             |
|  - Next: Specialty Bottle Check & Pre-op      - [ Prepare Questions Button ]           |
|                                                                                        |
|  [ CARD 3: PATHGUIDE SMART PROMPTS (12-COL) ]                                          |
|  - "Ask PathGuide anything about recovery, feeding bottles, or surgical timelines..."  |
|  - [ Chip: What to pack for lip surgery? ] [ Chip: Feeding tips with Haberman bottle ]  |
|                                                                                        |
|  [ CARD 4: BABY CARE (4-COL) ]  [ CARD 5: VOICE JOURNEY (4-COL)] [ CARD 6: VAULT (4)] |
|  - Today's Feeding: 680 ml      - Weekly Speech Goal: 3/5 days   - Recent: Operative Note|
|  - Weight: 6.2 kg (50th %ile)   - Target: /p/ and /b/ sounds     - Status: OCR Verified |
|  - [ Log Feeding Quick Action ] - [ Record 2-Min Practice ]      - [ Upload Record ]    |
|                                                                                        |
|  [ CARD 7: DAILY NOTE (6-COL) ]              [ CARD 8: THE VILLAGE SPOTLIGHT (6-COL) ] |
|  - Capture a milestone moment / photo log     - Trending: "Post-op arm restraints tips"|
|  - "Leo drank 120ml without burp fuss today!" - 14 supportive comments in #Stage2Club  |
+----------------------------------------------------------------------------------------+
```

---

## 5. UI Component Specifications

### 5.1 Buttons (`<Button />`)

| Variant | Styling / Classes | Use Case |
| :--- | :--- | :--- |
| **`primary`** | `bg-teal-900 hover:bg-teal-800 text-white font-medium rounded-xl px-5 py-2.5 shadow-warm-sm transition active:scale-[0.98]` | Main call-to-actions, form submissions |
| **`secondary`** | `bg-sage-100 hover:bg-sage-200 text-teal-900 font-medium rounded-xl px-5 py-2.5 transition` | Secondary actions, filtering |
| **`accent / coral`** | `bg-coral-500 hover:bg-coral-600 text-white font-medium rounded-xl px-5 py-2.5 shadow-warm-sm transition` | Highlighting key milestones, PathGuide triggers |
| **`outline`** | `border border-stone-300 hover:border-teal-900 bg-white text-charcoal-900 font-medium rounded-xl px-5 py-2.5 transition` | Tertiary options, cancel buttons |
| **`ghost`** | `hover:bg-teal-50 text-teal-900 font-medium rounded-xl px-4 py-2 transition` | Inline table actions, icon buttons |
| **`emergency`** | `bg-rose-600 hover:bg-rose-700 text-white font-semibold rounded-xl px-5 py-2.5 shadow-warm-md animate-pulse` | Immediate emergency escalation |

* **Button Sizes:**
  * `sm`: `h-8 px-3 text-xs rounded-lg`
  * `md`: `h-10 px-4 text-sm rounded-xl` (Standard)
  * `lg`: `h-12 px-6 text-base rounded-2xl`

---

### 5.2 Form Inputs & Controls

```
  Text Input (Normal)             Text Input (Focused)             Text Input (Error)
  +--------------------------+    +--------------------------+    +--------------------------+
  | Feeding Volume (ml)      |    | Feeding Volume (ml)      |    | Feeding Volume (ml)      |
  | 120                      |    | 120                      |    | -10                      |
  +--------------------------+    +--------------------------+    +--------------------------+
  border-stone-300 bg-white       border-teal-900 ring-2 teal/20   border-rose-500 text-rose-900
                                                                   [!] Volume must be positive
```

* **Text Inputs & Selects:** `bg-white border border-stone-200 rounded-xl px-4 py-2.5 text-charcoal-900 placeholder:text-charcoal-400 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900 transition`.
* **Checkbox & Radio:** Custom styled with `accent-teal-900` or SVG check inside `rounded-md border-stone-300`.
* **Toggle Switch:** Pill-shaped `w-12 h-6 bg-stone-200 peer-checked:bg-teal-900 rounded-full transition`.

---

### 5.3 Cards & Surface Containers (`<Card />`)
* **Standard Card:** `bg-white rounded-2xl border border-stone-200/80 shadow-warm-sm p-6`.
* **Interactive Hover Card:** `bg-white rounded-2xl border border-stone-200/80 shadow-warm-sm hover:shadow-warm-md hover:border-teal-800/30 transition-all duration-200 cursor-pointer p-6`.
* **Milestone Waypoint Card:** Left border accent colored by stage: `border-l-4 border-l-coral-500 bg-white rounded-r-2xl rounded-l-md shadow-warm-sm p-5`.

---

### 5.4 Badges, Tags & Chips (`<Badge />`)

```
  [ Stage 1: Infancy ]       [ ✓ Completed ]       [ ⏳ In Progress ]       [ ⚠ High Reflux ]
   bg-teal-100 text-teal-900   bg-sage-100 text-sage-800  bg-coral-100 text-coral-800   bg-rose-100 text-rose-800
```

* **Pill Token Classes:** `inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold tracking-wide`.

---

### 5.5 Alert Banners & Emergency Triggers (`<Alert />`)

#### Standard Informational Alert
```html
<div class="bg-teal-50 border border-teal-200 rounded-2xl p-4 flex items-start gap-3">
  <InfoIcon class="w-5 h-5 text-teal-800 flex-shrink-0 mt-0.5" />
  <div class="text-sm text-teal-950">
    <strong class="font-semibold">Surgical Prep Reminder:</strong> Fasting guidelines begin at midnight.
  </div>
</div>
```

#### Emergency Triage Alert (`[EMERGENCY_TRIGGER]`)
```html
<div class="bg-rose-50 border-2 border-rose-500 rounded-2xl p-5 shadow-warm-md flex items-start gap-4">
  <AlertTriangleIcon class="w-6 h-6 text-rose-600 flex-shrink-0 animate-bounce" />
  <div class="space-y-1">
    <h4 class="text-base font-bold text-rose-950">Immediate Medical Attention Required</h4>
    <p class="text-sm text-rose-800 leading-relaxed">
      The symptoms described (respiratory distress / high fever) require urgent clinical evaluation.
    </p>
    <div class="pt-2 flex gap-3">
      <a href="tel:911" class="bg-rose-600 text-white font-bold px-4 py-2 rounded-xl text-sm hover:bg-rose-700">
        Call Emergency (911)
      </a>
      <button class="bg-white border border-rose-300 text-rose-900 font-semibold px-4 py-2 rounded-xl text-sm">
        Call Cleft On-Call Team
      </button>
    </div>
  </div>
</div>
```

---

### 5.6 Timeline & Journey Path Components

```
      Stage 1 (Complete)        Stage 2 (Active Waypoint)        Stage 3 (Upcoming)
          ( ✓ ) ═══════════════════════ ( ◎ ) ----------------------- ( ○ )
      Prenatal Care              Primary Lip Repair             Primary Palate Repair
      Completed Jun 2026         Target: Oct 2026               Target: May 2027
```

* **Node States:**
  * *Completed Node:* `w-10 h-10 rounded-full bg-sage-500 text-white flex items-center justify-center shadow-warm-sm` (Contains checkmark icon).
  * *Active Node:* `w-12 h-12 rounded-full bg-coral-500 text-white flex items-center justify-center ring-4 ring-coral-100 shadow-warm-md animate-pulse` (Contains compass/target icon).
  * *Upcoming Node:* `w-10 h-10 rounded-full bg-stone-100 border-2 border-stone-300 text-charcoal-400 flex items-center justify-center` (Contains stage number).
* **Connecting Splines:**
  * *Completed segment:* `h-1 bg-sage-500 rounded-full`
  * *Upcoming segment:* `h-1 bg-stone-200 border-dashed rounded-full`

---

### 5.7 Empty States, Loading States & Skeleton Loaders

#### Empty State Pattern
```html
<div class="bg-white rounded-2xl border border-stone-200 p-12 text-center max-w-md mx-auto space-y-4">
  <div class="w-16 h-16 bg-teal-50 text-teal-800 rounded-full flex items-center justify-center mx-auto">
    <FolderOpenIcon class="w-8 h-8" />
  </div>
  <h3 class="text-lg font-bold text-charcoal-900">No medical records uploaded yet</h3>
  <p class="text-sm text-charcoal-600">
    Upload surgical summaries, audiology reports, or feeding notes to organize your timeline.
  </p>
  <button class="btn-primary">Upload First Document</button>
</div>
```

#### Skeleton Loader Standard
* Pulse animation: `animate-pulse bg-stone-200/80 rounded-xl`.
* Skeleton Card: Top banner skeleton (`h-6 w-1/3`), body lines (`h-4 w-full`, `h-4 w-5/6`), and action button placeholder (`h-10 w-28 rounded-xl`).

---

## 6. Accessibility & Ergonomics Standards (WCAG 2.1 AA/AAA)

1. **Color Contrast:** All body text meets or exceeds $4.5:1$ contrast against the `#FAF7F2` canvas and `#FFFFFF` cards. Deep Teal (`#0F4C5C`) on White achieves an outstanding $8.4:1$ ratio (AAA compliant).
2. **Keyboard Focus Rings:** Every interactive button, link, and input possesses an explicit `focus-visible:ring-2 focus-visible:ring-teal-700 focus-visible:ring-offset-2` state.
3. **Screen Reader ARIA:** Custom widgets (Voice Recorder, Milestone Nodes, PathGuide Drawers) include descriptive `aria-label`, `aria-expanded`, and `aria-live="polite"` status announcements.
4. **Touch Targets:** Mobile tap targets maintain a minimum dimension of $44 \times 44\text{ px}$.
5. **Reduced Motion:** All transitions and animations respect `prefers-reduced-motion: reduce`.

---

## 7. Iconography & Illustration Guidelines

* **Icon Library:** **Lucide React** (`lucide-react`) exclusively.
* **Stroke Width:** `1.75px` default (balanced, elegant line weight).
* **Icon Size Mapping:**
  * Inline Badges / Tags: `w-3.5 h-3.5` (14px)
  * Buttons & Form Controls: `w-4 h-4` (16px) or `w-5 h-5` (20px)
  * Sidebar Navigation: `w-5 h-5` (20px)
  * Section Headers / Empty States: `w-8 h-8` to `w-12 h-12` (32px–48px)
* **Illustration Aesthetic:** Hand-drawn warmth, soft organic shapes, soothing pastel fills, and uplifting family metaphors.

---

## 8. Tailwind CSS Configuration Reference (`tailwind.config.ts`)

```typescript
import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        ivory: {
          50: '#FAF7F2',
          100: '#F4EFE6',
          200: '#EBE3D5',
        },
        teal: {
          50: '#F0F7F8',
          100: '#E2EFF2',
          700: '#1C7289',
          800: '#155D70',
          900: '#0F4C5C',
          950: '#082E38',
        },
        sage: {
          100: '#EEF5F1',
          500: '#81B29A',
          600: '#6A9B84',
          700: '#52826C',
        },
        coral: {
          100: '#FAECE8',
          400: '#E89078',
          500: '#E07A5F',
          600: '#CC674C',
        },
        charcoal: {
          400: '#8A95A5',
          600: '#5A6578',
          800: '#3D4758',
          900: '#2D3748',
        },
      },
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', 'Inter', 'system-ui', 'sans-serif'],
        heading: ['Outfit', '"Plus Jakarta Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      borderRadius: {
        '2xl': '1.25rem',  // 20px
        '3xl': '1.75rem',  // 28px
        '4xl': '2.25rem',  // 36px
      },
      boxShadow: {
        'warm-sm': '0 1px 3px 0 rgba(45, 55, 72, 0.05), 0 1px 2px 0 rgba(45, 55, 72, 0.03)',
        'warm-md': '0 4px 12px -2px rgba(45, 55, 72, 0.08), 0 2px 6px -1px rgba(45, 55, 72, 0.04)',
        'warm-lg': '0 12px 24px -4px rgba(45, 55, 72, 0.10), 0 4px 8px -2px rgba(45, 55, 72, 0.05)',
        'warm-xl': '0 20px 32px -6px rgba(45, 55, 72, 0.14), 0 8px 16px -4px rgba(45, 55, 72, 0.06)',
      },
    },
  },
  plugins: [],
} satisfies Config;
```
