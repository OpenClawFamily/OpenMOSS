<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
    if (!password.value) {
        error.value = '请输入密码'
        return
    }
    loading.value = true
    error.value = ''
    try {
        await auth.login(password.value)
        // 初始化完成后跳转提示词管理，否则跳转仪表盘
        const target = route.query.from === 'setup' ? '/prompts' : '/dashboard'
        router.push(target)
    } catch (e: unknown) {
        const err = e as { response?: { data?: { detail?: string } } }
        error.value = err.response?.data?.detail || '登录失败，请检查密码'
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="flex min-h-screen items-center justify-center bg-background">
        <Card class="w-full max-w-sm">
            <CardHeader class="text-center">
                <div
                    class="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground text-xl font-bold">
                    M
                </div>
                <CardTitle class="text-2xl">OpenMOSS</CardTitle>
                <CardDescription>多 AI Agent 自组织协作平台</CardDescription>
            </CardHeader>
            <CardContent>
                <form @submit.prevent="handleLogin" class="space-y-4">
                    <div class="space-y-2">
                        <Label for="password">管理员密码</Label>
                        <Input id="password" v-model="password" type="password" placeholder="请输入管理员密码"
                            :disabled="loading" @keyup.enter="handleLogin" />
                    </div>
                    <p v-if="error" class="text-sm text-destructive">{{ error }}</p>
                    <details class="group text-center">
                        <summary
                            class="text-xs text-muted-foreground/60 cursor-pointer hover:text-muted-foreground transition-colors select-none list-none [&::-webkit-details-marker]:hidden">
                            忘记密码？
                        </summary>
                        <div
                            class="mt-2 rounded-lg border bg-muted/30 p-3 text-left text-xs text-muted-foreground space-y-1">
                            <p>1. 编辑服务器上的 <code class="rounded bg-muted px-1 py-0.5">config.yaml</code></p>
                            <p>2. 将 <code class="rounded bg-muted px-1 py-0.5">admin.password</code> 值改为新的明文密码</p>
                            <p>3. 重启服务，系统会自动加密处理</p>
                        </div>
                    </details>
                    <Button type="submit" class="w-full" :disabled="loading">
                        {{ loading ? '登录中...' : '登录' }}
                    </Button>
                </form>
            </CardContent>
        </Card>
    </div>
</template>