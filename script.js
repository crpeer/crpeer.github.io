/**
 * 函数名称: openModal
 * 功能描述: 控制全局模态框组件的激活状态，并调度异步渲染引擎提取云端静态 JSON 序列化数据。
 * 输入参数: {string} type - 核心业务标识符 (限定取值: 'gs' 代表原神, 'ak' 代表明日方舟)
 */
async function openModal(type) {
    // 状态初始化：全量隐蔽特定游戏数据视窗，重置高层级模态框激活态
    viewGs.style.display = 'none';
    viewAk.style.display = 'none';
    modal.classList.add('active');

    if (type === 'gs') {
        viewGs.style.display = 'block';
        try {
            // 缓存穿透策略：追加动态毫秒级时间戳尾巴，强制 CDN 节点与客户端更新文件流缓存
            const response = await fetch('data.json?timestamp=' + Date.now());
            if (!response.ok) {
                throw new Error(`网络通讯异常，远端 HTTP 状态码返回: ${response.status}`);
            }
            const dataset = await response.json();

            // 防御性数据管道：对历史嵌套结构与新版平铺结构进行解耦整合
            const statsPipeline = dataset.stats || dataset;
            const notePipeline = dataset.daily_note || dataset;

            // 1. 活跃天数、深境螺旋、成就、角色数量指标解析
            document.getElementById('gs-days').innerText = statsPipeline.active_day_number ?? dataset.days ?? '--';
            document.getElementById('gs-abyss').innerText = statsPipeline.spiral_abyss ?? dataset.abyss ?? '--';
            document.getElementById('gs-achieve').innerText = statsPipeline.achievement_number ?? dataset.achievements ?? '--';
            document.getElementById('gs-chars').innerText = statsPipeline.avatar_number ?? dataset.characters ?? '--';

            // 2. 原粹树脂实时便笺数据映射
            const currentResinValue = notePipeline.current_resin ?? dataset.resin;
            const maxResinValue = notePipeline.max_resin ?? dataset.max_resin ?? 200;
            document.getElementById('gs-resin').innerText = 
                (currentResinValue !== undefined) ? `${currentResinValue} / ${maxResinValue}` : '-- / --';

            // 3. 洞天财瓮累积数映射
            document.getElementById('gs-coin').innerText = notePipeline.current_home_coin ?? dataset.coin ?? '--';

            // 4. 每日委托剩余任务计算与安全回退机制
            if (notePipeline.remain_task_num !== undefined) {
                document.getElementById('gs-task').innerText = notePipeline.remain_task_num;
            } else if (notePipeline.finished_task_num !== undefined) {
                document.getElementById('gs-task').innerText = (notePipeline.total_task_num || 4) - notePipeline.finished_task_num;
            } else {
                document.getElementById('gs-task').innerText = dataset.task ?? '--';
            }

            // 5. 探索派遣完成状态映射
            if (notePipeline.current_expedition_num !== undefined) {
                document.getElementById('gs-expedition').innerText = `${notePipeline.current_expedition_num} / ${notePipeline.max_expedition_num || 5}`;
            } else {
                document.getElementById('gs-expedition').innerText = dataset.expeditions ?? '--';
            }

        } catch (error) {
            console.error("[渲染引擎拦截] 解析核心数据流 data.json 时捕获阻断性突发异常。详细堆栈:", error);
            
            // 系统级异常降级处理：全量脱敏相关 DOM 节点，避免页面暴露逻辑破碎信息
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