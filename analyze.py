import math
import xml.etree.ElementTree as ET
from pathlib import Path
import zipfile
import tempfile
import shutil

class Parser:
    def __init__(self, path):
        self.path = path
        self.tree = ET.parse(path)
        self.root = self.tree.getroot()

    # finding
    def look_up(self):
        for child in self.root:
            print(child.tag, child.attrib)

    def ID(self):
        Run_number = self.root.attrib.get("runNumber")
        return {"run_number": Run_number}

    def Track(self):
        #tracks amount
        track = self.root.find("Track")
        if track is None:
            return None
        n_tracks = int(track.attrib.get("count"))

        #get track values
        pt = self.read(track, "pt")
        if pt is None:
            return None
        pt = [float(i) for i in pt.split()]

        # count how much negative and positive tracks
        positive = 0
        negative = 0

        for i in pt:
            if i > 0:
                positive += 1
            elif i < 0:
                negative += 1
            else:
                pass

        abs_pt = [abs(i) for i in pt]
        max_pt = max(abs_pt)
        total_energy = sum(abs_pt)

        result = {"n_tracks": n_tracks, "n_pos_tracks": positive, "n_neg_tracks": negative, "max_track_pt": max_pt, "sum_track_pt": total_energy}
        return result

    def RVx(self):
        rvx = self.root.find("RVx")
        if rvx is None: return None

        primVxCand = rvx.find("primVxCand")
        if primVxCand is None: return None
        primVxCand = primVxCand.text.split()

        num_tracks = rvx.find('numTracks')
        if num_tracks is None: return None
        num_tracks = num_tracks.text.split()

        z = rvx.find("z")
        if z is None: return None
        z = z.text.split()

        ind = int(primVxCand.index('1'))

        z = z[ind]
        num_tracks = num_tracks[ind]

        result = {"primary_vertex_z": float(z), "primary_vertex_ntracks": int(num_tracks)}
        return result

    def ETMis(self):
        etmis_all = self.root.findall("ETMis")
        if len(etmis_all) == 0: return None
        etmis = None

        for i in etmis_all:
            key = i.attrib.get('storeGateKey')
            if key == 'MET_RefFinal':
                etmis = i
                break

        if etmis is None:
            return None
        else:
            result = {"etmis": float(etmis.find('et').text.strip())}

        return result

    def JET(self):
        jet = self.root.find("Jet")
        if jet is None: return None

        n_jet = int(jet.attrib.get("count"))

        et = jet.find("et")
        if et is None: return None
        et = et.text.strip().split()
        et = [float(i) for i in et]

        max_et = max(et)
        result = {"n_jets": n_jet, "leading_jet_et": max_et}

        return result

    def Event_Data(self):
        id_ = self.ID()
        track = self.Track()
        rvx = self.RVx()
        etmis = self.ETMis()
        jet = self.JET()

        result = {"id": id_, "track": track, "rvx": rvx, "met_reffinal": etmis, "jet": jet}
        return result

    # grabbing
    def read(self, block, element):
        if block is None:
            print("Track block not found")
            return None

        info = block.find(element)

        if info is None or info.text is None:
            print(f"{element} not found")
            return None

        return info.text

class Manual_Analyzer:
    def __init__(self, data):
        self.data = data

    def track_coef(self):
        track = self.data["track"]
        if not track:
            return None

        manual_counter = 0

        n_tracks = track["n_tracks"]
        n_pos_tracks = track["n_pos_tracks"]
        n_neg_tracks = track["n_neg_tracks"]
        max_track_pt = track["max_track_pt"]
        sum_track_pt = track["sum_track_pt"]

        # n_tracks
        if n_tracks <= 30:
            manual_counter += 3
        elif 31 <= n_tracks <= 80:
            manual_counter += 2
        elif 81 <= n_tracks <= 150:
            manual_counter += 1
        elif 151 <= n_tracks <= 300:
            manual_counter += 0
        else:
            manual_counter -= 3

        # charges
        if n_pos_tracks > 0 and n_neg_tracks > 0:
            manual_counter += 2
        else:
            manual_counter -= 3

        # charge balance
        if abs(n_pos_tracks - n_neg_tracks) <= 0.3 * n_tracks:
            manual_counter += 1

        # max_track_pt
        if max_track_pt < 5:
            manual_counter -= 2
        elif 5 <= max_track_pt < 20:
            manual_counter += 0
        elif 20 <= max_track_pt < 100:
            manual_counter += 2
        elif 100 <= max_track_pt < 500:
            manual_counter += 3
        else:
            manual_counter += 1

        # sum_track_pt
        if sum_track_pt < 50:
            manual_counter -= 1
        elif 50 <= sum_track_pt < 300:
            manual_counter += 2
        elif 300 <= sum_track_pt < 800:
            manual_counter += 1
        elif 800 <= sum_track_pt < 1500:
            manual_counter += 0
        else:
            manual_counter -= 2

        return manual_counter

    def rvx_coef(self):
        rvx = self.data["rvx"]
        track = self.data["track"]

        if not rvx:
            return None

        manual_counter = 0

        z = rvx["primary_vertex_z"]
        primary_vertex_ntracks = rvx["primary_vertex_ntracks"]
        n_tracks = track["n_tracks"]

        # z
        if abs(z) <= 10:
            manual_counter += 0
        elif 10 < abs(z) <= 15:
            manual_counter -= 1
        else:
            manual_counter -= 2

        # ratio of primary vertex tracks
        ratio = primary_vertex_ntracks / n_tracks

        if ratio >= 0.7:
            manual_counter += 2
        elif ratio >= 0.4:
            manual_counter += 1
        elif ratio >= 0.2:
            manual_counter += 0
        else:
            manual_counter -= 2

        return manual_counter

    def met_reffinal_coef(self):
        met_reffinal = self.data["met_reffinal"]
        if not met_reffinal:
            return None

        manual_counter = 0
        met = met_reffinal["etmis"]

        if met < 100:
            manual_counter += 3
        elif 100 <= met < 250:
            manual_counter += 2
        elif 250 <= met < 500:
            manual_counter += 1
        elif 500 <= met < 800:
            manual_counter -= 1
        else:
            manual_counter -= 3

        return manual_counter

    def jet_coef(self):
        jet = self.data["jet"]
        if not jet:
            return None

        manual_counter = 0
        n_jets = jet["n_jets"]
        leading_jet_et = jet["leading_jet_et"]

        # n_jets
        if n_jets <= 1:
            manual_counter += 3
        elif 2 <= n_jets <= 3:
            manual_counter += 1
        elif 4 <= n_jets <= 5:
            manual_counter -= 1
        else:
            manual_counter -= 3

        # leading_jet_et
        if leading_jet_et < 20:
            manual_counter += 2
        elif 20 <= leading_jet_et < 60:
            manual_counter += 1
        elif 60 <= leading_jet_et < 120:
            manual_counter += 0
        else:
            manual_counter -= 2

        return manual_counter

    def analyze(self):
        manual_score = 0

        track_coef = self.track_coef()
        rvx_coef = self.rvx_coef()
        met_reffinal_coef = self.met_reffinal_coef()
        jet_coef = self.jet_coef()

        parts = [
            track_coef,rvx_coef,met_reffinal_coef,jet_coef
        ]

        for part in parts:
            if part is not None:
                manual_score += part

        return {
            "manual_score": manual_score,
            "track_coef": self.track_coef(),
            "rvx_coef": self.rvx_coef(),
            "met_reffinal_coef": self.met_reffinal_coef(),
            "jet_coef": self.jet_coef()
        }

class Anomaly_Analyzer:
    def __init__(self, data):
        self.data = data

    def analyze(self):
        anomaly_score = 0

        track_coef = self.track_coef()
        met_reffinal_coef = self.met_reffinal_coef()
        jet_coef = self.jet_coef()

        parts = [
            track_coef, met_reffinal_coef, jet_coef
        ]

        for part in parts:
            if part is not None:
                anomaly_score += part

        return {
            "anomaly_score": anomaly_score,
            "track_coef": track_coef,
            "met_reffinal_coef": met_reffinal_coef,
            "jet_coef": jet_coef
        }

    def track_coef(self):

        track = self.data["track"]
        if not track:
            return None

        n_tracks = track["n_tracks"]
        max_track_pt = track["max_track_pt"]
        sum_track_pt = track["sum_track_pt"]

        anomaly_score = 0

        # n_tracks: крайности интересны
        if n_tracks <= 20:
            anomaly_score += 2
        elif n_tracks >= 500:
            anomaly_score += 3
        elif n_tracks >= 300:
            anomaly_score += 1

        # max_track_pt
        if max_track_pt >= 500:
            anomaly_score += 3
        elif max_track_pt >= 100:
            anomaly_score += 2
        elif max_track_pt >= 50:
            anomaly_score += 1

        # sum_track_pt
        if sum_track_pt >= 3000:
            anomaly_score += 3
        elif sum_track_pt >= 1500:
            anomaly_score += 2
        elif sum_track_pt >= 800:
            anomaly_score += 1

        return anomaly_score

    def met_reffinal_coef(self):
        met = self.data["met_reffinal"]
        if not met: return None

        met_reffinal = met["etmis"]

        anomaly_score = 0

        # MET
        if met_reffinal >= 1000:
            anomaly_score += 4
        elif met_reffinal >= 800:
            anomaly_score += 3
        elif met_reffinal >= 500:
            anomaly_score += 2
        elif met_reffinal >= 250:
            anomaly_score += 1

        return anomaly_score

    def jet_coef(self):
        jet = self.data["jet"]

        if not jet:
            return None

        anomaly_score = 0

        leading_jet_et = jet["leading_jet_et"]
        n_jets = jet["n_jets"]

        # leading jet
        if leading_jet_et >= 500:
            anomaly_score += 4
        elif leading_jet_et >= 150:
            anomaly_score += 3
        elif leading_jet_et >= 80:
            anomaly_score += 2
        elif leading_jet_et >= 40:
            anomaly_score += 1

        # много джетов тоже может быть аномально
        if n_jets >= 8:
            anomaly_score += 2
        elif n_jets >= 5:
            anomaly_score += 1

        return anomaly_score

class ContrastAnalyzer:
    def __init__(self, data):
        self.data = data

    def analyze(self):
        track = self.data["track"]
        jet = self.data["jet"]
        met = self.data["met_reffinal"]

        if not track or not jet or not met:
            return None

        n_tracks = track["n_tracks"]
        max_track_pt = track["max_track_pt"]
        sum_track_pt = track["sum_track_pt"]

        met_reffinal = met["etmis"]

        n_jets = jet["n_jets"]
        leading_jet_et = jet["leading_jet_et"]

        # 1. Насколько мало треков
        # Чем меньше n_tracks, тем больше scarcity
        # +1 чтобы не делить на 0
        scarcity = 80 / (n_tracks + 5)

        # 2. Сила странных признаков
        # log даёт плавный рост вместо диких прыжков
        met_part = math.log1p(met_reffinal / 100)
        jet_part = math.log1p(leading_jet_et / 50)
        pt_part = math.log1p(max_track_pt / 50)

        signal_strength = met_part + jet_part + pt_part

        # 3. Штраф за грязь
        noise_penalty = 0

        if n_tracks > 150:
            noise_penalty += 1
        if n_tracks > 300:
            noise_penalty += 2
        if n_tracks > 500:
            noise_penalty += 3

        if n_jets >= 4:
            noise_penalty += 1
        if n_jets >= 7:
            noise_penalty += 2

        # слишком большая суммарная насыщенность тоже часто каша
        if sum_track_pt > 1500:
            noise_penalty += 1
        if sum_track_pt > 3000:
            noise_penalty += 2

        contrast_score = scarcity * signal_strength * 10 - noise_penalty

        return {
            "contrast_score": round(contrast_score, 2),
            "scarcity": round(scarcity, 3),
            "signal_strength": round(signal_strength, 3),
            "noise_penalty": noise_penalty,
            "met_part": round(met_part, 3),
            "jet_part": round(jet_part, 3),
            "pt_part": round(pt_part, 3),
        }


def process_path(path_to_file, filename=None):
    path = Path(path_to_file)
    results = []

    def process_single(xml_path, filename=None):
        try:
            parser = Parser(str(xml_path))
            event_data = parser.Event_Data()

            anomaly_analyzer = Anomaly_Analyzer(event_data)
            manualy_analyzer = Manual_Analyzer(event_data)
            contrast_analyzer = ContrastAnalyzer(event_data)

            return {
                "file": str(filename or xml_path.name),
                "event_data": event_data,
                "anomaly": anomaly_analyzer.analyze(),
                "manual": manualy_analyzer.analyze(),
                "contrast": contrast_analyzer.analyze(),
            }

        except Exception as e:
            return {
                "file": str(filename or xml_path.name),
                "error": str(e)
            }

    # Если это папка
    if path.is_dir():
        for xml_file in path.rglob("*.xml"):
            results.append(process_single(xml_file, xml_file.name))

    # Если это один файл
    elif path.is_file():
        if path.suffix.lower() == ".xml":
            results.append(process_single(path, filename or path.name))

        elif path.suffix.lower() == ".zip":
            temp_dir = Path(tempfile.mkdtemp())

            try:
                with zipfile.ZipFile(path, "r") as zf:
                    zf.extractall(temp_dir)

                for xml_file in temp_dir.rglob("*.xml"):
                    results.append(process_single(xml_file, xml_file.name))

                if not results:
                    return "ZIP does not contain XML files"

            finally:
                shutil.rmtree(temp_dir, ignore_errors=True)

        else:
            return "Unsupported file type"

    else:
        return "Invalid path"

    output = []

    for i, res in enumerate(results, 1):
        output.append(f"--- FILE {i}: {res.get('file')} ---")

        if "error" in res:
            output.append(f"ERROR: {res['error']}")
        else:
            output.append(f"event data: {res['event_data']}")
            output.append(f"anomaly coef: {res['anomaly']}")
            output.append(f"manual coef: {res['manual']}")
            output.append(f"contrast coef: {res['contrast']}")

        output.append("")

    return results