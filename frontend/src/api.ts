import type {
  AskResponse,
  Explanation,
  Health,
  IdentifyResponse,
  Lang,
  MedIn,
  MedicineListResponse,
  SavedMedicine,
} from './types'

// ---- Device ID ----
// No login: each phone/browser gets a random ID, saved forever in localStorage.
// The backend uses it to keep each person's "My medicines" list separate.

const DEVICE_KEY = 'mediclear-device-id'

export function getDeviceId(): string {
  let id = localStorage.getItem(DEVICE_KEY)
  if (!id) {
    id = crypto.randomUUID()
    localStorage.setItem(DEVICE_KEY, id)
  }
  return id
}

// ---- Errors ----
// An Error that also remembers the HTTP status (e.g. 503 = service busy).

export class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

// ---- The one helper every call goes through ----

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers)
  headers.set('X-Device-Id', getDeviceId())
  // JSON bodies are strings; photo uploads are FormData and set their own type
  if (typeof options.body === 'string') {
    headers.set('Content-Type', 'application/json')
  }

  let res: Response
  try {
    res = await fetch(path, { ...options, headers })
  } catch {
    // fetch itself only fails when there is no network at all
    throw new ApiError(0, 'Cannot reach MediClear. Please check your internet connection.')
  }

  if (!res.ok) {
    let message = `Something went wrong (${res.status}). Please try again.`
    try {
      // FastAPI errors look like {"detail": "The voice service is busy..."}
      const body = await res.json()
      if (typeof body.detail === 'string') message = body.detail
    } catch {
      // the error body was not JSON, so keep the default message
    }
    throw new ApiError(res.status, message)
  }

  if (res.status === 204) return undefined as T // DELETE returns no body
  return (await res.json()) as T
}

// ---- One function per endpoint ----

export const api = {
  health: () => request<Health>('/api/health'),

  identifyText: (query: string) =>
    request<IdentifyResponse>('/api/identify/text', {
      method: 'POST',
      body: JSON.stringify({ query }),
    }),

  identifyPhoto: (file: File) => {
    const form = new FormData()
    form.append('image', file) // "image" must match the FastAPI parameter name
    return request<IdentifyResponse>('/api/identify', { method: 'POST', body: form })
  },

  explain: (drugKey: string, lang: Lang) =>
    request<Explanation>(`/api/explain/${encodeURIComponent(drugKey)}?lang=${lang}`),

  // Not a fetch: <audio src={...}> downloads the mp3 by itself
  audioUrl: (drugKey: string, lang: Lang) =>
    `/api/audio/${encodeURIComponent(drugKey)}?lang=${lang}`,

  ask: (question: string, lang: Lang, drugKey?: string) =>
    request<AskResponse>('/api/ask', {
      method: 'POST',
      body: JSON.stringify({ question, lang, drug_key: drugKey ?? null }),
    }),

  listMedicines: () => request<MedicineListResponse>('/api/medicines'),

  saveMedicine: (med: MedIn) =>
    request<SavedMedicine>('/api/medicines', {
      method: 'POST',
      body: JSON.stringify(med),
    }),

  deleteMedicine: (id: number) =>
    request<void>(`/api/medicines/${id}`, { method: 'DELETE' }),
}