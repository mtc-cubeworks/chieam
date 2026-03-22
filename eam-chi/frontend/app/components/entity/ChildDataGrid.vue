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
  "dirty-change": [isDirty: boolean];
  "save-complete": [];
  "loading-change": [isLoading: boolean];
}>();

const router = useRouter();
const { getChildRecords, bulkSaveChildren, getEntityOptions } = useApi();

const gridRef = ref<any>(null);
const gridData = ref<Record<string, any>[]>([]);

const childMeta = computed(() => props.childMeta);
const gridFetchFrom = useGridFetchFrom(childMeta, gridData);
const linkTitles = ref<Record<string, string>>({});
const loading = ref(false);
const dirty = ref(false);
const deletedIds = ref<string[]>([]);
const columnPinning = ref({ left: [] as string[], right: ["_actions"] });

watch(dirty, (val) => emit("dirty-change", val));
watch(loading, (val) => emit("loading-change", val));

// ── Lookup options ────────────────────────────────────────────────────────────
// Plain reactive arrays, one per entity. These are passed directly into
// cellDataTypeOptions.options in the column defs. When options arrive we
// splice() into the same array — Vue's proxy propagates the mutation to
// NuGrid's dropdown without touching the column definitions at all, so the
// columns computed never re-runs and the grid never remounts.

const lookupArrays: Record<string, any[]> = reactive({});
const lookupVersions: Record<string, number> = reactive({});
const lookupLabelCache: Record<string, Record<string, string>> = reactive({});
const linkFetchInFlight = new Set<string>();

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
    console.error(`[ChildDataGrid] fetch failed for "${entity}":`, err);
    linkFetchInFlight.delete(entity);
  }
}

// ── Visible fields ────────────────────────────────────────────────────────────

const childFields = computed<FieldMeta[]>(() => {
  if (!props.childMeta?.fields) return [];
  const filtered = props.childMeta.fields.filter((f) => {
    if (f.hidden) return false;
    if (
      [
        "id",
        "created_at",
        "updated_at",
        "total_amount",
        "workflow_state",
        "row_no",
      ].includes(f.name)
    )
      return false;
    if (f.name === props.fkField) return false;
    if (f.label === "#") return false;
    return true;
  });

  // Sort: editable fields first, then readonly fields at the end
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

// ── Columns ───────────────────────────────────────────────────────────────────
// Depends ONLY on childFields — never on options data or props.editable.
// Lookup columns get a reference to their lookupArrays[entity] array.
// That array is mutated in-place when options load, so no rebuild happens.

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
      return idx >= 0 ? idx + 1 : "";
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
    } else if (ft === "select" && field.options?.length) {
      col.cellDataType = "selection";
      const selectOptions = field.options.map((o: any) =>
        typeof o === "string" ? { label: o, value: o } : o,
      );
      col.cellDataTypeOptions = {
        options: selectOptions,
        searchable: true,
      };
      col.cell = ({ row }: { row: { original: Record<string, any> } }) => {
        const v = row.original[field.name];
        if (v === null || v === undefined || v === "") return "";
        const hit = selectOptions.find(
          (o: any) => String(o?.value) === String(v),
        );
        return hit?.label ?? v;
      };
    } else if (ft === "link" && field.link_entity) {
      const entity = field.link_entity;
      // ensureLookupArray creates the array if it doesn't exist yet.
      // We do NOT read .length or any value here — no reactive dependency
      // on the array contents is created in this computed.
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
      const isNewRow = String(row.original.id).startsWith("__new__");
      const items: any[] = [];

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
          onSelect: () => {
            const rowId = row.original.id;
            // Remove from grid
            const idx = gridData.value.findIndex((r) => r.id === rowId);
            if (idx >= 0) {
              gridData.value.splice(idx, 1);
            }
            // Track deletion if it's a saved row
            if (!isNewRow) {
              deletedIds.value.push(String(rowId));
            }
            dirty.value = true;
          },
        });
      }

      if (items.length === 0) return null;

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
                variant: "ghost",
                color: "gray",
                size: "sm",
                "aria-label": "Actions",
              }),
          },
        ),
      ]);
    },
  } as NuGridColumn<Record<string, any>>);

  return cols;
});

// ── NuGrid events ─────────────────────────────────────────────────────────────

function onCellEditingStarted(_event: any): void {
  // Intentionally no option prefetch here.
  // Lookup options are fetched by GridLinkEditor only when the USelectMenu opens.
}

async function onCellValueChanged(event: any): Promise<void> {
  if (!event.row?.original || !event.column?.id) return;
  const rowId = String(event.row.original.id);
  const fieldName = String(event.column.id);
  const newValue = event.newValue;

  event.row.original[fieldName] = newValue;
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

// ── Data ──────────────────────────────────────────────────────────────────────

async function loadData(): Promise<void> {
  if (!props.parentId || props.parentId === "new") return;
  loading.value = true;
  const timeout = setTimeout(() => {
    loading.value = false;
  }, 10_000);
  try {
    const res = await getChildRecords(
      props.parentEntity,
      props.parentId,
      props.childEntity,
    );
    if (res.status === "success") {
      gridData.value = (res.data ?? []).map((r: any) => ({ ...r }));
      const linkTitlesData = (res as any)._link_titles ?? {};
      linkTitles.value = linkTitlesData as Record<string, string>;

      // Seed label cache from linkTitles so display uses labels immediately
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
    console.error("[ChildDataGrid] load failed:", err);
  } finally {
    clearTimeout(timeout);
    loading.value = false;
  }
}

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

function getChildData(): Record<string, any>[] {
  return gridData.value;
}
function getDeletedIds(): string[] {
  return deletedIds.value;
}
function markAsSaved(): void {
  dirty.value = false;
  deletedIds.value = [];
}

async function saveAll(): Promise<void> {
  if (!dirty.value) return;
  loading.value = true;
  try {
    const res = await bulkSaveChildren(
      props.parentEntity,
      props.parentId,
      props.childEntity,
      gridData.value,
      deletedIds.value,
    );
    if (res.status === "success") {
      dirty.value = false;
      await loadData();
      emit("save-complete");
    }
  } catch (err) {
    console.error("[ChildDataGrid] save failed:", err);
  } finally {
    loading.value = false;
  }
}

defineExpose({ loadData, saveAll, getChildData, getDeletedIds, markAsSaved });

watch(
  () => [props.parentId, props.childEntity] as const,
  ([parentId, childEntity]) => {
    if (parentId && parentId !== "new" && childEntity) loadData();
  },
  { immediate: true },
);
</script>

<template>
  <div class="flex flex-col gap-2">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <UButton
          v-if="editable && canAdd"
          icon="i-lucide-plus"
          size="md"
          variant="outline"
          :disabled="loading"
          @click="addRow"
        >
          Add Line
        </UButton>
        <UBadge v-if="dirty" color="warning" variant="subtle" size="sm">
          Unsaved changes
        </UBadge>
      </div>
      <UButton
        icon="i-lucide-refresh-cw"
        size="md"
        variant="outline"
        :loading="loading"
        @click="loadData"
      />
    </div>

    <div
      v-if="loading && gridData.length === 0"
      class="flex items-center justify-center py-10"
    >
      <UIcon
        name="i-lucide-loader-2"
        class="animate-spin h-6 w-6 text-primary"
      />
    </div>

    <div
      v-else-if="!loading && gridData.length === 0"
      class="flex flex-col items-center justify-center gap-2 py-10 border border-dashed border-accented rounded-lg text-muted-foreground"
    >
      <UIcon name="i-lucide-inbox" class="w-8 h-8" />
      <p class="text-sm">
        No records yet{{
          editable && canAdd ? " — click Add Line to begin" : ""
        }}
      </p>
    </div>

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
                  startClicks: 'single',
                  startKeys: ['enter', 'f2', 'bs', 'alpha', 'numeric'],
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
  </div>
</template>
