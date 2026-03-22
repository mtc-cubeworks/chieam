<script setup lang="ts">
import WorkflowStates from "~/components/workflow/WorkflowStates.vue";
import WorkflowActions from "~/components/workflow/WorkflowActions.vue";
import WorkflowManagement from "~/components/workflow/WorkflowManagement.vue";

const activeTab = ref("workflows");

definePageMeta({ title: "Workflow", middleware: "auth" as any });
</script>

<template>
  <div class="space-y-6 px-3 py-3">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-foreground">Workflow</h1>
        <p class="text-muted-foreground text-sm">
          Manage global states, actions, and entity workflows
        </p>
      </div>
    </div>

    <UTabs
      v-model="activeTab"
      variant="link"
      :items="[
        { value: 'workflows', slot: 'workflows', label: 'Workflows' },
        { value: 'states', slot: 'states', label: 'States' },
        { value: 'actions', slot: 'actions', label: 'Actions' },
      ]"
      class="w-full"
      size="md"
    >
      <template #workflows>
        <div class="pt-4">
          <WorkflowManagement />
        </div>
      </template>

      <template #states>
        <div class="pt-4">
          <WorkflowStates />
        </div>
      </template>

      <template #actions>
        <div class="pt-4">
          <WorkflowActions />
        </div>
      </template>
    </UTabs>
  </div>
</template>
