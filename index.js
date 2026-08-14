    const JSON_FILE_PATH = './shishigami_setlists_2.json';
    let globalSongMap = {}; // 存儲彙整後的歌曲資料
    // 清理歌名（去除時間戳記與特殊空白）
    function cleanTitle(title) {
      if (!title) return "";
      return title
        .replace(/\d{1,2}:\d{2}/g, '')
        .replace(/[\u200B-\u200D\uFEFF]/g, '')
        .trim();
    }
    // 將時間格式 (HH:MM:SS 或 MM:SS) 轉換為總秒數 (以利 YouTube ?t=秒數 播放)
    function timeToSeconds(timeStr) {
      if (!timeStr) return 0;
      const clean = timeStr.replace(/[^0-9:]/g, '');
      const parts = clean.split(':').map(Number);
      if (parts.length === 3) {
        return parts[0] * 3600 + parts[1] * 60 + parts[2];
      } else if (parts.length === 2) {
        return parts[0] * 60 + parts[1];
      }
      return 0;
    }
    // 載入 JSON 資料
    async function loadData() {
      try {
        const response = await fetch(JSON_FILE_PATH);
        if (!response.ok) { throw new Error(`HTTP 錯誤！狀態碼: ${response.status}`); }
        const rawStreams = await response.json();
        initDashboard(rawStreams);
      } catch (error) { console.error('無法讀取 JSON 資料:', error); }
    }
    // 初始化儀表板
    function initDashboard(rawStreams) {
      globalSongMap = {};
      let totalTrackCount = 0;
      // 整理並索引資料
      rawStreams.forEach(stream => {
        const streamTitle = stream.title || "未知直播標題";
        const videoId = stream.video_id || "";
        if (stream.tracks && Array.isArray(stream.tracks)) {
          stream.tracks.forEach(track => {
            const title = cleanTitle(track.title);
            if (title && title !== "🎸") {
              if (!globalSongMap[title]) {
                globalSongMap[title] = {
                  title: title,
                  count: 0,
                  occurrences: []
                };
              }
              const seconds = timeToSeconds(track.timestamp);
              globalSongMap[title].count++;
              globalSongMap[title].occurrences.push({
                streamTitle: streamTitle,
                videoId: videoId,
                timestamp: track.timestamp,
                seconds: seconds
              });
              totalTrackCount++;
            }
          });
        }
      });
      const sortedSongs = Object.values(globalSongMap).sort((a, b) => b.count - a.count); // 轉換為陣列並按次數降序排序
      renderWordCloud(sortedSongs); // 繪製文字雲
      renderSongSearchList([], false); // 初始狀態不顯示歌曲列表
      // 搜尋事件監聽（去除所有半角/全角空格比對）
      const searchInput = document.getElementById('searchInput');
      searchInput.addEventListener('input', (e) => {
        const rawKeyword = e.target.value;
        const cleanKeyword = rawKeyword.toLowerCase().replace(/[\s\u3000]+/g, '');
        if (!cleanKeyword) {
          renderSongSearchList([], false);
          return;
        }
        const filtered = sortedSongs.filter(song => {
          const cleanSongTitle = song.title.toLowerCase().replace(/[\s\u3000]+/g, '');
          return cleanSongTitle.includes(cleanKeyword);
        });
        renderSongSearchList(filtered, true);
      });
      // 「我感覺幸運」按鈕獨立事件監聽
      document.getElementById('luckyBtn').addEventListener('click', () => {
        if (sortedSongs.length === 0) return;
        const totalWeight = sortedSongs.reduce((sum, song) => sum + song.count, 0); // 計算所有歌曲的總演唱次數
        let randomWeight = Math.random() * totalWeight; // 產生 0 到 totalWeight 之間的隨機數
        // 依據權重遞減尋找目標歌曲
        let randomSong = sortedSongs[0];
        for (const song of sortedSongs) {
          if (randomWeight < song.count) {
            randomSong = song;
            break;
          }
          randomWeight -= song.count;
        }
        // 套用搜尋與捲動
        searchInput.value = randomSong.title;
        searchInput.dispatchEvent(new Event('input'));
        document.getElementById('songListContainer').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });
    }
    // 繪製文字雲
    function renderWordCloud(songs) {
      const canvas = document.getElementById('wordCloudCanvas');
      const tooltip = document.getElementById('tooltip');
      const container = canvas.parentElement;
      canvas.width = container.clientWidth;
      canvas.height = container.clientHeight;
      const listData = songs.slice(0, 100).map(item => [item.title, item.count]);
      const colors = ['#f59e0b', '#38bdf8', '#34d399', '#f43f5e', '#a78bfa', '#fbbf24', '#f472b6'];
      WordCloud(canvas, {
        list: listData,
        gridSize: 12,
        weightFactor: function (size) {
          const maxCount = songs[0] ? songs[0].count : 1;
          return Math.max(14, (size / maxCount) * 50 + 10);
        },
        fontFamily: 'sans-serif',
        color: function () {
          return colors[Math.floor(Math.random() * colors.length)];
        },
        rotateRatio: 0.15,
        backgroundColor: 'transparent',
        hover: function (item, dimension, event) {
          if (item) {
            canvas.style.cursor = 'pointer';
            tooltip.classList.remove('d-none');
            tooltip.innerText = `${item[0]}：${item[1]}次`;
            const rect = container.getBoundingClientRect();
            const x = event.clientX - rect.left;
            const y = event.clientY - rect.top;
            tooltip.style.left = `${x + 15}px`;
            tooltip.style.top = `${y + 15}px`;
          } else {
            canvas.style.cursor = 'default';
            tooltip.classList.add('d-none');
          }
        },
        click: function (item) {
          if (item) {
            const searchInput = document.getElementById('searchInput');
            searchInput.value = item[0];
            searchInput.dispatchEvent(new Event('input'));
            searchInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }
      });
    }
    // 渲染歌曲搜尋與展開式列表
    function renderSongSearchList(songs, isSearching = true) {
      const container = document.getElementById('songListContainer');
      container.innerHTML = '';
      if (!isSearching) {
        container.innerHTML = `<div class="text-center py-5 text-secondary">請輸入歌曲名稱進行搜尋</div>`;
        return;
      }
      if (songs.length === 0) {
        container.innerHTML = `<div class="text-center py-5 text-secondary">找不到符合條件的歌曲</div>`;
        return;
      }
      songs.forEach((song, index) => {
        const card = document.createElement('div');
        card.className = 'card bg-dark border-secondary overflow-hidden flex-shrink-0';
        // 卡片標題區 (點擊展開/收合)
        const header = document.createElement('div');
        header.className = 'card-header bg-dark text-light border-secondary p-3 d-flex align-items-center justify-content-between cursor-pointer user-select-none';
        header.style.cursor = 'pointer';
        header.innerHTML = `
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-secondary text-light font-monospace">${index + 1}</span>
            <span class="fw-bold text-light fs-6">${song.title}</span>
          </div>
          <div class="d-flex align-items-center gap-2">
            <span class="badge bg-warning-subtle text-warning border border-warning-subtle px-2 py-1">
              ${song.count} 次
            </span>
            <span class="text-secondary small arrow-icon transition-transform">▼</span>
          </div>
        `;
        // 展開內容區 (預設隱藏)
        const content = document.createElement('div');
        content.className = 'card-body bg-black bg-opacity-25 border-top border-secondary p-3 d-none vstack gap-2';
        // 填入該歌曲出現過的所有直播細節
        song.occurrences.forEach(occ => {
          const ytUrl = `https://youtu.be/${occ.videoId}?t=${occ.seconds}`;
          const item = document.createElement('div');
          item.className = 'd-flex flex-column flex-sm-row align-items-sm-center justify-content-between gap-2 p-2 bg-dark border border-secondary rounded';
          item.innerHTML = `
            <div class="text-light small text-truncate" style="max-width: 600px;" title="${occ.streamTitle}">
              ${occ.streamTitle}
            </div>
            <a href="${ytUrl}" target="_blank" rel="noopener noreferrer" 
               class="btn btn-outline-warning btn-sm text-nowrap shrink-0 d-inline-flex align-items-center gap-1 ms-auto ms-sm-0">
               <span>${occ.timestamp}</span>
               <span>▶ 播放</span>
            </a>
          `;
          content.appendChild(item);
        });
        // 點擊事件：切換展開/收合狀態
        header.addEventListener('click', () => {
          const isHidden = content.classList.contains('d-none');
          const arrow = header.querySelector('.arrow-icon');
          if (isHidden) {
            content.classList.remove('d-none');
            arrow.style.transform = 'rotate(180deg)';
          } else {
            content.classList.add('d-none');
            arrow.style.transform = 'rotate(0deg)';
          }
        });
        card.appendChild(header);
        card.appendChild(content);
        container.appendChild(card);
      });
    }
    window.addEventListener('DOMContentLoaded', loadData);