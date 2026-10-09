# Ordering the remaining parts: amazon.fr vs mouser.fr (2026-10-07)

> **Revision 2026-10-09.1** · order history; key driver on the RAMPS E0 socket, UART pigtail — the hub-board parts here are spares now · log: `docs/revisions.md`

**Revision 2026-10-08.1 (2026-10-08):** a record of the 2026-10-07 order.
Some of these parts — the PTC fuse, the 100 µF capacitors, and (elsewhere) the
6-conductor cable and Phoenix connectors — are **no longer used** now that the
key driver is in the RAMPS E0 socket. They were bought; keep them as spares.
Nothing here needs re-ordering. See `docs/revisions.md` and `docs/bom.md`.

This covers everything still marked 🛒 in `docs/bom.md` ("Electronics
assembly — every discrete part", table A), plus the three tools on its
"Still to buy" list (multimeter, solder, flush cutters).

**Status (2026-10-07): ordered.** Paul placed the amazon.fr order: items
1, 2 and 5–8 of Table 1, with these changes (Paul's screenshots):
- **Capacitor:** Innfeeltech 100 µF 35 V radial, 50 pcs, €7.49, delivery
  Friday 9 Oct, instead of item 2. It isn't sold as low ESR
  (`control/wiring.md`, log 2026-10-07).
- **PTC fuse:** which listing isn't recorded. None arrives soon, so a
  **1.6 A T (slow-blow) 5 × 20 mm glass fuse** stands in for hub F1 until
  it does: AUKENIEN 120-piece slow-blow kit, 5 × 20 mm, 250 V, €15.99,
  Prime next day.

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
  - Items 1, 2 and 5–8: **€53.13**, plus €7 delivery on the fuse.
    (Correction, 2026-10-07: the search snippet said €2; Paul's basket
    shows €7.)
  - Items 1 and 2 ship slowly from their sellers. Alternates are under
    "If the fuse or capacitor ships too slowly" below. Neither part is
    needed before bring-up stage 5.
  - Most picks are generic, unbranded parts. That's fine for this use.
- **mouser.fr** has branded parts (Bourns, Panasonic, Würth, Samtec,
  Adafruit) and real stock counts.
  - It has no 20 AWG wire in a sensible length: the smallest spool found
    is 100 ft, at about $96 a colour. So it can't cover everything in one
    order.
  - The parts come to about $21 at mouser.com prices. That's under the
    €75 free-delivery threshold, so delivery would be charged (the amount
    wasn't found).
- **Checked (Paul, 2026-10-07), so items 3, 4 and 9–12 aren't needed:**
  - the **header strips** (male and female) came with another order;
  - the Phoenix pack holds **5 headers + 5 plugs**: 2 + 2 needed, 3 + 3
    spare;
  - the soldering station came with **solder and solder wick**;
  - Paul **has flush cutters** and **a multimeter**.

  **The order is items 1, 2 and 5–8.**
- **Why the DC-jack adapter (item 6):** the PSU ends in a barrel *plug*,
  but the hub's 12V IN and the RAMPS '5A' input are screw terminals. The
  adapter is the socket the plug goes into; two 20 AWG wires run from its
  screws to the hub.
  - Without it you'd cut the plug off and screw the bare leads in,
    identifying + with the multimeter. That's free but can't be undone.
  - Don't use the Mega's own barrel jack instead. It feeds only the Mega
    (VIN). The RAMPS motor rail would get no 12 V, because D1 conducts
    only from that rail to VIN (RAMPS KiCad netlist, `control/wiring.md`
    log 2026-10-07).

## Table 1 — amazon.fr

| # | Need | Pick (ASIN) | Pack | Price shown | Availability shown | Fit notes |
|---|---|---|---|---|---|---|
| 1 | PTC fuse, radial, 1.1 A hold, ≥ 16 V ×2 | 30V 1.1A resettable fuse, radial "Polyswitch" — [B0848QX3FS](https://www.amazon.fr/fusible-r%C3%A9armable-plomb-radial-Polyswitch/dp/B0848QX3FS) | 20 | €10.21 + €7 delivery (Paul's basket, 2026-10-07; the snippet said €2) | **31 Oct – 5 Nov** (Paul's basket, 2026-10-07); third-party seller (LingTongTrade) | radial, 30 V, 1.1 A: meets spec. Generic, no reviews |
| 2 | 100 µF ≥ 25 V low-ESR electrolytic ×2 | Elna RJH 35 V 100 µF, 8 × 12 mm — [B07H9BKFGF](https://www.amazon.fr/Condensateur-%C3%A9lectrolytique-Electrolytic-Capacitor-Elna/dp/B07H9BKFGF) | 20 | €9.46 | in stock, free delivery **14–16 Oct** (Paul's basket, 2026-10-07); sold by IT-Tronics GmbH | RJH is a low-impedance series. 3.5 mm lead pitch: bend the leads to fit the perfboard. Alternative: sourcing map low-ESR 35 V, 6.3 × 7 mm, 50 pcs, €9.99 — [B07LDZ5HF8](https://www.amazon.fr/sourcing-map-Radial-Faible-Resist/dp/B07LDZ5HF8) |
| 3+4 | **Not needed** (from another order) — header strips | IZOKEE male + female 40-pin kit — [B07DBY753C](https://www.amazon.fr/IZOKEE-Connecteur-Femelle-Broches-Prototype/dp/B07DBY753C) | 15 + 15 strips | €11.71 | not shown | 4.6/5 (683). Female strips don't snap: cut them with the flush cutters (you lose one pin per cut). One strip gives 2 × 8 + 1 × 2 |
| 5 | F–F jumpers 10–20 cm, ~20 | ELEGOO 120 Dupont wires, 20 cm (40 F–F) — [B01JD5WCG2](https://www.amazon.fr/Elegoo-Multicolore-M%C3%A2le-Femelle-M%C3%A2le-M%C3%A2le-Femelle-Femelle/dp/B01JD5WCG2) | 120 | €8.99 | not shown | 4.7/5 (2,811) |
| 6 | DC jack, female 5.5 × 2.1 mm → screw terminal | LitaElek 5.5 × 2.1 adapters — [B019HAC6V4](https://www.amazon.fr/LitaElek-Femelle-Adaptateur-Connecteur-dispositifs/dp/B019HAC6V4) | 5 female + 5 male | €8.99 | not shown | 4.5/5 (1,235), 3 A. Check + / − with the multimeter before first use |
| 7 | 20 AWG wire, red + black, ≥ 1 m each | QUARKZMAN 20 AWG 2-core PVC, red/black, 4.5 m — [B0CW9M53BS](https://www.amazon.fr/QUARKZMAN-Parall%C3%A8le-Conducteurs-Longueur-Diam%C3%A8tre/dp/B0CW9M53BS) | 4.5 m pair | €9.49 | "only 3 left" (snippet) | true 20 AWG, tinned copper. The cores peel apart |
| 8 | Zip ties ~100 mm | Gocableties 100 × 2.5 mm, black — [B072SLJR2T](https://www.amazon.fr/Gocableties-100-colliers-serrage-nylon-robuste/dp/B072SLJR2T) | 100 | €5.99 or €4.99 (snippets differ) | not shown | 4.5/5 |
| 9 | **Not needed** (5 + 5 on hand) — 5.08 mm 8-pin pluggable terminal | no reliable listing — see Table 3 | — | — | — | — |
| 10 | **Not needed** (Paul has one) — multimeter | **budget:** UNI-T UT33D+ — [B08W36VF6H](https://www.amazon.fr/UNI-T-UT33D-MIE0328-Miernik-Uniwersalny/dp/B08W36VF6H) · **better:** Fluke 101 — [B00V6BBRNQ](https://www.amazon.fr/Fluke-Multim%C3%A8tre-num%C3%A9rique-poche-101/dp/B00V6BBRNQ) | 1 | UT33D+ €22.23 · Fluke 101 €77.38 (other sellers from €65.01) | UT33D+: free delivery, "Amazon's Choice" | UT33D+: 4.6/5 (144), buzzer, diode test, manual ranging. Fluke 101 has a continuity beeper and DC V (Fluke spec) |
| 11 | **Not needed** (came with the station) — solder, ~0.8 mm | 63/37 rosin core 0.8 mm, 4 × 50 g — [B09L412D4X](https://www.amazon.fr/souder-colophane-bricolage-%C3%A9lectronique-paquet/dp/B09L412D4X) | 200 g | €14.99 | not shown | leaded. 4.3/5 (17 reviews only). Lead-free alternative: GTSE Sn99.3Cu0.7, 100 g, 4.5/5 (537) — [B08GGBT378](https://www.amazon.fr/GTSE-souder-colophane-soudure-%C3%A9lectrique/dp/B08GGBT378), €6.59–18.49 (snippets differ) |
| 12 | **Not needed** (on hand) — flush cutters | Knipex 78 61 125 SB Electronic Super Knips — [B000OIB7J6](https://www.amazon.fr/Knipex-78-61-125-SB/dp/B000OIB7J6) | 1 | €25.99 | not shown | 4.7/5 (3,695). Alternative: Hakko CHP-170, €24.31 — [B00FZPDG1K](https://www.amazon.fr/Hakko-CHP-170-Pince-coupe-fil-souple/dp/B00FZPDG1K) |

**Totals at the prices shown:**
- **The order (1, 2, 5–8): €53.13**, plus €7 delivery on the fuse (the
  snippet said €2; corrected 2026-10-07).
  Without the DC-jack adapter it's €44.14. Either is over the €35
  free-delivery threshold for the items Amazon ships itself.
- For the record:
  - €64.84 before the header strips were ruled out;
  - before items 9–12 were ruled out:
    - €87.07 with the UT33D+ (€142.22 with the Fluke);
    - before that, €128.05 with UT33D+, solder and Knipex (€183.20 with
      the Fluke).

**Free delivery** is over €35, but only for items sold or shipped by
Amazon ([help page](https://www.amazon.fr/gp/help/customer/display.html?nodeId=GZXW7X6AKTHNUP6H)).
Some picks look like third-party sellers, so check "Expédié par Amazon" on
each.

### If the fuse or capacitor ships too slowly (2026-10-07)

Paul's basket showed the fuse (item 1) arriving 31 Oct – 5 Nov and the
capacitor (item 2) 14–16 Oct, both from third-party sellers.

**Neither part holds up bring-up stages 0–4.**
- F1 feeds only the cable's 12 V to the key turner: hub 12V IN + → F1 →
  Phoenix pin 1 (`control/wiring.md` §5).
- C1 sits on the remote (key) driver board.
- Stages 0–4 use the dial drivers only; stage 4b says "the key turner is
  not needed yet". Leave F1's place on the hub empty until then, so the
  cable carries no 12 V.
- Both parts are first needed at **stage 5 (key turner)**.

So the slow listings may be fine. If you'd rather have them sooner, these
also meet the spec. **Delivery dates weren't visible from here**, so pick
whichever shows "Expédié par Amazon" or the earliest date in your basket.

**PTC fuse.** On a multi-value listing, select the **1.1 A** variant. The
part code ends in **110**, as in RUEF110 or JK30-110, meaning 1.10 A hold.
It needs 2 radial leads and a rating of ≥ 16 V. All the 30 V and 72 V
packs below have margin.

| Pick (ASIN) | Pack | Notes |
|---|---|---|
| JK30 30 V PPTC, radial ("DIP") — [B0D56N2RWZ](https://www.amazon.fr/Fusible-r%C3%A9initialisable-polym%C3%A8re-PPTC-pi%C3%A8ces/dp/B0D56N2RWZ) | 10 | **select 1.1 A** (the link may open on 0.5 A) |
| COJIC JK30 30 V PPTC, radial — [B0CPVKHC3L](https://www.amazon.fr/COJIC-PI%C3%88CES-fusible-r%C3%A9initialisable-polym%C3%A8re/dp/B0CPVKHC3L) | 10 | **select 1.1 A** |
| MYRRHE 30 V, RUEF110 option — [B0CPVDXLJQ](https://www.amazon.fr/MYRRHE-fusibles-r%C3%A9armables-enfichables-r%C3%A9armable/dp/B0CPVDXLJQ) | 10 | **select RUEF110 1.1 A** |
| FESTAS 30 V 1.1 A — [B0D4HMVP13](https://www.amazon.fr/Fusibles-r%C3%A9initialisables-thermistance-polym%C3%A8re-auto-r%C3%A9cup%C3%A9ration/dp/B0D4HMVP13) | 10 or 40 | **select 1.1 A** |
| RXEF 72 V assortment, 10 values × 5 pcs, includes 1.1 A — [B0C5SMK827](https://www.amazon.fr/Valeurs-Pi%C3%A8ces-fusible-auto-r%C3%A9armable-s%C3%A9rie/dp/B0C5SMK827) | 50 | no variant to pick; spare values for later |
| RGEF110, 16 V, 1.1 A — [B0DPC8W6GK](https://www.amazon.fr/Fusible-r%C3%A9initialisable-pi%C3%A8ces-RGEF110-fusible/dp/B0DPC8W6GK) | 50 | meets ≥ 16 V with no margin; prefer a 30 V one |

**Capacitor.** Keep it **low ESR**. The TMC2209 datasheet (§3) recommends
low-ESR electrolytics for VS filtering, with at least 100 µF near the
driver. Plain "100 µF 35 V" packs (no low-ESR claim) are a last resort.

| Pick (ASIN) | Pack | Notes |
|---|---|---|
| sourcing map low-ESR 100 µF 35 V, 105 °C, 6.3 × 7 mm — [B07LDZ5HF8](https://www.amazon.fr/sourcing-map-Radial-Faible-Resist/dp/B07LDZ5HF8) | 50 | ~€9.99 (snippet). **First choice.** A 6.3 mm can normally has 2.5 mm lead spacing, which fits the perfboard without bending |
| "faible ESR / haute fréquence" 100 µF 35 V, 6 × 12 mm — [B0CS34JZG2](https://www.amazon.fr/condensateur-%C3%A9lectrolytique-Industrial-Electrical-capacitors/dp/B0CS34JZG2) | 20 | unbranded; low ESR is the seller's claim |

Whichever you get, check the polarity when you fit it: the stripe marks −.

## Table 2 — mouser.fr

| # | Need | Part (manufacturer MPN, link) | Order qty | Price shown | Stock shown | Notes |
|---|---|---|---|---|---|---|
| 1 | PTC fuse ×2 | Bourns **MF-R110**, radial, 1.1 A hold / 2.2 A trip, 30 V — [⇄ link](https://www.mouser.fr/ProductDetail/Bourns/MF-R110?qs=wd8kHz0doL7LkwIbzZb5mA%3D%3D) | 2 | ~$0.40 each (mouser.com, unreliable) | 19,054 | alternative: Littelfuse RUEF110 — [⇄ link](https://www.mouser.fr/ProductDetail/Littelfuse/RUEF110?qs=hv6pn79dJPSNtwKNbPwPHQ%3D%3D) |
| 2 | 100 µF ≥ 25 V low ESR ×2 | Panasonic **EEU-FR1E101**, 25 V, 6.3 × 11.2 mm, 2.5 mm pitch, 130 mΩ — [⇄ link](https://www.mouser.fr/ProductDetail/Panasonic/EEU-FR1E101?qs=Ao3mORb5HCDieoJwtkb8Dw%3D%3D) | 2 | $0.45 each (mouser.com) | 19,980 | alternative: Rubycon 35ZLH100MEFC6.3X11 (35 V) — [⇄ link](https://www.mouser.fr/ProductDetail/Rubycon/35ZLH100MEFC6.3X11?qs=T3oQrply3y8xzyooRx3RZg%3D%3D) |
| 3 | **Not needed** — male header ≥ 13 pins | Würth **61302011121**, 1 × 20, 2.54 mm, gold — [⇄ link](https://www.mouser.fr/ProductDetail/Wurth-Elektronik/61302011121?qs=PhR8RmCirEbj/FsnpbhNaw%3D%3D) | 2 | $1.23 each (mouser.com) | 1,288 | |
| 4 | **Not needed** — female sockets 2 × (1 × 8) + 1 × (1 × 2) | Samtec **SSW-108-01-G-S** (1 × 8) — [⇄ link](https://www.mouser.fr/ProductDetail/Samtec/SSW-108-01-G-S?qs=FESYatJ8odLaL9GxbCQJ2g%3D%3D) and **SSW-102-01-G-S** (1 × 2) — [⇄ link](https://www.mouser.fr/ProductDetail/Samtec/SSW-102-01-G-S?qs=92ilVni64gwMaw8Iglb9kA%3D%3D) | 2 + 1 | 1 × 8: $1.76 each (mouser.com); 1 × 2: not shown | 1 × 8: 6,306 | |
| 5 | F–F jumpers ~20 | Adafruit **4447**, silicone F–F, 200 mm, 40 pcs — [⇄ link](https://www.mouser.fr/ProductDetail/Adafruit/4447?qs=CUBnOrq4ZJzovVmrsSU55g%3D%3D) | 1 | $9.95 (mouser.com) | 724–1,513 | |
| 6 | DC jack adapter, female | SparkFun **PRT-10288** "DC Barrel Jack Adapter – Female" — [⇄ link](https://www.mouser.fr/ProductDetail/SparkFun/PRT-10288?qs=WyAARYrbSnbv/ypDwaDLyg%3D%3D) | 1 | $2.95 (mouser.com) | 101 | **VERIFY 5.5 × 2.1 mm and screw terminals** on the page |
| 7 | 20 AWG wire, ≥ 1 m red + black | Alpha Wire 3053 RD005 / BK005, 100 ft spools | — | ~$96 per spool (mouser.com, a 3053 variant) | 239–251 | **not sensible for 2 m** (see Table 3) |
| 8 | Zip ties | Panduit **PLT1M-M**, 99 mm, natural — [⇄ link](https://www.mouser.fr/ProductDetail/Panduit/PLT1M-M?qs=PijdWQvv7l82QBSPSSlofg%3D%3D) | 100 | $0.064 each (mouser.com) | 709,949 | |
| 9 | **Not needed** (5 + 5 on hand) — Phoenix 8-pin, header + plug | header MSTBA 2,5/8-G-5,08 = **1757307** — [⇄ link](https://www.mouser.fr/ProductDetail/Phoenix-Contact/1757307?qs=o3rrLWFGhRl4IvmrdyQ5FA%3D%3D); plug MSTB 2,5/8-ST-5,08 = **1757077** (no page seen) | 2 + 2 | not shown | not shown | genuine Phoenix Contact |
| 10 | **Not needed** — multimeter | Extech **EX330** (Mouser 685-EX330), autoranging, 600 V DC, continuity — [⇄ link](https://www.mouser.fr/ProductDetail/Extech/EX330?qs=tv7vi16PWA4nsXR8adm%2Bmg%3D%3D) | 1 | **€66.39** ([mouser.fr listing](https://www.mouser.fr/Extech/Test-Measurement/Multimeters-Voltmeters/_/N-5gfo?P=1z13cd3)) | 11 | the only EUR price found. Alternative: Fluke 107 ESP, $160.99 |
| 11 | **Not needed** — solder | MG Chemicals **4900-35G**, SAC305 lead-free, 0.81 mm (Mouser 590-4900-35G) | 1 | $5.35 (old USD catalogue: may be stale) | not shown | no product page seen. Alternative: 4900-112G (¼ lb) — [⇄ link](https://www.mouser.fr/ProductDetail/MG-Chemicals/4900-112G?qs=YqNA2qefETAK87e3A6/Oig%3D%3D) |
| 12 | **Not needed** — flush cutters | Adafruit **152** (Hakko CHP-170) — [⇄ link](https://www.mouser.fr/ProductDetail/Adafruit/152?qs=N/3wi2MvZWC96jMaJ3xvTg%3D%3D) | 1 | $7.25 (mouser.com) | 588–621 | |

**Total:** about **$21** for items 1, 2, 5, 6 and 8 at mouser.com prices,
plus delivery (the order is under €75), plus the wire bought elsewhere.
- It was about $27 with the headers (items 3, 4).
- It was about $40 with items 11 and 12 as well.

Paul ruled those out on 2026-10-07.

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
| 5.08 mm 8-pin header + plug, with a price | generic listings only; the one price (€34.21, [B0D7714SNJ](https://www.amazon.fr/Bornier-enfichable-connecteur-5-08mm-femelle/dp/B0D7714SNJ)) doesn't say which variant | genuine Phoenix 1757307 + 1757077 found, no price | **not needed**: the Order 3 pack holds 5 + 5 (Paul, 2026-10-07) |
| 20 AWG wire in a short length | ✅ found (Table 1, #7) | ❌ only 100 ft spools (~$96 a colour) | Amazon, or any local electronics or DIY shop |
| Branded PTC fuse (Bourns / Littelfuse) | ❌ only generic 30 V 1.1 A packs | ✅ MF-R110, RUEF110 | generic is fine; Mouser if you want a brand |
| 4 mm standoffs (remote board) | not searched | not searched | thread and length wait for the remote-board mount design (`control/wiring.md` §6.2) |
| M3 × 3 / × 4 grub screws (optional, mechanical) | not searched | not searched | optional (`docs/bom.md`, dial unit v2) |

To let a future session read live amazon.fr / mouser.fr pages (current
price and stock), add `www.amazon.fr` and `www.mouser.fr` to the cloud
environment's allowed domains (network settings).
