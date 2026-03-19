<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useDebounceFn } from '@vueuse/core'
import {
    adminAgentApi,
    adminApi,
    type AdminAgentItem,
    type AdminAgentDetail,
    type AdminPageResponse,
} from '@/api/client'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Separator } from '@/components/ui/separator'
import { TooltipProvider } from '@/components/ui/tooltip'
import TextOverflowTooltip from '@/components/common/TextOverflowTooltip.vue'
import {
    Search,
    RefreshCw,
    Loader2,
    AlertCircle,
    Users,
    ArrowLeft,
    ArrowRight,
    KeyRound,
    Copy,
    Check,
} from 'lucide-vue-next'

// ─── 状态 ───

const PAGE_SIZE = 20

const keyword = ref('')
const roleFilter = ref('all')
const page = ref(1)

const loading = ref(false)
const loadingDetail = ref(false)
const listError = ref('')
const detailError = ref('')

const selectedAgentId = ref<string | null>(null)
const selectedAgent = ref<AdminAgentDetail | null>(null)

const pageData =
    ref<AdminPageResponse<AdminAgentItem>>(createEmptyPage<AdminAgentItem>())

let listRequestId = 0
let detailRequestId = 0
const detailKey = ref(0)

// ─── 选项 ───

const roleOptions = [
    { value: 'all', label: '全部角色' },
    { value: 'planner', label: '规划者' },
    { value: 'executor', label: '执行者' },
    { value: 'reviewer', label: '审查者' },
    { value: 'patrol', label: '巡查者' },
]

// ─── 工具函数 ───

function createEmptyPage<T>(): AdminPageResponse<T> {
    return { items: [], total: 0, page: 1, page_size: PAGE_SIZE, total_pages: 1, has_more: false }
}

function formatRole(role: string) {
    return ({ planner: '规划者', executor: '执行者', reviewer: '审查者', patrol: '巡查者' }[role] ?? role)
}

function getRoleBadgeClass(role: string) {
    return ({
        planner: 'border-violet-200 bg-violet-50 text-violet-700',
        executor: 'border-sky-200 bg-sky-50 text-sky-700',
        reviewer: 'border-amber-200 bg-amber-50 text-amber-700',
        patrol: 'border-teal-200 bg-teal-50 text-teal-700',
    }[role] ?? 'border-border bg-muted text-muted-foreground')
}

function formatStatus(status: string) {
    return ({ available: '在线', busy: '忙碌' }[status] ?? status)
}

function getStatusDotClass(status: string) {
    return ({
        available: 'bg-emerald-500',
        busy: 'bg-amber-500 animate-pulse',
    }[status] ?? 'bg-slate-400')
}

function formatDate(value: string | null) {
    if (!value) return '未记录'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '未记录'
    return new Intl.DateTimeFormat('zh-CN', {
        month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit',
    }).format(date)
}

function formatRelativeTime(value: string | null) {
    if (!value) return '从未'
    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return '从未'
    const now = Date.now()
    const diff = now - date.getTime()
    const mins = Math.floor(diff / 60000)
    if (mins < 1) return '刚刚'
    if (mins < 60) return `${mins} 分钟前`
    const hours = Math.floor(mins / 60)
    if (hours < 24) return `${hours} 小时前`
    const days = Math.floor(hours / 24)
    return `${days} 天前`
}

// ─── 数据加载 ───

const reloadDebounced = useDebounceFn(() => {
    page.value = 1
    void loadAgents()
}, 280)

watch([keyword, roleFilter], () => {
    loading.value = true
    reloadDebounced()
})

onMounted(() => {
    void loadAgents()
})

async function loadAgents() {
    const requestId = ++listRequestId
    loading.value = true
    listError.value = ''

    try {
        const response = await adminAgentApi.list({
            page: page.value,
            page_size: PAGE_SIZE,
            keyword: keyword.value.trim() || undefined,
            role: roleFilter.value === 'all' ? undefined : roleFilter.value,
            sort_by: 'created_at',
            sort_order: 'desc',
        })

        if (requestId !== listRequestId) return

        pageData.value = response.data

        if (!response.data.items.length) {
            selectedAgentId.value = null
            selectedAgent.value = null
            return
        }

        const firstAgent = response.data.items[0]
        if (!firstAgent) {
            selectedAgentId.value = null
            selectedAgent.value = null
            return
        }
        const currentIds = new Set(response.data.items.map(i => i.id))
        const nextId =
            selectedAgentId.value && currentIds.has(selectedAgentId.value)
                ? selectedAgentId.value
                : firstAgent.id

        const prevId = selectedAgentId.value
        selectedAgentId.value = nextId
        if (nextId !== prevId || !selectedAgent.value) {
            void loadAgentDetail(nextId)
        }
    } catch (error) {
        if (requestId !== listRequestId) return
        console.error('Failed to load agents', error)
        listError.value = 'Agent 列表加载失败，请稍后再试。'
        pageData.value = createEmptyPage<AdminAgentItem>()
        selectedAgentId.value = null
        selectedAgent.value = null
    } finally {
        if (requestId === listRequestId) loading.value = false
    }
}

async function loadAgentDetail(agentId: string) {
    const requestId = ++detailRequestId
    loadingDetail.value = true
    detailError.value = ''

    try {
        const response = await adminAgentApi.get(agentId)
        if (requestId !== detailRequestId || selectedAgentId.value !== agentId) return
        selectedAgent.value = response.data
        detailKey.value++
    } catch (error) {
        if (requestId !== detailRequestId) return
        console.error('Failed to load agent detail', error)
        detailError.value = 'Agent 详情加载失败，请重试。'
        selectedAgent.value = null
    } finally {
        if (requestId === detailRequestId) loadingDetail.value = false
    }
}

function selectAgent(agentId: string) {
    if (selectedAgentId.value === agentId) return
    selectedAgentId.value = agentId
    void loadAgentDetail(agentId)
}

function goToPage(p: number) {
    if (p < 1 || p > pageData.value.total_pages || p === page.value) return
    page.value = p
    void loadAgents()
}

function refreshList() {
    void loadAgents()
}

// ─── 计算属性 ───

const workloadTotal = computed(() => {
    if (!selectedAgent.value) return 0
    return selectedAgent.value.open_sub_task_count
})

// ─── 操作 ───

const showResetKeyConfirm = ref(false)
const showNewKeyDialog = ref(false)
const newApiKey = ref('')
const resettingKey = ref(false)
const keyCopied = ref(false)

async function handleResetKey() {
    if (!selectedAgentId.value) return
    resettingKey.value = true
    try {
        const response = await adminApi.resetKey(selectedAgentId.value)
        newApiKey.value = response.data.new_api_key
        showResetKeyConfirm.value = false
        showNewKeyDialog.value = true
    } catch (error) {
        console.error('Failed to reset key', error)
    } finally {
        resettingKey.value = false
    }
}

async function copyNewKey() {
    try {
        await navigator.clipboard.writeText(newApiKey.value)
        keyCopied.value = true
        setTimeout(() => { keyCopied.value = false }, 2000)
    } catch {
        // fallback: select text
    }
}
</script>

<template>
    <TooltipProvider>
        <div class="flex flex-col h-[calc(100vh-3.5rem)]">
            <!-- ─── 顶栏：搜索 + 筛选 + 刷新 ─── -->
            <header class="shrink-0 border-b border-border/40 bg-background px-4 py-3 space-y-2.5">
                <div class="flex items-center gap-3">
                    <div class="relative flex-1 max-w-md">
                        <Search
                            class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                        <Input v-model="keyword" class="h-9 bg-muted/30 pl-10 text-sm" placeholder="搜索 Agent 名称或描述…" />
                    </div>
                    <Badge variant="secondary" class="h-7 px-2.5 text-xs tabular-nums shrink-0">
                        {{ pageData.total }} 个 Agent
                    </Badge>
                    <Button variant="ghost" size="icon" class="h-8 w-8 shrink-0" :disabled="loading || loadingDetail"
                        @click="refreshList">
                        <RefreshCw class="h-3.5 w-3.5" :class="loading || loadingDetail ? 'animate-spin' : ''" />
                    </Button>
                </div>

                <div class="flex items-center gap-4">
                    <div class="flex flex-wrap gap-1.5">
                        <Button v-for="option in roleOptions" :key="option.value" size="sm"
                            :variant="roleFilter === option.value ? 'default' : 'ghost'"
                            class="h-7 rounded-full px-3 text-xs" @click="roleFilter = option.value">
                            {{ option.label }}
                        </Button>
                    </div>
                </div>
            </header>

            <!-- ─── 主体：左列表 + 右详情 ─── -->
            <div class="flex flex-1 min-h-0">
                <!-- Agent 列表 -->
                <div class="w-full lg:w-[380px] xl:w-[420px] shrink-0 border-r border-border/40 overflow-y-auto">
                    <!-- 错误 -->
                    <div v-if="listError" class="p-6 text-center">
                        <AlertCircle class="mx-auto h-5 w-5 text-muted-foreground" />
                        <p class="mt-2 text-sm">{{ listError }}</p>
                        <Button class="mt-3" size="sm" @click="refreshList">重新加载</Button>
                    </div>

                    <!-- 加载中 -->
                    <div v-else-if="loading" class="flex items-center justify-center py-16">
                        <Loader2 class="h-6 w-6 animate-spin text-muted-foreground" />
                    </div>

                    <!-- Agent 卡片列表 -->
                    <template v-else-if="pageData.items.length">
                        <div :key="`agents-${page}-${roleFilter}-${keyword}`" class="divide-y divide-border/30">
                            <button v-for="(agent, idx) in pageData.items" :key="agent.id" type="button"
                                class="w-full px-4 py-3 text-left transition-colors hover:bg-muted/30 animate-slide-up"
                                :class="selectedAgentId === agent.id ? 'bg-accent/50' : ''"
                                :style="{ animationDelay: `${idx * 40}ms` }" @click="selectAgent(agent.id)">
                                <div class="flex items-start justify-between gap-2">
                                    <div class="min-w-0 flex-1">
                                        <div class="flex items-center gap-1.5">
                                            <span class="inline-block w-1.5 h-1.5 rounded-full shrink-0"
                                                :class="getStatusDotClass(agent.status)" />
                                            <TextOverflowTooltip :text="agent.name" as="div"
                                                class="text-sm font-semibold leading-5" />
                                        </div>
                                        <TextOverflowTooltip :text="agent.description || '暂无描述'" as="p" :lines="1"
                                            class="mt-0.5 text-xs text-muted-foreground leading-4 pl-3" />
                                    </div>
                                    <Badge variant="outline" :class="getRoleBadgeClass(agent.role)"
                                        class="shrink-0 text-[10px] px-1.5">
                                        {{ formatRole(agent.role) }}
                                    </Badge>
                                </div>

                                <div class="mt-2 flex items-center gap-3 text-[11px] text-muted-foreground pl-3">
                                    <span class="tabular-nums font-medium"
                                        :class="agent.total_score >= 0 ? 'text-emerald-600' : 'text-rose-500'">
                                        {{ agent.total_score >= 0 ? '+' : '' }}{{ agent.total_score }} 分
                                    </span>
                                    <span v-if="agent.open_sub_task_count" class="tabular-nums">
                                        {{ agent.open_sub_task_count }} 个待办
                                    </span>
                                    <span v-if="agent.in_progress_count" class="text-sky-600 tabular-nums">
                                        {{ agent.in_progress_count }} 执行中
                                    </span>
                                    <span class="ml-auto tabular-nums">{{ formatRelativeTime(agent.last_request_at)
                                    }}</span>
                                </div>
                            </button>
                        </div>

                        <!-- 分页 -->
                        <div v-if="pageData.total_pages > 1"
                            class="flex items-center justify-center gap-2 py-3 border-t border-border/30 text-xs text-muted-foreground">
                            <Button variant="ghost" size="icon" class="h-7 w-7"
                                :disabled="pageData.page <= 1 || loading" @click="goToPage(pageData.page - 1)">
                                <ArrowLeft class="h-3 w-3" />
                            </Button>
                            <span class="tabular-nums">{{ pageData.page }} / {{ pageData.total_pages }}</span>
                            <Button variant="ghost" size="icon" class="h-7 w-7"
                                :disabled="pageData.page >= pageData.total_pages || loading"
                                @click="goToPage(pageData.page + 1)">
                                <ArrowRight class="h-3 w-3" />
                            </Button>
                        </div>
                    </template>

                    <!-- 空状态 -->
                    <div v-else class="flex flex-col items-center justify-center py-16 text-muted-foreground/50">
                        <Users class="h-6 w-6 mb-2" />
                        <p class="text-sm">没有找到匹配的 Agent</p>
                    </div>
                </div>

                <!-- ─── 右侧详情 ─── -->
                <div class="hidden lg:flex flex-col flex-1 min-h-0 overflow-y-auto">
                    <!-- 加载中 -->
                    <div v-if="loadingDetail" class="flex items-center justify-center flex-1">
                        <Loader2 class="h-6 w-6 animate-spin text-muted-foreground" />
                    </div>

                    <!-- 错误 -->
                    <div v-else-if="detailError"
                        class="flex flex-col items-center justify-center flex-1 text-muted-foreground/50">
                        <AlertCircle class="h-5 w-5 mb-2" />
                        <p class="text-sm">{{ detailError }}</p>
                        <Button v-if="selectedAgentId" class="mt-3" size="sm"
                            @click="loadAgentDetail(selectedAgentId)">重试</Button>
                    </div>

                    <!-- Agent 详情 -->
                    <div v-else-if="selectedAgent" :key="detailKey" class="p-6 space-y-6 animate-slide-up">
                        <!-- 头部 -->
                        <div>
                            <div class="flex items-start justify-between gap-3">
                                <div class="min-w-0 space-y-1">
                                    <h2 class="text-lg font-semibold leading-7">{{ selectedAgent.name }}</h2>
                                    <p class="text-sm text-muted-foreground leading-5">
                                        {{ selectedAgent.description || '暂无描述信息。' }}
                                    </p>
                                </div>
                                <div class="flex gap-1.5 shrink-0">
                                    <Badge variant="outline" :class="getRoleBadgeClass(selectedAgent.role)">
                                        {{ formatRole(selectedAgent.role) }}
                                    </Badge>
                                    <Badge variant="outline" class="gap-1">
                                        <span class="inline-block w-1.5 h-1.5 rounded-full"
                                            :class="getStatusDotClass(selectedAgent.status)" />
                                        {{ formatStatus(selectedAgent.status) }}
                                    </Badge>
                                </div>
                            </div>

                            <!-- 积分 + 排名 -->
                            <div class="mt-4 rounded-xl border border-border/50 bg-muted/20 p-3.5 space-y-3">
                                <div class="flex items-center justify-between">
                                    <span class="text-xs text-muted-foreground">积分总分</span>
                                    <span class="text-xl font-bold tabular-nums"
                                        :class="selectedAgent.total_score >= 0 ? 'text-emerald-600' : 'text-rose-500'">
                                        {{ selectedAgent.total_score >= 0 ? '+' : '' }}{{ selectedAgent.total_score }}
                                    </span>
                                </div>
                                <div class="flex gap-4 text-xs text-muted-foreground tabular-nums">
                                    <span>排名 <span class="font-medium text-foreground">{{ selectedAgent.rank
                                    }}</span> / {{ selectedAgent.total_agents }}</span>
                                    <span>奖励 <span class="font-medium text-emerald-600">{{
                                        selectedAgent.reward_count
                                            }}</span></span>
                                    <span>惩罚 <span class="font-medium text-rose-500">{{
                                        selectedAgent.penalty_count
                                            }}</span></span>
                                </div>
                            </div>
                        </div>

                        <!-- 工作负载 -->
                        <div>
                            <div class="text-xs font-medium text-muted-foreground/60 uppercase tracking-wider mb-2">
                                工作负载 · {{ workloadTotal }}
                            </div>
                            <div class="grid grid-cols-3 gap-2">
                                <div class="rounded-lg border border-border/50 bg-muted/20 p-3 text-center">
                                    <div class="text-lg font-bold tabular-nums text-indigo-600">
                                        {{ selectedAgent.assigned_count }}
                                    </div>
                                    <div class="text-[11px] text-muted-foreground mt-0.5">已分配</div>
                                </div>
                                <div class="rounded-lg border border-border/50 bg-muted/20 p-3 text-center">
                                    <div class="text-lg font-bold tabular-nums text-sky-600">
                                        {{ selectedAgent.in_progress_count }}
                                    </div>
                                    <div class="text-[11px] text-muted-foreground mt-0.5">执行中</div>
                                </div>
                                <div class="rounded-lg border border-border/50 bg-muted/20 p-3 text-center">
                                    <div class="text-lg font-bold tabular-nums text-amber-600">
                                        {{ selectedAgent.review_count }}
                                    </div>
                                    <div class="text-[11px] text-muted-foreground mt-0.5">待审查</div>
                                </div>
                                <div v-if="selectedAgent.rework_count"
                                    class="rounded-lg border border-border/50 bg-muted/20 p-3 text-center">
                                    <div class="text-lg font-bold tabular-nums text-orange-600">
                                        {{ selectedAgent.rework_count }}
                                    </div>
                                    <div class="text-[11px] text-muted-foreground mt-0.5">返工中</div>
                                </div>
                                <div v-if="selectedAgent.blocked_count"
                                    class="rounded-lg border border-border/50 bg-muted/20 p-3 text-center">
                                    <div class="text-lg font-bold tabular-nums text-rose-600">
                                        {{ selectedAgent.blocked_count }}
                                    </div>
                                    <div class="text-[11px] text-muted-foreground mt-0.5">阻塞</div>
                                </div>
                                <div class="rounded-lg border border-border/50 bg-muted/20 p-3 text-center">
                                    <div class="text-lg font-bold tabular-nums text-emerald-600">
                                        {{ selectedAgent.done_count }}
                                    </div>
                                    <div class="text-[11px] text-muted-foreground mt-0.5">已完成</div>
                                </div>
                            </div>
                        </div>

                        <Separator />

                        <!-- 时间信息 -->
                        <div class="space-y-2">
                            <div class="text-xs font-medium text-muted-foreground/60 uppercase tracking-wider mb-2">
                                时间信息
                            </div>
                            <div class="grid grid-cols-2 gap-3">
                                <div class="rounded-lg border border-border/50 bg-muted/20 p-3">
                                    <div class="text-[11px] text-muted-foreground/60">最近请求</div>
                                    <div class="mt-1 text-sm font-medium">
                                        {{ formatRelativeTime(selectedAgent.last_request_at) }}
                                    </div>
                                    <div class="text-[10px] text-muted-foreground mt-0.5">
                                        {{ formatDate(selectedAgent.last_request_at) }}
                                    </div>
                                </div>
                                <div class="rounded-lg border border-border/50 bg-muted/20 p-3">
                                    <div class="text-[11px] text-muted-foreground/60">最近活动</div>
                                    <div class="mt-1 text-sm font-medium">
                                        {{ formatRelativeTime(selectedAgent.last_activity_at) }}
                                    </div>
                                    <div class="text-[10px] text-muted-foreground mt-0.5">
                                        {{ formatDate(selectedAgent.last_activity_at) }}
                                    </div>
                                </div>
                            </div>
                            <div class="flex gap-4 text-[11px] text-muted-foreground/60 pt-1">
                                <span>创建于 {{ formatDate(selectedAgent.created_at) }}</span>
                                <span>Agent ID: {{ selectedAgent.id }}</span>
                            </div>
                        </div>

                        <Separator />

                        <!-- 操作 -->
                        <div>
                            <div class="text-xs font-medium text-muted-foreground/60 uppercase tracking-wider mb-3">
                                操作
                            </div>
                            <div class="flex flex-wrap gap-2">
                                <Button variant="outline" size="sm"
                                    class="gap-1.5 text-rose-600 hover:text-rose-700 hover:bg-rose-50"
                                    @click="showResetKeyConfirm = true">
                                    <KeyRound class="h-3.5 w-3.5" />
                                    重置 API Key
                                </Button>
                            </div>
                        </div>
                    </div>

                    <!-- 未选择 -->
                    <div v-if="!loadingDetail && !detailError && !selectedAgent"
                        class="flex flex-col items-center justify-center flex-1 text-muted-foreground/40">
                        <Users class="h-8 w-8 mb-3" />
                        <p class="text-sm font-medium text-muted-foreground/60">点击左侧 Agent 查看详情</p>
                        <p class="text-xs mt-1">积分、工作负载和活跃信息会在这里展示</p>
                    </div>
                </div>
            </div>
        </div>
    </TooltipProvider>

    <!-- 重置 API Key 确认弹窗 -->
    <Teleport to="body">
        <Transition name="fade">
            <div v-if="showResetKeyConfirm" class="fixed inset-0 z-50 flex items-center justify-center">
                <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="showResetKeyConfirm = false" />
                <div
                    class="relative z-10 w-full max-w-sm rounded-xl border bg-background p-6 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
                    <div class="space-y-2 text-center">
                        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-rose-100">
                            <KeyRound class="h-5 w-5 text-rose-600" />
                        </div>
                        <h2 class="text-lg font-semibold">重置 API Key</h2>
                        <p class="text-sm text-muted-foreground">
                            确认重置 <span class="font-medium text-foreground">{{ selectedAgent?.name }}</span> 的 API Key？旧
                            Key
                            将立即失效。
                        </p>
                    </div>
                    <div class="mt-6 flex gap-3">
                        <Button variant="outline" class="flex-1" :disabled="resettingKey"
                            @click="showResetKeyConfirm = false">取消</Button>
                        <Button variant="destructive" class="flex-1" :disabled="resettingKey" @click="handleResetKey">
                            <Loader2 v-if="resettingKey" class="h-4 w-4 animate-spin mr-1" />
                            确认重置
                        </Button>
                    </div>
                </div>
            </div>
        </Transition>
    </Teleport>

    <!-- 新 API Key 展示弹窗 -->
    <Teleport to="body">
        <Transition name="fade">
            <div v-if="showNewKeyDialog" class="fixed inset-0 z-50 flex items-center justify-center">
                <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" />
                <div
                    class="relative z-10 w-full max-w-md rounded-xl border bg-background p-6 shadow-2xl animate-in fade-in zoom-in-95 duration-200">
                    <div class="space-y-2 text-center">
                        <div class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-emerald-100">
                            <KeyRound class="h-5 w-5 text-emerald-600" />
                        </div>
                        <h2 class="text-lg font-semibold">新 API Key</h2>
                        <p class="text-sm text-muted-foreground">
                            请立即复制并保存，关闭后将无法再次查看！
                        </p>
                    </div>
                    <div class="mt-4 flex items-center gap-2 rounded-lg border bg-muted/30 px-3 py-2">
                        <code class="flex-1 text-sm font-mono break-all select-all">{{ newApiKey }}</code>
                        <Button variant="ghost" size="icon" class="h-8 w-8 shrink-0" @click="copyNewKey">
                            <Check v-if="keyCopied" class="h-4 w-4 text-emerald-500" />
                            <Copy v-else class="h-4 w-4" />
                        </Button>
                    </div>
                    <div class="mt-5 flex justify-center">
                        <Button class="px-8" @click="showNewKeyDialog = false; newApiKey = ''">
                            我已保存，关闭
                        </Button>
                    </div>
                </div>
            </div>
        </Transition>
    </Teleport>
</template>

<style scoped>
@keyframes slide-up-fade-in {
    from {
        opacity: 0;
        transform: translateY(12px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.animate-slide-up {
    animation: slide-up-fade-in 0.35s ease-out both;
}
</style>
