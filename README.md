# 工程电路与实验设计笔记

本仓库用于记录本人在 **模拟电路 / 仪表放大器 / 电流源 / 接口保护** 等工程实践中的
设计思路、选型分析和实际问题总结。

内容以 **工程实用** 和 **教学可复现** 为目标，主要面向：
- 自动化 / 电子相关专业学生
- 实验课程与工程实践
- 实际产品电路设计参考

---

## 📌 如何阅读本仓库（重要）

如果你是第一次打开，**建议按下面顺序阅读**：

1. 👉 **接口与保护类**
   - [模拟输入接口 TVS 保护设计](docs/tvs.md)
   - [INA141 输入 / 输出保护分析](docs/ina141.md)

2. 👉 **电流源与功率运放**
   - [OPA549 大电流源设计与应用](docs/opa549.md)
   - [恒流源精度与量程分析](docs/current_source.md)

3. 👉 **实验与工程经验**
   - [常见错误与踩坑记录](docs/mistakes.md)

---

原始文档来源：  
- [GitHub 仓库主页](https://github.com/username/my_repo)  
- [查看本文件原文](https://github.com/username/my_repo/blob/main/interface/tvs.md)


## 📂 目录结构说明

```text
.
├── README.md        # 仓库总说明（你正在看的这个）
├── docs/            # 主要技术文档（Markdown）
│   ├── tvs.md
│   ├── ina141.md
│   ├── opa549.md
│   └── current_source.md
└── images/          # 文档中引用的图片、波形、示意图
允许保留“工程妥协”和“非最优方案”的讨论

