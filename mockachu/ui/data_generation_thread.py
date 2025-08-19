from PyQt6.QtCore import QThread, pyqtSignal

class DataGenerationThread(QThread):

    progress = pyqtSignal(int)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, data_generator, request):
        super().__init__()
        self.data_generator = data_generator
        self.request = request

    def run(self):

        try:
            self.data_generator.reset_generators()

            self.progress.emit(0)

            data = self.data_generator.generate(self.request)

            self.progress.emit(100)
            self.finished.emit(data)

        except Exception as e:
            self.error.emit(str(e))
