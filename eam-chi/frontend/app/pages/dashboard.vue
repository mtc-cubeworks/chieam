<script setup lang="ts">
const { apiFetch, baseURL } = useApiFetch();
const toast = useToast();

interface DashboardData {
  work_orders: {
    total: number;
    open: number;
    in_progress: number;
    completed: number;
    other: number;
    high_priority_active: number;
    created_30d: number;
  };
  work_orders_by_type: { label: string; count: number }[];
  work_orders_by_status: { label: string; count: number }[];
  assets: { total: number; active: number; inactive: number; other: number };
  assets_by_class: { label: string; count: number }[];
  inventory: {
    total_lines: number;
    out_of_stock: number;
    low_stock: number;
    adequate: number;
  };
  purchase_requests: {
    total: number;
    draft: number;
    submitted: number;
    approved: number;
    rejected: number;
    created_30d: number;
  };
  maintenance: {
    total: number;
    completed: number;
    pending: number;
    completion_rate: number;
  };
  incidents: { total: number; open: number; closed: number };
  incidents_by_severity: { label: string; count: number }[];
  overdue_work_orders: number;
  recent_activity: { total_activities: number; work_orders_touched: number };
  stock_movements: {
    total_movements: number;
    total_issued: number;
    total_received: number;
  };
  budget: { budget_lines: number; total_budget: number; fiscal_year: number };
}

const data = ref<DashboardData | null>(null);
const loading = ref(true);

const loadDashboard = async () => {
  loading.value = true;
  try {
    const res = await apiFetch<{ status: string; data: DashboardData }>(
      `${baseURL}/dashboard`
    );
    if (res.status === "success") {
      data.value = res.data;
    }
  } catch (err: any) {
    toast.add({
      title: "Failed to load dashboard",
      description: err?.message,
      color: "error",
    });
  } finally {
    loading.value = false;
  }
};

const formatNumber = (n: number | undefined | null) => {
  if (n == null) return "0";
  return n.toLocaleString();
};

const formatCurrency = (n: number | undefined | null) => {
  if (n == null) return "₱0";
  return "₱" + n.toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 });
};

// Colors for status badges
const statusColor = (label: string): string => {
  const map: Record<string, string> = {
    Open: "blue",
    "In Progress": "warning",
    Completed: "success",
    Closed: "neutral",
    Cancelled: "error",
    Requested: "info",
    Approved: "success",
    Draft: "neutral",
    Submitted: "blue",
    Rejected: "error",
    Active: "success",
    Inactive: "neutral",
  };
  return map[label] || "neutral";
};

const severityColor = (label: string): string => {
  const map: Record<string, string> = {
    Critical: "error",
    High: "warning",
    Medium: "blue",
    Low: "success",
  };
  return map[label] || "neutral";
};

const inventoryStatusColor = (key: string): string => {
  const map: Record<string, string> = {
    out_of_stock: "error",
    low_stock: "warning",
    adequate: "success",
  };
  return map[key] || "neutral";
};

// Compute bar widths as percentages for simple inline charts
const maxCount = (items: { count: number }[]) =>
  Math.max(...items.map((i) => i.count), 1);

onMounted(loadDashboard);

definePageMeta({
  title: "Dashboard",
  middleware: "auth" as any,
});
</script>

<template>
  <div class="h-full min-h-0 overflow-y-auto p-4 space-y-6">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold">Dashboard</h1>
        <p class="text-sm text-muted-foreground">
          Real-time overview of your asset management system
        </p>
      </div>
      <UButton
        icon="i-lucide-refresh-cw"
        variant="outline"
        size="sm"
        :loading="loading"
        @click="loadDashboard"
      >
        Refresh
      </UButton>
    </div>

    <!-- Loading -->
    <div v-if="loading && !data" class="flex items-center justify-center py-20">
      <UIcon name="i-lucide-loader-2" class="animate-spin h-8 w-8 text-primary" />
    </div>

    <template v-if="data">
      <!-- ═══ ROW 1: Key Metrics ═══ -->
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <!-- Total Assets -->
        <div class="border border-accented rounded-lg p-4 bg-card">
          <div class="flex items-center gap-2 mb-2">
            <div class="p-1.5 rounded-md bg-blue-500/10">
              <UIcon name="i-lucide-box" class="h-4 w-4 text-blue-500" />
            </div>
            <span class="text-xs text-muted-foreground font-medium">Assets</span>
          </div>
          <p class="text-2xl font-bold">{{ formatNumber(data.assets.total) }}</p>
          <p class="text-xs text-muted-foreground mt-1">
            {{ formatNumber(data.assets.active) }} active
          </p>
        </div>

        <!-- Work Orders -->
        <div class="border border-accented rounded-lg p-4 bg-card">
          <div class="flex items-center gap-2 mb-2">
            <div class="p-1.5 rounded-md bg-amber-500/10">
              <UIcon name="i-lucide-clipboard-list" class="h-4 w-4 text-amber-500" />
            </div>
            <span class="text-xs text-muted-foreground font-medium">Work Orders</span>
          </div>
          <p class="text-2xl font-bold">{{ formatNumber(data.work_orders.total) }}</p>
          <p class="text-xs text-muted-foreground mt-1">
            {{ formatNumber(data.work_orders.created_30d) }} last 30d
          </p>
        </div>

        <!-- Overdue -->
        <div class="border border-accented rounded-lg p-4 bg-card">
          <div class="flex items-center gap-2 mb-2">
            <div class="p-1.5 rounded-md bg-red-500/10">
              <UIcon name="i-lucide-alert-triangle" class="h-4 w-4 text-red-500" />
            </div>
            <span class="text-xs text-muted-foreground font-medium">Overdue WOs</span>
          </div>
          <p class="text-2xl font-bold" :class="data.overdue_work_orders > 0 ? 'text-red-500' : ''">
            {{ formatNumber(data.overdue_work_orders) }}
          </p>
          <p class="text-xs text-muted-foreground mt-1">need attention</p>
        </div>

        <!-- Inventory -->
        <div class="border border-accented rounded-lg p-4 bg-card">
          <div class="flex items-center gap-2 mb-2">
            <div class="p-1.5 rounded-md bg-emerald-500/10">
              <UIcon name="i-lucide-package" class="h-4 w-4 text-emerald-500" />
            </div>
            <span class="text-xs text-muted-foreground font-medium">Inventory</span>
          </div>
          <p class="text-2xl font-bold">{{ formatNumber(data.inventory.total_lines) }}</p>
          <p class="text-xs text-muted-foreground mt-1">
            <span v-if="data.inventory.out_of_stock > 0" class="text-red-500 font-medium">
              {{ data.inventory.out_of_stock }} out of stock
            </span>
            <span v-else class="text-emerald-500">all stocked</span>
          </p>
        </div>

        <!-- Purchase Requests -->
        <div class="border border-accented rounded-lg p-4 bg-card">
          <div class="flex items-center gap-2 mb-2">
            <div class="p-1.5 rounded-md bg-violet-500/10">
              <UIcon name="i-lucide-file-text" class="h-4 w-4 text-violet-500" />
            </div>
            <span class="text-xs text-muted-foreground font-medium">PRs</span>
          </div>
          <p class="text-2xl font-bold">{{ formatNumber(data.purchase_requests.total) }}</p>
          <p class="text-xs text-muted-foreground mt-1">
            {{ formatNumber(data.purchase_requests.created_30d) }} last 30d
          </p>
        </div>

        <!-- Incidents -->
        <div class="border border-accented rounded-lg p-4 bg-card">
          <div class="flex items-center gap-2 mb-2">
            <div class="p-1.5 rounded-md bg-orange-500/10">
              <UIcon name="i-lucide-shield-alert" class="h-4 w-4 text-orange-500" />
            </div>
            <span class="text-xs text-muted-foreground font-medium">Incidents</span>
          </div>
          <p class="text-2xl font-bold">{{ formatNumber(data.incidents.total) }}</p>
          <p class="text-xs text-muted-foreground mt-1">
            <span v-if="data.incidents.open > 0" class="text-orange-500 font-medium">
              {{ data.incidents.open }} open
            </span>
            <span v-else>all resolved</span>
          </p>
        </div>
      </div>

      <!-- ═══ ROW 2: Work Orders + Assets ═══ -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Work Orders by Status -->
        <div class="border border-accented rounded-lg bg-card">
          <div class="p-4 border-b border-accented flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-clipboard-list" class="h-5 w-5 text-primary" />
              <h3 class="font-semibold text-sm">Work Orders by Status</h3>
            </div>
            <NuxtLink to="/work_order" class="text-xs text-primary hover:underline">
              View all →
            </NuxtLink>
          </div>
          <div class="p-4 space-y-2.5">
            <div
              v-for="item in data.work_orders_by_status"
              :key="item.label"
              class="flex items-center gap-3"
            >
              <span class="text-sm w-28 truncate" :title="item.label">{{ item.label }}</span>
              <div class="flex-1 h-6 bg-muted/40 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full bg-primary/70 transition-all duration-500"
                  :style="{
                    width: `${Math.max((item.count / maxCount(data.work_orders_by_status)) * 100, 2)}%`,
                  }"
                />
              </div>
              <span class="text-sm font-semibold w-10 text-right">{{ item.count }}</span>
            </div>
            <div v-if="data.work_orders_by_status.length === 0" class="text-center py-4 text-muted-foreground text-sm">
              No work orders found
            </div>
          </div>
        </div>

        <!-- Work Orders by Type -->
        <div class="border border-accented rounded-lg bg-card">
          <div class="p-4 border-b border-accented flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-wrench" class="h-5 w-5 text-primary" />
              <h3 class="font-semibold text-sm">Work Orders by Type</h3>
            </div>
            <UBadge
              :label="`${data.work_orders.high_priority_active} high priority`"
              color="warning"
              variant="soft"
              size="sm"
            />
          </div>
          <div class="p-4 space-y-2.5">
            <div
              v-for="item in data.work_orders_by_type"
              :key="item.label"
              class="flex items-center gap-3"
            >
              <span class="text-sm w-40 truncate" :title="item.label">{{ item.label }}</span>
              <div class="flex-1 h-6 bg-muted/40 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full bg-amber-500/60 transition-all duration-500"
                  :style="{
                    width: `${Math.max((item.count / maxCount(data.work_orders_by_type)) * 100, 2)}%`,
                  }"
                />
              </div>
              <span class="text-sm font-semibold w-10 text-right">{{ item.count }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ ROW 3: Assets + Inventory ═══ -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Assets by Class -->
        <div class="border border-accented rounded-lg bg-card">
          <div class="p-4 border-b border-accented flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-box" class="h-5 w-5 text-primary" />
              <h3 class="font-semibold text-sm">Assets by Class</h3>
            </div>
            <NuxtLink to="/asset" class="text-xs text-primary hover:underline">
              View all →
            </NuxtLink>
          </div>
          <div class="p-4 space-y-2.5">
            <div
              v-for="item in data.assets_by_class"
              :key="item.label"
              class="flex items-center gap-3"
            >
              <span class="text-sm w-40 truncate" :title="item.label">{{ item.label }}</span>
              <div class="flex-1 h-6 bg-muted/40 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full bg-blue-500/60 transition-all duration-500"
                  :style="{
                    width: `${Math.max((item.count / maxCount(data.assets_by_class)) * 100, 2)}%`,
                  }"
                />
              </div>
              <span class="text-sm font-semibold w-10 text-right">{{ item.count }}</span>
            </div>
          </div>
        </div>

        <!-- Inventory Health -->
        <div class="border border-accented rounded-lg bg-card">
          <div class="p-4 border-b border-accented flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-package" class="h-5 w-5 text-primary" />
              <h3 class="font-semibold text-sm">Inventory Health</h3>
            </div>
            <NuxtLink to="/inventory" class="text-xs text-primary hover:underline">
              View all →
            </NuxtLink>
          </div>
          <div class="p-4 space-y-4">
            <!-- Inventory bar -->
            <div class="space-y-2">
              <div class="flex h-8 rounded-full overflow-hidden bg-muted/40">
                <div
                  v-if="data.inventory.adequate > 0"
                  class="bg-emerald-500 transition-all duration-500"
                  :style="{ width: `${(data.inventory.adequate / Math.max(data.inventory.total_lines, 1)) * 100}%` }"
                  :title="`Adequate: ${data.inventory.adequate}`"
                />
                <div
                  v-if="data.inventory.low_stock > 0"
                  class="bg-amber-500 transition-all duration-500"
                  :style="{ width: `${(data.inventory.low_stock / Math.max(data.inventory.total_lines, 1)) * 100}%` }"
                  :title="`Low Stock: ${data.inventory.low_stock}`"
                />
                <div
                  v-if="data.inventory.out_of_stock > 0"
                  class="bg-red-500 transition-all duration-500"
                  :style="{ width: `${(data.inventory.out_of_stock / Math.max(data.inventory.total_lines, 1)) * 100}%` }"
                  :title="`Out of Stock: ${data.inventory.out_of_stock}`"
                />
              </div>
              <div class="flex items-center justify-center gap-6 text-xs">
                <div class="flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-emerald-500" />
                  Adequate ({{ data.inventory.adequate }})
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-amber-500" />
                  Low Stock ({{ data.inventory.low_stock }})
                </div>
                <div class="flex items-center gap-1.5">
                  <span class="w-2.5 h-2.5 rounded-full bg-red-500" />
                  Out of Stock ({{ data.inventory.out_of_stock }})
                </div>
              </div>
            </div>

            <!-- Stock Movements -->
            <div class="border-t border-accented pt-3">
              <p class="text-xs font-medium text-muted-foreground mb-2">
                Stock Movements (last 30 days)
              </p>
              <div class="grid grid-cols-3 gap-3 text-center">
                <div>
                  <p class="text-lg font-bold">{{ formatNumber(data.stock_movements.total_movements) }}</p>
                  <p class="text-xs text-muted-foreground">Movements</p>
                </div>
                <div>
                  <p class="text-lg font-bold text-red-500">{{ formatNumber(data.stock_movements.total_issued) }}</p>
                  <p class="text-xs text-muted-foreground">Issued</p>
                </div>
                <div>
                  <p class="text-lg font-bold text-emerald-500">{{ formatNumber(data.stock_movements.total_received) }}</p>
                  <p class="text-xs text-muted-foreground">Received</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ ROW 4: Maintenance + Purchase Requests + Incidents ═══ -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <!-- Maintenance -->
        <div class="border border-accented rounded-lg bg-card">
          <div class="p-4 border-b border-accented flex items-center gap-2">
            <UIcon name="i-lucide-calendar-check" class="h-5 w-5 text-primary" />
            <h3 class="font-semibold text-sm">Maintenance</h3>
          </div>
          <div class="p-4 space-y-4">
            <!-- Completion ring visual -->
            <div class="flex items-center justify-center">
              <div class="relative w-28 h-28">
                <svg class="w-28 h-28 -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="42" fill="none" stroke-width="8" class="stroke-muted/30" />
                  <circle
                    cx="50"
                    cy="50"
                    r="42"
                    fill="none"
                    stroke-width="8"
                    stroke-linecap="round"
                    class="stroke-emerald-500 transition-all duration-700"
                    :stroke-dasharray="`${data.maintenance.completion_rate * 2.64} 264`"
                  />
                </svg>
                <div class="absolute inset-0 flex flex-col items-center justify-center">
                  <span class="text-xl font-bold">{{ data.maintenance.completion_rate }}%</span>
                  <span class="text-[10px] text-muted-foreground">completed</span>
                </div>
              </div>
            </div>
            <div class="grid grid-cols-3 gap-2 text-center text-sm">
              <div>
                <p class="font-bold">{{ data.maintenance.total }}</p>
                <p class="text-xs text-muted-foreground">Total</p>
              </div>
              <div>
                <p class="font-bold text-emerald-500">{{ data.maintenance.completed }}</p>
                <p class="text-xs text-muted-foreground">Done</p>
              </div>
              <div>
                <p class="font-bold text-amber-500">{{ data.maintenance.pending }}</p>
                <p class="text-xs text-muted-foreground">Pending</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Purchase Requests -->
        <div class="border border-accented rounded-lg bg-card">
          <div class="p-4 border-b border-accented flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-shopping-cart" class="h-5 w-5 text-primary" />
              <h3 class="font-semibold text-sm">Purchase Requests</h3>
            </div>
            <NuxtLink to="/purchase_request" class="text-xs text-primary hover:underline">
              View all →
            </NuxtLink>
          </div>
          <div class="p-4 space-y-3">
            <div class="flex items-center justify-between py-1.5 border-b border-dashed border-accented last:border-0">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-neutral-400" />
                <span class="text-sm">Draft</span>
              </div>
              <span class="text-sm font-semibold">{{ data.purchase_requests.draft }}</span>
            </div>
            <div class="flex items-center justify-between py-1.5 border-b border-dashed border-accented last:border-0">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-blue-500" />
                <span class="text-sm">Submitted</span>
              </div>
              <span class="text-sm font-semibold">{{ data.purchase_requests.submitted }}</span>
            </div>
            <div class="flex items-center justify-between py-1.5 border-b border-dashed border-accented last:border-0">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-500" />
                <span class="text-sm">Approved</span>
              </div>
              <span class="text-sm font-semibold">{{ data.purchase_requests.approved }}</span>
            </div>
            <div class="flex items-center justify-between py-1.5">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-red-500" />
                <span class="text-sm">Rejected</span>
              </div>
              <span class="text-sm font-semibold">{{ data.purchase_requests.rejected }}</span>
            </div>
          </div>
        </div>

        <!-- Incidents by Severity -->
        <div class="border border-accented rounded-lg bg-card">
          <div class="p-4 border-b border-accented flex items-center justify-between">
            <div class="flex items-center gap-2">
              <UIcon name="i-lucide-shield-alert" class="h-5 w-5 text-primary" />
              <h3 class="font-semibold text-sm">Incidents by Severity</h3>
            </div>
            <NuxtLink to="/incident" class="text-xs text-primary hover:underline">
              View all →
            </NuxtLink>
          </div>
          <div class="p-4 space-y-2.5">
            <div
              v-for="item in data.incidents_by_severity"
              :key="item.label"
              class="flex items-center gap-3"
            >
              <span class="text-sm w-24 truncate" :title="item.label">{{ item.label }}</span>
              <div class="flex-1 h-6 bg-muted/40 rounded-full overflow-hidden">
                <div
                  class="h-full rounded-full transition-all duration-500"
                  :class="{
                    'bg-red-500': item.label === 'Critical',
                    'bg-orange-500': item.label === 'High',
                    'bg-amber-500': item.label === 'Medium',
                    'bg-emerald-500': item.label === 'Low',
                    'bg-neutral-400': !['Critical', 'High', 'Medium', 'Low'].includes(item.label)
                  }"
                  :style="{
                    width: `${Math.max((item.count / maxCount(data.incidents_by_severity)) * 100, 2)}%`,
                  }"
                />
              </div>
              <span class="text-sm font-semibold w-8 text-right">{{ item.count }}</span>
            </div>
            <div v-if="data.incidents_by_severity.length === 0" class="text-center py-4 text-muted-foreground text-sm">
              No incidents recorded
            </div>
          </div>
        </div>
      </div>

      <!-- ═══ ROW 5: Budget + Activity Summary ═══ -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Budget -->
        <div class="border border-accented rounded-lg bg-card">
          <div class="p-4 border-b border-accented flex items-center gap-2">
            <UIcon name="i-lucide-bar-chart-3" class="h-5 w-5 text-primary" />
            <h3 class="font-semibold text-sm">
              Budget Summary — FY {{ data.budget.fiscal_year }}
            </h3>
          </div>
          <div class="p-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="text-3xl font-bold">{{ formatCurrency(data.budget.total_budget) }}</p>
                <p class="text-sm text-muted-foreground mt-1">
                  across {{ data.budget.budget_lines }} cost codes
                </p>
              </div>
              <NuxtLink to="/annual_budget" class="text-xs text-primary hover:underline">
                View budget →
              </NuxtLink>
            </div>
          </div>
        </div>

        <!-- Activity Summary -->
        <div class="border border-accented rounded-lg bg-card">
          <div class="p-4 border-b border-accented flex items-center gap-2">
            <UIcon name="i-lucide-activity" class="h-5 w-5 text-primary" />
            <h3 class="font-semibold text-sm">Activity (Last 30 Days)</h3>
          </div>
          <div class="p-4">
            <div class="grid grid-cols-2 gap-6">
              <div class="text-center">
                <p class="text-3xl font-bold">{{ formatNumber(data.recent_activity.total_activities) }}</p>
                <p class="text-sm text-muted-foreground mt-1">WO Activities</p>
              </div>
              <div class="text-center">
                <p class="text-3xl font-bold">{{ formatNumber(data.recent_activity.work_orders_touched) }}</p>
                <p class="text-sm text-muted-foreground mt-1">Work Orders Touched</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
