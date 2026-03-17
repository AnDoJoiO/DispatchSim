import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useUiStore = defineStore('ui', () => {
  const debriefingId = ref(null)  // null = closed
  const editUserId   = ref(null)  // null = closed

  function openDebriefing(id)  { debriefingId.value = id }
  function closeDebriefing()   { debriefingId.value = null }
  function openEditUser(id)    { editUserId.value = id }
  function closeEditUser()     { editUserId.value = null }

  return { debriefingId, editUserId, openDebriefing, closeDebriefing, openEditUser, closeEditUser }
})
