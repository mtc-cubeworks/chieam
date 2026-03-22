<template>
  <div
    class="flex-1 min-h-0 overflow-auto qcal-wrap border-l border-r border-b border-muted"
  >
    <component
      :is="QCalendarResourceComp"
      ref="calendarRef"
      v-model="model"
      v-model:model-resources="resourcesModel"
      no-scroll
      view="day"
      resource-key="id"
      resource-label="name"
      :resource-min-height="70"
      :resource-height="120"
      :interval-start="5"
      :interval-count="30"
      :interval-minutes="30"
      hoverable
      focusable
      @click-interval="$emit('click-interval', $event)"
    >
      <template #resource-intervals="{ scope }">
        <template v-if="logResourceScope(scope)"></template>
        <template v-for="evt in getEvents(scope)" :key="evt.task.id">
          <div
            class="calendar-task-item calendar-task-item--absolute"
            :style="getEventStyle(evt)"
            :title="`${evt.task.start_time} ${evt.task.activity_name}`"
            @click.stop="$emit('open-detail', evt.task)"
          >
            <p
              class="font-semibold truncate"
              :style="{ color: evt.task.color, marginLeft: '4px' }"
            >
              {{ evt.task.activity_name }}
            </p>
          </div>
        </template>
      </template>
    </component>
  </div>
</template>

<script setup lang="ts">
import QCalendarResourcePlugin from "@quasar/quasar-ui-qcalendar/QCalendarResource";
import type { PmTask } from "~/composables/usePmCalendar";

const QCalendarResourceComp = (QCalendarResourcePlugin as any)
  .QCalendarResource;

const props = defineProps<{
  tasksByResource: Map<string, PmTask[]>;
  resources: { id: string; name: string }[];
}>();

defineEmits<{
  "click-interval": [payload: any];
  "open-detail": [task: PmTask];
}>();

const model = defineModel<string>({ required: true });

const calendarRef = ref<any>(null);

const resourcesModel = ref<{ id: string; name: string }[]>([]);

watch(
  () => props.resources,
  (val) => {
    resourcesModel.value = Array.isArray(val) ? [...val] : [];
  },
  { deep: true, immediate: true },
);

onMounted(() => {
  // Component mounted
});

watch(
  () => props.tasksByResource,
  (val) => {
    // Tasks by resource changed
  },
  { immediate: true },
);

function logResourceScope(scope: any) {
  // Resource scope logged
  return true;
}

function timeToMinutes(timeStr: string | undefined): number {
  if (!timeStr) return 0;
  const [h, m] = timeStr.split(":").map(Number);
  return (h || 0) * 60 + (m || 0);
}

type PositionedTask = {
  task: PmTask;
  left: number;
  width: number;
  top: number;
  height: number;
};

function getEvents(scope: any): PositionedTask[] {
  const tasks = props.tasksByResource.get(scope?.resource?.id) || [];
  if (!tasks.length) return [];

  const durationMinutes = 30;
  const rowHeight = 36;
  const rowGap = 4;
  const topBase = 2;

  const items = tasks
    .slice()
    .sort((a, b) => timeToMinutes(a.start_time) - timeToMinutes(b.start_time))
    .map((task) => {
      const start = timeToMinutes(task.start_time);
      const end = start + durationMinutes;
      const left = scope?.timeStartPosX
        ? scope.timeStartPosX(task.start_time)
        : 0;
      const width = scope?.timeDurationWidth
        ? scope.timeDurationWidth(durationMinutes)
        : 100;
      return { task, start, end, left, width };
    });

  const lanesEnd: number[] = [];
  const out: PositionedTask[] = [];

  for (const it of items) {
    let lane = lanesEnd.findIndex((laneEnd) => laneEnd <= it.start);
    if (lane === -1) {
      lane = lanesEnd.length;
      lanesEnd.push(it.end);
    } else {
      lanesEnd[lane] = it.end;
    }

    out.push({
      task: it.task,
      left: it.left,
      width: it.width,
      top: topBase + lane * (rowHeight + rowGap),
      height: rowHeight,
    });
  }

  return out;
}

function getEventStyle(evt: PositionedTask): Record<string, string> {
  return {
    top: `${evt.top}px`,
    left: `${evt.left}px`,
    width: `${evt.width}px`,
    height: `${evt.height}px`,
    backgroundColor: (evt.task.color || "#94a3b8") + "22",
    borderLeft: `6px solid ${evt.task.color || "#94a3b8"}`,
    borderRadius: "4px",
    position: "absolute",
    overflow: "hidden",
  };
}

defineExpose({
  prev: () => calendarRef.value?.prev(),
  next: () => calendarRef.value?.next(),
  moveToToday: () => calendarRef.value?.moveToToday(),
});
</script>

<style scoped>
.qcal-wrap :deep(.q-calendar-resource__resource--text) {
  margin-left: 12px;
  padding-left: 2px;
}
</style>
