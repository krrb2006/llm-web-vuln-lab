# B 第二轮迭代 DeepSeek V2 提交清单

V2 针对 V0/V1 真实残留问题补充了更严格的 POC 断言、localhost 目标限制、重定向和存储型 XSS 数据清理/浏览器触发要求。每条 V2 输入的 `code_input` SHA-256 与 V0/V1 相同；只改变 Prompt。使用 DeepSeek-V4.1-Flash，深度思考开启，联网搜索关闭；每条新开独立会话，保存完整首轮回答和真实提交时间。

|样本|run_id|输入|
|---|---|---|
|S001—S006|`DEV_S001_V2_R1`—`DEV_S006_V2_R1`|各运行目录下的 `input.txt`|
|S013—S018|`DEV_S013_V2_R1`—`DEV_S018_V2_R1`|各运行目录下的 `input.txt`|

V2 Prompt 候选哈希：SQLi `8f2fcafb576e990d1ef27527ce558830558fb87ea189ab32d8c10514e9c620ca`；XSS `3666ebeb28980e192172852639ab1759c94b6cbb2e5cdfe0c6f185a946841178`。这些是候选哈希，不是最终冻结值。V2 原文全部归档和人工复核前，不启动正式 36 条。
