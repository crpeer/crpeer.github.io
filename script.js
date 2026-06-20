// 假设你网页对应的ID是 gs-days, gs-resin 等
fetch('data.json')
    .then(response => response.json())
    .then(data => {
        document.getElementById('gs-days').innerText = data.days || '--';
        document.getElementById('gs-abyss').innerText = data.abyss || '--';
        document.getElementById('gs-achieve').innerText = data.achievements || '--';
        document.getElementById('gs-chars').innerText = data.characters || '--';
        
        document.getElementById('gs-resin').innerText = `${data.resin} / ${data.max_resin}`;
        document.getElementById('gs-coin').innerText = data.coin;
        document.getElementById('gs-task').innerText = data.task;
        document.getElementById('gs-expedition').innerText = data.expeditions;
    })
    .catch(err => console.error('数据加载失败:', err));