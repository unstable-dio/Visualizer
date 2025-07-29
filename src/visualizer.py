"""Realtime audio visualization utilities."""

import sys
import numpy as np
import pygame
import sounddevice as sd
import soundfile as sf
import queue


class AudioVisualizer:
    """Generate amplitude values from audio input for visualization."""
    def __init__(self, source=None, device=None, samplerate=44100, blocksize=1024):
        """Initialize the visualizer.

        Parameters
        ----------
        source : str or None, optional
            Path to an audio file to play and visualize. When ``None`` the
            microphone is used.
        device : int or None, optional
            Input device index used by :mod:`sounddevice`.
        samplerate : int, optional
            Sampling rate for audio capture in hertz.
        blocksize : int, optional
            Size of audio blocks passed to the callback.
        """

        self.source = source
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.device = device
        self.q = queue.Queue()
        self.stream = None
        self.playback_data = None
        self.playback_stream = None

    def audio_callback(self, indata, frames, time, status):
        """Handle audio input blocks and queue their amplitude.

        Parameters
        ----------
        indata : ndarray
            Incoming audio data.
        frames : int
            Number of frames in ``indata``.
        time : object
            Unused timing information provided by :mod:`sounddevice`.
        status : CallbackFlags
            Status flags indicating errors from :mod:`sounddevice`.
        """

        if status:
            print(status, file=sys.stderr)
        amplitude = np.linalg.norm(indata) / np.sqrt(len(indata))
        self.q.put(amplitude)

    def start(self):
        """Start audio capture and optional playback."""

        if self.source:
            # load file and start playback
            self.playback_data, file_sr = sf.read(self.source, dtype='float32')
            if self.samplerate is None:
                self.samplerate = file_sr
            self.playback_stream = sd.OutputStream(samplerate=self.samplerate,
                                                   channels=self.playback_data.shape[1] if self.playback_data.ndim > 1 else 1)
            self.playback_stream.start()
            self.playback_stream.write(self.playback_data)

        self.stream = sd.InputStream(device=self.device,
                                     channels=1,
                                     callback=self.audio_callback,
                                     samplerate=self.samplerate,
                                     blocksize=self.blocksize)
        self.stream.start()

    def stop(self):
        """Stop audio capture and playback streams."""

        if self.stream:
            self.stream.stop()
            self.stream.close()
        if self.playback_stream:
            self.playback_stream.stop()
            self.playback_stream.close()

    def get_amplitude(self):
        """Retrieve the latest amplitude value.

        Returns
        -------
        float
            The most recent amplitude measurement or ``0.0`` when no
            measurement is available.
        """

        try:
            return self.q.get_nowait()
        except queue.Empty:
            return 0.0



def run_visualizer(source=None):
    """Launch the visualization window.

    Parameters
    ----------
    source : str or None, optional
        Path to an audio file to visualize. When ``None`` the microphone
        is used.
    """

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Audio Visualizer')

    visualizer = AudioVisualizer(source=source,
                                device=device,
                                samplerate=samplerate,
                                blocksize=blocksize)
    visualizer.start()

    clock = pygame.time.Clock()
    running = True
    amplitude = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        amp = visualizer.get_amplitude()
        if amp:
            amplitude = amp

        screen.fill((0, 0, 0))
        height = int(amplitude * 400)
        height = max(10, min(height, 600))
        color_value = min(255, int(amplitude * 500))
        color = (color_value, 255 - color_value, 128)
        pygame.draw.rect(screen, color, (100, 300 - height//2, 600, height))
        pygame.display.flip()
        clock.tick(60)

    visualizer.stop()
    pygame.quit()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Simple audio visualizer")
    parser.add_argument('source', nargs='?', help='Optional audio file to play')
    parser.add_argument('--samplerate', type=int, default=44100,
                        help='Audio sampling rate (default: 44100)')
    parser.add_argument('--blocksize', type=int, default=1024,
                        help='Block size for audio capture (default: 1024)')
    parser.add_argument('--device', help='Input device name or index')
    args = parser.parse_args()

    run_visualizer(args.source,
                   samplerate=args.samplerate,
                   blocksize=args.blocksize,
                   device=args.device)
