<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-header class="navbar">
    <div class="navbar-left">
      <router-link to="/" class="navbar-brand">Network Ops</router-link>
      <el-menu
        mode="horizontal"
        :ellipsis="false"
        router
        class="navbar-menu"
      >
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/devices">设备管理</el-menu-item>
      </el-menu>
    </div>
    <div class="navbar-right">
      <span class="navbar-user">{{ authStore.user?.username }}</span>
      <el-button type="danger" text @click="handleLogout">退出</el-button>
    </div>
  </el-header>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 20px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  position: sticky;
  top: 0;
  z-index: 100;
}
.navbar-left {
  display: flex;
  align-items: center;
  gap: 24px;
}
.navbar-brand {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
  text-decoration: none;
}
.navbar-menu {
  border-bottom: none;
}
.navbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.navbar-user {
  font-size: 14px;
  color: #606266;
}
</style>
