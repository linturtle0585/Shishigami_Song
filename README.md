# 獅子神レオナ歌枠找歌系統
獅子神レオナ歌枠で歌ったの歌探すためのウェブサイト。 / 一個可以快速找到獅寶歌回唱過那些歌的網站。 / A website to find out the song which you want for ShishigamiReona's song.

## 專案說明
- [Demo網站](https://linturtle0585.github.io/Shishigami_Song/)

[獅子神レオナ](https://www.youtube.com/@Leona_Shishigami)是誰：是一名從2018年9月14日開始於YouTube活動的Vtuber，所屬業界團體Re:AcT。普通說話時有些咬舌頭的感覺，跟唱歌時的感覺形成較為極端的對比所以偶爾會被認為是兩個不同的人。主要以動漫曲和VOCALOID曲子為主，其中最為拿手的為敘事曲。

以上介紹來自[萌娘百科](https://zh.moegirl.org.cn/zh-tw/%E7%8B%AE%E5%AD%90%E7%A5%9E%E8%95%BE%E6%AC%A7%E5%A8%9C)

## 操作說明

### 1.「熱門歌曲排行榜」以文字雲形式展示了獅子神レオナ歷次歌回中唱過歌曲次數的統計，點選歌名可直接快速搜尋。

### 2.「歌曲搜尋」可以以模糊搜尋的方式尋找想要聽的曲目，點開歌曲的名稱可以看到有哪幾次歌回有唱到這首歌，可以點選右方的「播放」按鈕快速跳轉到Youtube來聽歌。

### 3.只是單純想放個音樂，但是沒有特別想聽的歌的時候，可以點選「我不知道要聽什麼」，會隨機挑選一首歌名顯示。

## 專案結構
```
Shishigami_Song/
    ├─ download_setlists.py             // 利用爬蟲API下載歌回清單內包含歌單時間軸的留言
    ├─ data_cleaning.py                 // 整理時間軸內的歌名
    ├─ index.js                         // 執行所需的JavaScript程式碼
    ├─ index.html                       // 主頁面
    ├─ shishigami_setlists.json         // 剛下載的原始資料
    ├─ shishigami_setlists_2.json       // 整理過後的歌單
    ├─ test.html                        // 測試用
    └─ README.md
```
