import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000,
})

export async function analyzeContract(file, instructions, voiceNote) {
  const form = new FormData()
  form.append('file', file)
  form.append('instructions', instructions || '')
  if (voiceNote) {
    form.append('voice_note', voiceNote)
  }
  const { data } = await api.post('/contract/analyze', form)
  return data
}

export async function healthCheck() {
  const { data } = await api.get('/health')
  return data
}
