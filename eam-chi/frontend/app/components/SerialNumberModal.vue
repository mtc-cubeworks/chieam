<script setup lang="ts">
const props = defineProps<{
  open: boolean;
  inventoryIds: string[];
  receiptId: string;
  entityName: string;
}>();

const emit = defineEmits<{
  close: [];
  submitted: [message: string];
}>();

const { postDocumentAction } = useEntityApi();
const toast = useToast();

interface SerialEntry {
  inventory_id: string;
  serial_number: string;
}

const entries = ref<SerialEntry[]>([]);
const submitting = ref(false);

watch(
  () => props.inventoryIds,
  (ids) => {
    entries.value = ids.map((id) => ({ inventory_id: id, serial_number: "" }));
  },
  { immediate: true },
);

const allFilled = computed(() =>
  entries.value.every((e) => e.serial_number.trim() !== ""),
);

const hasDuplicates = computed(() => {
  const seen = new Set<string>();
  for (const e of entries.value) {
    const sn = e.serial_number.trim();
    if (!sn) continue;
    if (seen.has(sn)) return true;
    seen.add(sn);
  }
  return false;
});

const submit = async () => {
  if (!allFilled.value) {
    toast.add({
      title: "Validation",
      description: "All serial numbers must be filled.",
      color: "warning",
    });
    return;
  }
  if (hasDuplicates.value) {
    toast.add({
      title: "Validation",
      description:
        "Duplicate serial numbers detected. Each item must have a unique serial number.",
      color: "warning",
    });
    return;
  }

  submitting.value = true;
  try {
    const response = await postDocumentAction(
      props.entityName,
      props.receiptId,
      "update_inventory_serialno",
      { serial_numbers: entries.value },
    );

    if (response.status === "success") {
      emit(
        "submitted",
        response.message || "Serial numbers saved successfully.",
      );
    } else {
      toast.add({
        title: "Error",
        description: response.message || "Failed to save serial numbers.",
        color: "error",
      });
    }
  } catch (err: any) {
    toast.add({
      title: "Error",
      description: err.message || "Unknown error.",
      color: "error",
    });
  } finally {
    submitting.value = false;
  }
};
</script>

<template>
  <UModal :open="open" @close="emit('close')" class="max-w-lg">
    <template #content>
      <div class="p-6 space-y-4">
        <div class="flex items-center gap-3">
          <UIcon name="i-lucide-scan-barcode" class="w-5 h-5 text-primary" />
          <h2 class="text-lg font-semibold">Enter Serial Numbers</h2>
        </div>

        <p class="text-sm text-muted-foreground">
          {{ inventoryIds.length }} serialized item(s) were received. Enter a
          unique serial number for each one.
        </p>

        <div class="space-y-3 max-h-[50vh] overflow-y-auto pr-1">
          <div
            v-for="(entry, index) in entries"
            :key="entry.inventory_id"
            class="flex items-center gap-3 p-3 border border-muted rounded-lg"
          >
            <div class="flex-1 min-w-0">
              <p class="text-xs text-muted-foreground font-mono truncate">
                {{ entry.inventory_id }}
              </p>
              <p class="text-xs text-muted-foreground">
                Item {{ index + 1 }} of {{ entries.length }}
              </p>
            </div>
            <UInput
              v-model="entry.serial_number"
              placeholder="e.g. SN-2024-001"
              class="w-48"
              :color="entry.serial_number.trim() === '' ? 'warning' : 'primary'"
              autofocus
            />
          </div>
        </div>

        <UAlert
          v-if="hasDuplicates"
          color="warning"
          variant="subtle"
          icon="i-lucide-alert-triangle"
          title="Duplicate serial numbers detected"
          description="Each inventory item must have a unique serial number."
        />

        <div class="flex justify-end gap-2 pt-2 border-t border-muted">
          <UButton
            variant="outline"
            @click="emit('close')"
            :disabled="submitting"
          >
            Cancel
          </UButton>
          <UButton
            :loading="submitting"
            :disabled="!allFilled || hasDuplicates"
            icon="i-lucide-check"
            @click="submit"
          >
            Save Serial Numbers
          </UButton>
        </div>
      </div>
    </template>
  </UModal>
</template>
