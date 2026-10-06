# Does the Fichet-Bauche "Complice" relock or lock out after wrong tries?

Researched 2026-10-06 (cloud session), for the `control/sequence.md` open
item "anti-manipulation relocking behaviour, before running thousands of
automated attempts".

## Answer

**No source I could find says the mechanical Complice counts wrong attempts,
adds penalty delays, or locks out.** What it does have is a **relocker
("délateur")** that blocks the lock *for good* when it is **attacked
mechanically or with heat**. So the risk to manage is force, not the number
of tries: never hammer or over-torque the key. The firmware is already built
that way. Confidence: medium. Only search-result excerpts were readable (the
manufacturer, retailer and manual pages are blocked from this session), and
they describe the *current* Complice, not necessarily this older safe.

## What the sources say

Quoted from search-engine excerpts. The pages themselves could not be
opened from here, so I couldn't check which sentence is on which page: treat
the links as where to look. Paul can open them.

1. **Lock = key lock + 3-counter mechanical combination, 8,000
   combinations.** "The MPx lock is systematically associated with the three
   Fichet-Bauche counter tube combination in Complice safes. The 3-counter
   combination offers up to 8,000 possible combinations." That matches our
   20 × 20 × 20. Retailers list the model as "Complice … Mxb & 3 Tubes".
   [lacledu16.fr](https://lacledu16.fr/en/products/complice-20l),
   [fichet-bauche.com Complice](https://www.fichet-bauche.com/product/complice-safe-40l-2/),
   [domoowe-coffre-fort.fr](https://www.domoowe-coffre-fort.fr/shop/coffre-fort/coffre-fort-a2p-classe-0/coffre-fort-fichet-bauche-complice-20-mxb-3-tubes/)
2. **Relocker triggered by attack.** "A relocking device blocks the lock
   definitively in the event of a mechanical or thermal attack"; "a délateur
   … that blocks the lock definitively in case of mechanical or thermal
   attack". Same sources, and
   [coffre-fort.com, Fichet AF II with MxB + 3 tube counters](https://www.coffre-fort.com/armoires-fortes-af2/2613-armoire-forte-fichet-af-ii-250l-serrure-mxb-3-tubes-compteurs.html).
3. **Anti-forget key retention**: "an anti-forget mechanism retains the key
   until the lock is locked". This only means the key can't be pulled out
   while the lock is open. It doesn't affect the robot.
4. **The manual** (Complice Installation and Use Manual, 94 pages,
   [ManualsLib 1388230](https://www.manualslib.com/manual/1388230/Fichet-Bauche-Complice.html))
   has sections "Opening the safe", "Setting the combination", "Checking the
   setting", "Scrambling the combination", "Troubleshooting". One excerpt:
   to change the combination, "Lock the MPX lock by turning the key
   counterclockwise and remove the key", then turn a change button inside the
   door. That fits Paul's observation: the key turns **clockwise** to open.
5. **Certifications**: A2P / EN 1143-1 for the safe; mechanical combination
   locks of this class are tested to EN 1300, which includes **manipulation
   resistance**. That's about not leaking the combination by feel (relevant
   to false sets), not a lockout feature.
   [BSI, EN 1300](https://knowledge.bsigroup.com/products/secure-storage-units-classification-for-high-security-locks-according-to-their-resistance-to-unauthorized-opening)
6. Fichet-Bauche patents on safe combination locks from the 1970s exist
   (FR2337241 "Serrure à combinaisons pour coffre-fort ou analogue",
   CA1066079). They might describe the counter mechanism of an older safe
   like this one; I couldn't open them (patents.google.com blocked).

## What this means for the robot (already in the firmware)

- **Limited force**: the key runs at ~2× the torque it takes to turn by hand
  (bench stage 5) and stops at the first StallGuard pulse. Dials run at
  ≤ 1 A. Nothing is hammered or retried at higher force.
- **If the relocker ever fired**, the key would most likely stop somewhere
  new, or not turn. The firmware notices: an attempt that stops well short of
  N is retried, and after 3 in a row it stops (`ERR EARLY`). The re-check
  every 200 attempts stops if N has moved (`ERR RECHECK`). Either way it
  stops and waits for Paul, with the log showing where it changed.
- **Every attempt's angle is logged**, so false sets (the fence dropping
  partway) can be told apart afterwards (`tools/logger.py --analyse`).

## Worth doing by hand before the long run (Paul)

1. Read the manual's "Opening the safe", "Scrambling the combination" and
   "Troubleshooting" pages (ManualsLib link above). Look for any warning about
   forcing the key, or about a sequence (e.g. counters set before the key is
   inserted).
2. With the dials at some setting, turn the key to its stop by hand, with
   normal force, 10 times. Does anything change (stop angle, feel, a click)?
