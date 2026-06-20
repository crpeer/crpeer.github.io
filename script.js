/**
 * 函数名称: openModal
 * 功能描述: 控制全局模态框组件的激活状态，并调度异步渲染引擎提取云端静态 JSON 数据。
 * 输入参数: {string} type - 核心业务标识符 ('gs' 代表原神, 'ak' 代表明日方舟)
 */
async function openModal(type) {
    // 状态初始化：隐藏所有特定游戏数据视窗，激活高层级模态框
    viewGs.style.display = 'none';
    viewAk.style.display = 'none';
    modal.classList.add('active');

    if (type === 'gs') {
        viewGs.style.display = 'block';
        try {
            // 缓存穿透策略：追加动态毫秒级时间戳，强制浏览器与 CDN 节点刷新文件流缓存
            const response = await fetch('data.json?timestamp=' + Date.now());
            if (!response.ok) {
                throw new Error(`网络通讯异常，远端 HTTP 状态码返回: ${response.status}`);
            }
            
            const data = await response.json();
            console.log("[系统日志] 成功读取远端数据集:", data);

            // 1. 基础战绩指标解析（严格映射 data.json 中的 stats 嵌套命名空间）
            if (data && data.stats) {
                document.getElementById('gs-days').innerText = data.stats.active_day_number ?? '--';
                document.getElementById('gs-abyss').innerText = data.stats.spiral_abyss ?? '--';
                document.getElementById('gs-achieve').innerText = data.stats.achievement_number ?? '--';
                document.getElementById('gs-chars').innerText = data.stats.avatar_number ?? '--';
            } else {
                console.warn("[数据警告] 未能在 JSON 中检索到 'stats' 节点");
            }

            // 2. 实时便签指标解析（严格映射 data.json 中的 daily_note 嵌套命名空间）
            if (data && data.daily_note) {
                const currentResinValue = data.daily_note.current_resin ?? '--';
                const maxResinValue = data.daily_note.max_resin ?? 160;
                document.getElementById('gs-resin').innerText = `${currentResinValue} / ${maxResinValue}`;
                
                document.getElementById('gs-coin').innerText = data.daily_note.current_home_coin ?? '--';
                document.getElementById('gs-task').innerText = data.daily_note.remain_task_num ?? '--';
                document.getElementById('gs-expedition').innerText = data.daily_note.current_expedition_num ?? '--';
            } else {
                console.warn("[数据警告] 未能在 JSON 中检索到 'daily_note' 节点");
            }

        } catch (error) {
            console.error("[渲染引擎拦截] 解析核心数据流 data.json 时捕获阻断性突发异常。详细堆栈:", error);
            
            // 系统级异常降级处理：全量脱敏相关 DOM 节点，避免页面暴露破碎信息
            const fallbackDomIDs = ['gs-days', 'gs-abyss', 'gs-achieve', 'gs-chars', 'gs-resin', 'gs-coin', 'gs-task', 'gs-expedition'];
            fallbackDomIDs.forEach(targetID => {
                const domNode = document.getElementById(targetID);
                if (domNode) domNode.innerText = '--';
            });
        }
    } else if (type === 'ak') {
        viewAk.style.display = 'block';
    }
}