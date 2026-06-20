// script.js
document.addEventListener('DOMContentLoaded', () => {
    fetch('data.json?t=' + new Date().getTime()) // 加上时间戳防缓存
        .then(response => response.json())
        .then(data => {
            console.log("数据加载成功:", data);

            // 1. 映射 stats (战绩)
            document.getElementById('gs-days').innerText = data.stats.active_day_number;
            document.getElementById('gs-abyss').innerText = data.stats.spiral_abyss;
            document.getElementById('gs-achieve').innerText = data.stats.achievement_number;
            document.getElementById('gs-chars').innerText = data.stats.avatar_number;

            // 2. 映射 daily_note (实时便笺)
            document.getElementById('gs-resin').innerText = `${data.daily_note.current_resin} / ${data.daily_note.max_resin}`;
            document.getElementById('gs-coin').innerText = `${data.daily_note.current_home_coin} / ${data.daily_note.max_home_coin}`;
            document.getElementById('gs-task').innerText = data.daily_note.remain_task_num;
            document.getElementById('gs-expedition').innerText = `${data.daily_note.current_expedition_num} / ${data.daily_note.max_expedition_num}`;
            
            // 3. 更新同步状态
            document.getElementById('sync-status').innerText = "云端已同步";
            document.getElementById('sync-status').style.color = "#22c55e"; // 绿色表示成功
        })
        .catch(err => {
            console.error("数据抓取失败:", err);
            document.getElementById('sync-status').innerText = "云端同步失败";
            document.getElementById('sync-status').style.color = "#ef4444";
        });
});

// 保持你原有的 Modal 逻辑
function openModal(type) {
    document.getElementById('global-modal').style.display = 'flex';
    if (type === 'gs') {
        document.getElementById('view-gs').style.display = 'block';
        document.getElementById('view-ak').style.display = 'none';
    } else if (type === 'ak') {
        document.getElementById('view-ak').style.display = 'block';
        document.getElementById('view-gs').style.display = 'none';
    }
}

function closeModal() {
    document.getElementById('global-modal').style.display = 'none';
}