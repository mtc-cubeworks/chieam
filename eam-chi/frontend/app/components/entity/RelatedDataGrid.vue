<script setup lang="ts">
import type { NuGridColumn } from "#nu-grid/types";
import type { EntityMeta, FieldMeta } from "~/composables/useApiTypes";

interface Props {
  parentEntity: string;
  parentId: string;
  childEntity: string;
  fkField: string;
  childMeta: EntityMeta | null;
  editable?: boolean;
  canAdd?: boolean;
  canDelete?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  editable: false,
  canAdd: false,
  canDelete: false,
});

const emit = defineEmits<{
  "loading-change": [isLoading: boolean];
  "refresh-needed": [];
}>();

const router = useRouter();
const cache = useCacheStore();
const {
  getEntityListView,
  bulkSaveChildren,
  getEntityOptions,
  postEntityAction,
  getEntityMeta,
} = useApi();
const toast = useToast();
const deleteDialog = useDeleteDialog();

const gridRef = ref<any>(null);
const gridData = ref<Record<string, any>[]>([]);
const linkTitles = ref<Record<string, string>>({});
const loading = ref(false);
const initialLoaded = ref(false);
const metadataLoading = ref(false);
const dirty = ref(false);
const dirtyRows = ref<Set<string>>(new Set());
const deletedIds = ref<string[]>([]);
const page = ref(1);
const pageSize = ref(20);
const total = ref(0);
const columnPinning = ref({ left: [] as string[], right: ["_actions"] });

watch(loading, (val) => emit("loading-change", val));

// Lookup options management (same pattern as ChildDataGrid)
const lookupArrays: Record<string, any[]> = reactive({});
const lookupVersions: Record<string, number> = reactive({});
const lookupLabelCache: Record<string, Record<string, string>> = reactive({});
const linkFetchInFlight = new Set<string>();

const cachedMetaKey = computed(() => `meta:entity:v2:${props.childEntity}`);

const resolvedChildMeta = computed<EntityMeta | null>(() => {
  if (props.childMeta) return props.childMeta;
  const metaRaw = cache.getFromLocalStorage<any>(cachedMetaKey.value);
  return (metaRaw as any)?.data ?? metaRaw ?? null;
});
const gridFetchFrom = useGridFetchFrom(resolvedChildMeta, gridData);

// Ensure metadata is available in localStorage
async function ensureMetadata(): Promise<void> {
  if (metadataLoading.value) return;

  // Check if metadata is already cached
  const existingMeta = cache.getFromLocalStorage<any>(cachedMetaKey.value);
  if (existingMeta) {
    return;
  }

  // Fetch and cache metadata
  metadataLoading.value = true;
  try {
    const res = await getEntityMeta(props.childEntity);
    if (res.status === "success" && res.data) {
      // Cache the metadata using the same mechanism as the API
      await cache.fetchCachedWithLocalStorage(
        cachedMetaKey.value,
        () => Promise.resolve(res),
        30 * 60 * 1000, // 30 minutes TTL
      );
    }
  } catch (err) {
    console.error(
      "[RelatedDataGrid] failed to fetch metadata for",
      props.childEntity,
      err,
    );
  } finally {
    metadataLoading.value = false;
  }
}

function getCachedSelectOptions(
  fieldName: string,
): Array<{ label: string; value: string }> {
  const metaRaw = cache.getFromLocalStorage<any>(cachedMetaKey.value);
  const meta = (metaRaw as any)?.data ?? metaRaw;
  const fields = (meta as any)?.fields || [];
  const f: any = fields.find((x: any) => x?.name === fieldName);
  const raw = f?.options;
  if (!Array.isArray(raw)) return [];
  const normalized = raw
    .map((o: any) => (typeof o === "string" ? { label: o, value: o } : o))
    .filter(Boolean)
    .map((o: any) => ({
      label:
        o?.label === null || o?.label === undefined
          ? String(o?.value)
          : String(o.label),
      value: o?.value === null || o?.value === undefined ? "" : String(o.value),
    }))
    .filter((o: any) => o.value !== "");

  return normalized;
}

const GridLinkEditor = defineComponent({
  name: "GridLinkEditor",
  props: {
    modelValue: { type: [String, Number, null] as any, default: null },
    entity: { type: String, required: true },
    disabled: { type: Boolean, default: false },
    labelKey: { type: String, default: "label" },
    valueKey: { type: String, default: "value" },
  },
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    const searchTerm = ref("");
    const debounced = refDebounced(searchTerm, 250);
    const items = ref<any[]>([]);
    const loadingItems = ref(false);

    async function loadOptions(search?: string) {
      loadingItems.value = true;
      try {
        const res = await getEntityOptions(
          props.entity,
          search || undefined,
          5,
        );
        if (res.status === "success") {
          const opts = (res.options ?? []).map((o: any) => ({ ...o }));
          items.value = opts;
          if (!lookupLabelCache[props.entity])
            lookupLabelCache[props.entity] = {};
          const cache = lookupLabelCache[props.entity];
          for (const o of opts) {
            const v = o[props.valueKey];
            const l = o[props.labelKey];
            if (v !== undefined && l !== undefined && cache) {
              cache[String(v)] = String(l);
            }
          }
        } else {
          items.value = [];
        }
      } catch (e) {
        console.error("[GridLinkEditor] options fetch error", props.entity, e);
        items.value = [];
      } finally {
        loadingItems.value = false;
      }
    }

    function handleOpen(isOpen: boolean) {
      if (isOpen) loadOptions("");
    }

    watch(debounced, (term) => {
      if (term === undefined) return;
      loadOptions(term || "");
    });

    function update(val: any) {
      emit("update:modelValue", val);
    }

    return () =>
      h(resolveComponent("USelectMenu") as any, {
        modelValue: props.modelValue,
        "onUpdate:modelValue": update,
        items: items.value,
        disabled: props.disabled,
        loading: loadingItems.value,
        ignoreFilter: true,
        labelKey: props.labelKey,
        valueKey: props.valueKey,
        searchable: true,
        class: "w-full",
        size: "md",
        "onUpdate:open": handleOpen,
        "onUpdate:searchTerm": (t: string) => {
          searchTerm.value = t || "";
        },
      });
  },
});

const GridSelectEditor = defineComponent({
  name: "GridSelectEditor",
  props: {
    modelValue: { type: [String, Number, null] as any, default: null },
    fieldName: { type: String, required: true },
    disabled: { type: Boolean, default: false },
  },
  emits: ["update:modelValue"],
  setup(p, { emit }) {
    const searchTerm = ref("");

    const items = computed(() => {
      const metaRaw = cache.getFromLocalStorage<any>(cachedMetaKey.value);
      const meta = (metaRaw as any)?.data ?? metaRaw;
      const fields = (meta as any)?.fields || [];
      const field = fields.find((f: any) => f?.name === p.fieldName);
      const raw = (field as any)?.options;
      const opts = Array.isArray(raw)
        ? raw.map((o: any) =>
            typeof o === "string" ? { label: o, value: o } : o,
          )
        : [];

      const normalized = opts
        .filter(Boolean)
        .map((o: any) => ({
          ...o,
          value:
            o?.value === null || o?.value === undefined ? "" : String(o.value),
          label:
            o?.label === null || o?.label === undefined
              ? String(o?.value)
              : String(o.label),
        }))
        .filter((o: any) => o.value !== "");

      const term = (searchTerm.value || "").toLowerCase();
      if (!term) return normalized;
      return normalized.filter((o: any) =>
        String(o?.label || "")
          .toLowerCase()
          .includes(term),
      );
    });

    function update(val: any) {
      emit("update:modelValue", val);
    }

    const displayValue = computed(() => {
      if (p.modelValue === null || p.modelValue === undefined) return null;
      const stringValue = String(p.modelValue);
      const option = items.value.find(
        (o: any) => String(o.value) === stringValue,
      );
      return option || null;
    });

    return () =>
      h(resolveComponent("USelectMenu") as any, {
        modelValue: displayValue.value,
        "onUpdate:modelValue": (selected: any) => {
          update(selected?.value ?? null);
        },
        items: items.value,
        disabled: p.disabled,
        searchable: true,
        ignoreFilter: true,
        valueKey: "value",
        labelKey: "label",
        class: "w-full",
        size: "md",
        "onUpdate:searchTerm": (t: string) => {
          searchTerm.value = t || "";
        },
      });
  },
});

function ensureLookupArray(entity: string): any[] {
  if (!lookupArrays[entity]) lookupArrays[entity] = [];
  if (lookupVersions[entity] === undefined) lookupVersions[entity] = 0;
  return lookupArrays[entity];
}

async function fetchLookupOptions(entity: string): Promise<void> {
  if (linkFetchInFlight.has(entity)) return;
  if (lookupArrays[entity]?.length) return;
  linkFetchInFlight.add(entity);
  try {
    const res = await getEntityOptions(entity, undefined, 5);
    if (res.status === "success") {
      const arr = ensureLookupArray(entity);
      arr.splice(0, arr.length, ...(res.options ?? []));
      lookupVersions[entity] = (lookupVersions[entity] ?? 0) + 1;
    }
  } catch (err) {
    console.error(`[RelatedDataGrid] fetch failed for "${entity}":`, err);
  } finally {
    linkFetchInFlight.delete(entity);
  }
}

async function cancelDirtyChanges(): Promise<void> {
  dirty.value = false;
  dirtyRows.value.clear();
  deletedIds.value = [];
  await loadData();
}

// Visible fields — sorted so editable fields come first, readonly at end
const childFields = computed<FieldMeta[]>(() => {
  if (!props.childMeta?.fields) {
    // If no props metadata, try to get from cache
    const metaRaw = cache.getFromLocalStorage<any>(cachedMetaKey.value);
    const meta = (metaRaw as any)?.data ?? metaRaw;
    if (!meta?.fields) return [];

    // Use cached metadata
    const fields = meta.fields.filter(
      (f: FieldMeta) => f.in_list_view && !f.hidden,
    );
    if (fields.length === 0) {
      return meta.fields
        .filter((f: FieldMeta) => !f.hidden && f.name !== "id")
        .slice(0, 6);
    }
    return fields.filter((f: FieldMeta) => {
      if (["id", "created_at", "updated_at", "workflow_state"].includes(f.name))
        return false;
      if (f.name === props.fkField) return false;
      return true;
    });
  }

  // Use props metadata if available
  let fields = props.childMeta.fields.filter(
    (f) => f.in_list_view && !f.hidden,
  );
  if (fields.length === 0) {
    fields = props.childMeta.fields
      .filter((f) => !f.hidden && f.name !== "id")
      .slice(0, 6);
  }

  const filtered = fields.filter((f) => {
    if (["id", "created_at", "updated_at", "workflow_state"].includes(f.name))
      return false;
    if (f.name === props.fkField) return false;
    return true;
  });

  // Sort: editable fields first, then readonly fields
  return [...filtered].sort((a, b) => {
    if (a.readonly && !b.readonly) return 1;
    if (!a.readonly && b.readonly) return -1;
    return 0;
  });
});

function getColumnSize(field: FieldMeta): number {
  switch (field.field_type) {
    case "link":
      return 280;
    case "text":
      return 240;
    case "int":
    case "integer":
      return 100;
    case "float":
      return 120;
    case "boolean":
      return 90;
    case "date":
      return 140;
    case "datetime":
      return 180;
    default:
      return 160;
  }
}

// Columns
const columns = computed<NuGridColumn<Record<string, any>>[]>(() => {
  const cols: NuGridColumn<Record<string, any>>[] = [];

  // Row-number column
  cols.push({
    accessorKey: "__item_no",
    header: "#",
    size: 50,
    minSize: 50,
    maxSize: 50,
    enableEditing: false,
    enableSorting: false,
    enableResizing: false,
    enableHiding: false,
    enableFocusing: false,
    cell: ({ row }: { row: { original: Record<string, any> } }) => {
      const idx = gridData.value.findIndex((r) => r.id === row.original.id);
      return idx >= 0 ? (page.value - 1) * pageSize.value + idx + 1 : "";
    },
  } as NuGridColumn<Record<string, any>>);

  for (const field of childFields.value) {
    const col: any = {
      accessorKey: field.name,
      header: field.required ? `${field.label} *` : field.label,
      size: getColumnSize(field),
      enableEditing: !field.readonly,
      enableSorting: false,
      enableResizing: true,
      enableHiding: false,
    };

    const ft = field.field_type;

    if (ft === "boolean") {
      col.cellDataType = "boolean";
    } else if (ft === "date") {
      col.cellDataType = "date";
    } else if (["int", "integer", "float", "number"].includes(ft)) {
      col.cellDataType = "number";
    } else if (ft === "select") {
      // Force plain-text rendering with custom editor.
      // NuGrid's built-in selection renderer can appear as a checkbox.
      col.cellDataType = "text";
      const rawOptions =
        Array.isArray(field.options) && field.options.length
          ? field.options
          : getCachedSelectOptions(field.name);
      const selectOptions = rawOptions.map((o: any) =>
        typeof o === "string" ? { label: o, value: o } : o,
      );
      col.cell = ({ row }: { row: { original: Record<string, any> } }) => {
        const v = row.original[field.name];
        if (v === null || v === undefined || v === "") return "";
        const hit = selectOptions.find(
          (o: any) => String(o?.value) === String(v),
        );
        return hit?.label ?? v;
      };
      col.editor = {
        component: GridSelectEditor,
        props: {
          fieldName: field.name,
        },
      };
    } else if (ft === "link" && field.link_entity) {
      const entity = field.link_entity;
      col.cellDataType = "text";
      col.cell = ({ row }: { row: { original: Record<string, any> } }) => {
        const v = row.original[field.name];
        if (!v) return "";
        const key = `${entity}::${v}`;
        const cachedLabel = lookupLabelCache[entity]?.[String(v)];
        return linkTitles.value[key] ?? cachedLabel ?? v;
      };
      col.editor = {
        component: GridLinkEditor,
        props: {
          entity,
          labelKey: "label",
          valueKey: "value",
          limit: 5,
        },
      };
    } else {
      col.cellDataType = "text";
    }

    cols.push(col as NuGridColumn<Record<string, any>>);
  }

  // Row action menu column
  cols.push({
    accessorKey: "_actions",
    header: "",
    size: 48,
    minSize: 48,
    maxSize: 48,
    enableEditing: false,
    enableSorting: false,
    enableResizing: false,
    enableHiding: false,
    enableFocusing: false,
    cell: ({ row }: { row: { original: Record<string, any> } }) => {
      const items: any[] = [];

      const isNewRow = String(row.original.id).startsWith("__new__");

      // View Details - only for saved rows
      if (!isNewRow) {
        items.push({
          label: "View Details",
          icon: "i-lucide-external-link",
          onSelect: () => {
            router.push(`/${props.childEntity}/${row.original.id}`);
          },
        });
      }

      // Delete - visible when canDelete is true
      if (props.canDelete) {
        items.push({
          label: "Delete",
          icon: "i-lucide-trash-2",
          onSelect: () => handleDeleteRow(row.original),
        });
      }

      return h("div", { class: "flex items-center justify-center" }, [
        h(
          resolveComponent("UDropdownMenu"),
          {
            items: [items],
          },
          {
            default: () =>
              h(resolveComponent("UButton"), {
                icon: "i-lucide-ellipsis-vertical",
                variant: "outline",
                color: "gray",
                size: "md",
                "aria-label": "Actions",
              }),
          },
        ),
      ]);
    },
  } as NuGridColumn<Record<string, any>>);

  return cols;
});

// NuGrid events — options are loaded only when the editor dropdown opens
function onCellEditingStarted(event: any): void {
  // Intentionally no option prefetch here.
  // Lookup options are fetched by GridLinkEditor only when the USelectMenu opens.
}

async function onCellValueChanged(event: any): Promise<void> {
  if (!event.row?.original || !event.column?.id) return;
  const rowId = String(event.row.original.id);
  const fieldName = String(event.column.id);
  const newValue = event.newValue;

  event.row.original[fieldName] = newValue;
  dirtyRows.value.add(rowId);
  dirty.value = true;

  // Apply fetch_from rules if this field is a source
  if (gridFetchFrom.isFetchFromSource(fieldName)) {
    const res = await gridFetchFrom.applyForRow(rowId, fieldName, newValue);
    if (res?.linkTitles && Object.keys(res.linkTitles).length) {
      linkTitles.value = { ...linkTitles.value, ...res.linkTitles };
      for (const [key, label] of Object.entries(res.linkTitles)) {
        const [entityKey, value] = key.split("::");
        if (!entityKey || !value) continue;
        if (!lookupLabelCache[entityKey]) lookupLabelCache[entityKey] = {};
        lookupLabelCache[entityKey][value] = String(label ?? value);
      }
    }
  }
}

// Delete handler — kept outside render function to avoid inject() context loss
async function handleDeleteRow(rowData: Record<string, any>): Promise<void> {
  const isNewRow = String(rowData.id).startsWith("__new__");
  if (isNewRow) {
    const idx = gridData.value.findIndex((r) => r.id === rowData.id);
    if (idx >= 0) gridData.value.splice(idx, 1);
    dirty.value = true;
    return;
  }

  const confirmed = await deleteDialog({
    entityName: props.childMeta?.label || props.childEntity,
    itemName: String(rowData.id),
  });
  if (!confirmed) return;

  try {
    const res = await postEntityAction(props.childEntity, {
      action: "delete",
      id: rowData.id,
    });
    if (res.status === "success") {
      if (res.message) {
        toast.add({ title: res.message, color: "success", type: "foreground" });
      }
      await loadData();
    } else {
      if (res.message) {
        toast.add({ title: res.message, color: "error", type: "foreground" });
      }
    }
  } catch (err: any) {
    if (err?.message) {
      toast.add({ title: err.message, color: "error", type: "foreground" });
    }
  }
}

// Data loading
async function loadData(): Promise<void> {
  if (!props.parentId || props.parentId === "new") return;
  loading.value = true;
  try {
    const res = await getEntityListView(props.childEntity, {
      page: page.value,
      pageSize: pageSize.value,
      filterField: props.fkField,
      filterValue: props.parentId,
    });

    if (res.status === "success") {
      gridData.value = (res.data ?? []).map((r: any) => ({ ...r }));
      total.value = res.total || 0;

      // Extract link titles from response (API returns _link_titles per-row)
      const linkTitlesData: Record<string, string> = {};
      for (const row of gridData.value) {
        const perRow = (row as any)?._link_titles;
        if (perRow && typeof perRow === "object") {
          Object.assign(linkTitlesData, perRow as Record<string, string>);
        }
      }
      linkTitles.value = linkTitlesData;

      // Seed label cache
      for (const [key, label] of Object.entries(
        linkTitlesData as Record<string, unknown>,
      )) {
        const [entityKey, value] = key.split("::");
        if (!entityKey || !value) continue;
        if (!lookupLabelCache[entityKey]) lookupLabelCache[entityKey] = {};
        lookupLabelCache[entityKey][value] = String(label ?? value);
      }
    }
  } catch (err) {
    console.error("[RelatedDataGrid] load failed:", err);
  } finally {
    loading.value = false;
  }
}

// Create an empty row for inline adding
function createEmptyRow(): Record<string, any> {
  const row: Record<string, any> = {
    id: `__new__${Date.now()}_${Math.random().toString(36).slice(2, 6)}`,
    [props.fkField]: props.parentId,
  };
  for (const field of childFields.value) {
    if (field.name === props.fkField) continue;
    row[field.name] = field.default ?? null;
  }
  return row;
}

function addRow(): void {
  gridData.value.push(createEmptyRow());
  dirty.value = true;
}

// Save dirty rows + new rows
async function saveDirtyRows(): Promise<void> {
  if (!dirty.value) return;

  // Collect new rows and changed existing rows
  const rowsToSave = gridData.value.filter((r) => {
    const id = String(r.id);
    return id.startsWith("__new__") || dirtyRows.value.has(id);
  });
  if (rowsToSave.length === 0 && deletedIds.value.length === 0) return;

  loading.value = true;
  try {
    const res = await bulkSaveChildren(
      props.parentEntity,
      props.parentId,
      props.childEntity,
      rowsToSave,
      deletedIds.value,
    );
    if (res.status === "success") {
      dirty.value = false;
      dirtyRows.value.clear();
      deletedIds.value = [];
      if (res.message) {
        toast.add({
          title: res.message,
          color: "success",
          type: "foreground",
        });
      }
      // Refetch to get computed/readonly fields updated by post-save hooks
      await loadData();
    } else {
      if (res.message) {
        toast.add({
          title: res.message,
          color: "error",
          type: "foreground",
        });
      }
    }
  } catch (err: any) {
    console.error("[RelatedDataGrid] save failed:", err);
    if (err?.message) {
      toast.add({
        title: err.message,
        color: "error",
        type: "foreground",
      });
    }
  } finally {
    loading.value = false;
  }
}

// Pagination
const totalPages = computed(() =>
  Math.max(1, Math.ceil(total.value / pageSize.value)),
);

async function setPage(newPage: number): Promise<void> {
  // Save dirty rows before changing page
  if (dirty.value) {
    await saveDirtyRows();
  }
  page.value = Math.max(1, Math.min(totalPages.value, newPage));
  await loadData();
}

// Expose methods
defineExpose({ loadData, saveDirtyRows, addRow });

// Watch for child entity changes and ensure metadata is loaded
watch(
  () => props.childEntity,
  async (newChildEntity) => {
    if (newChildEntity) {
      await ensureMetadata();
    }
  },
  { immediate: true },
);

// Watch for parent/child changes
watch(
  () => [props.parentId, props.childEntity, props.fkField] as const,
  async ([parentId, childEntity, fkField]) => {
    if (parentId && parentId !== "new" && childEntity && fkField) {
      // Ensure metadata is available before loading data
      await ensureMetadata();
      page.value = 1;
      loadData().then(() => {
        initialLoaded.value = true;
      });
    }
  },
  { immediate: true },
);

// Auto-save on tab blur
</script>

<template>
  <div class="flex flex-col gap-4">
    <!-- Toolbar (always visible) -->
    <div class="flex items-center justify-between px-1">
      <div class="flex items-center gap-2">
        <UButton
          v-if="editable && canAdd"
          icon="i-lucide-plus"
          size="md"
          variant="outline"
          @click="addRow"
        >
          Add Record
        </UButton>
      </div>
      <div class="flex items-center gap-2">
        <UChip v-if="dirty" variant="neutral" color="warning">
          <UButton
            v-if="dirty"
            icon="i-lucide-save"
            size="md"
            variant="soft"
            color="primary"
            :loading="loading"
            @click="saveDirtyRows"
          >
            Save
          </UButton>
        </UChip>
        <UButton
          v-if="dirty"
          icon="i-lucide-x"
          size="md"
          variant="outline"
          :loading="loading"
          @click="cancelDirtyChanges"
        />
        <UButton
          v-if="!dirty"
          icon="i-lucide-refresh-cw"
          size="md"
          variant="outline"
          :loading="loading"
          @click="loadData"
        />
      </div>
    </div>

    <!-- Metadata loading state -->
    <div v-if="metadataLoading" class="flex justify-center">
      <div class="w-full">
        <UEmpty
          icon="i-lucide-loader-circle"
          title="Loading entity metadata..."
          description="Please wait while we fetch the entity metadata."
        />
      </div>
    </div>

    <!-- Initial loading state (content only) -->
    <div v-else-if="loading && !initialLoaded" class="flex justify-center">
      <div class="w-full">
        <!-- <UEmpty
          icon="i-lucide-loader-circle"
          title="Fetching records..."
          description="Please wait while we fetch the related records."
        /> -->
        <USkeleton class="h-4 h-[80px]" />
      </div>
    </div>

    <template v-else>
      <!-- Empty state -->
      <div v-if="gridData.length === 0 && !loading">
        <UEmpty
          icon="i-lucide-file"
          title="No related records."
          description="No related records found. Create one to get started."
        />
      </div>

      <!-- Grid -->
      <div v-if="gridData.length > 0" class="overflow-x-auto">
        <div class="w-full">
          <NuGrid
            ref="gridRef"
            v-model:column-pinning="columnPinning"
            :data="gridData"
            :columns="columns"
            :get-row-id="(row: Record<string, any>) => String(row.id)"
            :layout="{
              autoSize: 'fill',
              resizeMode: 'shift',
            }"
            :editing="
              editable
                ? {
                    enabled: true,
                    startClicks: 'double',
                    startKeys: ['enter', 'f2'],
                  }
                : { enabled: false }
            "
            :focus="{ mode: 'cell' }"
            :column-defaults="{
              resize: true,
              reorder: false,
              wrapText: false,
              menu: undefined,
            }"
            @cell-editing-started="onCellEditingStarted"
            @cell-value-changed="onCellValueChanged"
            :ui="{
              root: 'w-full',
              base: 'w-full',
            }"
          />
        </div>
      </div>

      <!-- Pagination (only when multiple pages) -->
      <div v-if="totalPages > 1" class="flex items-center justify-between px-1">
        <div class="text-sm text-muted-foreground">
          Showing {{ (page - 1) * pageSize + 1 }} to
          {{ Math.min(page * pageSize, total) }} of {{ total }}
        </div>
        <UPagination
          :page="page"
          :items-per-page="pageSize"
          :total="total"
          :disabled="loading"
          @update:page="setPage"
        />
      </div>
    </template>
  </div>
</template>
