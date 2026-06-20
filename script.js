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

    // 2. 【功能二】预加载基础状态 (你可以把原本写在 modal 里的 fetch 放在这里)
    // 这里保持你原来获取 data.json 的逻辑
    fetch('data.json?t=' + new Date().getTime())
        .then(response => response.json())
        .then(data => {
            // 这里填写你原有的基础数据更新逻辑
            document.getElementById('gs-days').innerText = data.stats.active_day_number;
            document.getElementById('gs-abyss').innerText = data.stats.spiral_abyss;
            // ... 其他基础数据
        })
        .catch(err => console.error("基础数据加载失败"));
});

// 3. 【功能三】点击头像触发详细数据 (这里执行你的 Cookie 逻辑)
function openModal(type) {
    document.getElementById('global-modal').style.display = 'flex';
    
    if (type === 'gs') {
        document.getElementById('view-gs').style.display = 'block';
        document.getElementById('view-ak').style.display = 'none';
        
        // --- 请在这里放入你之前配置的【获取米游社详细数据】的 fetch 逻辑 ---
        console.log("正在尝试通过 Cookie 获取米游社详细详情...");
        // fetch('你的米游社API_URL', { headers: { 'Cookie': '...' } }) ...
        
    } else if (type === 'ak') {
        document.getElementById('view-ak').style.display = 'block';
        document.getElementById('view-gs').style.display = 'none';
    }
}

function closeModal() {
    document.getElementById('global-modal').style.display = 'none';
}