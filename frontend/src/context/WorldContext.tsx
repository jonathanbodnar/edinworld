import { createContext, useContext, useState, useCallback, useEffect, type ReactNode } from 'react'
import type {
  Epoch, EpochOverview, CultureDetail,
  ChapterDetail, SourceSet, ContextSet, ArtifactSet, ImageSet, NarrationPacket,
} from '../api'
import { api } from '../api'

interface WorldState {
  epochs: Epoch[]
  epochsLoading: boolean

  activeEpochId: string | null
  epochOverview: EpochOverview | null
  epochLoading: boolean

  activeCulture: string | null
  cultureDetail: CultureDetail | null
  cultureLoading: boolean

  activeChapterId: string | null
  chapterDetail: ChapterDetail | null
  sources: SourceSet[]
  contexts: ContextSet[]
  artifacts: ArtifactSet[]
  images: ImageSet[]
  narration: NarrationPacket | null
  chapterLoading: boolean
}

interface WorldContextValue extends WorldState {
  selectEpoch: (id: string) => Promise<void>
  selectCulture: (name: string | null) => Promise<void>
  selectChapter: (id: string) => Promise<void>
  clearSelection: () => void
}

const WorldCtx = createContext<WorldContextValue | null>(null)

export function useWorldContext() {
  const ctx = useContext(WorldCtx)
  if (!ctx) throw new Error('useWorldContext must be used within WorldProvider')
  return ctx
}

const INITIAL: WorldState = {
  epochs: [],
  epochsLoading: true,
  activeEpochId: null,
  epochOverview: null,
  epochLoading: false,
  activeCulture: null,
  cultureDetail: null,
  cultureLoading: false,
  activeChapterId: null,
  chapterDetail: null,
  sources: [],
  contexts: [],
  artifacts: [],
  images: [],
  narration: null,
  chapterLoading: false,
}

export function WorldProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<WorldState>(INITIAL)

  useEffect(() => {
    api.getEpochs()
      .then(epochs => setState(prev => ({ ...prev, epochs, epochsLoading: false })))
      .catch(err => {
        console.error('Failed to load epochs:', err)
        setState(prev => ({ ...prev, epochsLoading: false }))
      })
  }, [])

  const selectEpoch = useCallback(async (id: string) => {
    setState(prev => ({
      ...prev,
      activeEpochId: id,
      epochLoading: true,
      activeCulture: null,
      cultureDetail: null,
      activeChapterId: null,
      chapterDetail: null,
      sources: [],
      contexts: [],
      artifacts: [],
      images: [],
      narration: null,
    }))
    try {
      const overview = await api.getEpochOverview(id)
      setState(prev => ({ ...prev, epochOverview: overview, epochLoading: false }))
    } catch (err) {
      console.error('Failed to load epoch overview:', err)
      setState(prev => ({ ...prev, epochLoading: false }))
    }
  }, [])

  const selectCulture = useCallback(async (name: string | null) => {
    if (!name) {
      setState(prev => ({ ...prev, activeCulture: null, cultureDetail: null }))
      return
    }
    setState(prev => ({ ...prev, activeCulture: name, cultureLoading: true }))
    try {
      const detail = await api.getCultureDetail(state.activeEpochId!, name)
      setState(prev => ({ ...prev, cultureDetail: detail, cultureLoading: false }))
    } catch (err) {
      console.error('Failed to load culture detail:', err)
      setState(prev => ({ ...prev, cultureLoading: false }))
    }
  }, [state.activeEpochId])

  const selectChapter = useCallback(async (id: string) => {
    setState(prev => ({ ...prev, activeChapterId: id, chapterLoading: true }))
    try {
      const [detail, sources, contexts, artifacts, images] = await Promise.all([
        api.getChapterDetail(id),
        api.getChapterSources(id),
        api.getChapterContext(id),
        api.getChapterArtifacts(id),
        api.getChapterImages(id),
      ])

      let narration: NarrationPacket | null = null
      try {
        const narrations = await api.getNarration(id)
        if (narrations.length > 0) narration = narrations[0]
      } catch { /* narration may not exist yet */ }

      setState(prev => ({
        ...prev,
        activeChapterId: id,
        chapterDetail: detail,
        sources,
        contexts,
        artifacts,
        images,
        narration,
        chapterLoading: false,
      }))
    } catch (err) {
      console.error('Failed to load chapter:', err)
      setState(prev => ({ ...prev, chapterLoading: false }))
    }
  }, [])

  const clearSelection = useCallback(() => {
    setState(prev => ({
      ...prev,
      activeEpochId: null,
      epochOverview: null,
      activeCulture: null,
      cultureDetail: null,
      activeChapterId: null,
      chapterDetail: null,
      sources: [],
      contexts: [],
      artifacts: [],
      images: [],
      narration: null,
    }))
  }, [])

  return (
    <WorldCtx.Provider value={{ ...state, selectEpoch, selectCulture, selectChapter, clearSelection }}>
      {children}
    </WorldCtx.Provider>
  )
}
