<template>
  <div
    class="flex-1 min-h-0 overflow-auto qcal-wrap border-l border-r border-b border-muted"
  >
    <component
      :is="QCalendarDayComp"
      date-header="inline"
      ref="calendarRef"
      v-model="model"
      no-scroll
      view="day"
      :interval-start="8"
      :interval-count="30"
      :interval-minutes="30"
      hoverable
      focusable
      @click-interval="$emit('click-interval', $event)"
    >
      <template #day-body="{ scope }">
        <template
          v-for="task in tasksByDate.get(scope.timestamp.date) || []"
          :key="task.id"
        >
          <div
            class="calendar-task-item calendar-task-item--absolute"
            :style="getEventStyle(task)"
            :title="`${task.start_time} ${task.activity_name}`"
            @click.stop="$emit('open-detail', task)"
          >
            <p
              class="font-semibold truncate"
              :style="{ color: task.color, marginLeft: '8px' }"
            >
              {{ task.activity_name }}
            </p>
          </div>
        </template>
      </template>
    </component>
  </div>
</template>

<script setup lang="ts">
import QCalendarDayPlugin from "@quasar/quasar-ui-qcalendar/QCalendarDay";
import type { PmTask } from "~/composables/usePmCalendar";

const QCalendarDayComp = (QCalendarDayPlugin as any).QCalendarDay;

const props = defineProps<{
  tasksByDate: Map<string, PmTask[]>;
}>();

defineEmits<{
  "click-interval": [payload: any];
  "open-detail": [task: PmTask];
}>();

const model = defineModel<string>({ required: true });

const calendarRef = ref<any>(null);

function timeToOffset(timeStr: string | undefined): number {
  if (!timeStr) return 0;
  const [h, m] = timeStr.split(":").map(Number);
  const intervalStart = 8; // Match :interval-start="8"
  const intervalHeight = 40; // QCalendar default interval height
  const intervalMinutes = 30; // Match :interval-minutes="30"

  const totalMinutes = (h! - intervalStart) * 60 + (m || 0);
  return (totalMinutes / intervalMinutes) * intervalHeight;
}

function getEventStyle(task: PmTask): Record<string, string> {
  const top = timeToOffset(task.start_time);
  return {
    top: `${top}px`,
    height: "40px", // Match interval height
    backgroundColor: (task.color || "#94a3b8") + "22",
    borderLeft: `6px solid ${task.color || "#94a3b8"}`,
    position: "absolute",
    left: "0px",
    right: "0px",
  };
}

function formatTime(hour: number): string {
  const period = hour >= 12 ? "PM" : "AM";
  const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
  return `${displayHour}${period}`;
}

defineExpose({
  prev: () => calendarRef.value?.prev(),
  next: () => calendarRef.value?.next(),
  moveToToday: () => calendarRef.value?.moveToToday(),
});
</script>

<style scoped>
.qcal-wrap :deep(.q-calendar) {
  overflow: unset !important;
}

.qcal-wrap :deep(.q-calendar-day__head) {
  position: sticky;
  top: 0;
  z-index: 3;
  background: var(--calendar-background);
}

.qcal-wrap :deep(.q-calendar__header--inline) {
  padding: 4px;
}

.qcal-wrap :deep(.q-calendar-day__head--weekday) {
  padding: 4px;
  font-size: 12px;
  text-transform: uppercase;
  font-weight: 400;
}

.qcal-wrap :deep(.q-calendar-day__head--date) {
  padding: 4px;
}
</style>
