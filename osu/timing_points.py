from . import hitobjects

class TimingPoint:
    def __init__(self, *args):
        self.offset = int(args[0])
        self.bpm = float(args[1])
        self.meter = int(args[2])
        self.sample_set = hitobjects.SampleSet(int(args[3]))
        self.sample_index = int(args[4])
        self.volume = int(args[5])
        self.inherited = bool(int(args[6]))
        self.kiai = bool(int(args[7]))

def create(obj):
    return TimingPoint(*obj)