import { ref, watch } from 'vue'

const isDark = ref(false)

// 从 localStorage 恢复主题
const saved = localStorage.getItem('theme')
if (saved === 'dark') {
  isDark.value = true
  document.documentElement.classList.add('dark')
}

export function useTheme() {
  function toggleTheme() {
    isDark.value = !isDark.value
    if (isDark.value) {
      document.documentElement.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }

  return { isDark, toggleTheme }
}
