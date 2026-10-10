// TypeScript copies of backend/app/schemas.py. Keep them in sync.

export type Lang = 'en' | 'hi' | 'mr'

export type Health = {
  status: string
  drugs: number
  brands: number
}

// ---- Identify (POST /api/identify, /api/identify/text) ----

export type IngredientInfo = {
  key: string // e.g. "paracetamol", used for explain/audio/save
  name: string // display name
  strength: string | null
  source: string | null
  verified: boolean
}

export type IdentifyStatus = 'ok' | 'unreadable' | 'low_confidence' | 'not_in_db' | 'error'

export type IdentifyResponse = {
  status: IdentifyStatus
  brand: string | null
  ingredients: IngredientInfo[]
  unverified: string[]
  reasons: string[]
  disclaimer: string
}

// ---- Explain (GET /api/explain/{drug_key}) ----

export type Explanation = {
  drug_key: string
  name: string
  lang: Lang
  available: boolean // false when no trusted source exists
  message: string | null // shown instead when not available
  used_for: string
  how_it_works: string
  how_to_take: string
  avoid: string[]
  side_effects: string[]
  see_doctor_if: string[]
  sources: string[]
  generated_by: 'database' | 'llm' | 'none'
  disclaimer: string
}

export type AskLabel =
  | 'refuse_to_doctor'
  | 'emergency_112'
  | 'answer_from_db'
  | 'not_in_db'
  | 'stay_in_scope'

export type AskResponse = {
  label: AskLabel
  message: string | null // fixed text for every label except answer_from_db
  explanation: Explanation | null // only for answer_from_db
  disclaimer: string
}

// ---- My medicines (GET/POST/DELETE /api/medicines) ----

export type AlertLevel = 'warning' | 'timing' | 'caution'

export type InteractionAlert = {
  level: AlertLevel
  kind: 'same_ingredient' | 'pair' | 'same_class'
  between: string[] // the two medicine labels
  ingredients: string[]
  message: string
  sources: string[]
}

export type MedIn = {
  label: string
  ingredients: string[] // ingredient keys
}

export type SavedMedicine = {
  id: number
  label: string
  ingredients: string[]
  created_at: string // ISO date string; JSON has no date type
}

export type MedicineListResponse = {
  medicines: SavedMedicine[]
  alerts: InteractionAlert[]
  disclaimer: string
}

// Frontend only: the medicine the user is currently looking at
export type Drug = {
  key: string
  name: string
}