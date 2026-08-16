<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://user-images.githubusercontent.com/124475503/227062194-11a2e228-61ef-4fe7-a6c7-1a0ebba8f417.png">
  <source media="(prefers-color-scheme: light)" srcset="https://user-images.githubusercontent.com/124475503/227062235-ef1eaff8-238a-40e1-955b-4b2a9880d6dd.png">
  <img alt="Infinity-Drive Logo" src="https://user-images.githubusercontent.com/124475503/227062235-ef1eaff8-238a-40e1-955b-4b2a9880d6dd.png">
</picture>

A terminal-based Python script that allows YouTube to act as storage for any type of file.

This is a fork of [**rondotcomYT/Infinity-Drive**](https://github.com/rondotcomYT/Infinity-Drive) with significant performance optimizations to the encoding and decoding pipeline.

All credit for the original concept belongs to [**DvorakDwarf**](https://github.com/DvorakDwarf) and their [**Infinite-Storage-Glitch**](https://github.com/DvorakDwarf/Infinite-Storage-Glitch) project.

## Performance Improvements

This fork replaces the original pixel-by-pixel processing (using `PIL.ImageDraw` and `Image.getpixel()` inside nested loops) with vectorized NumPy operations, removes the per-frame disk cache, and fixes an inefficient frame-seeking pattern during decoding.

Benchmarked with a 10 MB input file:

| Metric | Original | Optimized | Improvement |
|---|---|---|---|
| **Encoding time** | 140.86s | 31.78s | **~4.4x faster** |
| **Decoding time** | 3m 2s (182s) | 14s | **~13x faster** |
| **Decoding speed** | 35 FP/s | 413 FP/s | **~11.8x faster** |
| Output video size | 140.5 MB | 172.6 MB | — |
| Output video duration | 3:23 | 3:23 (unchanged) | — |

Files encoded with the original version remain fully compatible for decoding with this optimized fork, and vice versa — the underlying encoding scheme (density metadata, bit-to-pixel mapping) is unchanged.

## A Few Words

This project started as a beginner-friendly script, and while the core logic remains the same, this fork focuses purely on making the existing approach run as fast as possible on the CPU without altering the encoding format. Please keep in mind that some rough edges may still exist, and feel free to report any [**issues**](https://github.com/rondotcomYT/Infinity-Drive/issues) — or issues specific to this fork in its own issue tracker.

## Installation and Setup

1. [**Install Python 3**](https://www.python.org/downloads/)
2. Clone the repository `git clone https://github.com/IvanSCP/Infinity-Drive-optimized.git`
   - [**Download Git**](https://github.com/git-guides/install-git) if you do not have it installed
3. Install requirements `pip install -r requirements.txt`
   - [**Download pip**](https://pip.pypa.io/en/stable/installation/) if you do not have it installed
4. Run Infinity-Drive `python Infinity-Drive.py`
5. Follow on-screen instructions
