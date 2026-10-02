import React, { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Input } from '../../components/common/Input';
import { Badge } from '../../components/common/Badge';
import { domainApi } from '../../core/api/domain';
import { useActiveParish } from '../../core/hooks/useActiveParish';
import { useAuthStore } from '../../core/store/authStore';

type Row = Record<string, any>;
const managerRoles = ['SUPER_ADMIN', 'CHANCELLOR', 'PARISH_PRIEST'];

export const SurveysPage: React.FC = () => {
  const client = useQueryClient();
  const { activeParishId } = useActiveParish();
  const role = useAuthStore((state) => state.user?.role || '');
  const canManage = managerRoles.includes(role);
  const canSubmit = role === 'PARISH_SECRETARY';
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [question, setQuestion] = useState('');
  const [questionType, setQuestionType] = useState('TEXT');
  const [options, setOptions] = useState('');
  const [questionItems, setQuestionItems] = useState<Row[]>([]);
  const [selected, setSelected] = useState<Row | null>(null);
  const [answers, setAnswers] = useState<Record<string, unknown>>({});
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const surveysQuery = useQuery({ queryKey: ['surveys', activeParishId], queryFn: () => domainApi.listSurveys(activeParishId!), enabled: Boolean(activeParishId) });
  const summaryQuery = useQuery({ queryKey: ['survey-summary', selected?.id], queryFn: () => domainApi.getSurveySummary(selected!.id), enabled: Boolean(selected?.id) });
  const responsesQuery = useQuery({ queryKey: ['survey-responses', selected?.id], queryFn: () => domainApi.listSurveyResponses(selected!.id), enabled: Boolean(selected?.id) });
  const refresh = () => client.invalidateQueries({ queryKey: ['surveys', activeParishId] });
  const createMutation = useMutation({
    mutationFn: () => domainApi.createSurvey({ title, description: description || null, parish_id: activeParishId, status: 'DRAFT', questions: questionItems }),
    onSuccess: () => { setTitle(''); setDescription(''); setQuestion(''); setOptions(''); setQuestionItems([]); setNotice('Draft survey created.'); setError(null); refresh(); },
    onError: (e: any) => setError(e?.response?.data?.detail || 'Unable to create survey.'),
  });
  const updateMutation = useMutation({ mutationFn: ({ id, status }: { id: string; status: string }) => domainApi.updateSurvey(id, { status }), onSuccess: (updated) => { setSelected((current) => current?.id === updated.id ? updated : current); setNotice('Survey status updated.'); setError(null); refresh(); } });
  const respondMutation = useMutation({ mutationFn: () => domainApi.submitSurveyResponse(selected!.id, { respondent_parish_id: activeParishId, answers }), onSuccess: () => { setAnswers({}); setNotice('Survey response submitted.'); setError(null); client.invalidateQueries({ queryKey: ['survey-responses', selected?.id] }); client.invalidateQueries({ queryKey: ['survey-summary', selected?.id] }); refresh(); }, onError: (e: any) => setError(e?.response?.data?.detail || 'Unable to submit response.') });

  const setAnswer = (id: string, value: unknown) => setAnswers((existing) => ({ ...existing, [id]: value }));
  const renderQuestion = (q: Row) => {
    if (q.question_type === 'BOOLEAN') return <select className="mt-1 w-full rounded-lg border px-3 py-2" required={q.required} value={String(answers[q.id] ?? '')} onChange={(e) => setAnswer(q.id, e.target.value === '' ? '' : e.target.value === 'true')}><option value="">Choose…</option><option value="true">Yes</option><option value="false">No</option></select>;
    if (q.question_type === 'SINGLE_CHOICE') return <select className="mt-1 w-full rounded-lg border px-3 py-2" required={q.required} value={String(answers[q.id] ?? '')} onChange={(e) => setAnswer(q.id, e.target.value)}><option value="">Choose…</option>{q.options?.map((item: string) => <option key={item}>{item}</option>)}</select>;
    if (q.question_type === 'MULTIPLE_CHOICE') return <div className="mt-2 space-y-1">{q.options?.map((item: string) => <label key={item} className="flex gap-2 text-sm"><input type="checkbox" checked={Array.isArray(answers[q.id]) && (answers[q.id] as string[]).includes(item)} onChange={(e) => { const current = Array.isArray(answers[q.id]) ? answers[q.id] as string[] : []; setAnswer(q.id, e.target.checked ? [...current, item] : current.filter((value) => value !== item)); }} />{item}</label>)}</div>;
    if (q.question_type === 'NUMBER' || q.question_type === 'RATING') return <Input type="number" required={q.required} value={String(answers[q.id] ?? '')} onChange={(e) => setAnswer(q.id, e.target.value === '' ? '' : Number(e.target.value))} />;
    if (q.question_type === 'DATE') return <Input type="date" required={q.required} value={String(answers[q.id] ?? '')} onChange={(e) => setAnswer(q.id, e.target.value)} />;
    return <textarea className="mt-1 min-h-20 w-full rounded-lg border p-3" required={q.required} value={String(answers[q.id] ?? '')} onChange={(e) => setAnswer(q.id, e.target.value)} />;
  };

  return <div className="space-y-6">
    <header><h1 className="text-xl font-bold text-gray-900">Pastoral surveys</h1><p className="mt-1 text-xs text-gray-500">Build parish questionnaires, collect returns, and review aggregated responses.</p></header>
    {error && <p role="alert" className="rounded border border-red-200 bg-red-50 p-2 text-sm text-red-700">{error}</p>}{notice && <p role="status" className="rounded border border-green-200 bg-green-50 p-2 text-sm text-green-700">{notice}</p>}
    {canManage && <Card title="Create a draft survey"><form className="space-y-3" onSubmit={(e) => { e.preventDefault(); if (!questionItems.length) { setError('Add at least one question before creating the survey.'); return; } setError(null); createMutation.mutate(); }}><div className="grid gap-3 sm:grid-cols-2"><Input label="Survey title" required value={title} onChange={(e) => setTitle(e.target.value)} /><Input label="Description" value={description} onChange={(e) => setDescription(e.target.value)} /></div><Input label="Question text" value={question} onChange={(e) => setQuestion(e.target.value)} /><div className="grid gap-3 sm:grid-cols-2"><label className="block text-sm">Question type<select className="mt-1 w-full rounded-lg border px-3 py-2" value={questionType} onChange={(e) => setQuestionType(e.target.value)}>{['TEXT', 'NUMBER', 'BOOLEAN', 'SINGLE_CHOICE', 'MULTIPLE_CHOICE', 'RATING', 'DATE'].map((x) => <option key={x}>{x}</option>)}</select></label>{['SINGLE_CHOICE', 'MULTIPLE_CHOICE'].includes(questionType) && <Input label="Options (one per line)" value={options} onChange={(e) => setOptions(e.target.value)} />}</div><Button size="sm" variant="outline" type="button" onClick={() => { const choices = options.split('\n').map((x) => x.trim()).filter(Boolean); if (!question.trim() || (['SINGLE_CHOICE', 'MULTIPLE_CHOICE'].includes(questionType) && !choices.length)) { setError('Enter a question and add choice options where required.'); return; } setQuestionItems([...questionItems, { id: crypto.randomUUID(), question_text: question.trim(), question_type: questionType, required: true, ...(['SINGLE_CHOICE', 'MULTIPLE_CHOICE'].includes(questionType) ? { options: choices } : {}) }]); setQuestion(''); setOptions(''); setError(null); }}>Add question ({questionItems.length})</Button>{questionItems.map((item, index) => <div key={item.id} className="flex items-center justify-between rounded border p-2 text-sm"><span>{index + 1}. {item.question_text} · {item.question_type}</span><Button size="sm" variant="ghost" type="button" onClick={() => setQuestionItems(questionItems.filter((q) => q.id !== item.id))}>Remove</Button></div>)}<div className="flex justify-end"><Button size="sm" type="submit" disabled={!activeParishId || createMutation.isPending}>Create draft</Button></div></form></Card>}
    <Card title="Surveys in this parish"><div className="space-y-2">{surveysQuery.data?.map((survey: Row) => <div key={survey.id} className="flex flex-wrap items-center justify-between gap-3 rounded border p-3"><button className="text-left" onClick={() => { setSelected(survey); setAnswers({}); setError(null); }}><strong className="text-sm">{survey.title}</strong><span className="ml-2 text-xs text-gray-500">{survey.response_count} responses</span><p className="text-xs text-gray-500">{survey.description}</p></button><div className="flex items-center gap-2"><Badge variant={survey.status === 'ACTIVE' ? 'success' : 'neutral'}>{survey.status}</Badge>{canManage && survey.status !== 'ARCHIVED' && <Button size="sm" variant="outline" onClick={() => updateMutation.mutate({ id: survey.id, status: survey.status === 'ACTIVE' ? 'CLOSED' : 'ACTIVE' })}>{survey.status === 'ACTIVE' ? 'Close responses' : 'Activate'}</Button>}<Button size="sm" variant="outline" onClick={() => setSelected(survey)}>Review</Button></div></div>)}{!surveysQuery.isLoading && !surveysQuery.data?.length && <p className="py-4 text-sm text-gray-500">{surveysQuery.isError ? 'Unable to load surveys.' : 'No surveys are assigned to this parish.'}</p>}</div></Card>
    {selected && <div className="grid gap-4 lg:grid-cols-2"><Card title={`Survey · ${selected.title}`}><p className="mb-4 text-xs text-gray-500">Status: {selected.status} · {selected.response_count} submissions</p>{selected.status === 'ACTIVE' && canSubmit && <form className="space-y-4" onSubmit={(e) => { e.preventDefault(); setError(null); respondMutation.mutate(); }}>{selected.questions?.map((q: Row) => <div key={q.id}><label className="block text-sm font-medium">{q.question_text}{q.required ? ' *' : ''}</label>{renderQuestion(q)}</div>)}{selected.questions?.length ? <Button size="sm" type="submit" disabled={respondMutation.isPending}>Submit parish response</Button> : <p className="text-xs text-gray-500">This survey has no questions configured.</p>}</form>}</Card><Card title="Response summary">{summaryQuery.isLoading ? <p className="text-sm text-gray-500">Loading summary…</p> : summaryQuery.data ? <><p className="mb-3 text-sm">Total responses: <strong>{summaryQuery.data.total_responses}</strong></p><div className="space-y-3">{Object.entries(summaryQuery.data.question_summaries || {}).map(([key, value]: [string, any]) => <div key={key} className="rounded bg-gray-50 p-3 text-xs"><strong>{selected.questions?.find((q: Row) => q.id === key)?.question_text || key}</strong><pre className="mt-2 whitespace-pre-wrap">{JSON.stringify(value, null, 2)}</pre></div>)}</div></> : <p className="text-sm text-gray-500">Summary not available.</p>}</Card></div>}
  </div>;
};
