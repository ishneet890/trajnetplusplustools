from collections import namedtuple


PygameTrackRow = namedtuple('Row', ['frame', 'pedestrian', 'x', 'y', 'group', 'obstacles', 'prediction_number', 'scene_id'])
PygameTrackRow.__new__.__defaults__ = (None, None, None, None, None, None, None, None)
PygameSceneRow = namedtuple('Row', ['scene', 'pedestrian', 'start', 'end', 'group', 'fps', 'obstacles'])
PygameSceneRow.__new__.__defaults__ = (None, None, None, None, None, None)
