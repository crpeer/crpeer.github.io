const modal = document.getElementById('global-modal');
const viewGs = document.getElementById('view-gs');
const viewAk = document.getElementById('view-ak');

// 🟢 控制模块开关与云端数据绑定
async function openModal(type) {
    viewGs.style.display = 'none';
    viewAk.style.display = 'none';
    modal.classList.add('active');

    if (type === 'gs') {
        viewGs.style.display = 'block';
        try {
            // 异步拉取 GitHub Actions 跑出来的静态 JSON 文件
            const response = await fetch('data.json');
            const data = await response.json();
            
            // 将数据精准填入对应的 DOM 节点
            document.getElementById('gs-days').innerText = data.days || '--';
            document.getElementById('gs-abyss').innerText = data.abyss || '--';
            document.getElementById('gs-achieve').innerText = data.achievements || '--';
            document.getElementById('gs-chars').innerText = data.characters || '--';
            document.getElementById('gs-resin').innerText = `${data.resin} / ${data.max_resin}`;
            document.getElementById('gs-coin').innerText = data.coin;
            document.getElementById('gs-task').innerText = data.task;
            document.getElementById('gs-expedition').innerText = data.expeditions;
        } catch (e) {
            console.error("未能成功同步云端 data.json 数据流，请检查 Actions 运行情况。");
        }
    } else if (type === 'ak') {
        viewAk.style.display = 'block';
    }
}

function closeModal() { 
    modal.classList.remove('active'); 
}

// 🌐 异步抓取机核网新鮮游戏新闻
async function fetchGcoresNews() {
    const newsBox = document.getElementById('news-box');
    try {
        const res = await fetch(`https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent('https://www.gcores.com/rss')}`);
        const data = await res.json();
        if (data.status === 'ok') {
            newsBox.innerHTML = data.items.slice(0, 4).map(item => `
                <a href="${item.link}" target="_blank" class="news-card-real">
                    <div class="news-date">📅 ${item.pubDate.split(' ')[0]}</div>
                    <div class="news-title">${item.title}</div>
                </a>
            `).join('');
            document.getElementById('sync-status').innerText = "数据已同步";
        }
    } catch (e) {
        newsBox.innerHTML = '<div class="news-card-real"><div class="news-title">资讯链路同步失败</div></div>';
    }
}

// 页面加载完成后自动获取新闻
window.addEventListener('DOMContentLoaded', fetchGcoresNews);