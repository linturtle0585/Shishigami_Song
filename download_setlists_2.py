import json
from tqdm import tqdm
from download_setlists import get_playlist_videos, extract_setlist_comments

results = []
json_filename = 'shishigami_setlists.json'
playlist_url = 'https://www.youtube.com/playlist?list=PLTUPXbT5Ni8zmczjbAriHiGYeJAPxoT8g'
videos = get_playlist_videos(playlist_url)

with open(json_filename, 'r', encoding='utf-8') as file:
    data = json.load(file)
exist_titles = [i['title'] for i in data]
now_titles = [i['title'] for i in videos]
new_titles = list(filter(lambda x: x is not None, [i for i in now_titles if i not in exist_titles]))

for title in tqdm(new_titles):
    video_id = [video['video_id'] for video in videos if video['title'] == title][0]
    results.append(extract_setlist_comments(video_id))
none_tracks_list = [item for item in results if item.get("tracks") is None]
tracks_list = []
for none_track in tqdm(none_tracks_list):
    video_id = none_track['video_id']
    tracks_list.append(extract_setlist_comments(video_id))
final_results = [item for item in results if item.get("tracks") is not None]
final_results.extend([item for item in tracks_list if item.get("tracks") is not None])
video_map = {v["video_id"]: v.get("title") for v in videos if "video_id" in v}
for item in final_results:
    item.pop("raw_text", None)
    video_id = item.get("video_id")
    if video_id in video_map:
        item["title"] = video_map[video_id]
data.extend(final_results)

with open(json_filename, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False)
print(f"\n已順利將結果儲存至 `{json_filename}`")