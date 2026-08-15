import re, yt_dlp
import json
from tqdm import tqdm
from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_RECENT

def timestamp_to_seconds(ts_str):
    """轉為總秒數，方便比較大小"""
    parts = [int(p) for p in ts_str.split(':')]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        return parts[0] * 60 + parts[1]
    return 0

def extract_clean_setlist(raw_text):
    """從單則留言文字中提取『時間嚴格遞增』的歌單列表"""
    # 定義時間戳正則表達式 (支援 M:SS、MM:SS、H:MM:SS、HH:MM:SS)
    ts_regex = r'(?:\d{1,2}:)?\d{1,2}:\d{2}'
    timestamp_pattern = re.compile(rf'({ts_regex})\s*〜?\s*(.+)')
    lines = raw_text.split('\n')
    clean_tracks = []
    last_seconds = -1  #記錄前一首歌曲的時間（秒）
    for line in lines:
        match = timestamp_pattern.search(line.strip())
        if match:
            timestamp = match.group(1)
            raw_title = match.group(2)
            song_title = re.sub(ts_regex, '', raw_title) #移除歌名內後續出現的所有時間戳
            song_title = re.sub(r'^[-\s〜~]+', '', song_title) #清除開頭的破折號、波浪號或殘留空格
            song_title = re.sub(r':[a-zA-Z0-9_+-]+:', '', song_title) #清除:emoji_name:格式的表情符號標籤
            song_title = re.sub(r'\s+', ' ', song_title).strip() #整理連續空格並修剪首尾
            curr_seconds = timestamp_to_seconds(timestamp)
            if curr_seconds > last_seconds:
                clean_tracks.append({'timestamp': timestamp, 'title': song_title})
                last_seconds = curr_seconds
            else:
                break
                
    return clean_tracks

def extract_setlist_comments(video_id):
    video_url = "https://www.youtube.com/watch?v={0}".format(video_id)
    downloader = YoutubeCommentDownloader()
    comments = downloader.get_comments_from_url(video_url, sort_by=SORT_BY_RECENT)
    found_setlists = []
    for comment in comments:
        text = comment.get('text', '')
        clean_tracks = extract_clean_setlist(text)
        if len(clean_tracks) >= 3:
            found_setlists.append({'author': comment.get('author'),
                                   'votes': comment.get('votes', 0),
                                   'tracks': clean_tracks,
                                   'raw_text': text,
                                   'video_id': video_id})
    # 如果有符合條件的留言，挑選按讚數最高的
    if found_setlists:
        best_setlist = max(found_setlists, key=lambda x: int(x['votes'] or 0))
        best_setlist.pop('votes', None)
        return best_setlist
    return {'video_id': video_id, 'tracks': None}

def get_playlist_videos(playlist_url):
    ydl_opts = {'extract_flat': True,
                'skip_download': True,
                'quiet': True,
                'ignoreerrors': True}
    video_list = []
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        print("正在抓取播放清單資訊...")
        info = ydl.extract_info(playlist_url, download=False)
        if 'entries' in info:
            entries = [e for e in info['entries'] if e is not None]
            for entry in entries:
                title = entry.get('title')
                video_id = entry.get('id')
                video_list.append({'title': title, 'video_id': video_id})
    return video_list

# ---------------- 執行區 ----------------
def main():
    results = []
    playlist_url = 'https://www.youtube.com/playlist?list=PLTUPXbT5Ni8zmczjbAriHiGYeJAPxoT8g'
    videos = get_playlist_videos(playlist_url)
    for video in tqdm(videos):
        video_id = video['video_id']
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
    # 儲存為 JSON
    json_filename = 'youtube_setlists.json'
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump(final_results, f, ensure_ascii=False)
    print(f"\n已順利將結果儲存至 `{json_filename}`")
if __name__ == '__main__':
    main()