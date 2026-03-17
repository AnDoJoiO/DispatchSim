import { describe, it, expect } from 'vitest'
import * as config from '@/config'

describe('config', () => {
  it('exports all expected constants', () => {
    expect(config.VOICE_THRESHOLD).toBeTypeOf('number')
    expect(config.SILENCE_MS).toBeTypeOf('number')
    expect(config.MIN_DURATION_MS).toBeTypeOf('number')
    expect(config.MIN_BLOB_BYTES).toBeTypeOf('number')
    expect(config.SILENCE_DELAY).toBeTypeOf('number')
    expect(config.MIC_GRACE_PERIOD).toBeTypeOf('number')
    expect(config.TTS_RESUME_DELAY).toBeTypeOf('number')
    expect(config.MIN_REAL_WORDS).toBeTypeOf('number')
    expect(config.MAX_SILENCE_REACTIONS).toBeTypeOf('number')
    expect(config.WORD_RE).toBeInstanceOf(RegExp)
  })

  it('VOICE_THRESHOLD is reasonable (10-100)', () => {
    expect(config.VOICE_THRESHOLD).toBeGreaterThanOrEqual(10)
    expect(config.VOICE_THRESHOLD).toBeLessThanOrEqual(100)
  })

  it('SILENCE_DELAY is at least 5 seconds', () => {
    expect(config.SILENCE_DELAY).toBeGreaterThanOrEqual(5000)
  })

  it('MAX_SILENCE_REACTIONS is positive', () => {
    expect(config.MAX_SILENCE_REACTIONS).toBeGreaterThan(0)
  })

  it('WORD_RE matches real words and ignores short ones', () => {
    const matches = 'Hola món a b'.match(config.WORD_RE) || []
    expect(matches).toContain('Hola')
    expect(matches).toContain('món')
    expect(matches).not.toContain('a')
    expect(matches).not.toContain('b')
  })
})
