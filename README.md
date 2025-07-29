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

To visualize microphone input in amplitude mode:

```bash
python src/visualizer.py
```


To visualize microphone input in frequency mode:

```bash
python src/visualizer.py --mode frequency

```

To visualize a specific audio file (e.g., `song.wav`):

```bash
python src/visualizer.py song.wav
```

You can also display frequency bars for the file:

```bash
python src/visualizer.py song.wav --mode frequency
```

A window will open showing bars that react to the audio input.

