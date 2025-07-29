import sys
import numpy as np
import pygame
import sounddevice as sd
import soundfile as sf
import queue


class AudioVisualizer:
    def __init__(self, source=None, device=None, samplerate=44100, blocksize=1024):
        self.source = source
        self.samplerate = samplerate
        self.blocksize = blocksize
        self.device = device
        self.q = queue.Queue()
        self.stream = None
        self.playback_data = None
        self.playback_stream = None

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        amplitude = np.linalg.norm(indata) / np.sqrt(len(indata))
        self.q.put(amplitude)

    def start(self):
        if self.source:
            # load file and start playback
            try:
                self.playback_data, file_sr = sf.read(self.source, dtype='float32')
            except Exception as e:
                print(f"Failed to read '{self.source}': {e}")
                return False
            if self.samplerate is None:
                self.samplerate = file_sr
            try:
                self.playback_stream = sd.OutputStream(
                    samplerate=self.samplerate,
                    channels=self.playback_data.shape[1] if self.playback_data.ndim > 1 else 1)
                self.playback_stream.start()
                self.playback_stream.write(self.playback_data)
            except Exception as e:
                print(f"Failed to play '{self.source}': {e}")
                return False

        self.stream = sd.InputStream(device=self.device,
                                     channels=1,
                                     callback=self.audio_callback,
                                     samplerate=self.samplerate,
                                     blocksize=self.blocksize)
        self.stream.start()
        return True

    def stop(self):
        if self.stream:
            self.stream.stop()
            self.stream.close()
        if self.playback_stream:
            self.playback_stream.stop()
            self.playback_stream.close()

    def get_amplitude(self):
        try:
            return self.q.get_nowait()
        except queue.Empty:
            return 0.0


def run_visualizer(source=None):
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption('Audio Visualizer')

    visualizer = AudioVisualizer(source=source)
    if not visualizer.start():
        pygame.quit()
        return

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
    source = sys.argv[1] if len(sys.argv) > 1 else None
    run_visualizer(source)
