import lzma
import time
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as mpatches

from . import beatmap as osu_beatmap

class Replay:
    def __init__(self, file):
        self.game_mode = read_byte(file)

        # Sem minigames
        if self.game_mode != 0:
            return None

        # Versão do osu! e hash do mapa. A gente ignora.
        self.osu_version = read_int(file)
        self.map_md5 = read_binary_string(file)
        
        # Nome do jogador.
        self.player = read_binary_string(file)

        # Hash do replay. Dava pra usar, mas é meio desnecessário.
        self.replay_md5 = read_binary_string(file)

        # Acertos
        self.n_300s = read_short(file)
        self.n_100s = read_short(file)
        self.n_50s = read_short(file)
        self.n_geki = read_short(file)
        self.n_katu = read_short(file)
        self.n_misses = read_short(file)

        # Score e combo
        self.score = read_int(file)
        self.max_combo = read_short(file)
        self.perfect = read_byte(file)

        # Acurácia
        total = self.n_300s + self.n_100s + self.n_50s + self.n_misses
        self.accuracy = (self.n_300s + self.n_100s / 3 + self.n_50s / 6) / total

        # Mods (ignora)
        self.mods = read_int(file)

        # Gráfico de vida. Vide site para o formato.
        life_graph = read_binary_string(file)
        self.life_graph = [t.split('|') for t in life_graph.split(',')[:-1]]

        # Timestamp do replay (ignora)
        self.timestamp = read_long(file)
        
        # Informações do replay em si
        replay_length = read_int(file)
        replay_data = lzma.decompress(file.read(replay_length)).decode('utf8')

        data = [t.split("|") for t in replay_data.split(',')[:-1]]
        self.data = [(int(w), float(x), float(y), int(z)) for w, x, y, z in data]

        # Não usado
        _ = read_long(file)

def read_byte(file):
    return ord(file.read(1))

def read_short(file):
    return read_byte(file) + (read_byte(file) << 8)

def read_int(file):
    return read_short(file) + (read_short(file) << 16)

def read_long(file):
    return read_int(file) + (read_int(file) << 32)

def read_uleb128(file):
    n = 0
    i = 0
    while True:
        byte = read_byte(file)
        n += (byte & 0x7F) << i
        if byte & 0x80 != 0:
            i += 7
        else:
            return n

def read_binary_string(file):
    while True:
        flag = read_byte(file)
        if flag == 0x00:
            return ""
        elif flag == 0x0b:
            length = read_uleb128(file)
            return file.read(length).decode('utf8')
        else:
            raise RuntimeError("Invalid file")

def load(filename):
    with open(filename, "rb") as file:
        return Replay(file)

def draw_cursor(ax, x, y, z):
    keys = int(z)
    if keys & 0x01:
        cursor = 'ro'
    elif keys & 0x02:
        cursor = 'go'
    else:
        cursor = 'y+'
    ax.plot([x], [384 - y], cursor)
    
def draw_slider(ax, beatmap, radius, t, obj):
    path = obj[5].split("|")
    stype = path.pop(0)

    points = [(obj[0], 384 - obj[1])] + [(int(x), 384 - int(y)) for x, y in [t.split(':') for t in path]]
    codes = []

    if stype == 'L':
        codes.append(Path.MOVETO)
        for i in range(1, len(points)):
            codes.append(Path.LINETO)

    elif stype == 'P':  # Círculo perfeito
        codes.append(Path.MOVETO)
        codes.append(Path.CURVE3)
        codes.append(Path.CURVE3)

    else: # Bezier
        n = 0
        for i in range(0, len(points)):
            n += 1
            repeated = i + 1 < len(points) and points[i] == points[i + 1]
            if i + 1 == len(points) or n == 4 or repeated:
                if n == 2:
                    codes.append(Path.MOVETO)
                    codes.append(Path.LINETO)
                elif n == 3:
                    codes.append(Path.MOVETO)
                    codes.append(Path.CURVE3)
                    codes.append(Path.CURVE3)
                elif n == 4:
                    codes.append(Path.MOVETO)
                    codes.append(Path.CURVE4)
                    codes.append(Path.CURVE4)
                    codes.append(Path.CURVE4)
                n = 0
                
    preempt, fade = beatmap.approach_rate()
    duration = beatmap.slider_duration(obj)
    if t < obj[2] + preempt + duration:
        alpha = 1
    else:
        alpha = 1 - (t - (obj[2] + preempt + duration)) / osu_beatmap.SLIDER_FADEOUT
                
    slider = mpatches.PathPatch(
        Path(points, codes),
        fc="none", capstyle='round', transform=ax.transData, fill=False,
        edgecolor=(1.0, 1.0, 1.0, alpha), linewidth=radius, joinstyle='bevel', zorder=-2
    )
    ax.add_patch(slider)

    slider = mpatches.PathPatch(
        Path(points, codes),
        fc="none", capstyle='round', transform=ax.transData, fill=False,
        edgecolor="#333333", linewidth=radius-4, joinstyle='bevel', zorder=-1
    )
    ax.add_patch(slider)

last_nc = 0
current_color = 0

def draw_hit_objects(ax, beatmap, t, objs):
    global current_color, last_nc
    
    circles = ([], [], [])
    radius = (27.2 - 2.24 * beatmap['CircleSize'])
    combo_colors = [(1.0, 0, 0), (0, 1.0, 0), (0, 1.0, 0), (1.0, 1.0, 0)]
    
    # Sliders
    for obj in objs:
        color = current_color
        if obj[3] & 4 and obj[2] > last_nc:
            last_nc = obj[2]
            current_color += 1
            current_color %= len(combo_colors)
            color = current_color
        elif obj[2] < last_nc:
            color = (len(combo_colors) + current_color - 1) % len(combo_colors)
            
        # Spinner
        if obj[3] & 8:
            ax.plot([obj[0]], [obj[1]], 'yo', fillstyle='none', markersize=128)
            
        else:
            # Slider
            if obj[3] & 2:
                draw_slider(ax, beatmap, radius, t, obj)
                
            # Círculo (Slider também tem)
            circles[0].append(obj[0])
            circles[1].append(384 - obj[1])

            preempt, fade = beatmap.approach_rate()

            if t > obj[2] + preempt:
                alpha = 1 - (t - obj[2] - preempt) / osu_beatmap.CIRCLE_FADEOUT
            elif t < obj[2] + fade:
                alpha = 1 - ((obj[2] + fade) - t) / fade
            else:
                alpha = 1
            alpha = max([0, min(1, alpha)])
            
            
            r, g, b = combo_colors[color]
            circles[2].append((r, g, b, alpha))
            
    ax.scatter(circles[0], circles[1], color=circles[2], s=radius ** 2)

def cursor_state(replay, time):
    tt = 0
    for t in replay:
        w, x, y, z = t

        if w > 0:
            tt += w
        else:
            continue

        if tt > time:
            break

    return x, y, z

def preview(beatmap, replay_data):
    plt.ion()

    fig = plt.figure(facecolor='#333333')
    ax = fig.add_subplot(1, 1, 1)

    ax.clear()
    ax.axis('off')
    fig.canvas.draw()

    plt.show()

    delta = 0
    tt = 0
    for t in replay_data[0]:
        w, x, y, z = t
        
        if w > 0:
            tt += w
            
        sec = w / 1000
        
        # Frame skip
        if delta > sec:
            delta -= sec
            continue
        
        # Espera o tempo especificado entre o estado atual e o anterior
        # no arquivo de replay
        if sec > 0:
            time.sleep(sec - delta)
            delta = 0
        
        start = time.time()

        # Limpa tudo
        ax.clear()
        ax.axis('off')
        ax.set_xlim((-32, 512 + 32))
        ax.set_ylim((-32, 384 + 32))
        fig.canvas.draw_idle()
        
        # Desenha o objeto do mapa
        objs = beatmap.visible_objects(tt)
        
        if len(objs) > 0:
            draw_hit_objects(ax, beatmap, tt, objs)
            
        draw_cursor(ax, x, y, z)

        for d in replay_data[1:]:
            x, y, z = cursor_state(d, tt)
            draw_cursor(ax, x, y, z)

        fig.canvas.draw()
        
        # Calcula o atraso
        delta += time.time() - start