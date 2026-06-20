document.addEventListener('DOMContentLoaded', () => {
    // 1. 【功能一】自动加载实时资讯 (无需任何维护，自动在线)
    const rssUrl = "https://www.gcores.com/rss";
    const api = `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(rssUrl)}`;

    fetch(api)
        .then(response => response.json())
        .then(data => {
            const newsBox = document.getElementById('news-box');
            newsBox.innerHTML = ''; 
            const items = data.items.slice(0, 3);
            items.forEach(item => {
                const div = document.createElement('div');
                div.className = 'news-card-real';
                div.innerHTML = `<a href="${item.link}" target="_blank" style="text-decoration:none; color:inherit;"><div class="news-title">${item.title}</div></a>`;
                newsBox.appendChild(div);
            });
        })
        .catch(err => {
            document.getElementById('news-box').innerHTML = '<div class="news-card-real"><div class="news-title">资讯服务暂不可用</div></div>';
        });

    // 2. 【功能二】预加载基础状态
    // 初始化全局数据变量
    window.genshinData = null;
    
    fetch('data.json?t=' + new Date().getTime())
        .then(response => response.json())
        .then(data => {
            window.genshinData = data;
            // 更新页面上的基础数据
            document.getElementById('gs-days').innerText = data.stats.active_day_number;
            document.getElementById('gs-abyss').innerText = data.stats.spiral_abyss;
            document.getElementById('gs-achieve').innerText = data.stats.achievement_number;
            document.getElementById('gs-chars').innerText = data.stats.avatar_number;
            document.getElementById('gs-resin').innerText = data.daily_note.current_resin + ' / ' + data.daily_note.max_resin;
            document.getElementById('gs-coin').innerText = data.daily_note.current_home_coin;
            document.getElementById('gs-task').innerText = data.daily_note.remain_task_num;
            document.getElementById('gs-expedition').innerText = data.daily_note.current_expedition_num + ' / ' + data.daily_note.max_expedition_num;
        })
        .catch(err => console.error("基础数据加载失败", err));
});

// 3. 【功能三】点击头像触发详细数据
function openModal(type) {
    document.getElementById('global-modal').style.display = 'flex';
    
    if (type === 'gs') {
        document.getElementById('view-gs').style.display = 'block';
        document.getElementById('view-ak').style.display = 'none';
        
        // 从预加载的数据更新模态框内容
        if (window.genshinData) {
            const data = window.genshinData;
            document.getElementById('gs-days').innerText = data.stats.active_day_number;
            document.getElementById('gs-abyss').innerText = data.stats.spiral_abyss;
            document.getElementById('gs-achieve').innerText = data.stats.achievement_number;
            document.getElementById('gs-chars').innerText = data.stats.avatar_number;
            document.getElementById('gs-resin').innerText = data.daily_note.current_resin + ' / ' + data.daily_note.max_resin;
            document.getElementById('gs-coin').innerText = data.daily_note.current_home_coin;
            document.getElementById('gs-task').innerText = data.daily_note.remain_task_num;
            document.getElementById('gs-expedition').innerText = data.daily_note.current_expedition_num + ' / ' + data.daily_note.max_expedition_num;
        } else {
            console.log("正在加载原神数据...");
            // 如果预加载失败，尝试再加载一次
            fetch('data.json?t=' + new Date().getTime())
                .then(response => response.json())
                .then(data => {
                    window.genshinData = data;
                    document.getElementById('gs-days').innerText = data.stats.active_day_number;
                    document.getElementById('gs-abyss').innerText = data.stats.spiral_abyss;
                    document.getElementById('gs-achieve').innerText = data.stats.achievement_number;
                    document.getElementById('gs-chars').innerText = data.stats.avatar_number;
                    document.getElementById('gs-resin').innerText = data.daily_note.current_resin + ' / ' + data.daily_note.max_resin;
                    document.getElementById('gs-coin').innerText = data.daily_note.current_home_coin;
                    document.getElementById('gs-task').innerText = data.daily_note.remain_task_num;
                    document.getElementById('gs-expedition').innerText = data.daily_note.current_expedition_num + ' / ' + data.daily_note.max_expedition_num;
                })
                .catch(err => console.error("数据加载失败", err));
        }
        
    } else if (type === 'ak') {
        document.getElementById('view-ak').style.display = 'block';
        document.getElementById('view-gs').style.display = 'none';
    }
}

function closeModal() {
    document.getElementById('global-modal').style.display = 'none';
}