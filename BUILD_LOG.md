# food-picture-01 — build log

- Started: 2026-11-14 ~07:40 WIB (00:40 UTC). Deadline: 2026-11-15T00:00:00Z
  (Sun 15 Nov 07:00 WIB).
- Kit: downloaded 2026-11-14 from https://make.fun/c/food-picture-01/kit,
  unpacked to ~/workspace/makefun/kits/food-picture-01/.
- Rules read: bounty page + competition.yaml. Entry: Python 3.13 main.py at
  repo root, stdlib only, no network, deterministic. Writes
  /output/entry.png (PNG/JPEG, <=1 MiB, <=1024x1024), runs twice, identical
  bytes. Judged pairwise by an AI judge on appetite first, then texture,
  styling/light, craft, reads at ~300 px. Prize table: $50 / $20 / $10 /
  $5 x7 / $1.50 x90, top 100 share $250.
- Concept: one dish close up — steaming bowl of ramen on a warm wooden
  table (golden broth, noodle swirls, two soft eggs, chashu, green onions,
  nori, chopsticks, steam, window light). No faces, no text.
- Renderer: pure-stdlib Python PNG encoder (zlib + struct + CRC32); scene
  computed pixel by pixel. No PIL, no randomness.
- Validation (2026-11-14 ~07:45 WIB): PNG 138,316 bytes (<1 MiB),
  1024x1024. Two runs byte-identical (sha256
  0262953bcd28172437aa839fd91f1b1b794fcfaf7a432c5372fc8cb462c01a0c),
  10.5 s/run (limit 60 s). Pixel spot-checks confirm the scene (warm wood,
  broth + chashu, both yolks, nori, both chopsticks, steam).
- Status: entry complete and validated locally. Bundle + check and GitHub
  repo + submission NOT done — needs chief's go-ahead.
- Revision 2026-11-14 ~11:05 WIB (submit-time fix for kit check
  thinking_revised: entrypoint took its final content from 1 message only):
  raised the nori sheet so it visibly sticks up above the rim behind the
  egg — NORI_POLY top 424/430 -> 392/398. Re-validated: PNG 138,366 bytes
  (<1 MiB), 1024x1024, two runs byte-identical (sha256
  8a85f131c97947028833ffa5d38f537f8709560d9a48817c617890b7a6f3180a);
  spot-checks: nori pixels at (320,400)/(320,410) = (22,38,24), 1,464 nori
  pixels above the rim; broth, yolk and chopstick pixels unchanged.
