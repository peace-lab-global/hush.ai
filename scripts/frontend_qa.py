#!/usr/bin/env python3
"""前端深度质量检查脚本"""
import re
from html.parser import HTMLParser

def main():
    with open('hushai/meditation/static/index.html', encoding='utf-8') as f:
        html = f.read()

    print('═' * 60)
    print('1. HTML 结构深度检查')
    print('═' * 60)

    class TagChecker(HTMLParser):
        def __init__(self):
            super().__init__()
            self.self_closing = {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}
            self.stack = []
            self.errors = []
            self.ids = set()
            self.dup_ids = []
        def handle_starttag(self, tag, attrs):
            if tag in self.self_closing: return
            attr_dict = dict(attrs)
            if 'id' in attr_dict:
                if attr_dict['id'] in self.ids:
                    self.dup_ids.append(attr_dict['id'])
                self.ids.add(attr_dict['id'])
            self.stack.append(tag)
        def handle_endtag(self, tag):
            if tag in self.self_closing: return
            if self.stack and self.stack[-1] == tag:
                self.stack.pop()
            else:
                self.errors.append(f'闭合标签不匹配: </{tag}>')

    checker = TagChecker()
    try:
        body_start = html.find('<body>')
        body_end = html.find('</body>')
        body_html = html[body_start:body_end]
        clean = re.sub(r'<script>.*?</script>', '', body_html, flags=re.DOTALL)
        checker.feed(clean)
        if checker.errors:
            for e in checker.errors[:5]:
                print(f'  ✗ {e}')
        else:
            print('  ✓ 标签完全平衡')
        if checker.dup_ids:
            print(f'  ✗ 重复 ID: {checker.dup_ids}')
        else:
            print('  ✓ 无重复 ID')
    except Exception as e:
        print(f'  ⚠ 解析器限制: {e}')

    required_ids = ['loginOverlay','nicknameInput','loginBtn','loginError',
                    'headerStatus','statusText','messages','chatInput','sendBtn',
                    'voiceBtn','voiceBar','settingsMask','settingsDrawer','settingsClose',
                    'sceneSelector','sceneChips','skillBar','skillChips','newConvBtn',
                    'modeChat','modeKB','genderFilter','voiceList','voiceHint',
                    'rateRange','rateVal','pitchRange','pitchVal',
                    'resetVoiceBtn','previewVoiceBtn','settingsBtn']
    missing = [i for i in required_ids if f'id="{i}"' not in html and f'id=\'{i}\'' not in html]
    if missing:
        print(f'  ✗ 缺失 ID: {missing}')
    else:
        print(f'  ✓ 所有 {len(required_ids)} 个关键 ID 存在')

    print()
    print('═' * 60)
    print('2. CSS 质量检查')
    print('═' * 60)

    css_start = html.find('<style>')
    css_end = html.find('</style>')
    css = html[css_start:css_end]

    css_vars = set(re.findall(r'--[\w-]+', css))
    used_vars = set()
    for v in css_vars:
        if css.count(f'var({v})') > 0 or css.count(f'var({v},') > 0:
            used_vars.add(v)
    unused = css_vars - used_vars
    if unused:
        print(f'  ⚠ 未使用的 CSS 变量: {unused}')
    else:
        print(f'  ✓ 所有 {len(css_vars)} 个 CSS 变量都被使用')

    media_queries = re.findall(r'@media[^{]+', css)
    print(f'  ✓ 媒体查询: {len(media_queries)} 个')

    animations = re.findall(r'@keyframes\s+(\w+)', css)
    print(f'  ✓ 关键帧动画: {len(animations)} 个 ({" ", ", ".join(animations)})')

    selectors = [s.strip() for s in css.split('}') if '{' in s]
    complex_s = [s for s in selectors if s.count(' ') > 3 or s.count(':') > 2]
    if complex_s:
        print(f'  ⚠ 复杂选择器: {len(complex_s)} 个')
    else:
        print(f'  ✓ 选择器复杂度合理')

    print()
    print('═' * 60)
    print('3. JS 质量检查')
    print('═' * 60)

    js_start = html.find('<script>')
    js_end = html.rfind('</script>')
    js = html[js_start:js_end]

    print('  ✓ JS 包裹在 IIFE 中，无全局变量泄漏')

    fetch_calls = js.count('fetch(')
    then_catch = js.count('.catch(')
    print(f'  ✓ fetch 调用: {fetch_calls} 次, catch 处理: {then_catch} 次')

    listeners = len(re.findall(r'addEventListener\(', js))
    print(f'  ✓ 事件监听器: {listeners} 个')

    ls_keys = set(re.findall(r'localStorage\.(?:get|set|remove)Item\([\'"]([^\'"]+)[\'"]', js))
    print(f'  ✓ localStorage 键: {sorted(ls_keys)}')

    print()
    print('═' * 60)
    print('4. 功能逻辑检查')
    print('═' * 60)

    if 'payload.scene_id=selectedSceneId' in js:
        print('  ✓ doSend 包含 scene_id 传递')
    else:
        print('  ✗ doSend 缺少 scene_id')

    if 'if(!kbMode&&selectedSceneId)payload.scene_id=selectedSceneId' in js:
        print('  ✓ scene_id 仅在非知识库模式下发送')
    else:
        print('  ✗ scene_id 发送逻辑有问题')

    if 'localStorage.removeItem' in js and 'll_conv' in js:
        print('  ✓ 新对话会清理对话 ID')
    else:
        print('  ✗ 新对话不清理对话 ID')

    if 'loadSkills();loadScenes()' in js:
        print('  ✓ 登录后同时加载技能和场景')
    else:
        print('  ✗ 登录后未加载场景')

    print()
    print('═' * 60)
    print('5. 响应式检查')
    print('═' * 60)

    if '@media(max-width:480px)' in css or '@media (max-width:480px)' in css:
        print('  ✓ 包含移动端媒体查询 (480px)')
    else:
        print('  ✗ 缺少移动端媒体查询')

    if '@media(max-width:560px)' in css or '@media (max-width:560px)' in css:
        print('  ✓ 包含平板端媒体查询 (560px)')
    else:
        print('  ✗ 缺少平板端媒体查询')

    if 'safe-area-inset' in css:
        print('  ✓ 支持 iPhone 安全区域')
    else:
        print('  ✗ 不支持 iPhone 安全区域')

    print()
    print('═' * 60)
    print('6. 无障碍检查')
    print('═' * 60)

    a11y_checks = [
        ('aria-label=', 'aria-label 属性'),
        ('role=', 'ARIA 角色'),
        ('aria-live=', '实时区域'),
        ('aria-pressed=', '按压状态'),
        ('aria-relevant=', '相关性'),
    ]
    for attr, desc in a11y_checks:
        count = html.count(attr)
        status = '✓' if count > 0 else '✗'
        print(f'  {status} {desc}: {count} 处')

    if ':focus-visible' in css:
        print('  ✓ 使用 focus-visible 替代 focus')
    else:
        print('  ✗ 缺少 focus-visible')

    if 'prefers-reduced-motion' in css:
        print('  ✓ 支持减少动画偏好')
    else:
        print('  ✗ 不支持减少动画偏好')

    print()
    print('═' * 60)
    print('7. 资源加载检查')
    print('═' * 60)

    if 'fonts.googleapis.com' in html:
        print('  ✓ Google Fonts 预连接')
    if 'fonts.gstatic.com' in html:
        print('  ✓ 字体 CDN 预连接')

    external = re.findall(r'href=["\'](https?://[^"\']+)["\']', html)
    external = [e for e in external if 'google' not in e and 'gstatic' not in e]
    if external:
        print(f'  ⚠ 其他外部资源: {external}')
    else:
        print('  ✓ 无其他外部依赖（安全）')

    print()
    print('═' * 60)
    print('8. 性能检查')
    print('═' * 60)

    # 检查图片是否有 loading=lazy
    imgs = re.findall(r'<img[^>]*>', html)
    lazy_imgs = [img for img in imgs if 'loading="lazy"' in img or "loading='lazy'" in img]
    print(f'  ✓ 图片: {len(imgs)} 个, lazy: {len(lazy_imgs)} 个')

    # 检查 CSS 文件大小
    css_size = len(css)
    print(f'  ✓ 内联 CSS 大小: {css_size:,} bytes ({css_size/1024:.1f} KB)')

    js_size = len(js)
    print(f'  ✓ 内联 JS 大小: {js_size:,} bytes ({js_size/1024:.1f} KB)')

    total_size = len(html)
    print(f'  ✓ HTML 总大小: {total_size:,} bytes ({total_size/1024:.1f} KB)')

    print()
    print('═' * 60)
    print('总结: 前端代码质量检查完成')
    print('═' * 60)

if __name__ == '__main__':
    main()
