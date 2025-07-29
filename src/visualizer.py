import sys
import argparse
import numpy as np
import pygame
import sounddevice as sd
import soundfile as sf
import queue


class AudioVisualizer:
    def __init__(self, source=None, device=None, samplerate=44100, blocksize=1024, mode="amplitude"):
        self.source = source
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.device = device
        self.mode = mode
        self.q = queue.Queue()
        self.stream = None
        self.playback_data = None
        self.playback_stream = None

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        if self.mode == "amplitude":
            amplitude = np.linalg.norm(indata) / np.sqrt(len(indata))
            self.q.put(amplitude)
        else:
            data = indata[:, 0]
            spectrum = np.abs(np.fft.rfft(data))
            freqs = np.fft.rfftfreq(len(data), d=1.0 / self.samplerate)

            def band_power(low, high):
                idx = np.logical_and(freqs >= low, freqs < high)
                if np.any(idx):
                    return float(np.mean(spectrum[idx]))
                return 0.0

            bass = band_power(20, 250)
            mid = band_power(250, 4000)
            high = band_power(4000, self.samplerate / 2)
            self.q.put((bass, mid, high))

    def start(self):
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
        if self.stream:
            self.stream.stop()
            self.stream.close()
        if self.playback_stream:
            self.playback_stream.stop()
            self.playback_stream.close()

    def get_data(self):
        try:
            return self.q.get_nowait()
        except queue.Empty:
            if self.mode == "amplitude":
                return 0.0
            return (0.0, 0.0, 0.0)


def run_visualizer(source=None, mode="amplitude"):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Audio Visualizer')

    visualizer = AudioVisualizer(source=source, mode=mode)
    visualizer.start()

    clock = pygame.time.Clock()
    running = True
    amplitude = 0
    bands = (0.0, 0.0, 0.0)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        data = visualizer.get_data()
        if mode == "amplitude":
            if data:
                amplitude = data
        else:
            if any(data):
                bands = data

        screen.fill((0, 0, 0))
        if mode == "amplitude":
            height = int(amplitude * 400)
            height = max(10, min(height, 600))
            color_value = min(255, int(amplitude * 500))
            color = (color_value, 255 - color_value, 128)
            pygame.draw.rect(screen, color, (100, 300 - height//2, 600, height))
        else:
            bar_width = 180
            for i, val in enumerate(bands):
                height = int(val * 0.05)
                height = max(10, min(height, 600))
                color = (int(85 * i + 85), 255 - int(85 * i + 85), 128)
                x = 100 + i * (bar_width + 20)
                pygame.draw.rect(screen, color, (x, 300 - height//2, bar_width, height))
        pygame.display.flip()
        clock.tick(60)

    visualizer.stop()
    pygame.quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simple audio visualizer")
    parser.add_argument("source", nargs="?", help="Audio file to play and visualize")
    parser.add_argument("--mode", choices=["amplitude", "frequency"], default="amplitude",
                        help="Visualization mode")
    args = parser.parse_args()
    run_visualizer(args.source, mode=args.mode)
