# Ordering the remaining parts: amazon.fr vs mouser.fr (2026-10-07)

This covers everything still marked 🛒 in `docs/bom.md` ("Electronics
assembly — every discrete part", table A), plus the three tools on its
"Still to buy" list (multimeter, solder, flush cutters).

**How the prices were found:** both sites block page views from the cloud
session, so every price and stock figure below comes from **web-search
snapshots**, not from the live pages. Treat them as a guide, and **check
price, stock and seller on each page before you order.**
- **amazon.fr** prices are in EUR, including VAT, as the search snapshot
  showed them.
- **mouser.fr**: only one EUR price came through (the multimeter). Every
  other Mouser price is **USD from mouser.com**; the French price will
  differ and may be shown without VAT.
- Mouser links marked ⇄ were built from a mouser.com result. If one fails,
  search the part number on mouser.fr.

## Recommendation

- **One order that covers everything: amazon.fr.**
  - The parts come to about **€65**.
  - With the three tools it's about **€128** (budget multimeter) or **€183**
    (Fluke 101).
  - Most picks are generic, unbranded parts. That's fine for this use.
- **mouser.fr** has branded parts (Bourns, Panasonic, Würth, Samtec,
  Adafruit) and real stock counts.
  - It has no 20 AWG wire in a sensible length: the smallest spool found
    is 100 ft, at about $96 a colour. So it can't cover everything in one
    order.
  - Free delivery starts at €75; the parts alone come to about $40 at
    mouser.com prices.
- **Before you order, check three things:**
  1. Does the Phoenix pack (Order 3) hold **2 headers + 2 plugs**? If yes,
     skip item 9.
  2. Did the soldering station come with solder? If yes, skip item 11.
  3. Do you already have flush cutters? If yes, skip item 12.

## Table 1 — amazon.fr

| # | Need | Pick (ASIN) | Pack | Price shown | Availability shown | Fit notes |
|---|---|---|---|---|---|---|
| 1 | PTC fuse, radial, 1.1 A hold, ≥ 16 V ×2 | 30V 1.1A resettable fuse, radial "Polyswitch" — [B0848QX3FS](https://www.amazon.fr/fusible-r%C3%A9armable-plomb-radial-Polyswitch/dp/B0848QX3FS) | 20 | €10.21 (+ €2 delivery in snippet) | not shown; third-party seller | radial, 30 V, 1.1 A: meets spec. Generic, no reviews |
| 2 | 100 µF ≥ 25 V low-ESR electrolytic ×2 | Elna RJH 35 V 100 µF, 8 × 12 mm — [B07H9BKFGF](https://www.amazon.fr/Condensateur-%C3%A9lectrolytique-Electrolytic-Capacitor-Elna/dp/B07H9BKFGF) | 20 | €9.46 | not shown | RJH is a low-impedance series. 3.5 mm lead pitch: bend the leads to fit the perfboard. Alternative: sourcing map low-ESR 35 V, 6.3 × 7 mm, 50 pcs, €9.99 — [B07LDZ5HF8](https://www.amazon.fr/sourcing-map-Radial-Faible-Resist/dp/B07LDZ5HF8) |
| 3+4 | 2.54 mm male + female header strips | IZOKEE male + female 40-pin kit — [B07DBY753C](https://www.amazon.fr/IZOKEE-Connecteur-Femelle-Broches-Prototype/dp/B07DBY753C) | 15 + 15 strips | €11.71 | not shown | 4.6/5 (683). Female strips don't snap: cut them with the flush cutters (you lose one pin per cut). One strip gives 2 × 8 + 1 × 2 |
| 5 | F–F jumpers 10–20 cm, ~20 | ELEGOO 120 Dupont wires, 20 cm (40 F–F) — [B01JD5WCG2](https://www.amazon.fr/Elegoo-Multicolore-M%C3%A2le-Femelle-M%C3%A2le-M%C3%A2le-Femelle-Femelle/dp/B01JD5WCG2) | 120 | €8.99 | not shown | 4.7/5 (2,811) |
| 6 | DC jack, female 5.5 × 2.1 mm → screw terminal | LitaElek 5.5 × 2.1 adapters — [B019HAC6V4](https://www.amazon.fr/LitaElek-Femelle-Adaptateur-Connecteur-dispositifs/dp/B019HAC6V4) | 5 female + 5 male | €8.99 | not shown | 4.5/5 (1,235), 3 A. Check + / − with the multimeter before first use |
| 7 | 20 AWG wire, red + black, ≥ 1 m each | QUARKZMAN 20 AWG 2-core PVC, red/black, 4.5 m — [B0CW9M53BS](https://www.amazon.fr/QUARKZMAN-Parall%C3%A8le-Conducteurs-Longueur-Diam%C3%A8tre/dp/B0CW9M53BS) | 4.5 m pair | €9.49 | "only 3 left" (snippet) | true 20 AWG, tinned copper. The cores peel apart |
| 8 | Zip ties ~100 mm | Gocableties 100 × 2.5 mm, black — [B072SLJR2T](https://www.amazon.fr/Gocableties-100-colliers-serrage-nylon-robuste/dp/B072SLJR2T) | 100 | €5.99 or €4.99 (snippets differ) | not shown | 4.5/5 |
| 9 | *Only if short:* 5.08 mm 8-pin pluggable terminal, header + plug | no reliable listing — see Table 3 | — | — | — | — |
| 10 | Multimeter (continuity beeper, DC V) | **budget:** UNI-T UT33D+ — [B08W36VF6H](https://www.amazon.fr/UNI-T-UT33D-MIE0328-Miernik-Uniwersalny/dp/B08W36VF6H) · **better:** Fluke 101 — [B00V6BBRNQ](https://www.amazon.fr/Fluke-Multim%C3%A8tre-num%C3%A9rique-poche-101/dp/B00V6BBRNQ) | 1 | UT33D+ €22.23 · Fluke 101 €77.38 (other sellers from €65.01) | UT33D+: free delivery, "Amazon's Choice" | UT33D+: 4.6/5 (144), buzzer, diode test, manual ranging. Fluke 101 has a continuity beeper and DC V (Fluke spec) |
| 11 | Solder, flux core, ~0.8 mm | 63/37 rosin core 0.8 mm, 4 × 50 g — [B09L412D4X](https://www.amazon.fr/souder-colophane-bricolage-%C3%A9lectronique-paquet/dp/B09L412D4X) | 200 g | €14.99 | not shown | leaded. 4.3/5 (17 reviews only). Lead-free alternative: GTSE Sn99.3Cu0.7, 100 g, 4.5/5 (537) — [B08GGBT378](https://www.amazon.fr/GTSE-souder-colophane-soudure-%C3%A9lectrique/dp/B08GGBT378), €6.59–18.49 (snippets differ) |
| 12 | Flush cutters | Knipex 78 61 125 SB Electronic Super Knips — [B000OIB7J6](https://www.amazon.fr/Knipex-78-61-125-SB/dp/B000OIB7J6) | 1 | €25.99 | not shown | 4.7/5 (3,695). Alternative: Hakko CHP-170, €24.31 — [B00FZPDG1K](https://www.amazon.fr/Hakko-CHP-170-Pince-coupe-fil-souple/dp/B00FZPDG1K) |

**Totals at the prices shown:**
- Parts (1–8): **€64.84**, plus €2 delivery on the fuse.
- With UT33D+, solder and Knipex: **€128.05**.
- With the Fluke 101 instead: **€183.20**.

**Free delivery** is over €35, but only for items sold or shipped by
Amazon ([help page](https://www.amazon.fr/gp/help/customer/display.html?nodeId=GZXW7X6AKTHNUP6H)).
Some picks look like third-party sellers, so check "Expédié par Amazon" on
each.

## Table 2 — mouser.fr

| # | Need | Part (manufacturer MPN, link) | Order qty | Price shown | Stock shown | Notes |
|---|---|---|---|---|---|---|
| 1 | PTC fuse ×2 | Bourns **MF-R110**, radial, 1.1 A hold / 2.2 A trip, 30 V — [⇄ link](https://www.mouser.fr/ProductDetail/Bourns/MF-R110?qs=wd8kHz0doL7LkwIbzZb5mA%3D%3D) | 2 | ~$0.40 each (mouser.com, unreliable) | 19,054 | alternative: Littelfuse RUEF110 — [⇄ link](https://www.mouser.fr/ProductDetail/Littelfuse/RUEF110?qs=hv6pn79dJPSNtwKNbPwPHQ%3D%3D) |
| 2 | 100 µF ≥ 25 V low ESR ×2 | Panasonic **EEU-FR1E101**, 25 V, 6.3 × 11.2 mm, 2.5 mm pitch, 130 mΩ — [⇄ link](https://www.mouser.fr/ProductDetail/Panasonic/EEU-FR1E101?qs=Ao3mORb5HCDieoJwtkb8Dw%3D%3D) | 2 | $0.45 each (mouser.com) | 19,980 | alternative: Rubycon 35ZLH100MEFC6.3X11 (35 V) — [⇄ link](https://www.mouser.fr/ProductDetail/Rubycon/35ZLH100MEFC6.3X11?qs=T3oQrply3y8xzyooRx3RZg%3D%3D) |
| 3 | male header ≥ 13 pins | Würth **61302011121**, 1 × 20, 2.54 mm, gold — [⇄ link](https://www.mouser.fr/ProductDetail/Wurth-Elektronik/61302011121?qs=PhR8RmCirEbj/FsnpbhNaw%3D%3D) | 2 | $1.23 each (mouser.com) | 1,288 | |
| 4 | female sockets 2 × (1 × 8) + 1 × (1 × 2) | Samtec **SSW-108-01-G-S** (1 × 8) — [⇄ link](https://www.mouser.fr/ProductDetail/Samtec/SSW-108-01-G-S?qs=FESYatJ8odLaL9GxbCQJ2g%3D%3D) and **SSW-102-01-G-S** (1 × 2) — [⇄ link](https://www.mouser.fr/ProductDetail/Samtec/SSW-102-01-G-S?qs=92ilVni64gwMaw8Iglb9kA%3D%3D) | 2 + 1 | 1 × 8: $1.76 each (mouser.com); 1 × 2: not shown | 1 × 8: 6,306 | |
| 5 | F–F jumpers ~20 | Adafruit **4447**, silicone F–F, 200 mm, 40 pcs — [⇄ link](https://www.mouser.fr/ProductDetail/Adafruit/4447?qs=CUBnOrq4ZJzovVmrsSU55g%3D%3D) | 1 | $9.95 (mouser.com) | 724–1,513 | |
| 6 | DC jack adapter, female | SparkFun **PRT-10288** "DC Barrel Jack Adapter – Female" — [⇄ link](https://www.mouser.fr/ProductDetail/SparkFun/PRT-10288?qs=WyAARYrbSnbv/ypDwaDLyg%3D%3D) | 1 | $2.95 (mouser.com) | 101 | **VERIFY 5.5 × 2.1 mm and screw terminals** on the page |
| 7 | 20 AWG wire, ≥ 1 m red + black | Alpha Wire 3053 RD005 / BK005, 100 ft spools | — | ~$96 per spool (mouser.com, a 3053 variant) | 239–251 | **not sensible for 2 m** (see Table 3) |
| 8 | Zip ties | Panduit **PLT1M-M**, 99 mm, natural — [⇄ link](https://www.mouser.fr/ProductDetail/Panduit/PLT1M-M?qs=PijdWQvv7l82QBSPSSlofg%3D%3D) | 100 | $0.064 each (mouser.com) | 709,949 | |
| 9 | *Only if short:* Phoenix 8-pin, header + plug | header MSTBA 2,5/8-G-5,08 = **1757307** — [⇄ link](https://www.mouser.fr/ProductDetail/Phoenix-Contact/1757307?qs=o3rrLWFGhRl4IvmrdyQ5FA%3D%3D); plug MSTB 2,5/8-ST-5,08 = **1757077** (no page seen) | 2 + 2 | not shown | not shown | genuine Phoenix Contact |
| 10 | Multimeter | Extech **EX330** (Mouser 685-EX330), autoranging, 600 V DC, continuity — [⇄ link](https://www.mouser.fr/ProductDetail/Extech/EX330?qs=tv7vi16PWA4nsXR8adm%2Bmg%3D%3D) | 1 | **€66.39** ([mouser.fr listing](https://www.mouser.fr/Extech/Test-Measurement/Multimeters-Voltmeters/_/N-5gfo?P=1z13cd3)) | 11 | the only EUR price found. Alternative: Fluke 107 ESP, $160.99 |
| 11 | Solder | MG Chemicals **4900-35G**, SAC305 lead-free, 0.81 mm (Mouser 590-4900-35G) | 1 | $5.35 (old USD catalogue: may be stale) | not shown | no product page seen. Alternative: 4900-112G (¼ lb) — [⇄ link](https://www.mouser.fr/ProductDetail/MG-Chemicals/4900-112G?qs=YqNA2qefETAK87e3A6/Oig%3D%3D) |
| 12 | Flush cutters | Adafruit **152** (Hakko CHP-170) — [⇄ link](https://www.mouser.fr/ProductDetail/Adafruit/152?qs=N/3wi2MvZWC96jMaJ3xvTg%3D%3D) | 1 | $7.25 (mouser.com) | 588–621 | |

**Total:** about **$40** for items 1–6, 8, 11 and 12 at mouser.com
prices. Add **€66.39** for the EX330, and the wire bought elsewhere.

**Shipping:**
- Free on most orders **over €75**
  ([mouser.fr help](https://www.mouser.fr/help/orders-shipping)).
- Ships the same day; delivery takes 2–5 days.
- The sale terms say prices exclude VAT; check at checkout.

## Table 3 — not found on either site

None of the **required** parts is missing from both sites: every one is on
at least one. What's left:

| Item | amazon.fr | mouser.fr | What to do |
|---|---|---|---|
| 5.08 mm 8-pin header + plug, with a price | generic listings only; the one price (€34.21, [B0D7714SNJ](https://www.amazon.fr/Bornier-enfichable-connecteur-5-08mm-femelle/dp/B0D7714SNJ)) doesn't say which variant | genuine Phoenix 1757307 + 1757077 found, no price | only needed if the Order 3 pack is short of 2 + 2. Price it on mouser.fr then |
| 20 AWG wire in a short length | ✅ found (Table 1, #7) | ❌ only 100 ft spools (~$96 a colour) | Amazon, or any local electronics or DIY shop |
| Branded PTC fuse (Bourns / Littelfuse) | ❌ only generic 30 V 1.1 A packs | ✅ MF-R110, RUEF110 | generic is fine; Mouser if you want a brand |
| 4 mm standoffs (remote board) | not searched | not searched | thread and length wait for the remote-board mount design (`control/wiring.md` §6.2) |
| M3 × 3 / × 4 grub screws (optional, mechanical) | not searched | not searched | optional (`docs/bom.md`, dial unit v2) |

To let a future session read live amazon.fr / mouser.fr pages (current
price and stock), add `www.amazon.fr` and `www.mouser.fr` to the cloud
environment's allowed domains (network settings).
