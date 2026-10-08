# Does the Fichet-Bauche "Complice" relock or lock out after wrong tries?

> **Revision 2026-10-08.1** · project revision baseline (this research is unchanged by the E0 wiring change) · log: `../docs/revisions.md`


Researched 2026-10-06 (cloud session), for the `control/sequence.md` open
item "anti-manipulation relocking behaviour, before running thousands of
automated attempts". Updated the same evening with the manual's own "Normal
use" text (a screenshot from Paul) and Paul's checks on the real key.

## Answer

**No source I could find says the mechanical Complice counts wrong attempts,
adds penalty delays, or locks out.** What it does have is a **relocker
("délateur")** that blocks the lock *for good* when it is **attacked
mechanically or with heat**. So the risk to manage is force, not the number
of tries: never hammer or over-torque the key. The firmware is already built
that way. Confidence: medium-high. The manual's normal-use procedure
(below) has no limit on tries or waiting time. Paul has read the manual: it
has **no warning about entering wrong combinations** (2026-10-06). The
relocker details come from search-result excerpts (the pages are blocked
from this session) and describe the *current* Complice.

**New point from the manual — to check before the long run:** in normal use
you **set the combination first, then insert the key**. The robot keeps the
key inserted, at rest, while it turns the dials. Paul (2026-10-06): the
dials turn with the key at its start, and still click with the key turned to
its ~100° stop. Paul's two cautions (possibilities, no source):
- The lock might let the bolts retract only if the key has gone back to the
  start since the combination was set. Firmware v0.2 returns the key to its
  rest stop after every attempt, so it doesn't depend on this.
- The lock might only count a combination dialled with the key *out*, as
  in the manual. The dials turning with the key in doesn't rule this out.
  If it's true, the robot can't open the safe without a way to pull the key
  out and push it back in at every attempt. There's no bench test I know of
  that settles it short of finding the combination. Stage 4b.6 gives a weak
  hint, and the first full run is the real test.

Searched again 2026-10-06 (evening) for how the 3-tube combination and the
M3B key interact: nothing found. Fichet's manual PDF and the patent sites
are blocked from the cloud session. A search excerpt mentions a separate
Fichet "3-tube combination" user manual; Paul may have it.

## What the sources say

**0. The Complice manual, "Opening the safe" page, NORMAL USE** (screenshot
from Paul, `docs/photos/complice_manual_normal_use.png` — primary source):

> **Opening the combination**: Dial the combination - Insert the key into the
> M3b lock and turn it clockwise - Pull on the key to open the door.
> **Closing - Locking**: Close the door - Turn the key anticlockwise to engage
> the bolt - Remove the key - Scramble the combination.

- No limit on tries, and no waiting time, in normal use.
- Order: combination first, then the key (see the new point above).
- Clockwise opens; anticlockwise engages the bolt, and the key comes out only
  then. That matches Paul's checks (2026-10-06): the key goes in one way only;
  from there it won't turn anticlockwise at all; it turns ~100° clockwise to
  its stop; it can only be removed back at the start position.
- "Pull on the key to open the door": the robot only turns the key. On a
  success it holds the key where it got to; Paul takes the key turner off and
  pulls.
- This manual calls the key lock "M3b"; current sales pages say "MxB" or
  "MPx" — a different generation, probably.

Points 1–6 are quoted from search-engine excerpts. The pages themselves could not be
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

1. Done (Paul, 2026-10-06): the manual has no warning about wrong
   combinations.
2. **With the key inserted at rest, can each dial still be turned by hand
   with the tube key?** If not, the robot as designed can't work: it can't
   take the key out between tries. Done (Paul, 2026-10-06): yes, at the
   key's start, and they still click with the key at its ~100° stop.
3. With the dials at some setting, turn the key to its stop by hand, with
   normal force, 10 times. Does anything change (stop angle, feel, a click)?
