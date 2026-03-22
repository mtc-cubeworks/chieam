<script setup lang="ts">
import { h, resolveComponent } from "vue";
import { upperFirst } from "scule";
import { refDebounced } from "@vueuse/core";
import type { TableColumn, TableRow } from "@nuxt/ui";
import type { EntityMeta, FieldMeta } from "~/composables/useApiTypes";
import type { DropdownMenuItem } from "@nuxt/ui";
import { useTreeView } from "~/composables/useTreeView";
import { resolveCellValue } from "~/utils/cellFormat";
import { useWorkflowApi } from "~/composables/useWorkflowApi";

const route = useRoute();
const router = useRouter();
const {
  getEntityMeta,
  getEntityList,
  getEntityListView,
  deleteEntity,
  exportEntity,
  getEntityTree,
} = useApi();
const { getWorkflowStates } = useWorkflowApi();
const { hasParentField } = useTreeView();
const toast = useToast();
const confirmDialog = useConfirmDialog();
const deleteDialog = useDeleteDialog();
const UCheckbox = resolveComponent("UCheckbox");
const UButton = resolveComponent("UButton");
const UDropdownMenu = resolveComponent("UDropdownMenu");

const entityName = computed(() => route.params.entity as string);
const entityMeta = ref<EntityMeta | null>(null);
const data = ref<any[]>([]);
const treeData = ref<any[]>([]);
const linkTitles = ref<Record<string, Record<string, string>>>({});
const loading = ref(true);
const metaLoading = ref(true);
const permissionsLoading = ref(true);
const permissions = ref<Record<string, boolean> | null>(null);
const treeLoading = ref(false);
const error = ref("");
const viewMode = ref<"list" | "tree" | "diagram">("list");
const canUseTreeView = computed(
  () => !!entityMeta.value?.is_tree && !!entityMeta.value?.tree_parent_field,
);
const canUseDiagramView = computed(() => !!entityMeta.value?.is_diagram);

const pagination = reactive({
  pageIndex: 0,
  pageSize: 10,
  total: 0,
});

const pageSizeOptions = [10, 20, 50, 100].map((size) => ({
  label: `${size} / page`,
  value: size,
}));

// Computed property to get current page (1-based)
const currentPage = computed(() => pagination.pageIndex + 1);
const pageStart = computed(() => {
  if (!pagination.total || data.value.length === 0) return 0;
  return pagination.pageIndex * pagination.pageSize + 1;
});
const pageEnd = computed(() => {
  if (!pagination.total || data.value.length === 0) return 0;
  return Math.min(
    pagination.total,
    pagination.pageIndex * pagination.pageSize + data.value.length,
  );
});

const searchInput = ref("");
const searchDebounced = refDebounced(searchInput, 400);

const filters = reactive({
  sortField: "",
  sortOrder: "desc" as "asc" | "desc",
});

const filterField = ref<string | null>(null);
const columnVisibility = ref<Record<string, boolean>>({});
const rowSelection = ref<Record<string, boolean>>({});
const sorting = ref<{ id: string; desc: boolean }[]>([]);

const table = useTemplateRef<{ tableApi?: any }>("table");

const workflowStates = ref<any[]>([]);
const workflowStatesById = computed(() => {
  const map = new Map<string, any>();
  for (const s of workflowStates.value || []) {
    if (s?.id) map.set(String(s.id), s);
  }
  return map;
});
const workflowStatesBySlug = computed(() => {
  const map = new Map<string, any>();
  for (const s of workflowStates.value || []) {
    if (s?.slug) map.set(String(s.slug), s);
  }
  return map;
});

const getWorkflowStateByValue = (value: string) => {
  if (!value) return null;
  return (
    workflowStatesById.value.get(value) ||
    workflowStatesBySlug.value.get(value) ||
    null
  );
};

const NAMED_COLOR_MAP: Record<string, string> = {
  blue: "info",
  cyan: "info",
  teal: "info",
  green: "success",
  lime: "success",
  yellow: "warning",
  amber: "warning",
  orange: "warning",
  red: "error",
  pink: "error",
  rose: "error",
  purple: "secondary",
  violet: "secondary",
  indigo: "secondary",
  gray: "neutral",
  grey: "neutral",
  slate: "neutral",
  zinc: "neutral",
};

const normalizeBadgeColor = (color?: string) => {
  if (!color) return "neutral" as const;

  const c = String(color).toLowerCase().trim();
  if (
    c === "primary" ||
    c === "secondary" ||
    c === "success" ||
    c === "info" ||
    c === "warning" ||
    c === "error" ||
    c === "neutral"
  ) {
    return c as any;
  }

  if (NAMED_COLOR_MAP[c]) return NAMED_COLOR_MAP[c] as any;

  if (/^#[0-9a-f]{6}$/i.test(c)) {
    const r = parseInt(c.slice(1, 3), 16);
    const g = parseInt(c.slice(3, 5), 16);
    const b = parseInt(c.slice(5, 7), 16);
    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);
    const delta = max - min;
    if (delta === 0) return "neutral" as const;

    let hue = 0;
    if (max === r) hue = ((g - b) / delta) % 6;
    else if (max === g) hue = (b - r) / delta + 2;
    else hue = (r - g) / delta + 4;
    hue = Math.round(hue * 60);
    if (hue < 0) hue += 360;

    if (hue >= 330 || hue < 20) return "error" as const;
    if (hue >= 20 && hue < 70) return "warning" as const;
    if (hue >= 70 && hue < 170) return "success" as const;
    if (hue >= 170 && hue < 255) return "info" as const;
    if (hue >= 255 && hue < 330) return "secondary" as const;
  }

  return "neutral" as const;
};

const selectedCount = computed(
  () => table.value?.tableApi?.getFilteredSelectedRowModel().rows.length || 0,
);

const viewModeItems = computed(() => {
  const items: any[] = [
    {
      label: "List View",
      icon: "i-lucide-list",
      onSelect: () => (viewMode.value = "list"),
    },
  ];
  if (canUseTreeView.value) {
    items.push({
      label: "Tree View",
      icon: "i-lucide-list-tree",
      onSelect: () => (viewMode.value = "tree"),
    });
  }
  if (canUseDiagramView.value) {
    items.push({
      label: "Diagram View",
      icon: "i-lucide-git-branch",
      onSelect: () => (viewMode.value = "diagram"),
    });
  }
  return [items];
});

const perms = computed(() => permissions.value || undefined);
const canCreate = computed(() => perms.value?.can_create === true);
const canDelete = computed(() => perms.value?.can_delete === true);
const canRead = computed(() => perms.value?.can_read !== false);

const bulkMenuItems = computed(() => {
  if (!selectedCount.value) return [];
  const items: any[] = [];

  items.push({
    label: "Export",
    icon: "i-lucide-download",
    onSelect: async () => {
      const selectedRows =
        table.value?.tableApi?.getFilteredSelectedRowModel().rows || [];
      if (selectedRows.length === 0) return;

      try {
        const blob = await exportEntity(entityName.value);
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${entityName.value}_export_${new Date().toISOString().split("T")[0]}.xlsx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);

        toast.add({
          title: "Success",
          description: "Export completed successfully",
          color: "success",
        });
      } catch (error: any) {
        toast.add({
          title: "Error",
          description: error.message || "Failed to export records",
          color: "error",
        });
      }
    },
  });

  if (canDelete.value) {
    items.push({
      label: `Delete (${selectedCount.value})`,
      icon: "i-lucide-trash-2",
      color: "error",
      onSelect: () => {
        const selectedRows =
          table.value?.tableApi?.getFilteredSelectedRowModel().rows || [];
        if (selectedRows.length === 0) return;

        const count = selectedRows.length;
        (async () => {
          const confirmed = await confirmDialog({
            title: "Delete Records",
            description: `Are you sure you want to delete ${count} record${count > 1 ? "s" : ""}? This action cannot be undone.`,
            confirmLabel: "Delete",
            confirmColor: "error",
          });
          if (!confirmed) return;

          try {
            const deletePromises = selectedRows.map((row: any) =>
              deleteEntity(entityName.value, row.original.id),
            );

            await Promise.all(deletePromises);

            toast.add({
              title: "Success",
              description: `Deleted ${count} record${count > 1 ? "s" : ""} successfully`,
              color: "success",
            });

            rowSelection.value = {};
            await loadData();
          } catch (error: any) {
            toast.add({
              title: "Error",
              description: error.message || "Failed to delete records",
              color: "error",
            });
          }
        })();
      },
    });
  }

  return [items];
});

const filterFieldOptions = computed(() => {
  const options = (entityMeta.value?.fields || [])
    .filter(
      (field: FieldMeta) =>
        !field.hidden && field.name !== "id" && field.in_list_view,
    )
    .map((field: FieldMeta) => ({
      label: field.label,
      value: field.name,
    }));
  return [{ label: "No filter", value: null }, ...options];
});

const columnVisibilityItems = computed((): any[] => {
  const fields = visibleFields.value || [];
  return fields
    .filter((f) => f.id !== "select")
    .map((f) => ({
      label: f.header,
      type: "checkbox" as const,
      checked: columnVisibility.value[f.id] !== false,
      onUpdateChecked(checked: boolean) {
        columnVisibility.value = {
          ...columnVisibility.value,
          [f.id]: !!checked,
        };
      },
      onSelect(e: Event) {
        e.preventDefault();
      },
    }));
});

const visibleFields = computed(() => {
  if (!entityMeta.value?.fields) return [];

  const fields: {
    id: string;
    accessorKey: string;
    header: string;
    fieldName: string;
  }[] = [];

  // Add in_list_view fields
  entityMeta.value.fields
    .filter((f: FieldMeta) => f.in_list_view && !f.hidden)
    .forEach((f: FieldMeta) => {
      fields.push({
        id: f.name,
        accessorKey: f.name,
        header: f.label,
        fieldName: f.name,
      });
    });

  // Add workflow_state if entity has it
  const hasWorkflowState = entityMeta.value.fields.some(
    (f: FieldMeta) => f.name === "workflow_state",
  );
  if (hasWorkflowState) {
    fields.push({
      id: "workflow_state",
      accessorKey: "workflow_state",
      header: "Status",
      fieldName: "workflow_state",
    });
  }

  // Always add "Last Edited" as the last column (uses updated_at)
  fields.push({
    id: "_last_edited",
    accessorKey: "updated_at",
    header: "",
    fieldName: "_last_edited",
  });

  return fields;
});

const tableColumns = computed<TableColumn<any>[]>(() => {
  const selectionColumn: TableColumn<any> = {
    id: "select",
    header: ({ table }) =>
      h(UCheckbox, {
        modelValue: table.getIsSomePageRowsSelected()
          ? "indeterminate"
          : table.getIsAllPageRowsSelected(),
        "onUpdate:modelValue": (value: boolean | "indeterminate") =>
          table.toggleAllPageRowsSelected(!!value),
        "aria-label": "Select all",
      }),
    cell: ({ row }) =>
      h(UCheckbox, {
        modelValue: row.getIsSelected(),
        "onUpdate:modelValue": (value: boolean | "indeterminate") =>
          row.toggleSelected(!!value),
        "aria-label": "Select row",
      }),
    enableSorting: false,
    enableHiding: false,
  };

  const fieldColumns = visibleFields.value.map(
    ({ id, accessorKey, header }) => ({
      id,
      accessorKey,
      header: ({ column }: { column: any }) =>
        h(UButton, {
          color: "neutral",
          variant: "ghost",
          label: header,
          icon: column.getIsSorted()
            ? column.getIsSorted() === "asc"
              ? "i-lucide-arrow-up-narrow-wide"
              : "i-lucide-arrow-down-wide-narrow"
            : "i-lucide-arrow-up-down",
          class:
            "-mx-2.5 data-[state=open]:bg-elevated max-w-[320px] truncate justify-start",
          onClick: () => column.toggleSorting(column.getIsSorted() === "asc"),
        }),
    }),
  );

  return [selectionColumn, ...fieldColumns];
});

const getCellValue = (row: any, fieldName: string) => {
  return resolveCellValue(row, fieldName, entityMeta.value?.fields);
};

// Workflow states are pre-fetched at login (useAuth → getWorkflowStates) and
// stored in localStorage with a 24h TTL (key: "workflow:states").
// This call hits the cache instantly — no network request on normal page loads.
// The status column badges (workflow_state) use getWorkflowStateByValue() which
// resolves by both UUID and slug, then normalizeBadgeColor() maps named colors
// (e.g. "blue", "green") to Nuxt UI semantic tokens (e.g. "info", "success").
const loadWorkflowStates = async () => {
  try {
    const res = await getWorkflowStates();
    workflowStates.value = res?.data || [];
  } catch (_e) {
    workflowStates.value = [];
  }
};

const loadMetadata = async () => {
  try {
    metaLoading.value = true;
    permissionsLoading.value = true;
    const metaRes = await getEntityMeta(entityName.value);
    entityMeta.value = metaRes.data;
    permissions.value =
      (metaRes.data?.permissions as Record<string, boolean> | undefined) ||
      null;
  } catch (err: any) {
    error.value = err.message || "Failed to load metadata";
    console.error(err);
  } finally {
    metaLoading.value = false;
    permissionsLoading.value = false;
  }
};

const loadData = async () => {
  try {
    loading.value = true;
    error.value = "";

    const sort = sorting.value[0];
    // Map _last_edited back to updated_at for backend
    const resolvedSortField =
      sort?.id === "_last_edited"
        ? "updated_at"
        : sort?.id || filters.sortField || undefined;
    const resolvedSortOrder = sort
      ? sort.desc
        ? "desc"
        : "asc"
      : filters.sortOrder;

    const listRes = await getEntityListView(entityName.value, {
      page: currentPage.value,
      pageSize: pagination.pageSize,
      sortField: resolvedSortField,
      sortOrder: resolvedSortOrder,
      filterField: filterField.value || undefined,
      filterValue: searchDebounced.value || undefined,
    });

    // Extract link titles from each record
    const titles: Record<string, Record<string, string>> = {};
    (listRes.data || []).forEach((record: any, index: number) => {
      if (record._link_titles) {
        titles[index] = record._link_titles;
      }
    });
    linkTitles.value = titles;

    data.value = listRes.data || [];
    pagination.total = listRes.total || 0;
  } catch (err: any) {
    error.value = err.message || "Failed to load data";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const loadTreeData = async () => {
  if (!entityMeta.value?.is_tree) return;

  try {
    treeLoading.value = true;
    const response = await getEntityTree(entityName.value, {
      parentField: entityMeta.value.tree_parent_field || undefined,
      titleField: entityMeta.value.title_field || undefined,
    });

    if (response.status === "success") {
      treeData.value = response.data || [];
    } else {
      throw new Error(response.message || "Failed to load tree data");
    }
  } catch (err: any) {
    console.error("Tree data load error:", err);
    treeData.value = [];
  } finally {
    treeLoading.value = false;
  }
};

const handleCreate = () => {
  router.push(`/${entityName.value}/new`);
};

const handleView = (row: any) => {
  router.push(`/${entityName.value}/${row.id}`);
};

const handleRowSelect = (event: Event, row: TableRow<any>) => {
  const target = event.target as HTMLElement;
  if (target?.closest("input[type='checkbox']")) return;
  handleView(row.original || row);
};

const handleEdit = (row: any) => {
  router.push(`/${entityName.value}/${row.id}?edit=true`);
};

const handleDeleteClick = (row: any) => {
  const itemName =
    row[entityMeta.value?.title_field || "name"] || `ID: ${row.id}`;

  (async () => {
    const confirmed = await deleteDialog({
      entityName: upperFirst(entityName.value),
      itemName,
    });
    if (!confirmed) return;

    const response = await deleteEntity(entityName.value, row.id);
    if (response.status === "success") {
      toast.add({ title: "Deleted successfully", color: "success" });
      await loadData();
    } else {
      throw new Error(response.message || "Delete failed");
    }
  })().catch((err: any) => {
    toast.add({
      title: "Error",
      description: err?.message || "Delete failed",
      color: "error",
    });
  });
};

watch(
  entityName,
  async () => {
    pagination.pageIndex = 0;
    searchInput.value = "";
    filterField.value = null;
    entityMeta.value = null;
    permissions.value = null;
    error.value = "";
    await Promise.all([loadMetadata(), loadData(), loadWorkflowStates()]);
  },
  { immediate: true },
);

// Debounced search triggers reload
watch([searchDebounced, sorting, filterField], () => {
  pagination.pageIndex = 0;
  loadData();
});

// Page changes trigger reload
watch(
  () => pagination.pageIndex,
  (newVal, oldVal) => {
    if (oldVal !== undefined && newVal !== oldVal) {
      loadData();
    }
  },
);

const handlePageSizeChange = (value: number | string | null) => {
  const nextSize = Number(value || pagination.pageSize);
  if (!Number.isFinite(nextSize) || nextSize === pagination.pageSize) return;

  pagination.pageSize = nextSize;
  pagination.pageIndex = 0;
  loadData();
};

// Watch viewMode changes to load tree data only when switching to tree view
watch(
  () => viewMode.value,
  async (newMode, oldMode) => {
    if (newMode === "tree" && oldMode !== "tree" && entityMeta.value?.is_tree) {
      await loadTreeData();
    }
  },
);

definePageMeta({
  middleware: "auth" as any,
});
</script>

<template>
  <div class="h-full min-h-0 flex flex-col gap-6 px-3 py-3">
    <!-- Header -->
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-2">
        <h1 class="text-3xl font-bold">
          {{ entityMeta?.label || entityName }}
        </h1>
        <UBadge variant="subtle">
          {{ pagination.total || 0 }}
        </UBadge>
      </div>

      <div class="flex items-center gap-2">
        <UDropdownMenu
          v-if="
            (canUseTreeView || canUseDiagramView) && !metaLoading && entityMeta
          "
          :items="viewModeItems"
          :content="{ align: 'end', side: 'bottom', sideOffset: 8 }"
        >
          <UButton
            :icon="
              viewMode === 'list'
                ? 'i-lucide-list'
                : viewMode === 'tree'
                  ? 'i-lucide-list-tree'
                  : 'i-lucide-git-branch'
            "
            :label="
              viewMode === 'list'
                ? 'List View'
                : viewMode === 'tree'
                  ? 'Tree View'
                  : 'Diagram View'
            "
            variant="outline"
          />
        </UDropdownMenu>
        <div class="flex justify-end">
          <USkeleton v-if="permissionsLoading" class="h-9 w-28" />
          <template v-else>
            <UDropdownMenu
              v-if="selectedCount"
              :items="bulkMenuItems"
              :content="{ align: 'end', side: 'bottom', sideOffset: 8 }"
            >
              <UButton
                icon="i-lucide-chevron-down"
                label="Actions"
                variant="solid"
              />
            </UDropdownMenu>
            <UButton
              v-else
              icon="i-lucide-plus"
              :disabled="!canCreate"
              @click="handleCreate"
            >
              Add New
            </UButton>
          </template>
        </div>
      </div>
    </div>

    <div class="flex-1 min-h-0 flex flex-col">
      <!-- Table Toolbar (only for list view) -->
      <div
        v-if="viewMode === 'list'"
        class="flex flex-wrap items-center gap-3 px-4 py-3.5 border border-muted rounded-t-lg"
      >
        <USelect
          v-model="filterField"
          :items="filterFieldOptions"
          class="w-48"
          placeholder="Filter field"
        />
        <UInput
          v-model="searchInput"
          placeholder="Search..."
          icon="i-lucide-search"
          class="flex-1 min-w-[150px] max-w-[300px]"
        />
        <UButton
          variant="outline"
          icon="i-lucide-refresh-cw"
          :loading="loading"
          @click="loadData"
        />
        <UDropdownMenu
          :items="columnVisibilityItems"
          :content="{ align: 'end' }"
        >
          <UButton
            label="Columns"
            color="neutral"
            variant="outline"
            trailing-icon="i-lucide-chevron-down"
            class="ml-auto"
            aria-label="Columns select dropdown"
          />
        </UDropdownMenu>
      </div>

      <!-- Tree View -->
      <TreeView
        v-if="viewMode === 'tree' && canUseTreeView"
        :data="treeData"
        :entity-meta="entityMeta"
        :loading="treeLoading"
        @view="handleView"
        @edit="handleEdit"
        @delete="handleDeleteClick"
      />

      <!-- Diagram View -->
      <DiagramView
        v-if="viewMode === 'diagram' && canUseDiagramView"
        :entity-name="entityName"
        :entity-meta="entityMeta"
        :loading="loading"
        @view="handleView"
      />

      <!-- Data Table -->
      <div
        v-if="viewMode === 'list' && !error && (!metaLoading || loading)"
        class="flex-1 min-h-0 flex flex-col border-l border-r border-b border-muted rounded-b-lg"
      >
        <UTable
          ref="table"
          v-model:row-selection="rowSelection"
          v-model:sorting="sorting"
          v-model:column-visibility="columnVisibility"
          :data="data"
          :columns="metaLoading ? [] : tableColumns"
          :loading="loading"
          manual-sorting
          sticky
          class="flex-1 min-h-0 max-h-full"
          @select="handleRowSelect"
        >
          <template
            v-for="col in visibleFields"
            :key="col.id"
            #[`${col.id}-cell`]="{ row }"
          >
            <div class="max-w-[320px] truncate">
              <UBadge
                v-if="col.id === 'workflow_state'"
                size="md"
                variant="subtle"
                class="max-w-[320px] truncate"
                :color="
                  normalizeBadgeColor(
                    getWorkflowStateByValue(
                      String(getCellValue(row.original, col.fieldName)),
                    )?.color,
                  )
                "
              >
                {{
                  getWorkflowStateByValue(
                    String(getCellValue(row.original, col.fieldName)),
                  )?.label || getCellValue(row.original, col.fieldName)
                }}
              </UBadge>
              <UBadge
                v-else-if="col.id === 'status'"
                size="sm"
                variant="subtle"
                color="neutral"
                class="max-w-[320px] truncate"
              >
                {{ getCellValue(row.original, col.fieldName) }}
              </UBadge>
              <template v-else>
                {{ getCellValue(row.original, col.fieldName) }}
              </template>
            </div>
          </template>
          <template #loading>
            <div class="flex items-center justify-center py-12">
              <UIcon
                name="i-lucide-loader-2"
                class="h-6 w-6 animate-spin text-primary"
              />
            </div>
          </template>
          <template #empty>
            <div class="text-center py-12">
              <UIcon
                name="i-lucide-inbox"
                class="h-12 w-12 mx-auto text-muted-foreground mb-4"
              />
              <h3 class="text-lg font-medium mb-2">No records found</h3>
              <p class="text-muted-foreground mb-4">
                Get started by creating a new
                {{ entityMeta?.label || "record" }}.
              </p>
              <UButton
                v-if="!permissionsLoading"
                icon="i-lucide-plus"
                :disabled="!canCreate"
                @click="handleCreate"
              >
                Create New
              </UButton>
            </div>
          </template>
        </UTable>

        <!-- Pagination -->
        <div
          class="flex justify-between items-center gap-3 border-t border-default py-3.5 px-4"
        >
          <div class="text-sm text-muted space-y-1">
            <div>{{ selectedCount }} row(s) selected.</div>
            <div>
              Showing {{ pageStart }}-{{ pageEnd }} of {{ pagination.total }}.
            </div>
          </div>
          <div class="flex items-center gap-3">
            <USelect
              :model-value="pagination.pageSize"
              :items="pageSizeOptions"
              value-key="value"
              class="w-28"
              @update:model-value="handlePageSizeChange"
            />
            <UPagination
              :page="currentPage"
              :items-per-page="pagination.pageSize"
              :total="pagination.total"
              @update:page="
                (p) => {
                  pagination.pageIndex = p - 1;
                }
              "
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Error State -->
    <UAlert v-if="error" color="error" icon="i-lucide-alert-circle">
      <template #title>Error loading data</template>
      <template #description>{{ error }}</template>
    </UAlert>
  </div>
</template>
