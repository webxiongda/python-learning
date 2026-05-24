import { useEffect, useMemo, useState } from 'react';
import type { FormEvent } from 'react';
import {
  AlertCircle,
  BookOpen,
  CheckCircle2,
  ClipboardCheck,
  Code2,
  FileText,
  Gauge,
  ListChecks,
  LogOut,
  NotebookPen,
  RefreshCw,
  Search,
  Sparkles,
  TimerReset
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

type LayerKey = 'theory' | 'demo' | 'check' | 'project';
type ViewKey = 'dashboard' | 'today' | 'study' | 'cards' | 'portfolio' | 'interview';

type ChapterProgress = Record<LayerKey | 'review', boolean>;

type ChapterMeta = {
  no: number;
  title: string;
  summary: string;
  priority: string;
  hours: string;
  folder: string;
  finished: string;
  progress: ChapterProgress;
};

type ChapterContent = ChapterMeta & {
  content: Record<LayerKey, string>;
};

type ReviewTask = {
  id: string;
  chapterNo: number;
  title: string;
  round: string;
  dueDate: string;
  status: string;
  due: boolean;
};

type ReviewCard = {
  id: number;
  chapterNo: number;
  chapterTitle: string;
  type: string;
  prompt: string;
  expected: string;
  dueDate: string;
  status: string;
};

type StudyLog = {
  date: string;
  chapter: string;
  layer: string;
  action: string;
  minutes: string;
  reflection: string;
};

type Summary = {
  current: string;
  completed: number;
  total: number;
  percent: number;
  currentChapter?: ChapterMeta;
  dueReviews: ReviewTask[];
  recentLogs: StudyLog[];
};

type TodayPlan = {
  focus: string;
  currentChapter?: ChapterMeta;
  dueReviews: ReviewTask[];
  dueCards: ReviewCard[];
  blocks: string[];
  acceptance: string[];
};

type PortfolioEvidence = {
  id: number;
  chapterNo: number;
  milestone: string;
  evidenceType: string;
  body: string;
  createdAt: string;
};

type Portfolio = {
  totalEvidence: number;
  milestones: string[];
  evidence: PortfolioEvidence[];
};

type InterviewCategory = {
  category: string;
  label: string;
  total: number;
  attempted: number;
  mastered: number;
};

type InterviewQuestion = {
  id: number;
  category: string;
  difficulty: string;
  frequency: string;
  prompt: string;
  relatedChapterNo: number | null;
  relatedChapterTitle: string | null;
  source: string;
  attempted: boolean;
  mastered: boolean;
};

type InterviewAttempt = {
  id: number;
  answer: string;
  selfAssessed: string;
  aiScore: number | null;
  aiFeedback: string | null;
  createdAt: string;
};

type UserDto = {
  id: number;
  username: string;
};

type AuthResponse = {
  token: string;
  user: UserDto;
};

const tokenKey = 'python-fastapi-workbench-token';
const layerMeta: Array<{ key: LayerKey; label: string; icon: typeof BookOpen }> = [
  { key: 'theory', label: '理论', icon: BookOpen },
  { key: 'demo', label: 'Demo', icon: Code2 },
  { key: 'check', label: '自测', icon: ClipboardCheck },
  { key: 'project', label: '项目任务', icon: ListChecks }
];

async function api<T>(url: string, init?: RequestInit): Promise<T> {
  const token = localStorage.getItem(tokenKey);
  const response = await fetch(url, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {})
    },
    ...init
  });
  if (!response.ok) {
    if (response.status === 401 || response.status === 403) {
      localStorage.removeItem(tokenKey);
    }
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || data.error || `Request failed: ${response.status}`);
  }
  return response.json();
}

function priorityClass(priority: string) {
  if (priority.includes('L1')) return 'priority l1';
  if (priority.includes('L2')) return 'priority l2';
  return 'priority l3';
}

function getInitialView(): ViewKey {
  const view = new URLSearchParams(window.location.search).get('view');
  return view === 'today' || view === 'study' || view === 'cards' || view === 'portfolio' || view === 'interview' ? view : 'dashboard';
}

function getInitialChapter() {
  const chapter = Number(new URLSearchParams(window.location.search).get('chapter'));
  return Number.isInteger(chapter) && chapter >= 1 && chapter <= 60 ? chapter : 1;
}

export default function App() {
  const [authUser, setAuthUser] = useState<UserDto | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [view, setView] = useState<ViewKey>(getInitialView);
  const [chapters, setChapters] = useState<ChapterMeta[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [today, setToday] = useState<TodayPlan | null>(null);
  const [selectedNo, setSelectedNo] = useState(getInitialChapter);
  const [activeLayer, setActiveLayer] = useState<LayerKey>('theory');
  const [chapter, setChapter] = useState<ChapterContent | null>(null);
  const [reviews, setReviews] = useState<ReviewTask[]>([]);
  const [cards, setCards] = useState<ReviewCard[]>([]);
  const [portfolio, setPortfolio] = useState<Portfolio | null>(null);
  const [categories, setCategories] = useState<InterviewCategory[]>([]);
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [query, setQuery] = useState('');
  const [note, setNote] = useState('');
  const [validationSummary, setValidationSummary] = useState('');
  const [validationEvidence, setValidationEvidence] = useState('');
  const [answer, setAnswer] = useState('');
  const [cardAnswer, setCardAnswer] = useState('');
  const [portfolioEvidence, setPortfolioEvidence] = useState('');
  const [interviewAnswer, setInterviewAnswer] = useState('');
  const [lastAttempt, setLastAttempt] = useState<InterviewAttempt | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('ai_backend');
  const [selectedQuestionId, setSelectedQuestionId] = useState<number | null>(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [mistakeReason, setMistakeReason] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');

  async function refresh() {
    const [nextSummary, nextChapters, nextReviews, nextToday, nextCards, nextPortfolio] = await Promise.all([
      api<Summary>('/api/summary'),
      api<ChapterMeta[]>('/api/chapters'),
      api<ReviewTask[]>('/api/reviews'),
      api<TodayPlan>('/api/today'),
      api<ReviewCard[]>('/api/cards/due'),
      api<Portfolio>('/api/portfolio')
    ]);
    setSummary(nextSummary);
    setChapters(nextChapters);
    setReviews(nextReviews);
    setToday(nextToday);
    setCards(nextCards);
    setPortfolio(nextPortfolio);
    if (!chapter && nextSummary.currentChapter) {
      setSelectedNo(nextSummary.currentChapter.no);
    }
  }

  async function refreshInterview(category = selectedCategory) {
    const [nextCategories, nextQuestions] = await Promise.all([
      api<InterviewCategory[]>('/api/interview/categories'),
      api<InterviewQuestion[]>(`/api/interview/questions?category=${encodeURIComponent(category)}`)
    ]);
    setCategories(nextCategories);
    setQuestions(nextQuestions);
    if (!selectedQuestionId && nextQuestions.length > 0) {
      setSelectedQuestionId(nextQuestions[0].id);
    }
  }

  useEffect(() => {
    const token = localStorage.getItem(tokenKey);
    if (!token) {
      setAuthReady(true);
      return;
    }
    api<UserDto>('/api/auth/me')
      .then((user) => setAuthUser(user))
      .catch((error) => {
        setMessage(error.message);
        localStorage.removeItem(tokenKey);
      })
      .finally(() => setAuthReady(true));
  }, []);

  useEffect(() => {
    if (!authUser) return;
    refresh()
      .then(() => refreshInterview())
      .catch((error) => setMessage(error.message));
  }, [authUser]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (view !== 'dashboard') params.set('view', view);
    if (view === 'study') params.set('chapter', String(selectedNo));
    window.history.replaceState(null, '', params.toString() ? `?${params.toString()}` : window.location.pathname);
  }, [view, selectedNo]);

  useEffect(() => {
    if (!authUser) return;
    setActiveLayer('theory');
    api<ChapterContent>(`/api/chapters/${selectedNo}`)
      .then((data) => {
        setChapter(data);
        setNote('');
        setValidationSummary('');
        setValidationEvidence('');
        setAnswer('');
        setShowAnswer(false);
        setMistakeReason('');
        setPortfolioEvidence('');
      })
      .catch((error) => setMessage(error.message));
  }, [selectedNo, authUser]);

  const filteredChapters = useMemo(() => {
    const keyword = query.trim().toLowerCase();
    if (!keyword) return chapters;
    return chapters.filter((item) => `${item.no} ${item.title} ${item.summary} ${item.priority}`.toLowerCase().includes(keyword));
  }, [chapters, query]);

  const dueReviews = reviews.filter((item) => item.due);
  const currentContent = chapter?.content[activeLayer] ?? '';
  const answerContent = activeLayer === 'check' ? currentContent.split('## 参考答案')[1] : '';
  const questionContent = activeLayer === 'check' ? currentContent.split('## 参考答案')[0] : currentContent;
  const selectedQuestion = questions.find((item) => item.id === selectedQuestionId) ?? questions[0];

  async function runAction(action: () => Promise<void>, success: string) {
    setBusy(true);
    setMessage('');
    try {
      await action();
      await refresh();
      if (view === 'interview') await refreshInterview();
      if (chapter) setChapter(await api<ChapterContent>(`/api/chapters/${chapter.no}`));
      setMessage(success);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : '操作失败');
    } finally {
      setBusy(false);
    }
  }

  function openChapter(no: number, targetView: ViewKey = 'study') {
    setSelectedNo(no);
    setView(targetView);
  }

  function handleAuth(response: AuthResponse) {
    localStorage.setItem(tokenKey, response.token);
    setAuthUser(response.user);
  }

  function logout() {
    localStorage.removeItem(tokenKey);
    setAuthUser(null);
    setSummary(null);
    setChapters([]);
    setReviews([]);
    setChapter(null);
  }

  function markLayerDone() {
    if (!chapter) return;
    if (activeLayer === 'check') {
      setMessage('自测层需要先提交自己的答案，通过后会自动完成');
      return;
    }
    runAction(
      () =>
        api('/api/validations', {
          method: 'POST',
          body: JSON.stringify({
            chapterNo: chapter.no,
            layer: activeLayer,
            summary: validationSummary,
            evidence: validationEvidence
          })
        }),
      '验收已保存，进度已更新'
    );
  }

  function saveNote() {
    if (!chapter || !note.trim()) return;
    runAction(
      () =>
        api('/api/notes', {
          method: 'POST',
          body: JSON.stringify({ chapterNo: chapter.no, title: chapter.title, body: note })
        }),
      '笔记已保存'
    );
    setNote('');
  }

  function submitCheck(passed: boolean) {
    if (!chapter || !answer.trim()) return;
    runAction(
      () =>
        api('/api/check-result', {
          method: 'POST',
          body: JSON.stringify({
            chapterNo: chapter.no,
            chapterTitle: chapter.title,
            answer,
            passed,
            symptom: '自测自评未通过',
            reason: mistakeReason || '答案不完整或关键概念不稳',
            fix: '回看理论与 Demo，重新完成本节自测'
          })
        }),
      passed ? '自测记录已保存' : '自测记录与错题卡已保存'
    );
    setAnswer('');
    setMistakeReason('');
  }

  function toggleAnswer() {
    if (!chapter) return;
    const next = !showAnswer;
    setShowAnswer(next);
    if (next) {
      api('/api/check-reveals', {
        method: 'POST',
        body: JSON.stringify({ chapterNo: chapter.no, chapterTitle: chapter.title })
      }).catch((error) => setMessage(error.message));
    }
  }

  function completeReview(chapterNo: number) {
    runAction(
      () =>
        api('/api/reviews', {
          method: 'PATCH',
          body: JSON.stringify({ chapterNo })
        }),
      '复习已完成'
    );
  }

  function answerReviewCard(cardId: number, remembered: boolean) {
    runAction(
      async () => {
        const nextCards = await api<ReviewCard[]>(`/api/cards/${cardId}/answer`, {
          method: 'POST',
          body: JSON.stringify({ answer: cardAnswer, remembered })
        });
        setCards(nextCards);
      },
      remembered ? '复习卡已完成' : '已加入明日加练'
    );
    setCardAnswer('');
  }

  function savePortfolioEvidence() {
    if (!chapter || !portfolioEvidence.trim()) return;
    runAction(
      async () => {
        const nextPortfolio = await api<Portfolio>('/api/portfolio/evidence', {
          method: 'POST',
          body: JSON.stringify({
            chapterNo: chapter.no,
            milestone: `Day ${String(chapter.no).padStart(2, '0')} ${chapter.title}`,
            evidenceType: 'manual',
            body: portfolioEvidence
          })
        });
        setPortfolio(nextPortfolio);
      },
      '作品集证据已保存'
    );
    setPortfolioEvidence('');
  }

  function submitInterviewAnswer() {
    if (!selectedQuestion || !interviewAnswer.trim()) return;
    runAction(
      async () => {
        const attempt = await api<InterviewAttempt>('/api/interview/attempts', {
          method: 'POST',
          body: JSON.stringify({ questionId: selectedQuestion.id, answer: interviewAnswer, selfAssessed: 'partial' })
        });
        setLastAttempt(attempt);
      },
      '面试回答已记录'
    );
    setInterviewAnswer('');
  }

  function changeInterviewCategory(category: string) {
    setSelectedCategory(category);
    setSelectedQuestionId(null);
    refreshInterview(category).catch((error) => setMessage(error.message));
  }

  if (!authReady) return <div className="auth-loading">正在读取账号状态...</div>;
  if (!authUser) return <AuthScreen onAuthed={handleAuth} message={message} setMessage={setMessage} />;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">Py</div>
          <div>
            <h1>Python AI 后端</h1>
            <p>{authUser.username}</p>
          </div>
          <button className="icon-button" onClick={logout} title="退出登录">
            <LogOut size={18} />
          </button>
        </div>

        <nav className="nav">
          <button className={view === 'dashboard' ? 'active' : ''} onClick={() => setView('dashboard')}><Gauge size={18} /> 总览</button>
          <button className={view === 'today' ? 'active' : ''} onClick={() => setView('today')}><ClipboardCheck size={18} /> 今日</button>
          <button className={view === 'study' ? 'active' : ''} onClick={() => setView('study')}><BookOpen size={18} /> 学习</button>
          <button className={view === 'cards' ? 'active' : ''} onClick={() => setView('cards')}><TimerReset size={18} /> 卡片</button>
          <button className={view === 'portfolio' ? 'active' : ''} onClick={() => setView('portfolio')}><ListChecks size={18} /> 作品</button>
          <button className={view === 'interview' ? 'active' : ''} onClick={() => setView('interview')}><Sparkles size={18} /> AI 面试</button>
        </nav>

        <div className="search-box">
          <Search size={16} />
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索章节" />
        </div>

        <div className="chapter-list">
          {filteredChapters.map((item) => {
            const done = item.progress.theory && item.progress.demo && item.progress.check && item.progress.project;
            return (
              <button key={item.no} className={`chapter-link ${selectedNo === item.no ? 'selected' : ''}`} onClick={() => openChapter(item.no)}>
                <span className="chapter-no">{String(item.no).padStart(2, '0')}</span>
                <span className="chapter-title">{item.title}</span>
                {done ? <CheckCircle2 size={16} className="done-icon" /> : null}
              </button>
            );
          })}
        </div>
      </aside>

      <main className="workspace">
        {message ? <div className="toast"><AlertCircle size={16} /> {message}</div> : null}

        {view === 'dashboard' ? <Dashboard summary={summary} chapters={chapters} dueReviews={dueReviews} onOpenChapter={openChapter} /> : null}
        {view === 'today' ? <Today today={today} onOpenChapter={openChapter} onSwitchView={setView} onCompleteReview={completeReview} /> : null}

        {view === 'study' && chapter ? (
          <section className="study-layout">
            <div className="reader">
              <header className="reader-header">
                <div>
                  <div className="eyebrow">Day {String(chapter.no).padStart(2, '0')}</div>
                  <h2>{chapter.title}</h2>
                  <p>{chapter.summary}</p>
                </div>
                <div className="chapter-meta">
                  <span className={priorityClass(chapter.priority)}>{chapter.priority}</span>
                  <span>{chapter.hours}</span>
                </div>
              </header>

              <div className="layer-tabs">
                {layerMeta.map((item) => {
                  const Icon = item.icon;
                  return (
                    <button key={item.key} className={activeLayer === item.key ? 'active' : ''} onClick={() => setActiveLayer(item.key)}>
                      <Icon size={17} /> {item.label}
                      {chapter.progress[item.key] ? <CheckCircle2 size={15} /> : null}
                    </button>
                  );
                })}
              </div>

              <article className="markdown-body">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                  {activeLayer === 'check' && !showAnswer ? questionContent : currentContent}
                </ReactMarkdown>
              </article>
            </div>

            <aside className="coach-panel">
              <div className="step-status">
                {layerMeta.map((item) => (
                  <div key={item.key} className={chapter.progress[item.key] ? 'done' : ''}>
                    <span>{item.label}</span>
                    <CheckCircle2 size={16} />
                  </div>
                ))}
              </div>

              <button className="primary-action" disabled={busy || chapter.progress[activeLayer]} onClick={markLayerDone}>
                <CheckCircle2 size={18} /> {activeLayer === 'check' ? '自测通过后自动完成' : '提交验收并完成'}
              </button>

              <section className="side-section">
                <h3><ClipboardCheck size={17} /> 强验收</h3>
                {activeLayer === 'check' ? (
                  <>
                    <textarea value={answer} onChange={(event) => setAnswer(event.target.value)} placeholder="先写自己的答案，再看参考答案" />
                    <textarea value={mistakeReason} onChange={(event) => setMistakeReason(event.target.value)} placeholder="如果没通过，写清根因" />
                    <div className="button-row">
                      <button onClick={() => submitCheck(true)} disabled={busy || !answer.trim()}>通过</button>
                      <button onClick={() => submitCheck(false)} disabled={busy || !answer.trim()}>需复习</button>
                    </div>
                    <button className="ghost-action" onClick={toggleAnswer}>{showAnswer ? '隐藏参考答案' : '查看参考答案'}</button>
                    {showAnswer && answerContent ? <div className="answer-preview"><ReactMarkdown remarkPlugins={[remarkGfm]}>{answerContent}</ReactMarkdown></div> : null}
                  </>
                ) : (
                  <>
                    <textarea value={validationSummary} onChange={(event) => setValidationSummary(event.target.value)} placeholder="用 3-5 句话讲清本节核心概念或完成内容" />
                    <textarea value={validationEvidence} onChange={(event) => setValidationEvidence(event.target.value)} placeholder="Demo / 项目需要写运行命令、接口响应、截图路径或 README 片段" />
                  </>
                )}
              </section>

              <section className="side-section">
                <h3><NotebookPen size={17} /> 学习笔记</h3>
                <textarea value={note} onChange={(event) => setNote(event.target.value)} placeholder="记录坑点、类比、代码片段" />
                <button onClick={saveNote} disabled={!note.trim() || busy}><FileText size={16} /> 保存笔记</button>
              </section>

              <section className="side-section">
                <h3><ListChecks size={17} /> 作品证据</h3>
                <textarea value={portfolioEvidence} onChange={(event) => setPortfolioEvidence(event.target.value)} placeholder="项目链接、命令输出、接口截图、关键设计说明" />
                <button onClick={savePortfolioEvidence} disabled={!portfolioEvidence.trim() || busy}>加入作品集</button>
              </section>
            </aside>
          </section>
        ) : null}

        {view === 'cards' ? <Cards cards={cards} cardAnswer={cardAnswer} setCardAnswer={setCardAnswer} onAnswer={answerReviewCard} /> : null}
        {view === 'portfolio' ? <PortfolioView portfolio={portfolio} /> : null}
        {view === 'interview' ? (
          <InterviewView
            categories={categories}
            questions={questions}
            selectedCategory={selectedCategory}
            selectedQuestion={selectedQuestion}
            selectedQuestionId={selectedQuestionId}
            answer={interviewAnswer}
            lastAttempt={lastAttempt}
            onCategory={changeInterviewCategory}
            onSelectQuestion={setSelectedQuestionId}
            onAnswer={setInterviewAnswer}
            onSubmit={submitInterviewAnswer}
            busy={busy}
          />
        ) : null}
      </main>
    </div>
  );
}

function AuthScreen({ onAuthed, message, setMessage }: { onAuthed: (response: AuthResponse) => void; message: string; setMessage: (message: string) => void }) {
  const [username, setUsername] = useState('python_ai_dev');
  const [secret, setSecret] = useState('local-secret');
  const [mode, setMode] = useState<'login' | 'register'>('register');
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setMessage('');
    try {
      const response = await api<AuthResponse>(`/api/auth/${mode}`, {
        method: 'POST',
        body: JSON.stringify({ username, secret })
      });
      onAuthed(response);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : '认证失败');
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-screen">
      <form className="auth-panel" onSubmit={submit}>
        <div className="brand-mark large">Py</div>
        <h1>Python FastAPI 学习工作台</h1>
        <p>面向 AI 应用后端的 60 章学习、验收、复习和面试训练。</p>
        <label>账号<input value={username} onChange={(event) => setUsername(event.target.value)} /></label>
        <label>本地密钥<input type="password" value={secret} onChange={(event) => setSecret(event.target.value)} /></label>
        <div className="button-row">
          <button type="button" className={mode === 'register' ? 'selected' : ''} onClick={() => setMode('register')}>注册</button>
          <button type="button" className={mode === 'login' ? 'selected' : ''} onClick={() => setMode('login')}>登录</button>
        </div>
        <button className="primary-action" disabled={busy}>{mode === 'register' ? '创建并进入' : '登录'}</button>
        {message ? <div className="inline-error">{message}</div> : null}
      </form>
    </main>
  );
}

function Dashboard({ summary, chapters, dueReviews, onOpenChapter }: { summary: Summary | null; chapters: ChapterMeta[]; dueReviews: ReviewTask[]; onOpenChapter: (no: number) => void }) {
  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <div className="eyebrow">FastAPI + AI Backend</div>
          <h2>学习总览</h2>
        </div>
        <button onClick={() => window.location.reload()}><RefreshCw size={16} /> 刷新</button>
      </header>
      <div className="metrics-grid">
        <Metric label="当前章节" value={summary?.current ?? '-'} />
        <Metric label="完成进度" value={`${summary?.percent ?? 0}%`} />
        <Metric label="已完成" value={`${summary?.completed ?? 0}/${summary?.total ?? 60}`} />
        <Metric label="到期复习" value={String(dueReviews.length)} />
      </div>
      <section className="panel">
        <h3>章节推进</h3>
        <div className="chapter-grid">
          {chapters.map((chapter) => (
            <button key={chapter.no} onClick={() => onOpenChapter(chapter.no)} className="chapter-tile">
              <span>{String(chapter.no).padStart(2, '0')}</span>
              <strong>{chapter.title}</strong>
              <small>{chapter.priority}</small>
            </button>
          ))}
        </div>
      </section>
    </section>
  );
}

function Today({ today, onOpenChapter, onSwitchView, onCompleteReview }: { today: TodayPlan | null; onOpenChapter: (no: number) => void; onSwitchView: (view: ViewKey) => void; onCompleteReview: (chapterNo: number) => void }) {
  return (
    <section className="page-stack">
      <header className="page-header">
        <div>
          <div className="eyebrow">Today</div>
          <h2>{today?.focus ?? '今日计划'}</h2>
        </div>
        {today?.currentChapter ? <button onClick={() => onOpenChapter(today.currentChapter!.no)}>继续学习</button> : null}
      </header>
      <div className="two-column">
        <section className="panel">
          <h3>时间块</h3>
          <ul>{today?.blocks.map((item) => <li key={item}>{item}</li>)}</ul>
        </section>
        <section className="panel">
          <h3>验收标准</h3>
          <ul>{today?.acceptance.map((item) => <li key={item}>{item}</li>)}</ul>
        </section>
      </div>
      <section className="panel">
        <h3>到期复习</h3>
        {today?.dueReviews.length ? today.dueReviews.map((item) => (
          <div className="list-row" key={item.id}>
            <span>{item.round} · {item.title}</span>
            <button onClick={() => onCompleteReview(item.chapterNo)}>完成</button>
          </div>
        )) : <p className="muted">今天没有到期复习。</p>}
      </section>
      <button onClick={() => onSwitchView('cards')}>查看复习卡</button>
    </section>
  );
}

function Cards({ cards, cardAnswer, setCardAnswer, onAnswer }: { cards: ReviewCard[]; cardAnswer: string; setCardAnswer: (value: string) => void; onAnswer: (cardId: number, remembered: boolean) => void }) {
  return (
    <section className="page-stack">
      <header className="page-header"><div><div className="eyebrow">Spaced Review</div><h2>复习卡</h2></div></header>
      {cards.length ? cards.map((card) => (
        <section className="panel" key={card.id}>
          <h3>{card.chapterTitle}</h3>
          <p>{card.prompt}</p>
          <textarea value={cardAnswer} onChange={(event) => setCardAnswer(event.target.value)} placeholder="先回忆，再对照期望答案" />
          <p className="muted">期望：{card.expected}</p>
          <div className="button-row">
            <button onClick={() => onAnswer(card.id, true)}>记住了</button>
            <button onClick={() => onAnswer(card.id, false)}>明天再练</button>
          </div>
        </section>
      )) : <section className="panel"><p className="muted">暂无到期复习卡。</p></section>}
    </section>
  );
}

function PortfolioView({ portfolio }: { portfolio: Portfolio | null }) {
  return (
    <section className="page-stack">
      <header className="page-header"><div><div className="eyebrow">Portfolio</div><h2>作品集证据</h2></div><strong>{portfolio?.totalEvidence ?? 0} 条</strong></header>
      <section className="panel">
        <h3>目标里程碑</h3>
        <div className="tag-row">{portfolio?.milestones.map((item) => <span key={item}>{item}</span>)}</div>
      </section>
      {portfolio?.evidence.length ? portfolio.evidence.map((item) => (
        <section className="panel" key={item.id}>
          <h3>{item.milestone}</h3>
          <p>{item.body}</p>
          <small>{item.evidenceType} · {new Date(item.createdAt).toLocaleString()}</small>
        </section>
      )) : <section className="panel"><p className="muted">完成项目验收或手动添加证据后会出现在这里。</p></section>}
    </section>
  );
}

function InterviewView(props: {
  categories: InterviewCategory[];
  questions: InterviewQuestion[];
  selectedCategory: string;
  selectedQuestion?: InterviewQuestion;
  selectedQuestionId: number | null;
  answer: string;
  lastAttempt: InterviewAttempt | null;
  onCategory: (category: string) => void;
  onSelectQuestion: (questionId: number) => void;
  onAnswer: (value: string) => void;
  onSubmit: () => void;
  busy: boolean;
}) {
  return (
    <section className="interview-layout">
      <aside className="panel interview-side">
        <h3>训练分类</h3>
        {props.categories.map((category) => (
          <button key={category.category} className={props.selectedCategory === category.category ? 'active-list-button' : ''} onClick={() => props.onCategory(category.category)}>
            <span>{category.label}</span>
            <small>{category.attempted}/{category.total}</small>
          </button>
        ))}
        <h3>题目</h3>
        {props.questions.map((question) => (
          <button key={question.id} className={props.selectedQuestionId === question.id ? 'active-list-button' : ''} onClick={() => props.onSelectQuestion(question.id)}>
            <span>{question.prompt}</span>
            {question.mastered ? <CheckCircle2 size={15} /> : null}
          </button>
        ))}
      </aside>
      <section className="panel interview-main">
        {props.selectedQuestion ? (
          <>
            <div className="eyebrow">{props.selectedQuestion.difficulty} · {props.selectedQuestion.frequency}</div>
            <h2>{props.selectedQuestion.prompt}</h2>
            <textarea value={props.answer} onChange={(event) => props.onAnswer(event.target.value)} placeholder="按真实面试回答，先讲设计边界，再讲关键实现和取舍" />
            <button className="primary-action" disabled={props.busy || props.answer.trim().length < 12} onClick={props.onSubmit}>
              <Sparkles size={18} /> 提交回答
            </button>
            {props.lastAttempt ? (
              <div className="feedback">
                <strong>{props.lastAttempt.aiScore} 分</strong>
                <p>{props.lastAttempt.aiFeedback}</p>
              </div>
            ) : null}
          </>
        ) : <p className="muted">请选择一道题。</p>}
      </section>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return <section className="metric"><span>{label}</span><strong>{value}</strong></section>;
}
