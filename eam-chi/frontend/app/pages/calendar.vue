<template>
  <div
    class="pm-calendar-page h-full min-h-0 flex flex-col gap-3 overflow-hidden p-3"
  >
    <!-- Header -->
    <div class="flex items-center justify-between flex-shrink-0">
      <div>
        <h1 class="text-2xl font-semibold">PM Calendar</h1>
        <p class="text-sm text-gray-500">
          Preventive Maintenance scheduling &amp; task management
        </p>
      </div>
    </div>

    <!-- Calendar Container -->
    <div class="flex-1 min-h-0 flex flex-col overflow-hidden">
      <!-- Toolbar -->
      <div
        class="shrink-0 flex items-center justify-between bg-card px-3 py-2 border border-gray-200 dark:border-gray-800 rounded-t-lg"
      >
        <!-- View switcher (left) -->
        <UTabs
          v-model="activeView"
          :items="views"
          :content="false"
          variant="pill"
          color="neutral"
          size="sm"
          class="w-auto"
        />

        <!-- Header label (center) -->
        <h3 class="text-base font-semibold min-w-[160px] text-center">
          {{ headerLabel }}
        </h3>

        <!-- Right: navigation -->
        <div class="flex items-center gap-2">
          <UButton
            label="Today"
            variant="ghost"
            size="md"
            color="neutral"
            @click="goToToday"
          />

          <UButton
            icon="i-lucide-chevron-left"
            variant="outline"
            size="md"
            @click="onPrev"
            color="neutral"
          />

          <UButton
            icon="i-lucide-chevron-right"
            variant="outline"
            size="md"
            @click="onNext"
            color="neutral"
          />
        </div>
      </div>

      <!-- Loading -->
      <div
        v-if="loading"
        class="flex-1 min-h-0 flex items-center justify-center border border-muted"
      >
        <UIcon
          name="i-lucide-loader-2"
          class="w-6 h-6 animate-spin text-gray-400"
        />
      </div>

      <!-- ── Views ──────────────────────────────────────────────────────────── -->
      <CalendarMonthView
        v-else-if="activeView === 'month'"
        ref="activeCalendarRef"
        v-model="calendarValue"
        :tasks-by-date="tasksByDate"
        @click-day="onClickDay"
        @click-date="onClickDate"
        @open-detail="openDetail"
      />

      <CalendarDayView
        v-else-if="activeView === 'day'"
        ref="activeCalendarRef"
        v-model="calendarValue"
        :tasks-by-date="tasksByDate"
        @click-interval="onClickInterval"
        @open-detail="openDetail"
      />

      <CalendarWeekView
        v-else-if="activeView === 'week'"
        ref="activeCalendarRef"
        v-model="calendarValue"
        :tasks-by-date="tasksByDate"
        @click-interval="onClickInterval"
        @open-detail="openDetail"
      />

      <CalendarResourceView
        v-else-if="activeView === 'resource'"
        ref="activeCalendarRef"
        v-model="calendarValue"
        :tasks-by-resource="tasksByResource"
        :resources="resourceList"
        @click-interval="onClickInterval"
        @open-detail="openDetail"
      />
    </div>

    <!-- Detail Modal -->
    <UModal
      v-model:open="detailModalOpen"
      :title="selectedTask?.activity_name || 'Task Details'"
      :description="selectedTask?.id"
    >
      <template #body>
        <div class="space-y-4" v-if="selectedTask">
          <div class="flex items-center justify-between">
            <span
              class="inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium text-white"
              :style="{ backgroundColor: selectedTask.color }"
            >
              {{ selectedTask.workflow_state }}
            </span>
          </div>

          <div class="grid grid-cols-2 gap-3 text-sm">
            <div>
              <span class="text-gray-500">Date</span>
              <p class="font-medium">{{ selectedTask.due_date }}</p>
            </div>
            <div>
              <span class="text-gray-500">Time</span>
              <p class="font-medium">{{ selectedTask.start_time }}</p>
            </div>
            <div>
              <span class="text-gray-500">Assigned To</span>
              <p class="font-medium">{{ selectedTask.laborer || "—" }}</p>
            </div>
            <div>
              <span class="text-gray-500">Site</span>
              <p class="font-medium">{{ selectedTask.site || "—" }}</p>
            </div>
          </div>

          <div v-if="selectedTask.notes">
            <span class="text-sm text-gray-500">Notes</span>
            <p class="text-sm">{{ selectedTask.notes }}</p>
          </div>
        </div>
      </template>
    </UModal>
  </div>
</template>

<script setup lang="ts">
import type { TabsItem } from "@nuxt/ui";
import type {
  PmTask,
  ActivityOption,
  LaborOption,
  TimeSlot,
  HolidayItem,
} from "~/composables/usePmCalendar";
import "~/components/calendar/qcalendar-theme.css";

const toast = useToast();
const {
  fetchTasks,
  fetchWorkOrderActivities,
  fetchTask,
  fetchWorkOrderActivity,
  fetchActivities,
  fetchLabor,
  fetchTimeSlots,
  fetchHolidays,
} = usePmCalendar();

// ── View switcher ────────────────────────────────────────────────────────────
const views: TabsItem[] = [
  { value: "day", label: "Day" },
  { value: "week", label: "Week" },
  { value: "month", label: "Month" },
  { value: "resource", label: "Resource" },
];
const activeView = ref<"month" | "week" | "day" | "resource">("month");

// ── State ────────────────────────────────────────────────────────────────────
const loading = ref(true);

const currentYear = ref(new Date().getFullYear());
const currentMonth = ref(new Date().getMonth() + 1);

const tasks = ref<PmTask[]>([]);
const activities = ref<ActivityOption[]>([]);
const labor = ref<LaborOption[]>([]);
const timeSlots = ref<TimeSlot[]>([]);
const holidays = ref<HolidayItem[]>([]);

const detailModalOpen = ref(false);
const selectedTask = ref<PmTask | null>(null);

const calendarValue = ref("");

// ── Active calendar ref (exposed by each view component) ─────────────────────
const activeCalendarRef = ref<{
  prev: () => void;
  next: () => void;
  moveToToday: () => void;
} | null>(null);

function parseYmd(value: string) {
  const [y, m, d] = value.split("-").map((x) => Number(x));
  return new Date(y || 1970, (m || 1) - 1, d || 1);
}

function formatLongDate(d: Date) {
  return d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function startOfWeek(d: Date) {
  const day = d.getDay();
  const diff = (day + 6) % 7;
  const out = new Date(d);
  out.setDate(d.getDate() - diff);
  out.setHours(0, 0, 0, 0);
  return out;
}

function endOfWeek(d: Date) {
  const s = startOfWeek(d);
  const out = new Date(s);
  out.setDate(s.getDate() + 6);
  return out;
}

const headerLabel = computed(() => {
  if (activeView.value === "month") return monthLabel.value;
  if (!calendarValue.value) return monthLabel.value;

  const d = parseYmd(calendarValue.value);
  if (activeView.value === "day" || activeView.value === "resource") {
    return formatLongDate(d);
  }

  // week
  const s = startOfWeek(d);
  const e = endOfWeek(d);
  const sameMonth =
    s.getMonth() === e.getMonth() && s.getFullYear() === e.getFullYear();
  const sLabel = s.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
  const eLabel = e.toLocaleDateString("en-US", {
    month: sameMonth ? undefined : "short",
    day: "numeric",
    year: "numeric",
  });
  return `${sLabel} – ${eLabel}`;
});

// ── Computed ─────────────────────────────────────────────────────────────────
const monthLabel = computed(() => {
  const d = new Date(currentYear.value, currentMonth.value - 1, 1);
  return d.toLocaleDateString("en-US", { month: "long", year: "numeric" });
});

const tasksByDate = computed(() => {
  const m = new Map<string, PmTask[]>();
  tasks.value.forEach((t) => {
    if (!m.has(t.due_date)) m.set(t.due_date, []);
    m.get(t.due_date)!.push(t);
  });
  m.forEach((arr) =>
    arr.sort((a, b) => (a.start_time || "").localeCompare(b.start_time || "")),
  );
  return m;
});

const tasksByResource = computed(() => {
  const m = new Map<string, PmTask[]>();
  tasks.value.forEach((t) => {
    const key = t.assigned_to || "__unassigned";
    if (!m.has(key)) m.set(key, []);
    m.get(key)!.push(t);
  });
  return m;
});

const resourceList = computed(() =>
  labor.value.map((l) => ({ id: l.id, name: l.laborer })),
);

watch(
  () => resourceList.value,
  (val) => {
    // Resource list changed
  },
  { deep: true },
);

watch(
  () => tasksByResource.value,
  (val) => {
    // Tasks by resource changed
  },
  { immediate: true },
);

// ── Helpers ──────────────────────────────────────────────────────────────────
function formatDate(d: Date): string {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

// ── Navigation ───────────────────────────────────────────────────────────────
function goToToday() {
  activeCalendarRef.value?.moveToToday();
}

function onPrev() {
  activeCalendarRef.value?.prev();
}

function onNext() {
  activeCalendarRef.value?.next();
}

watch(
  () => calendarValue.value,
  async (val, oldVal) => {
    const m = parseYmd(val);
    currentYear.value = m.getFullYear();
    currentMonth.value = Number(m.getMonth() + 1);
    const oldMonth = oldVal ? oldVal.slice(0, 7) : "";
    if (val.slice(0, 7) !== oldMonth) {
      loadTasks();
    }
  },
  { immediate: true },
);

// Reload tasks when switching to resource view
watch(
  () => activeView.value,
  (newView, oldView) => {
    if (newView === "resource" && oldView !== "resource") {
      loadTasks();
    }
  },
);

// ── Data Loading ─────────────────────────────────────────────────────────────
async function loadTasks() {
  loading.value = true;
  try {
    // Use different API based on active view
    if (activeView.value === "resource") {
      const raw = await fetchWorkOrderActivities(
        currentYear.value,
        currentMonth.value,
      );
      tasks.value = raw;
    } else {
      const raw = await fetchTasks(currentYear.value, currentMonth.value);
      tasks.value = raw;
    }
  } catch (e: any) {
    toast.add({
      title: "Error loading tasks",
      description: e?.message || "Unknown error",
      color: "error",
    });
  } finally {
    loading.value = false;
  }
}

async function loadDropdowns() {
  try {
    const [acts, lbr, ts, hol] = await Promise.all([
      fetchActivities(),
      fetchLabor(),
      fetchTimeSlots(),
      fetchHolidays(currentYear.value),
    ]);
    activities.value = acts;
    labor.value = lbr;
    timeSlots.value = ts;
    holidays.value = hol;
  } catch (e: any) {
    // Error loading dropdowns
  }
}

async function openDetail(task: PmTask) {
  try {
    // Use different API based on active view
    const fullTask =
      activeView.value === "resource"
        ? await fetchWorkOrderActivity(task.id)
        : await fetchTask(task.id);
    selectedTask.value = fullTask;
    detailModalOpen.value = true;
  } catch (e: any) {
    // Error loading task details
    toast.add({
      title: "Error",
      description: "Failed to load task details",
      color: "error",
    });
  }
}

// ── QCalendar handlers ───────────────────────────────────────────────────────
function onClickInterval(_payload: any) {
  notifyReadOnly();
}

function onClickDay(_payload: any) {
  notifyReadOnly();
}

function onClickDate(_payload: any) {
  notifyReadOnly();
}

function notifyReadOnly() {
  toast.add({
    title: "Read-only",
    description:
      "Create and updates must be done through the standard process, not in the calendar view.",
    color: "neutral",
  });
}

// ── Init ─────────────────────────────────────────────────────────────────────
onMounted(async () => {
  await loadDropdowns();
  const today = new Date();
  calendarValue.value = formatDate(today);
});
</script>
