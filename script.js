document.addEventListener('DOMContentLoaded', () => {
    // 1. 【功能一】自动加载实时资讯
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

    // 2. 【功能二】预加载原神实时数据
    window.genshinData = null;
    
    loadGenshinData();
});

// 从 data.json 加载实时数据
function loadGenshinData() {
    fetch('data.json?t=' + new Date().getTime())
        .then(response => response.json())
        .then(data => {
            window.genshinData = data;
            console.log("✅ 原神实时数据加载成功:", data);
            updateGenshinDisplay(data);
        })
        .catch(err => {
            console.error("❌ 数据加载失败", err);
        });
}

// 更新显示的数据
function updateGenshinDisplay(data) {
    try {
        if (document.getElementById('gs-days')) {
            document.getElementById('gs-days').innerText = data.stats.active_day_number || '--';
            document.getElementById('gs-abyss').innerText = data.stats.spiral_abyss || '--';
            document.getElementById('gs-achieve').innerText = data.stats.achievement_number || '--';
            document.getElementById('gs-chars').innerText = data.stats.avatar_number || '--';
        }
        
        if (document.getElementById('gs-resin')) {
            const resin = data.daily_note;
            document.getElementById('gs-resin').innerText = (resin.current_resin || 0) + ' / ' + (resin.max_resin || 200);
            document.getElementById('gs-coin').innerText = resin.current_home_coin || 0;
            document.getElementById('gs-task').innerText = resin.remain_task_num || 0;
            document.getElementById('gs-expedition').innerText = (resin.current_expedition_num || 0) + ' / ' + (resin.max_expedition_num || 5);
        }
    } catch (err) {
        console.error("❌ 更新显示数据失败:", err);
    }
}

// 3. 【功能三】点击头像打开详情页
function openModal(type) {
    console.log("🔔 点击了按钮，type:", type);
    
    const modal = document.getElementById('global-modal');
    if (!modal) {
        console.error("❌ 找不到 modal 元素!");
        return;
    }
    
    if (type === 'gs') {
        console.log("🎮 准备显示原神数据...");
        document.getElementById('view-gs').style.display = 'block';
        document.getElementById('view-ak').style.display = 'none';
        
        // 确保显示最新数据
        if (window.genshinData) {
            console.log("✅ 显示预加载的原神数据");
            updateGenshinDisplay(window.genshinData);
        } else {
            console.log("⏳ 数据未预加载，正在加载...");
            loadGenshinData();
        }
        
    } else if (type === 'ak') {
        console.log("🦅 准备显示明日方舟数据...");
        document.getElementById('view-ak').style.display = 'block';
        document.getElementById('view-gs').style.display = 'none';
    }
    
    // 显示模态框
    modal.style.display = 'flex';
    console.log("✨ 模态框已显示");
}

function closeModal() {
    console.log("❌ 关闭模态框");
    const modal = document.getElementById('global-modal');
    if (modal) {
        modal.style.display = 'none';
    }
}
