# Visualizer

This project provides a simple Python-based audio visualizer. It can listen to live microphone input or play back an audio file while displaying a fullscreen-style animation that reacts to the music.

## Requirements
- Python 3.12 or newer
- `pygame`
- `sounddevice`
- `soundfile`
- `numpy`

You can install the dependencies with:

```bash
pip install pygame sounddevice soundfile numpy
```

## Running

To visualize microphone input:

```bash
python src/visualizer.py
```

You can optionally specify the audio samplerate, block size, and device:

```bash
python src/visualizer.py --samplerate 48000 --blocksize 2048 --device 1
```

To visualize a specific audio file (e.g., `song.wav`):

```bash
python src/visualizer.py song.wav
```

List available audio devices with:

```bash
python -m sounddevice
```

## Troubleshooting

- If no audio is captured or playback fails, verify the correct device index or
  name is used. Run `python -m sounddevice` to see all available devices.
- Ensure your operating system allows Python to access the microphone or audio
  input. On Linux you may need to add your user to the `audio` group.
- Some devices require specific sample rates or block sizes. Try adjusting the
  `--samplerate` or `--blocksize` arguments if you encounter errors.

A window will open showing a dynamic bar that reacts to the audio amplitude.
