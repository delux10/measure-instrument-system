<template>
  <div style="
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    position: relative; overflow: hidden;
  ">
    <!-- 背景装饰圆 -->
    <div style="
      position: absolute; width: 400px; height: 400px; border-radius: 50%;
      background: rgba(255,255,255,0.05); top: -100px; right: -100px;
    "></div>
    <div style="
      position: absolute; width: 300px; height: 300px; border-radius: 50%;
      background: rgba(255,255,255,0.04); bottom: -50px; left: -80px;
    "></div>

    <transition name="login-zoom" appear>
      <div style="
        width: 420px; background: rgba(255,255,255,0.95);
        backdrop-filter: blur(20px); border-radius: 16px;
        padding: 40px; box-shadow: 0 20px 60px rgba(0,0,0,0.15);
        position: relative; z-index: 1;
      ">
        <!-- 标题 -->
        <div style="text-align: center; margin-bottom: 32px">
          <div style="
            width: 56px; height: 56px; border-radius: 14px;
            background: linear-gradient(135deg, #409EFF, #337ecc);
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 16px; box-shadow: 0 4px 12px rgba(64,158,255,0.3);
          ">
            <el-icon :size="28" color="#fff"><Monitor /></el-icon>
          </div>
          <h2 style="margin: 0 0 4px; font-size: 22px; font-weight: 700; color: #1a1a2e">计量仪器管理系统</h2>
          <p style="margin: 0; color: #909399; font-size: 14px">请登录您的账户以继续</p>
        </div>

        <!-- 表单 -->
        <el-form
          ref="formRef"
          :model="loginForm"
          :rules="rules"
          size="large"
          @keyup.enter="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="用户名"
              :prefix-icon="User"
              style="height: 44px"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="密码"
              :prefix-icon="Lock"
              show-password
              style="height: 44px"
            />
          </el-form-item>

          <el-form-item style="margin-bottom: 0">
            <el-button
              type="primary"
              style="width: 100%; height: 44px; font-size: 15px; border-radius: 10px;
                     background: linear-gradient(135deg, #409EFF, #337ecc);
                     border: none; box-shadow: 0 4px 12px rgba(64,158,255,0.3)"
              :loading="loading"
              @click="handleLogin"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await userStore.login(loginForm)
    ElMessage.success('登录成功')
    router.push('/dashboard')
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || '登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-zoom-enter-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
}
.login-zoom-enter-from {
  opacity: 0;
  transform: scale(0.92) translateY(20px);
}
</style>
