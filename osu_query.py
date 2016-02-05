import json
import urllib2
import urllib
import time

MODS = {"nomod", "hidden", "hardrock","doubletime","freemod", "tiebreaker"}
DIFFICULTIES = {"beginner": 0, "standard": 1, "expert":2}
NUM_DIFFICULTIES = 3

def _read_config():
    f = open("config.json")
    json_data = f.read()
    f.close()
    return json.loads(json_data)

config = _read_config()

def _query_api(command, parameters):
    params = urllib.urlencode(parameters)
    url = "https://osu.ppy.sh/api/" + command +"?k=" + config["osu_api_key"]
    response = None
    while response is None:
        try:
            response = urllib2.urlopen(url, params).read()
            time.sleep(1)
        except urllib2.HTTPError:
            print "error!"
            time.sleep(1)
    return json.loads(response)
    
    
class MatchInfo:
        
    def __init__(self, match_id):
        command = "get_match"
        parameters = {
            "mp": match_id,
        }
        self.match = _query_api(command, parameters)
        
    def get_games(self):
        if  self.match is None:
            return list()
        return self.match["games"]

class BeatmapInfo:
    
    def __init__(self, beatmap_id):
        command = "get_beatmaps"
        parameters = {
            "b": beatmap_id,
        }
        self.beatmap = _query_api(command, parameters)[0]

    def __str__(self):
        return self.get_artist() + " - " + self.get_song_name() + "[" + self.get_difficulty_name() + "]"
    
    def get_artist(self):
        return self.beatmap["artist"]
    
    def get_creator(self):
        return self.beatmap["creator"]
    
    def get_song_name(self):
        return self.beatmap["title"]
    
    def get_difficulty_name(self):
        return self.beatmap["version"]
    
    def get_star_rating(self):
        return self.beatmap["difficultyrating"]
    
    def get_drain_time(self):        
        return self.beatmap["hit_length"]
    
    def get_total_length(self):
        return self.beatmap["total_length"]
 
    def get_bpm(self):
        return self.beatmap["bpm"]
    
    def get_map_set_id(self):
        return int(self.beatmap["beatmapset_id"])
        
    def get_beatmap_id(self):
        return int(self.beatmap["beatmap_id"])
    
    def get_beatmap_data(self, mod):
        beatmap_data = dict()
        beatmap_data["mapid"] = self.get_beatmap_id()
        beatmap_data["setid"] = self.get_map_set_id()
        beatmap_data["title"] = self.get_song_name()
        beatmap_data["artist"] = self.get_artist()
        beatmap_data["creator"] = self.get_creator()
        beatmap_data["version"] = self.get_difficulty_name()
        beatmap_data["star"] = self.get_star_rating()
        if mod is "doubletime":
            print mod
            beatmap_data["drain"] = self.get_drain_time()/1.5
            beatmap_data["length"] = self.get_total_length()/1.5
        else:
            beatmap_data["drain"] = self.get_drain_time()
            beatmap_data["length"] = self.get_total_length()
        beatmap_data["type"] = mod
        return beatmap_data


def _output(output_file, data):
    with open(output_file, 'w') as fp:
        json.dump(data, fp, indent=2)
         
def _is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
        
def get_beatmaps(input_file):
    beatmaps = dict()
    with open(input_file) as f:
        for line in f:
            line = line[:-1]
            if _is_int(line):
                beatmaps[line] = BeatmapInfo(line)
    return beatmaps

def num_maps_played(beatmaps, input_file, output_file):
    maps_played = {}
    with open(input_file) as f:
        for match_id in f:
            games = MatchInfo(match_id).get_games()
            for game in games[:5]:
                beatmap_id = game["beatmap_id"]
                map_key = None
                if beatmap_id in beatmaps:
                    map_key = str(beatmaps[beatmap_id])
                    if map_key not in maps_played:
                        maps_played[map_key] = 1
                    else:
                        maps_played[map_key] = maps_played[map_key] + 1
                    
    _output(output_file, maps_played)
    return maps_played


def output_mappools(beatmaps, input_file, output_file):
    map_pool = [[] for i in range(0,3)]
    mod = ""
    diff = 0
    with open(input_file) as f:
        for line in f:
            line = line[:-1].lower()
            if _is_int(line):
                try:
                    map_pool[diff] = map_pool[diff] + [beatmaps[line].get_beatmap_data(mod)]
                except KeyError:
                    print line
            else:
                if line in MODS:
                    mod = line
                elif line in DIFFICULTIES:
                    diff = DIFFICULTIES[line]
    _output(output_file, map_pool)
    return map_pool

if __name__ == "__main__":
    beatmaps = get_beatmaps("maps.txt")
    output_mappools(beatmaps, "maps.txt", "mappools.json")
    
    
    
