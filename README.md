# food-picture-01 — Steaming Bowl of Ramen

Entry for [make.fun/bounty/food-picture-01](https://make.fun/bounty/food-picture-01)
— "Make the best-looking food picture", $250 USDC escrowed, ends
Sun 15 Nov 2026 07:00 WIB (Sun 15 Nov 00:00 UTC).

## Concept

One dish, close up: a steaming bowl of ramen on a warm wooden table —
golden broth with noodle swirls, two soft eggs, chashu, green onions, nori,
chopsticks resting on the rim, steam rising, soft window light. Warm and
glossy, no faces, no text: the food is the whole picture, and it still reads
as appetising at ~300 px.

## How to run

Python 3.13, standard library only. No network, no randomness.

```sh
python3 main.py   # writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png)
```

## Validation (2026-11-14 ~07:45 WIB)

- PNG 138,316 bytes (< 1 MiB), 1024x1024.
- Two runs byte-identical (sha256
  `0262953bcd28172437aa839fd91f1b1b794fcfaf7a432c5372fc8cb462c01a0c`).
- ~10.5 s/run (limit 60 s).
- Pixel spot-checks confirm the scene: warm wood table, broth + chashu,
  both egg yolks, nori, both chopsticks, steam over the bowl.

## Status

Entry complete and validated locally. GitHub repo + bundle + submission NOT
done — needs chief's go-ahead.
