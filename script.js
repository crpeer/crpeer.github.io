document.addEventListener('DOMContentLoaded', () => {
    // 1. 获取游戏数据
    fetch('data.json?t=' + new Date().getTime())
        .then(response => response.json())
        .then(data => {
            document.getElementById('gs-days').innerText = data.stats.active_day_number;
            document.getElementById('gs-abyss').innerText = data.stats.spiral_abyss;
            document.getElementById('gs-achieve').innerText = data.stats.achievement_number;
            document.getElementById('gs-chars').innerText = data.stats.avatar_number;
            
            document.getElementById('gs-resin').innerText = `${data.daily_note.current_resin} / ${data.daily_note.max_resin}`;
            document.getElementById('gs-coin').innerText = `${data.daily_note.current_home_coin} / ${data.daily_note.max_home_coin}`;
            document.getElementById('gs-task').innerText = data.daily_note.remain_task_num;
            document.getElementById('gs-expedition').innerText = `${data.daily_note.current_expedition_num} / ${data.daily_note.max_expedition_num}`;
            
            document.getElementById('sync-status').innerText = "云端已同步";
        })
        .catch(err => console.error("数据加载失败"));

    // 2. 获取资讯列表
    fetch('news.json?t=' + new Date().getTime())
        .then(response => response.json())
        .then(newsList => {
            const newsBox = document.getElementById('news-box');
            newsBox.innerHTML = '';
            newsList.forEach(item => {
                const div = document.createElement('div');
                div.className = 'news-card-real';
                div.innerHTML = `<div class="news-title">${item.title}</div>`;
                newsBox.appendChild(div);
            });
        })
        .catch(() => {
            document.getElementById('news-box').innerHTML = '<div class="news-card-real"><div class="news-title">资讯服务暂不可用</div></div>';
        });
});

function openModal(type) {
    document.getElementById('global-modal').style.display = 'flex';
    document.getElementById('view-gs').style.display = (type === 'gs') ? 'block' : 'none';
    document.getElementById('view-ak').style.display = (type === 'ak') ? 'block' : 'none';
}

function closeModal() {
    document.getElementById('global-modal').style.display = 'none';
}