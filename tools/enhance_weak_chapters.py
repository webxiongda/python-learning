from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = ROOT / "chapters"

FILES = {
    "theory": "01-theory.md",
    "demo": "02-demo.md",
    "check": "03-check.md",
    "project": "04-project-task.md",
}

SKELETON_SIGNALS = (
    "说清它解决的问题、输入输出、常见边界和项目落点",
    "先用最小代码跑通",
    "不依赖复制粘贴的最小示例",
    "业务练习模块",
    "你正在维护一个 Python 全栈项目",
)


@dataclass(frozen=True)
class Chapter:
    no: str
    title: str
    topic: str
    priority: str
    duration: str
    path: Path


BLUEPRINTS: dict[str, dict[str, object]] = {
    "05": {
        "focus": "把字符串当成不可变文本值处理，熟悉清洗、拼接、格式化、编码和业务校验。",
        "mental": "字符串不是字符数组的可变容器，每次 `strip`、`replace`、`lower` 都返回新字符串。",
        "project": "CLI 学员信息清洗器：读取姓名、邮箱、标签，输出规范化后的结构化字典。",
        "demo": "文本清洗和报告格式化",
        "traps": ["误以为字符串方法会原地修改", "混淆字节长度和字符长度", "把 f-string 用来拼 SQL"],
    },
    "06": {
        "focus": "掌握列表的可变性、元组的结构化含义、切片复制和常见序列操作。",
        "mental": "列表适合表示会变化的一组数据，元组适合表示固定结构的一条记录。",
        "project": "任务队列整理器：接收任务列表，去除空任务，按优先级输出待办。",
        "demo": "任务列表筛选和坐标元组解包",
        "traps": ["函数默认参数使用空列表", "切片得到浅拷贝却误以为深拷贝", "遍历时修改同一个列表"],
    },
    "07": {
        "focus": "用字典表达业务对象，用集合表达去重和成员关系。",
        "mental": "字典是键到值的映射，集合是只关心是否存在的哈希容器。",
        "project": "接口请求统计器：按用户聚合请求次数，输出活跃用户集合。",
        "demo": "用户字典归一化和标签集合去重",
        "traps": ["直接访问不存在的键导致 `KeyError`", "使用可变对象作为 key", "忽略集合无序性"],
    },
    "08": {
        "focus": "用 `pathlib` 和上下文管理器可靠读写文本、JSON 和小型数据文件。",
        "mental": "文件 IO 是外部资源访问，必须考虑编码、路径、关闭、异常和幂等。",
        "project": "学习日志归档器：把每日学习记录追加到 JSONL 文件并支持读取统计。",
        "demo": "文本文件读写和 JSONL 追加",
        "traps": ["省略编码导致跨平台乱码", "用相对路径但不知道当前工作目录", "忘记关闭文件句柄"],
    },
    "09": {
        "focus": "区分异常处理、业务校验和错误传播，写出可排查的失败路径。",
        "mental": "异常不是隐藏错误的工具，而是把失败从发生位置传递到能处理的位置。",
        "project": "配置加载器：读取配置、校验字段、对缺失和非法值给出清晰错误。",
        "demo": "输入解析和自定义业务异常",
        "traps": ["裸 `except` 吞掉真实错误", "把所有异常都转成字符串", "只测成功路径"],
    },
    "10": {
        "focus": "把 01-09 的语法、函数、容器、文件和异常串成一个可交付 CLI 项目。",
        "mental": "里程碑项目检验的是组织代码、处理输入、保存数据和写 README 的完整能力。",
        "project": "学生成绩管理系统：新增、查询、统计、导入导出和错误处理。",
        "demo": "成绩记录 CRUD 和文件持久化",
        "traps": ["所有逻辑写在一个 `while True`", "没有数据模型", "不保存可复现的运行示例"],
    },
    "15": {
        "focus": "理解 import 搜索路径、包初始化、模块边界和可复用代码组织。",
        "mental": "模块是文件级复用单元，包是目录级命名空间；入口脚本不应该承载业务逻辑。",
        "project": "把前面 CLI 项目拆成 `models.py`、`services.py`、`cli.py` 和 `storage.py`。",
        "demo": "包内导入和命令入口分离",
        "traps": ["在包内混用脚本式相对路径", "循环导入", "`__init__.py` 里放重业务逻辑"],
    },
    "16": {
        "focus": "用正则做文本识别、提取和校验，但不把复杂业务全部塞进一个表达式。",
        "mental": "正则适合描述局部文本模式，复杂流程应该拆成多个可读步骤。",
        "project": "日志解析器：提取时间、级别、接口路径和状态码并生成统计。",
        "demo": "邮箱提取和日志行解析",
        "traps": ["贪婪匹配吃掉过多文本", "忘记转义特殊字符", "用正则解析完整 HTML/JSON"],
    },
    "17": {
        "focus": "处理日期、时间差、格式化和时区，避免本地时间在系统边界出错。",
        "mental": "内部存储尽量用 UTC 或明确时区，展示层再格式化成本地时间。",
        "project": "复习计划生成器：根据完成日期生成 +3/+7/+30 复习日期。",
        "demo": "时区时间和复习日期计算",
        "traps": ["混用 naive 和 aware datetime", "把日期字符串当日期对象", "忽略夏令时和时区"],
    },
    "18": {
        "focus": "掌握 `collections`、`itertools`、`functools` 等能减少重复代码的标准库工具。",
        "mental": "标准库是 Python 项目的基础设施，优先使用成熟工具再考虑手写。",
        "project": "学习数据统计器：用 Counter/defaultdict/groupby 统计章节进度。",
        "demo": "Counter 聚合和 lru_cache 缓存",
        "traps": ["重复造轮子", "滥用 itertools 写出不可读代码", "缓存可变或不稳定结果"],
    },
    "19": {
        "focus": "用类型注解表达函数契约，让 IDE、mypy 和读者提前发现问题。",
        "mental": "类型注解不是运行时强校验，它是设计接口、协作和重构的文档。",
        "project": "给 CLI 工具补齐类型注解，并用 `mypy` 检查核心模块。",
        "demo": "TypedDict、dataclass 和泛型函数",
        "traps": ["把 `Any` 当万能修复", "注解和实际返回值不一致", "忽略 Optional 分支"],
    },
    "20": {
        "focus": "交付一个可安装、可测试、可文档化的 Python 工具库。",
        "mental": "工具库的价值在稳定接口、清晰错误、测试覆盖和可复用文档。",
        "project": "文本与数据清洗工具库：slugify、safe_int、load_jsonl、group_by_key。",
        "demo": "函数库结构和 pytest 用例",
        "traps": ["只写 demo 不写包结构", "没有版本和 README", "测试只覆盖 happy path"],
    },
    "25": {
        "focus": "区分实例方法、类方法、静态方法和类变量的适用边界。",
        "mental": "实例方法操作对象状态，类方法操作类级构造，静态方法只是放在类命名空间里的纯函数。",
        "project": "用户模型工厂：支持从邮箱、字典、数据库行构造用户对象。",
        "demo": "类方法构造器和静态校验器",
        "traps": ["用类变量保存实例状态", "所有函数都塞进类里", "类方法里硬编码父类名"],
    },
    "26": {
        "focus": "用 ABC 和 Protocol 表达接口约束，降低业务代码对具体实现的依赖。",
        "mental": "ABC 是显式继承契约，Protocol 更适合鸭子类型和可替换依赖。",
        "project": "存储接口抽象：文件存储、内存存储、SQLite 存储共享同一协议。",
        "demo": "Protocol 驱动的 Repository",
        "traps": ["把接口设计成上帝对象", "抽象过早", "只写继承不写行为测试"],
    },
    "27": {
        "focus": "用 dataclass 表达数据结构，用 Enum 限制状态值，用不可变对象减少副作用。",
        "mental": "数据类负责承载数据，不应混入过多流程控制；枚举让状态值可读且受限。",
        "project": "订单状态模型：订单、状态枚举、状态流转校验。",
        "demo": "frozen dataclass 和枚举状态机",
        "traps": ["可变默认值", "把 Enum 和字符串随意混用", "数据类承担过重业务"],
    },
    "28": {
        "focus": "理解常用设计模式解决的变化点，而不是背类图。",
        "mental": "模式的核心是隔离变化：创建变化、算法变化、通知变化、装饰变化。",
        "project": "通知发送器：策略模式选择渠道，装饰器模式添加日志和重试。",
        "demo": "策略模式和工厂函数",
        "traps": ["为简单逻辑强行套模式", "继承层级过深", "忽略 Python 函数本身就是对象"],
    },
    "29": {
        "focus": "用 pytest 写能保护重构的测试，掌握 fixture、参数化和 mock 边界。",
        "mental": "测试描述行为，不复制实现；测试失败信息应该能指导下一步修复。",
        "project": "为工具库补单元测试：正常、异常、边界、回归用例。",
        "demo": "参数化测试和临时目录 fixture",
        "traps": ["只测一条成功路径", "过度 mock 自己的代码", "测试名不能说明行为"],
    },
    "30": {
        "focus": "用 OOP、设计模式和测试完成一个小型领域项目。",
        "mental": "对象设计不是类越多越好，而是职责清楚、接口稳定、测试容易写。",
        "project": "图书馆管理系统：图书、用户、借阅、归还、逾期统计。",
        "demo": "领域对象和服务层协作",
        "traps": ["模型对象直接读写文件", "服务层没有测试", "异常和返回值混乱"],
    },
    "35": {
        "focus": "理解元类、类装饰器和动态创建类的适用场景。",
        "mental": "元编程是在定义阶段改造对象模型，能少用就少用，优先选择普通函数和装饰器。",
        "project": "插件注册器：类装饰器自动登记处理器，按类型分发任务。",
        "demo": "类装饰器注册和 `type()` 动态创建类",
        "traps": ["为了炫技使用元类", "隐藏控制流导致难调试", "破坏 IDE 和类型检查"],
    },
    "36": {
        "focus": "掌握 map/filter/reduce、partial、纯函数和不可变思维在数据处理中的价值。",
        "mental": "函数式风格适合数据变换流水线，但可读性优先于一行写完。",
        "project": "学习记录分析流水线：过滤、映射、分组、汇总输出报告。",
        "demo": "纯函数转换和 `functools.partial`",
        "traps": ["嵌套 lambda 过深", "在纯函数里修改外部状态", "为了函数式牺牲可读性"],
    },
    "37": {
        "focus": "理解引用计数、垃圾回收、弱引用、slots 和内存分析基本方法。",
        "mental": "Python 自动管理内存，但对象引用关系和缓存策略仍会造成泄漏。",
        "project": "缓存监控实验：比较普通字典缓存、lru_cache 和 weakref 的行为。",
        "demo": "对象生命周期和 tracemalloc 快照",
        "traps": ["全局缓存无限增长", "循环引用里包含 `__del__`", "过早使用 `__slots__`"],
    },
    "38": {
        "focus": "用测量驱动优化，掌握 cProfile、timeit、lru_cache 和数据结构选择。",
        "mental": "性能优化先定位瓶颈，再改算法、数据结构或 IO 模式。",
        "project": "慢查询模拟器：对文本统计函数做 profile 并优化。",
        "demo": "cProfile 定位热点和缓存优化",
        "traps": ["凭感觉优化", "优化后不保留回归测试", "忽略 IO 比 CPU 更慢"],
    },
    "39": {
        "focus": "用 logging、pdb 和结构化日志建立可排查的调试能力。",
        "mental": "日志是系统运行时证据，调试是缩小问题范围的过程。",
        "project": "API 请求日志器：记录 request_id、路径、耗时、异常和业务结果。",
        "demo": "结构化日志和断点调试",
        "traps": ["用 print 替代日志系统", "日志没有上下文", "生产环境输出敏感信息"],
    },
    "40": {
        "focus": "综合 asyncio、aiohttp、限速、重试和数据存储完成并发爬虫项目。",
        "mental": "并发爬虫的难点不是发很多请求，而是控制速率、失败重试、数据一致性和可恢复。",
        "project": "异步网页标题采集器：读取 URL、并发抓取、限速、重试、保存结果。",
        "demo": "并发抓取和失败重试",
        "traps": ["无限并发压垮目标服务", "没有超时", "失败后丢失上下文"],
    },
    "46": {
        "focus": "掌握 SQLite、PostgreSQL 驱动和 SQL 基础 CRUD，为 FastAPI 数据持久化打底。",
        "mental": "数据库是持久化状态的系统边界，SQL 是描述集合操作和约束的语言。",
        "project": "学习记录数据库：建表、插入、查询、更新完成状态。",
        "demo": "SQLite 参数化查询和事务提交",
        "traps": ["字符串拼接 SQL", "忘记事务提交", "没有唯一约束导致重复数据"],
    },
    "47": {
        "focus": "用 SQLAlchemy 2.x 建模、管理 Session、表达关系，并理解 Alembic 迁移职责。",
        "mental": "ORM 不是隐藏数据库，而是把对象状态变化翻译成 SQL。",
        "project": "FastAPI 学习记录 ORM：User、ChapterProgress、ReviewTask 三张表。",
        "demo": "声明式模型和 Session 生命周期",
        "traps": ["把 Session 当全局单例", "N+1 查询", "模型变更后忘记迁移"],
    },
    "48": {
        "focus": "用 Redis 做缓存、过期时间、计数器和轻量限流。",
        "mental": "缓存是加速读路径的副本，必须考虑失效、穿透、击穿和一致性。",
        "project": "AI 回答缓存：按 prompt hash 缓存模型响应并设置 TTL。",
        "demo": "setex 缓存和滑动窗口计数",
        "traps": ["没有 TTL", "把 Redis 当主数据库", "缓存 key 没有命名规范"],
    },
    "49": {
        "focus": "设计稳定、可演进、可观测的 REST API，包含版本、错误、分页和限流。",
        "mental": "API 是团队和系统之间的契约，命名、状态码和错误结构要稳定。",
        "project": "学习工作台 API 规范：章节、进度、复习卡、AI 面试题接口设计。",
        "demo": "统一错误响应和分页查询",
        "traps": ["动词式 URL 混乱", "所有错误都返回 200", "响应结构频繁变化"],
    },
    "50": {
        "focus": "交付 FastAPI AI 助手 API，覆盖聊天、流式输出、任务状态和历史记录。",
        "mental": "AI 后端的核心是把不稳定模型能力包装成稳定业务接口。",
        "project": "AI Assistant API：会话、消息、流式响应、任务表、历史查询。",
        "demo": "SSE 流式接口和本地模型适配器占位",
        "traps": ["路由里直接调用模型 SDK", "没有超时和取消", "不记录请求和模型输出"],
    },
    "54": {
        "focus": "用 GitHub Actions 建立测试、构建、质量检查和部署前门禁。",
        "mental": "CI/CD 是把人工发布步骤固化成可重复流水线。",
        "project": "学习工作台 CI：运行 pytest、内容检查、前端 build。",
        "demo": "GitHub Actions workflow 和失败定位",
        "traps": ["只在本地跑测试", "CI 使用和本地不同的命令", "密钥写进仓库"],
    },
    "56": {
        "focus": "掌握输入验证、SQL 注入防御、密钥管理、认证和日志脱敏。",
        "mental": "安全不是最后补丁，而是每个边界的默认约束。",
        "project": "FastAPI 安全加固：Pydantic 校验、密码哈希、JWT、敏感日志过滤。",
        "demo": "参数化查询和安全配置加载",
        "traps": ["信任前端输入", "密钥提交到 Git", "日志记录 token 和密码"],
    },
    "57": {
        "focus": "用 NumPy 和 Pandas 完成数据读取、清洗、聚合和基础分析。",
        "mental": "数据分析先确认字段含义、缺失值、异常值，再做统计。",
        "project": "学习行为分析：读取学习日志 CSV，统计章节耗时和完成率。",
        "demo": "DataFrame 清洗和分组聚合",
        "traps": ["不看数据类型", "忽略缺失值", "链式赋值导致结果不可控"],
    },
    "58": {
        "focus": "用 matplotlib、seaborn、plotly 表达数据趋势、分布和对比。",
        "mental": "可视化服务于问题回答，不是图越炫越好。",
        "project": "学习进度仪表盘：章节完成趋势、复习到期分布、错题类型占比。",
        "demo": "柱状图、折线图和交互图",
        "traps": ["坐标轴和单位不清", "颜色过多", "图表没有回答业务问题"],
    },
    "59": {
        "focus": "整理 Python 面试高频点和系统设计模式，能讲清 FastAPI AI 后端方案。",
        "mental": "面试考的是取舍和边界，不只是背 API。",
        "project": "AI 学习助手系统设计：认证、聊天、任务、缓存、限流、观测。",
        "demo": "系统设计拆解模板和容量估算",
        "traps": ["只说技术名词不说为什么", "没有失败路径", "忽略数据一致性和成本"],
    },
    "60": {
        "focus": "把路线收束成作品集、简历话术、进阶方向和持续学习计划。",
        "mental": "总结不是结束，而是把能力转化成可展示、可复盘、可继续迭代的资产。",
        "project": "Python AI 后端作品集 README：项目清单、架构图、接口、部署和复盘。",
        "demo": "简历项目描述和后续路线规划",
        "traps": ["只列技术栈不列成果", "没有可运行链接或截图", "进阶路线没有优先级"],
    },
}


def parse_chapters() -> list[Chapter]:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    rows: list[Chapter] = []
    pattern = re.compile(
        r"^\|\s*(\d{2})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(L\d[^|]+?)\s*\|\s*([^|]+?)\s*\|"
    )
    for line in readme.splitlines():
        match = pattern.match(line)
        if not match:
            continue
        no, title, topic, priority, duration = [part.strip() for part in match.groups()]
        matches = sorted(CHAPTERS.glob(f"{no}-*"))
        if matches:
            rows.append(Chapter(no, title, topic, priority, duration, matches[0]))
    return rows


def points(topic: str) -> list[str]:
    return [part.strip() for part in re.split(r"[、,，/]+", topic) if part.strip()]


def blueprint(chapter: Chapter) -> dict[str, object]:
    base = BLUEPRINTS.get(chapter.no)
    if base:
        return base
    ps = points(chapter.topic)
    first = ps[0] if ps else chapter.title
    return {
        "focus": f"把 {chapter.topic} 学到能解释、能运行、能在 FastAPI 或数据项目里落地。",
        "mental": f"先判断 {first} 解决的边界问题，再决定它属于入口层、业务层、数据层还是测试层。",
        "project": f"{chapter.title} 小练习：围绕 {first} 做一个可运行、可测试、可记录结果的模块。",
        "demo": f"{first} 最小实践",
        "traps": ["只背概念不运行代码", "忽略异常路径", "没有把结果写进项目记录"],
    }


def line_count(path: Path) -> int:
    if not path.exists():
        return 0
    return len(path.read_text(encoding="utf-8").splitlines())


def has_skeleton(path: Path) -> bool:
    if not path.exists():
        return True
    content = path.read_text(encoding="utf-8")
    return any(signal in content for signal in SKELETON_SIGNALS)


def weak_files(chapter: Chapter) -> set[str]:
    thresholds = {"theory": 100, "demo": 100, "check": 75, "project": 75}
    weak = {
        key
        for key, filename in FILES.items()
        if line_count(chapter.path / filename) < thresholds[key] or has_skeleton(chapter.path / filename)
    }
    if "theory" in weak:
        return set(FILES)
    return weak


def bullet(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def fenced(code: str, lang: str = "python") -> str:
    return f"```{lang}\n{code.strip()}\n```"


def indent(text: str) -> str:
    return textwrap.dedent(text).strip()


def demo_code(chapter: Chapter, bp: dict[str, object]) -> str:
    no = chapter.no
    if no == "46":
        return indent(
            """
            import sqlite3
            from pathlib import Path

            DB_PATH = Path("learning.db")

            def connect():
                return sqlite3.connect(DB_PATH)

            def init_db(conn):
                conn.execute(
                    "create table if not exists progress("
                    "chapter_no integer primary key, title text not null, done integer not null)"
                )
                conn.commit()

            def save_progress(conn, chapter_no, title, done=False):
                conn.execute(
                    "insert into progress(chapter_no, title, done) values (?, ?, ?) "
                    "on conflict(chapter_no) do update set title=excluded.title, done=excluded.done",
                    (chapter_no, title, int(done)),
                )
                conn.commit()

            def list_progress(conn):
                return conn.execute(
                    "select chapter_no, title, done from progress order by chapter_no"
                ).fetchall()
            """
        )
    if no == "47":
        return indent(
            """
            from sqlalchemy import Boolean, Integer, String, create_engine, select
            from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

            class Base(DeclarativeBase):
                pass

            class ChapterProgress(Base):
                __tablename__ = "chapter_progress"

                chapter_no: Mapped[int] = mapped_column(Integer, primary_key=True)
                title: Mapped[str] = mapped_column(String(120))
                done: Mapped[bool] = mapped_column(Boolean, default=False)

            engine = create_engine("sqlite:///learning.db")
            Base.metadata.create_all(engine)

            def save_progress(chapter_no: int, title: str, done: bool = False) -> None:
                with Session(engine) as session:
                    item = session.get(ChapterProgress, chapter_no)
                    if item is None:
                        item = ChapterProgress(chapter_no=chapter_no, title=title, done=done)
                        session.add(item)
                    else:
                        item.title = title
                        item.done = done
                    session.commit()

            def list_progress() -> list[ChapterProgress]:
                with Session(engine) as session:
                    return list(session.scalars(select(ChapterProgress).order_by(ChapterProgress.chapter_no)))
            """
        )
    if no == "48":
        return indent(
            """
            from hashlib import sha256
            from time import time

            cache = {}

            def cache_key(prompt):
                return "ai:answer:" + sha256(prompt.encode("utf-8")).hexdigest()

            def set_cached(prompt, answer, ttl_seconds=60):
                cache[cache_key(prompt)] = {"answer": answer, "expires_at": time() + ttl_seconds}

            def get_cached(prompt):
                item = cache.get(cache_key(prompt))
                if not item or item["expires_at"] < time():
                    return None
                return item["answer"]
            """
        )
    if no in {"49", "50", "56"}:
        return indent(
            """
            from fastapi import FastAPI, HTTPException
            from pydantic import BaseModel, Field

            app = FastAPI()

            class ChatRequest(BaseModel):
                message: str = Field(min_length=1, max_length=2000)

            @app.post("/api/v1/chat")
            def chat(request: ChatRequest):
                if "token" in request.message.lower():
                    raise HTTPException(status_code=400, detail={"code": "unsafe_input", "message": "输入包含敏感字段"})
                return {"data": {"reply": f"收到：{request.message}"}, "error": None}
            """
        )
    if no == "54":
        return indent(
            """
            name: quality
            on: [push, pull_request]
            jobs:
              test:
                runs-on: ubuntu-latest
                steps:
                  - uses: actions/checkout@v4
                  - uses: actions/setup-python@v5
                    with:
                      python-version: "3.11"
                  - run: python -m pip install -r backend/requirements.txt
                  - run: python -m pytest backend/tests/test_workbench_api.py -q
                  - run: python tools/check_learning_repo.py
            """
        )
    if no in {"57", "58"}:
        return indent(
            """
            import pandas as pd

            rows = [
                {"chapter": 44, "minutes": 90, "done": True},
                {"chapter": 45, "minutes": 120, "done": False},
                {"chapter": 50, "minutes": 180, "done": True},
            ]

            df = pd.DataFrame(rows)
            summary = df.groupby("done")["minutes"].agg(["count", "sum", "mean"])
            print(summary)
            """
        )
    if no in {"59", "60"}:
        return indent(
            """
            def describe_project():
                return {
                    "name": "Python FastAPI AI Learning Workbench",
                    "problem": "把学习路线、强验收、复习和 AI 面试训练集中到一个系统",
                    "backend": ["FastAPI", "SQLAlchemy", "SQLite", "JWT"],
                    "ai_ready": ["streaming", "RAG boundary", "interview scoring service"],
                    "evidence": ["tests passing", "local demo", "README", "screenshots"],
                }

            print(describe_project())
            """
        )
    return indent(
        f"""
        def normalize_text(value):
            if value is None:
                raise ValueError("value 不能为空")
            text = str(value).strip()
            if not text:
                raise ValueError("value 不能是空字符串")
            return text

        def build_record(raw_value, tags=None):
            tags = tags or []
            clean_tags = sorted({{normalize_text(tag).lower() for tag in tags if str(tag).strip()}})
            return {{"title": normalize_text(raw_value), "tags": clean_tags, "source": "{chapter.title}"}}

        print(build_record("{bp["demo"]}", ["Python", " api ", "Python"]))
        """
    )


def theory(chapter: Chapter) -> str:
    bp = blueprint(chapter)
    ps = points(chapter.topic)
    concepts = "\n".join(
        f"### {idx}. {point}\n\n"
        f"- 要解决的问题：{point} 帮你处理 `{chapter.title}` 中最常见的真实开发场景。\n"
        f"- 项目落点：在 FastAPI、CLI、数据处理或测试代码里，把它放到清晰的函数或模块边界内。\n"
        f"- 验收方式：写出一个最小例子，再说明失败输入会发生什么。"
        for idx, point in enumerate(ps, 1)
    )
    traps = bullet(bp["traps"])  # type: ignore[arg-type]
    return f"""# 第{chapter.no}章：{chapter.title} — 理论篇

## 本章定位

{bp["focus"]}

- 优先级：{chapter.priority}
- 建议投入：{chapter.duration}
- 主线关联：Python 基础能力最终要服务于 FastAPI、数据处理、工程化和 AI 应用后端。
- 交付物：可运行 Demo、自测答案、项目任务记录和复习笔记。

## 心智模型

{bp["mental"]}

学习本章时不要只记 API 名称，要持续回答三个问题：

1. 这个能力解决什么问题？
2. 它应该放在项目的哪一层？
3. 输入异常、数据为空或规模变大时会怎样？

## 核心知识点

{concepts}

## 在项目中的使用场景

- FastAPI 接口：把输入解析、业务规则、数据访问和错误响应拆开。
- AI 应用后端：把模型调用、提示词、缓存、日志、任务状态和历史记录拆成稳定边界。
- 数据处理任务：读取外部数据后，先清洗和校验，再聚合、转换和输出。
- 测试与复盘：给核心函数写边界用例，把踩坑写回 `mistakes.md`。

## 常见错误和排查信号

{traps}

排查时优先看：

- 输入是否符合预期类型和结构。
- 函数是否有明确返回值，而不是只打印。
- 异常是否带有足够上下文。
- 是否能用一个最小测试复现问题。

## 面试高频问题

1. {chapter.title} 在真实项目里解决什么问题？
2. 如果输入为空、重复、非法或特别大，你会如何处理？
3. 它和相邻章节的能力边界是什么？
4. 在 FastAPI 或 AI 应用后端里，你会把这部分逻辑放在哪一层？
5. 你会写哪些测试保护这段逻辑？

## 本章验收口径

- 能用自己的话讲清 `{chapter.topic}` 的核心价值。
- 能写出至少一个不依赖复制粘贴的最小 Demo。
- 能指出两个常见坑，并说明如何排查。
- 能把本章能力落到 `{bp["project"]}`。
"""


def demo(chapter: Chapter) -> str:
    bp = blueprint(chapter)
    code = demo_code(chapter, bp)
    lang = "yaml" if chapter.no == "54" else "python"
    validation_call = '"把这里替换成 Demo 1 的核心函数调用"'
    if chapter.no not in {"46", "47", "48", "49", "50", "54", "56", "57", "58", "59", "60"}:
        validation_call = 'build_record(case, ["Python", "AI", "python"])'
    return f"""# 第{chapter.no}章：{chapter.title} — Demo 篇

## Demo 1：{bp["demo"]}

### 目标

用一个最小、可运行、可修改的例子验证本章核心能力。

### 示例代码

{fenced(code, lang)}

### 运行方式

```bash
python demo_{chapter.no}.py
```

如果本章示例是配置文件或 workflow，把代码保存为对应文件后按文档命令运行。

### 观察点

- 输出是否是结构化结果，而不是散乱打印。
- 输入为空、重复或非法时是否能得到清晰反馈。
- 哪些部分可以拆成函数并单独测试。

## Demo 2：加入边界条件

把 Demo 1 改造成下面的调用方式：

```python
cases = [
    "normal input",
    "  input with spaces  ",
    "",
    None,
]

for case in cases:
    try:
        print(case, "=>", {validation_call})
    except Exception as exc:
        print(case, "=> ERROR:", exc)
```

要求你能解释：

- 哪些输入应该被接受。
- 哪些输入应该抛错。
- 错误信息是否能帮助定位问题。

## Demo 3：接近项目的分层

把代码拆成三层：

- `load_*`：读取输入，可以来自文件、HTTP 请求或数据库。
- `process_*`：纯业务处理，尽量只接收参数并返回结构化结果。
- `save_*` 或 `render_*`：保存或展示结果。

建议目录：

```text
projects/chapter-{chapter.no}/
├── README.md
├── src/
│   └── main.py
└── tests/
    └── test_main.py
```

## 常见错误

{bullet(bp["traps"])}

## 复盘问题

1. 本章 Demo 里哪个函数最值得写测试？
2. 如果把它接到 FastAPI 路由，路由层应该只做什么？
3. 如果后续要支持 AI 应用场景，哪些输入输出需要记录？
"""


def check(chapter: Chapter) -> str:
    bp = blueprint(chapter)
    ps = points(chapter.topic)
    concept_questions = "\n".join(
        f"{idx}. `{point}` 解决什么问题？请给出一个项目场景。"
        for idx, point in enumerate(ps[:5], 1)
    )
    return f"""# 第{chapter.no}章：{chapter.title} — 自测与验收

## 1. 概念题

{concept_questions}

## 2. 代码题

下面代码可以跑，但不适合放进真实项目。请指出问题并改造。

```python
def process(data):
    result = []
    for item in data:
        if item:
            result.append(str(item).strip())
    print(result)
```

改造要求：

- 函数必须有明确返回值。
- 处理 `None`、空字符串、重复数据。
- 至少写 3 个断言或手动验收用例。
- 不在业务函数里直接 `print`。

## 3. 项目应用题

你要完成 `{bp["project"]}`。

请回答：

1. 入口层、业务层、数据层分别负责什么？
2. 哪些输入需要校验？
3. 失败时返回异常、错误码还是空结果？为什么？
4. 哪些结果要写入 README 作为验收证据？

## 4. 费曼输出题

不用术语堆砌，用 5 句话向一个刚学 Python 的人解释本章：

- 第 1 句：本章解决什么实际问题。
- 第 2 句：最重要的概念是什么。
- 第 3 句：最容易踩的坑是什么。
- 第 4 句：在 FastAPI 或 AI 后端里如何使用。
- 第 5 句：怎样证明自己真的掌握了。

## 参考答案要点

- 能把 `{chapter.title}` 和真实输入、输出、异常路径联系起来。
- 能把代码拆成可测试函数，而不是只写脚本。
- 能说明边界输入如何处理。
- 能把本章能力落到 `projects/chapter-{chapter.no}/`。
- 能把不会的问题写入根目录 `mistakes.md` 并安排复习。
"""


def project_task(chapter: Chapter) -> str:
    bp = blueprint(chapter)
    return f"""# 第{chapter.no}章：{chapter.title} — 项目任务

## 任务目标

完成：{bp["project"]}

这个任务不是写一段孤立 Demo，而是要留下可复盘的项目证据。默认目录：

```text
projects/chapter-{chapter.no}/
├── README.md
├── src/
│   └── main.py
└── tests/
    └── test_main.py
```

## 功能要求

1. 提供一个清晰入口，可以是 CLI、脚本函数或 FastAPI 路由。
2. 至少包含一个核心业务函数，业务函数必须返回结构化数据。
3. 至少处理 3 类输入：正常输入、空输入、非法输入。
4. 错误信息要能帮助定位问题。
5. README 记录运行命令、示例输入、示例输出和复盘结论。

## 最小接口设计

无论你最终写 CLI 还是 API，都先把核心逻辑设计成下面这种形态：

```python
def validate_input(raw):
    \"\"\"校验外部输入，失败时抛出带上下文的异常。\"\"\"


def run_business(payload):
    \"\"\"只处理业务规则，返回 dict/list/dataclass，不直接 print。\"\"\"


def render_result(result):
    \"\"\"把结构化结果转换成人能阅读的文本或 HTTP 响应。\"\"\"
```

这样做的目的：

- 入口层可以替换成 CLI、FastAPI 路由或定时任务。
- 业务层可以直接写 pytest。
- 输出层可以记录到 README、日志或接口响应。
- 后续接 AI 能力时，可以把 prompt、模型响应、缓存 key 和任务状态放在清晰边界内。

## 推荐实现步骤

1. 在 `projects/chapter-{chapter.no}/README.md` 写清任务目标。
2. 在 `src/main.py` 写最小可运行版本。
3. 把输入校验和业务处理拆成函数。
4. 在 `tests/test_main.py` 写 3 个测试或手动验收用例。
5. 运行示例，把输出贴回 README。
6. 把踩坑或不会的问题补到根目录 `mistakes.md`。

## 验收清单

- [ ] 可以用一条命令运行。
- [ ] 有正常输入示例。
- [ ] 有空输入或非法输入示例。
- [ ] 核心逻辑不是只靠 `print`。
- [ ] README 包含运行结果。
- [ ] 能说明本章知识点在 FastAPI / AI 后端里的落点。
- [ ] 至少记录一个失败案例和修复过程。
- [ ] 至少有一个函数能被单独测试。

## README 必须包含的内容

- `# Chapter {chapter.no} {chapter.title}`
- `## 功能说明`：用 3-5 句话说明这个项目解决什么问题。
- `## 运行命令`：写真实命令，例如 `python src/main.py`。
- `## 示例输入`：贴一个正常输入和一个异常输入。
- `## 示例输出`：贴真实输出，不写“略”。
- `## 边界处理`：说明空输入、非法输入、重复输入如何处理。
- `## 复盘`：记录一个踩坑点、原因和修复方式。

## 扩展任务

- 给核心函数补类型注解。
- 加一个 pytest 测试文件。
- 如果适合 Web 场景，把入口改成 FastAPI 路由。
- 如果适合 AI 场景，补充请求日志、缓存键或任务状态字段设计。

## 提交证据

学习工作台里提交项目验收时，至少填写：

- 项目目录：`projects/chapter-{chapter.no}/`
- 运行命令。
- 一段示例输出。
- 一个你修过的错误或边界问题。
"""


GENERATORS = {
    "theory": theory,
    "demo": demo,
    "check": check,
    "project": project_task,
}


def write_if_changed(path: Path, content: str) -> bool:
    content = content.rstrip() + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    changed: dict[str, list[str]] = {}
    for chapter in parse_chapters():
        weak = weak_files(chapter)
        if not weak:
            continue
        for key in sorted(weak):
            filename = FILES[key]
            if write_if_changed(chapter.path / filename, GENERATORS[key](chapter)):
                changed.setdefault(chapter.no, []).append(filename)
    if not changed:
        print("No weak chapter files found.")
        return 0
    for no, files in changed.items():
        print(f"{no}: {', '.join(files)}")
    print(f"Updated {sum(len(files) for files in changed.values())} files in {len(changed)} chapters.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
