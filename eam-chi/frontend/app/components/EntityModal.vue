<template>
  <UModal
    v-model:open="modalStore.isOpen"
    :title="`Add ${entityMeta?.label || modalStore.entity}`"
    :description="
      entityMeta?.description ||
      `Fill out the fields to add a new ${entityMeta?.label || modalStore.entity}.`
    "
  >
    <template #body>
      <UForm
        v-if="modalStore.entity && entityMeta"
        :state="form"
        @submit="handleSubmit"
        class="space-y-4"
      >
        <template v-for="field in formFields" :key="field.name">
          <UFormField
            v-if="!field.hidden && field.name !== 'id'"
            :label="field.label"
            :name="field.name"
            :required="field.required"
          >
            <template v-if="isPrefilled(field.name)">
              <!-- For link fields, show disabled input -->
              <UInput
                v-if="
                  field.field_type === 'link' ||
                  field.field_type === 'parent_child_link' ||
                  field.field_type === 'query_link'
                "
                :model-value="getPrefillDisplayValue(field)"
                disabled
                class="w-full"
                size="md"
              />
              <!-- For other field types, use EntityFieldRenderer but with pre-filled value -->
              <EntityFieldRenderer
                v-else
                :field="field"
                v-model="form[field.name]"
                :disabled="field.readonly"
                :link-options="linkOptions"
                :on-load-link-options="loadLinkOptions"
                :entity-name="modalStore.entity"
                :form-state="form"
              />
            </template>

            <EntityFieldRenderer
              v-else
              :field="field"
              v-model="form[field.name]"
              :disabled="field.readonly"
              :link-options="linkOptions"
              :on-load-link-options="loadLinkOptions"
              :entity-name="modalStore.entity"
              :form-state="form"
            />
          </UFormField>
        </template>
      </UForm>
    </template>
    <template #footer="{ close }">
      <UButton
        label="Cancel"
        color="neutral"
        variant="outline"
        @click="modalStore.close()"
        :disabled="loading"
      />
      <UButton
        label="Create"
        color="neutral"
        :disabled="loading"
        @click="handleSubmit"
      />
    </template>
  </UModal>
</template>

<script setup lang="ts">
import { useEntityModalStore } from "~/stores/entityModal";

const modalStore = useEntityModalStore();
const { getEntityMeta, getEntityOptions } = useApi();
const toast = useToast();

const loading = ref(false);
const entityMeta = ref<any>(null);
const form = ref<Record<string, any>>({});
const linkOptions = ref<Record<string, any[]>>({});
const loadingLinks = ref<Record<string, boolean>>({});

watch(
  () => modalStore.entity,
  async (entity) => {
    if (entity) {
      try {
        const response = await getEntityMeta(entity);
        entityMeta.value = response.data;

        form.value = { ...modalStore.prefillData };
      } catch (error: any) {
        toast.add({
          title: "Error",
          description: "Failed to load entity metadata",
          color: "error",
        });
        modalStore.close();
      }
    }
  },
);

const formFields = computed(() => {
  return entityMeta.value?.fields || [];
});

const isPrefilled = (fieldName: string) => {
  return modalStore.prefillData.hasOwnProperty(fieldName);
};

const getPrefillDisplayValue = (field: any) => {
  const value = modalStore.prefillData[field.name];
  return value;
};

const loadLinkOptions = async (fieldName: string, linkEntity: string) => {
  if (linkOptions.value[linkEntity]) return;

  loadingLinks.value[linkEntity] = true;
  try {
    const response = await getEntityOptions(linkEntity);
    if (response.status === "success") {
      linkOptions.value[linkEntity] = response.options;
    }
  } catch (error) {
    console.error(`Failed to load options for ${fieldName}:`, error);
  } finally {
    loadingLinks.value[linkEntity] = false;
  }
};

const handleSubmit = async () => {
  loading.value = true;
  try {
    await modalStore.submit(form.value);
    toast.add({
      title: "Success",
      description: `${entityMeta.value?.label} created successfully`,
      color: "success",
    });
  } catch (error: any) {
    toast.add({
      title: "Error",
      description: error.message || "Failed to create record",
      color: "error",
    });
  } finally {
    loading.value = false;
  }
};
</script>
