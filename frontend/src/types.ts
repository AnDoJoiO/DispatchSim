// ── Models principals ─────────────────────────────────────

export interface User {
  id: number
  username: string
  role: 'admin' | 'formador' | 'operador'
  is_active: boolean
  expires_at?: string | null
}

export interface Scenario {
  id: number
  title: string
  incident_type: string
  base_location: string
  location_exact?: string | null
  victim_status?: string | null
  initial_emotion?: string | null
  creator_id?: number | null
  created_at: string
}

export interface Incident {
  id: number
  type: string
  location: string
  description: string
  priority: number
  created_at: string
  creator_id?: number | null
  operator_id?: number | null
  scenario_id?: number | null
  call_status: 'esperant' | 'en_curs' | 'finalitzada'
  call_start_at?: string | null
  type_decided_at?: string | null
  call_end_at?: string | null
}

export interface ChatMessage {
  id: number
  role: 'operator' | 'alertant' | 'system'
  content: string
  voice?: string | null
}

export interface ChatResponse {
  role: string
  content: string
  voice: string
  call_ended: boolean
}

export interface TokenResponse {
  access_token: string
  user: User
}

// ── History ──────────────────────────────────────────────

export interface CallHistorySummary {
  id: number
  type: string
  location: string
  priority: number
  call_end_at: string
  duration_seconds: number | null
  scenario_title: string | null
  message_count: number
}

export interface InterventionData {
  id: number
  incident_id: number
  exact_address: string
  contact_phone: string
  num_injured: number
  additional_risks: string
  operator_notes: string
  saved_at: string
}

export interface TranscriptMessage {
  role: string
  content: string
  timestamp: string
}

export interface CallDebriefingDetail {
  id: number
  type: string
  location: string
  description: string
  priority: number
  call_start_at: string | null
  call_end_at: string | null
  type_decided_at: string | null
  duration_seconds: number | null
  initial_response_seconds: number | null
  scenario_title: string | null
  transcript: TranscriptMessage[]
  intervention: InterventionData | null
}

// ── Payloads ─────────────────────────────────────────────

export interface InterventionSave {
  incident_id: number
  exact_address: string
  contact_phone: string
  num_injured: number
  additional_risks: string
  operator_notes: string
}

export interface ScenarioCreate {
  title: string
  incident_type: string
  base_location: string
  location_exact?: string
  victim_status?: string
  initial_emotion?: string
  instructions_ia: string
}

export interface IncidentCreate {
  scenario_id?: number
  type?: string
  location?: string
  description?: string
  priority: number
}
