---
kind: frontend_style
name: 管理后台原生 CSS 主题与模板样式体系
category: frontend_style
scope:
    - '**'
source_files:
    - hushai/meditation/admin/static/css/admin.css
    - hushai/meditation/admin/templates/base.html
    - hushai/meditation/static/index.html
---

本仓库的前端样式集中在 hushai.meditation.admin 子模块，采用「Jinja2 模板 + 单文件原生 CSS」的轻量方案，未引入 Tailwind、Bootstrap 或任何 CSS-in-JS 框架。

1. 系统与方法论
- 样式组织：单一主样式表 admin.css（约 1800 行），通过 :root CSS 自定义属性集中定义设计令牌（颜色、阴影、圆角、过渡、字体族），形成“纸本档案”风格的设计系统。
- 模板渲染：所有页面继承 base.html，统一注入 Google Fonts（Fraunces / Plus Jakarta Sans / Noto Sans SC）、Font Awesome 6 图标库与 admin.css；各页面通过 {% block %} 扩展标题与内容区。
- 交互脚本：base.html 内置原生 JS 实现 Toast、Loading 遮罩、Modal 对话框、侧边栏折叠/分组、异步请求封装等通用 UI 行为，不依赖第三方前端框架。

2. 关键文件
- hushai/meditation/admin/static/css/admin.css：全局样式与设计令牌中心
- hushai/meditation/admin/templates/base.html：布局骨架、资源注入与通用交互脚本
- hushai/meditation/admin/templates/*.html：业务页面模板（仪表盘、用户、对话、记忆、知识库、技能、场景、审计日志、设置、咨询看板、咨询师、预约、订单等）
- hushai/meditation/static/index.html：冥想入口页（内联大量样式，独立于 admin 主题）
- knowledge/open-cognition/visualization/*.html：知识可视化报告页，各自内嵌 @import 字体与独立样式，不属于 admin 主题体系

3. 架构与约定
- 设计令牌：以 --primary/--accent/--bg-* 等变量统一品牌色、背景层级、文本色、边框与阴影；圆角 --radius-sm/--radius/--radius-lg 与过渡 --transition 贯穿全栈组件。
- 组件类名：使用语义化 BEM 风格前缀（如 .card/.card-header/.card-body、.stat-card、.quick-action-card、.data-table、.badge-*、.btn-*、.toast-*、.modal-*、.sidebar.collapsed 等），在模板中直接复用。
- 响应式策略：仅通过一个 @media (max-width: 768px) 断点处理移动端布局（侧边栏变顶栏、网格单列、表格横向滚动）。
- 字体与图标：Google Fonts 预连接加载 Fraunces（展示标题）+ Plus Jakarta Sans/Noto Sans SC（UI 正文）；图标统一 Font Awesome 6 的 <i class="fas ..."> 形式。
- 静态资源路径：admin 下资源通过 /admin/static/... 暴露，base.html 中以绝对路径引用 favicon.svg 与 admin.css。

4. 开发者应遵循的规则
- 新增颜色/尺寸/字体时优先修改 :root 中的 CSS 变量，禁止在组件类中硬编码具体值。
- 复用已有组件类（.card/.btn/.badge/.form-control/.toast/*/.modal/* 等），避免为相似 UI 新建重复类。
- 模板只负责结构块与数据绑定，不要在内联 style 中写样式；如需页面级微调，使用 {% block extra_css %} 追加。
- 交互逻辑优先使用 base.html 提供的 window.showToast/showLoading/showModal/asyncRequest 等 API，保持全局一致的用户反馈体验。
- 图标一律使用 Font Awesome 6 的 fas/fa-solid 类名，不在 HTML 中手写 SVG。
- 新增页面需继承 base.html，并在 title/page_title/breadcrumb/content 块中填充内容，确保侧边栏导航与面包屑一致性。
- 响应式改动仅在现有 768px 断点基础上扩展，避免引入新的断点破坏整体布局节奏。
- 知识可视化目录下的 *.html 是独立报告产物，不与 admin 主题共享样式，不应在其中引用 admin.css。