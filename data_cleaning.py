import json
import re
from collections import Counter, defaultdict

json_filename = 'koyori_setlists'

def normalize_dashes(s):
    """將所有特殊 Unicode 連字號、破折號與全形減號統一替換為標準 ASCII '-' (\u002d)"""
    return re.sub(r'[\u2010-\u2015\u2212\uff0d]', '-', s)

def normalize_base(s):
    """連字號統一 + 全形 !/? 轉半形 + 轉小寫"""
    s = normalize_dashes(s)
    s = s.replace('！', '!').replace('？', '?')
    return s.lower()

def unify_titles(data, key_func, tag_name):
    """依據 key_func 分組，將同組內的非主流寫法統一為出現次數最多的版本"""
    title_counts = Counter(track["title"]
                           for item in data if item.get("tracks")
                           for track in item["tracks"]
                           if track.get("title"))
    groups = defaultdict(list)
    for title in title_counts.keys():
        groups[key_func(title)].append(title)
    mapping = {}
    for norm_key, variants in groups.items():
        if len(variants) > 1:
            best_variant = max(variants, key=lambda x: (title_counts[x], x))
            for v in variants:
                if v != best_variant:
                    mapping[v] = best_variant
                    print(f"[{tag_name}] '{v}' (出現 {title_counts[v]} 次) -> '{best_variant}' (出現 {title_counts[best_variant]} 次)")
    if mapping:
        for item in data:
            if item.get("tracks"):
                for track in item["tracks"]:
                    if track.get("title") in mapping:
                        track["title"] = mapping[track["title"]]
    else:
        print(f"未發現需要修正的 [{tag_name}] 歌名。")

def trim_hyphenated_titles(data, min_prefix_count=2):
    """含 '-' 且 '-' 前的主歌名獨立出現 >= min_prefix_count 次者，裁切 '-' 及後方文字"""
    counts = Counter(t["title"]
                     for item in data
                     for t in item.get("tracks", [])
                     if t.get("title"))
    hyphen_modified = False
    for item in data:
        for t in item.get("tracks", []):
            title = t.get("title", "")
            if "-" in title:
                prefix = title.split("-", 1)[0]
                if counts.get(prefix, 0) >= min_prefix_count:
                    t["title"] = prefix
                    hyphen_modified = True
                    print(f"[含歌手/副標題修正] '{title}' -> '{prefix}' (主歌名 '{prefix}' 獨立出現過 {counts[prefix]} 次)")
    if not hyphen_modified:
        print("未發現符合裁切條件的 '-' 歌名。")

def remove_parentheses_key(s):
    """括號清洗 key：先基礎規格化，再剝離外層或內含括號與註解文字"""
    s_norm = normalize_base(s)
    if re.match(r'^[（\(][^（\(\)）]+[）\)]$', s_norm):
        s_norm = s_norm[1:-1]
    cleaned = re.sub(r'[（\(].*?[）\)]', '', s_norm)
    return cleaned if cleaned else s_norm

def trim_affix_symbols(data, min_count=1):
    """歷遍歌名，若僅頭尾符號/長音號不同，統一為出現次數最多的版本"""
    def strip_env_symbols_key(s):
        s_norm = normalize_base(s)
        # 匹配頭尾符號 (這裡保留中間的 '-' 避免把單字中間的連字線刪掉)
        symbol_pattern = r'^[\W_ー〜～~]+|[\W_ー〜～~]+$'
        cleaned = re.sub(symbol_pattern, '', s_norm)
        return cleaned if cleaned else s_norm
    unify_titles(data, key_func=strip_env_symbols_key, tag_name="頭尾符號修正")

# ==================== 主程式流程 ====================
with open(json_filename + '.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for item in data:
    if item.get("tracks"):
        new_tracks = []
        for track in item["tracks"]:
            if "title" in track and track["title"]:
                title = track["title"]
                title = normalize_dashes(title) # 先將所有特殊 Unicode 連字號轉為標準 '-'
                # 斜線拆分：若斜線後字數 < 斜線前字數的 3 倍才保留前面，否則保持原歌名
                if len(parts := re.split(r'[/／]', title, 1)) == 2 and len(parts[1]) < 3 * len(parts[0]):
                    title = parts[0]
                # 若遇到「」或【】，優先提取包起來的文字
                match = re.search(r"[「【](.*?)[」】]", title)
                if match:
                    title = match.group(1)
                # 移除 "." 前面的數字/空白前綴（如 "01." 或 " ."）
                if "." in title:
                    prefix = title.split(".", 1)[0]
                    if not prefix.strip() or prefix.strip().isdigit():
                        title = title.split(".", 1)[1]
                title = re.sub(r'\s+', '', title).replace("|", "") # 移除所有空白（包含全角空白與 \xa0）與 "|" 符號
                title = re.sub(r'[\U00010000-\U0010FFFF\u2600-\u27BF]', '', title) # 移除所有繪文字 (Emoji) 與特殊符號
                if title == "W":
                    title = "W/X/Y"
                if title == "開始" or "告知" in title:
                    continue
                track["title"] = title
            new_tracks.append(track)
        item["tracks"] = new_tracks

target_video = "【 歌枠】Happy Halloween、お菓子ちょうだい！50音順に歌おう～！🎃【獅子神レオナ/Re:AcT】"
for item in data:
    if item.get("title") == target_video:
        for t in item.get("tracks", []):
            if title := t.get("title"):
                t["title"] = title[1:]

unify_titles(data, key_func=normalize_base, tag_name="規格化修正") # 初步大小寫與標點全半形修正
# 副標題 (-) 與括號內容修剪
trim_hyphenated_titles(data, min_prefix_count=2)
unify_titles(data, key_func=remove_parentheses_key, tag_name="括號差修正")
trim_affix_symbols(data, min_count=1) # 頭尾符號修剪

with open(json_filename + '_2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n已順利將結果儲存至 `{json_filename}_2.json`")