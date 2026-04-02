const BASE = '/world-api'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`API error ${res.status}: ${await res.text()}`)
  }
  return res.json()
}

export interface Epoch {
  id: string
  title: string
  time_start: number | null
  time_end: number | null
  summary: string | null
  version: number
  is_current: boolean
  chapter_count: number
}

export interface Chapter {
  id: string
  epoch_id: string
  title: string
  time_start: number | null
  time_end: number | null
  chapter_summary: string | null
  chapter_order: number
  version: number
  is_current: boolean
}

export interface ChapterDetail extends Chapter {
  actors: Actor[]
  events: CanonEvent[]
  places: Place[]
}

export interface Actor {
  id: string
  canonical_name: string
  actor_type: string
  summary: string | null
  time_start: number | null
  time_end: number | null
}

export interface CanonEvent {
  id: string
  canonical_name: string
  event_type: string
  summary: string | null
  time_start: number | null
  time_end: number | null
}

export interface Place {
  id: string
  canonical_name: string
  place_type: string
  summary: string | null
}

export interface SourceSet {
  id: string
  chapter_id: string
  source_record_id: string
  title: string | null
  excerpt: string | null
  relevance_weight: number
  image_ref: string | null
  source_type: string | null
}

export interface ContextSet {
  id: string
  chapter_id: string
  contextual_statement_id: string
  summary: string | null
  artifact_description: string | null
  relevance_weight: number
}

export interface ArtifactSet {
  id: string
  chapter_id: string
  raw_object_id: string
  title: string | null
  description: string | null
  image_url: string | null
  location: string | null
  date_label: string | null
}

export interface ImageSet {
  id: string
  chapter_id: string
  image_url: string | null
  caption: string | null
  image_type: string | null
  display_order: number
}

export interface NarrationPacket {
  id: string
  chapter_id: string
  intro_summary: string | null
  core_summary: string | null
  branch_summary: string | null
  version: number
}

export interface ChatQueryResult {
  session_id: string
  answer_packet_id: string
  answer: string
  answer_mode: string
  confidence: number
  sources: AnswerSource[]
  contexts: AnswerContext[]
}

export interface AnswerSource {
  id: string
  source_record_id: string
  excerpt: string | null
  support_type: string | null
  weight: number
}

export interface AnswerContext {
  id: string
  contextual_statement_id: string
  summary: string | null
  weight: number
}

export interface ChatSession {
  id: string
  chapter_id: string | null
  created_at: string
  updated_at: string
  message_count: number
}

export interface ChatMessage {
  id: string
  session_id: string
  role: string
  content: string
  answer_packet_id: string | null
  created_at: string
}

export const api = {
  getEpochs: () => request<Epoch[]>('/epochs'),
  getChapters: (epochId?: string) =>
    request<Chapter[]>(epochId ? `/chapters?epoch_id=${epochId}` : '/chapters'),
  getChapterDetail: (id: string) => request<ChapterDetail>(`/chapters/${id}`),
  getChapterSources: (id: string) => request<SourceSet[]>(`/chapters/${id}/sources`),
  getChapterContext: (id: string) => request<ContextSet[]>(`/chapters/${id}/context`),
  getChapterArtifacts: (id: string) => request<ArtifactSet[]>(`/chapters/${id}/artifacts`),
  getChapterImages: (id: string) => request<ImageSet[]>(`/chapters/${id}/images`),
  getNarration: (chapterId: string) => request<NarrationPacket[]>(`/narration-packets/${chapterId}`),
  chatQuery: (query: string, chapterId?: string, sessionId?: string) =>
    request<ChatQueryResult>('/chat/query', {
      method: 'POST',
      body: JSON.stringify({
        query,
        chapter_id: chapterId || null,
        session_id: sessionId || null,
      }),
    }),
  getChatSessions: (chapterId?: string) =>
    request<ChatSession[]>(chapterId ? `/chat/sessions?chapter_id=${chapterId}` : '/chat/sessions'),
  getChatSession: (id: string) =>
    request<ChatSession & { messages: ChatMessage[] }>(`/chat/sessions/${id}`),
}
