<script setup lang="ts">
import { h, resolveComponent } from "vue";
import type {
  EntityMeta,
  FieldMeta,
  WorkflowAction,
  DocumentAction,
  AttachmentItem,
} from "~/composables/useApiTypes";
import { useCacheStore } from "~/stores/cache";
import { useFormState } from "~/composables/useFormState";
import { resolveCellValue } from "~/utils/cellFormat";
import { LazyBlockingLoadingOverlay, USeparator } from "#components";
import { updateLinkedTitlesCache } from "~/composables/useEntityApi";

const route = useRoute();
const router = useRouter();
const {
  getEntityMeta,
  getEntityDetail,
  postEntityAction,
  postDocumentAction,
  postWorkflowAction,
  getEntityOptions,
  getEntityList,
  getEntityListView,
  getAttachments,
  uploadAttachment,
  getAttachmentDownloadUrl,
  deleteAttachment,
  exportEntity,
  getWorkflowTransitions,
  getChildRecords,
  bulkSaveChildren,
  getEntityPrefill,
} = useApi();
const toast = useToast();
const confirmDialog = useConfirmDialog();
const deleteDialog = useDeleteDialog();
const overlay = useOverlay();

const entityName = computed(() => route.params.entity as string);
const recordId = computed(() => route.params.id as string);
const isNew = computed(() => recordId.value === "new");
const isEditMode = ref(false);
const activeTab = computed({
  get() {
    const tab = route.query.tab;
    return typeof tab === "string" && tab.length ? tab : "details";
  },
  set(tab) {
    const nextTab = typeof tab === "string" && tab.length ? tab : "details";
    const nextQuery = { ...route.query };
    if (nextTab === "details") {
      delete nextQuery.tab;
    } else {
      nextQuery.tab = nextTab;
    }

    router.replace({
      path: route.path,
      query: nextQuery,
      hash: route.hash,
    });
  },
});

const entityMeta = ref<EntityMeta | null>(null);
const formData = ref<Record<string, any>>({});
const originalData = ref<Record<string, any>>({});
const workflowActions = ref<WorkflowAction[]>([]);
const linkedCounts = ref<Record<string, number>>({});
const relatedMeta = ref<Record<string, EntityMeta>>({});

// Related data grid refs (for NuGrid-based related entity tabs)
const relatedGridRefs = ref<Record<string, any>>({});

// Child data grid refs (for NuGrid-based editable child tables)
const childGridRefs = ref<Record<string, any>>({});
const childGridDirty = ref<Record<string, boolean>>({});
const childGridLoading = ref<Record<string, boolean>>({});
const childEntityMeta = ref<Record<string, EntityMeta>>({});
const dataLoading = ref(true);
const workflowLoading = ref(false);
const metaLoading = ref(true);
const permissionsLoading = ref(true);
const permissions = ref<Record<string, boolean> | null>(null);
// Page-level loading should not wait for child grid lines.
const loading = computed(() => dataLoading.value);
function setChildGridLoading(entity: string, isLoading: boolean) {
  childGridLoading.value[entity] = isLoading;
}
function handleChildGridLoading(isLoading: boolean, entity: string) {
  setChildGridLoading(entity, isLoading);
}
const saving = ref(false);
const error = ref("");
const savingOverlay = overlay.create(LazyBlockingLoadingOverlay, {
  destroyOnClose: false,
  props: {
    title: "Executing...",
  },
});

// Print preview composable
const {
  previewHtml: printPreviewHtml,
  showPreview: showPrintPreview,
  loading: printLoading,
  openPreview: openPrintPreview,
  printDirect,
  downloadPdf,
  printFromPreview,
} = usePrintPreview();
const previewIframe = ref<HTMLIFrameElement | null>(null);

function resizeIframe() {
  const iframe = previewIframe.value;
  if (!iframe) return;
  try {
    const doc = iframe.contentDocument || iframe.contentWindow?.document;
    if (doc?.body) {
      const contentHeight =
        doc.documentElement.scrollHeight || doc.body.scrollHeight;
      if (contentHeight > 0) {
        const wrapper = iframe.parentElement;
        if (wrapper) {
          wrapper.style.paddingTop = "0";
          wrapper.style.height = `${contentHeight}px`;
        }
        iframe.style.height = `${contentHeight}px`;
      }
    }
  } catch (_error) {
    // Keep aspect-ratio wrapper fallback
  }
}

// Attachment state
const attachments = ref<AttachmentItem[]>([]);
const attachmentsLoading = ref(false);
const attachmentUploading = ref(false);
const attachmentFileInput = ref<HTMLInputElement | null>(null);

// Serial number modal state (triggered by confirm_receipt on serialized items)
const serialModalOpen = ref(false);
const serialModalInventoryIds = ref<string[]>([]);
const serialModalReceiptId = ref("");

const allowAttachments = computed(() => {
  const config = entityMeta.value?.attachment_config;
  return config?.allow_attachments === true;
});

const attachmentCount = computed(() => attachments.value.length);

const loadAttachments = async () => {
  if (isNew.value || !allowAttachments.value) return;
  attachmentsLoading.value = true;
  try {
    const res = await getAttachments(entityName.value, recordId.value);
    if (res.status === "success") {
      attachments.value = res.data || [];
    }
  } catch (err) {
    console.error("Failed to load attachments", err);
  } finally {
    attachmentsLoading.value = false;
  }
};

const handleAttachmentUpload = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const files = input.files;
  if (!files || files.length === 0) return;

  attachmentUploading.value = true;
  try {
    for (const file of Array.from(files)) {
      const res = await uploadAttachment(
        entityName.value,
        recordId.value,
        file,
      );
      if (res.status === "success") {
        if (res.message) {
          toast.add({
            title: res.message,
            color: "success",
            type: "foreground",
          });
        }
      } else {
        toast.add({
          title: res.message || `Upload failed: ${file.name}`,
          color: "error",
          type: "foreground",
        });
      }
    }
    await loadAttachments();
  } catch (err: any) {
    if (err?.message) {
      toast.add({ title: err.message, color: "error", type: "foreground" });
    }
  } finally {
    attachmentUploading.value = false;
    // Reset file input
    if (input) input.value = "";
  }
};

const handleDeleteAttachment = (attachment: AttachmentItem) => {
  (async () => {
    const confirmed = await deleteDialog({
      entityName: "Attachment",
      itemName: attachment.file_name,
    });
    if (!confirmed) return;

    try {
      const res = await deleteAttachment(
        entityName.value,
        recordId.value,
        attachment.id,
      );
      if (res.status === "success") {
        if (res.message) {
          toast.add({
            title: res.message,
            color: "success",
            type: "foreground",
          });
        }
        await loadAttachments();
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
  })();
};

const handleDownloadAttachment = (attachment: AttachmentItem) => {
  const url = getAttachmentDownloadUrl(
    entityName.value,
    recordId.value,
    attachment.id,
  );
  // Add auth token to download URL
  const token = localStorage.getItem("auth_token");
  const link = document.createElement("a");
  link.href = url + (token ? `?token=${token}` : "");
  link.download = attachment.file_name;
  link.target = "_blank";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
};

const linkOptions = ref<Record<string, { value: string; label: string }[]>>({});
const linkTitles = ref<Record<string, string>>({});
const loadedLinkFields = ref<Set<string>>(new Set());

const fetchFromLoading = ref<Record<string, boolean>>({});
const setFetchFromLoading = (fieldName: string, isLoading: boolean) => {
  fetchFromLoading.value[fieldName] = isLoading;
};
const setFetchFromLinkTitle = (
  linkEntity: string,
  id: string,
  title: string,
) => {
  const key = `${linkEntity}::${id}`;
  linkTitles.value[key] = title;
  updateLinkedTitlesCache({ [key]: title });
};

// Form state management
import { matchesCondition } from "~/composables/useFormState";
const {
  isFormEditable,
  canAddChildren,
  resolveFieldState,
  resolveTabState,
  fieldStates,
  visibleFields: formStateVisibleFields,
} = useFormState(entityMeta, formData, linkedCounts, isNew);

// Declarative fetch_from: auto-fills fields when a linked field changes
import { useFetchFrom } from "~/composables/useFetchFrom";
useFetchFrom(entityMeta, formData, {
  setLoading: setFetchFromLoading,
  setLinkTitle: setFetchFromLinkTitle,
});

const editableFields = computed(() => {
  const fields = formStateVisibleFields.value.filter((f: FieldMeta) => {
    if (isNew.value) return !f.readonly;
    return isEditMode.value ? !f.readonly : true;
  });

  return fields;
});

const canEdit = computed(() => {
  if (permissionsLoading.value) return false;
  const perms = permissions.value;
  if (!perms) return false;
  if (isNew.value) return perms.can_create === true;
  // Check both permission and form state editability
  return perms.can_update === true && isFormEditable.value;
});

const canDelete = computed(() => {
  if (permissionsLoading.value) return false;
  const perms = permissions.value;
  if (!perms) return false;
  return !isNew.value && perms.can_delete === true;
});

// Lazy-load link options when a select field is opened
const loadLinkOptionsForField = async (
  fieldName: string,
  linkEntity: string,
) => {
  // Cache by linkEntity (not fieldName) so multiple fields pointing to the same
  // entity share the same options list.
  if (loadedLinkFields.value.has(linkEntity)) return;

  loadedLinkFields.value.add(linkEntity);

  try {
    const response = await getEntityOptions(linkEntity);
    if (response.status === "success") {
      linkOptions.value[linkEntity] = response.options;
    }
  } catch (err) {
    console.error(`Failed to load options for ${fieldName}:`, err);
    // Remove from loaded set so it can be retried
    loadedLinkFields.value.delete(linkEntity);
  }
};

// Get display label for a link field value using _link_titles
const getLinkDisplayLabel = (
  fieldName: string,
  linkEntity: string,
  value: any,
): string => {
  if (!value) return "";
  const key = `${linkEntity}::${value}`;
  return linkTitles.value[key] || String(value);
};

const workflowMeta = computed(() => (entityMeta.value as any)?.workflow);
const normalizeWorkflowState = (state: string | null | undefined) => {
  if (!state) return null;
  const wf = workflowMeta.value;
  const states = Array.isArray(wf?.states) ? wf.states : [];
  const s = String(state);
  const direct = states.find((x: any) => x?.slug === s);
  if (direct?.slug) return String(direct.slug);
  const lower = s.toLowerCase();
  const bySlugLower = states.find(
    (x: any) => String(x?.slug || "").toLowerCase() === lower,
  );
  if (bySlugLower?.slug) return String(bySlugLower.slug);
  const byLabelLower = states.find(
    (x: any) => String(x?.label || "").toLowerCase() === lower,
  );
  if (byLabelLower?.slug) return String(byLabelLower.slug);
  return s;
};
const currentWorkflowState = computed(() => {
  const v = formData.value?.workflow_state;
  if (v) return normalizeWorkflowState(String(v));
  return normalizeWorkflowState(
    workflowMeta.value?.initial_state ||
      workflowMeta.value?.default_state ||
      null,
  );
});

const handleWorkflowTransition = async (
  actionSlug: string,
  actionLabel?: string,
) => {
  if (saving.value) return;
  try {
    saving.value = true;
    const response = await postWorkflowAction(
      entityName.value,
      recordId.value,
      actionSlug,
    );

    if (response.status === "success") {
      if (response.message) {
        toast.add({
          title: response.message,
          color: "success",
          type: "foreground",
        });
      }
      await loadData();
      await loadRelated();
    } else {
      if (response.message) {
        toast.add({
          title: response.message,
          color: "error",
          type: "foreground",
        });
      }
    }
  } catch (err: any) {
    if (err?.message) {
      toast.add({ title: err.message, color: "error", type: "foreground" });
    }
  } finally {
    saving.value = false;
  }
};

const workflowMenuItems = computed(() => {
  if (isNew.value) return [];
  const wf = workflowMeta.value;
  if (!wf?.enabled) return [];

  // Use workflow_actions from API response (already filtered by current state)
  const actions = workflowActions.value || [];
  if (!actions.length) return [];

  const items = actions.map((action: any) => ({
    label: action.action_label || action.action_slug,
    onSelect: () =>
      handleWorkflowTransition(action.action_slug, action.action_label),
  }));

  return items.length ? [items] : [];
});

const currentWorkflowStateLabel = computed(() => {
  const wf = workflowMeta.value;
  const slug = currentWorkflowState.value;
  if (!wf?.enabled || !slug) return "";
  const states = Array.isArray(wf.states) ? wf.states : [];
  const match = states.find((s: any) => s?.slug === slug);
  return match?.label ? String(match.label) : String(slug);
});

const showWorkflowButton = computed(() => {
  if (permissionsLoading.value) return false;
  const perms = permissions.value;
  const wf = workflowMeta.value;
  return (
    !isNew.value &&
    !!wf?.enabled &&
    wf?.show_actions !== false &&
    perms?.can_update !== false
  );
});

const showWorkflowButtonSkeleton = computed(() => {
  const wf = workflowMeta.value;
  return (
    !isNew.value &&
    !!wf?.enabled &&
    wf?.show_actions !== false &&
    (dataLoading.value || permissionsLoading.value)
  );
});

const showWorkflowBadge = computed(() => {
  const wf = workflowMeta.value;
  return (
    !isNew.value &&
    !!wf?.enabled &&
    wf?.show_actions === false &&
    !!formData.value?.workflow_state
  );
});

const isWorkflowDisabled = computed(() => {
  return workflowLoading.value || workflowActions.value.length === 0;
});

// Document Actions
const visibleDocumentActions = computed(() => {
  if (isNew.value || !entityMeta.value?.actions) return [];
  if (permissionsLoading.value) return [];
  const perms = permissions.value;
  if (!perms) return [];
  if (perms?.can_update === false) return [];

  return entityMeta.value.actions.filter((action: DocumentAction) => {
    if (!action.show_when) return true;

    return matchesCondition(action.show_when, formData.value, entityMeta.value);
  });
});

const handleDocumentAction = async (action: DocumentAction) => {
  if (saving.value) return;
  // Show confirmation if required
  if (action.confirm) {
    const confirmed = await confirmDialog({
      title: "Confirm Action",
      description: action.confirm,
      confirmLabel: "Proceed",
    });
    if (!confirmed) return;
  }
  await executeDocumentAction(action);
};

const executeDocumentAction = async (action: DocumentAction) => {
  if (saving.value) return;
  try {
    saving.value = true;
    const response = await postDocumentAction(
      entityName.value,
      recordId.value,
      action.action,
    );

    if (response.status === "success") {
      // Check for nested data error (e.g., generate_rfq failed inside)
      const nested = (response as any).data;
      if (nested?.status === "error") {
        const msg = nested.message || response.message;
        if (msg) {
          toast.add({
            title: msg,
            color: "error",
            type: "foreground",
          });
        }
      } else {
        // Handle serialized items: open serial number modal instead of redirecting
        if (
          nested?.action === "need_update_serial_num" &&
          nested?.inventory_ids?.length
        ) {
          if (response.message) {
            toast.add({
              title: response.message,
              color: "success",
              type: "foreground",
            });
          }
          await loadData();
          await loadRelated();
          // Open serial number modal
          serialModalInventoryIds.value = nested.inventory_ids;
          serialModalReceiptId.value = recordId.value;
          serialModalOpen.value = true;
          return;
        }

        if (response.message) {
          toast.add({
            title: response.message,
            color: "success",
            type: "foreground",
          });
        }

        // Reload data to reflect any changes
        await loadData();
        await loadRelated();

        // Handle redirect if response includes a path (e.g., generate_id)
        if (nested?.path) {
          router.push(nested.path);
        }
      }
    } else {
      if (response.message) {
        toast.add({
          title: response.message,
          color: "error",
          type: "foreground",
        });
      }
    }
  } catch (err: any) {
    if (err?.message) {
      toast.add({ title: err.message, color: "error", type: "foreground" });
    }
  } finally {
    saving.value = false;
  }
};

const onSerialNumbersSubmitted = async (message: string) => {
  serialModalOpen.value = false;
  toast.add({ title: message, color: "success", type: "foreground" });
  await loadData();
  await loadRelated();
};

// Helper to get permissions for a linked entity from metadata
const getLinkPermissions = (linkEntity: string) => {
  const links = entityMeta.value?.links || [];
  const link = links.find((l: any) => l?.entity === linkEntity);
  return (
    link?.permissions || {
      can_read: true,
      can_create: true,
      can_update: true,
      can_delete: true,
    }
  );
};

const relatedTabs = computed(() => {
  const links = entityMeta.value?.links || [];
  return links
    .filter((link) => link?.entity && link?.fk_field)
    .filter((link) => {
      // Apply tab visibility rules from form_state
      const tabState = resolveTabState(link.entity);
      return tabState.visible;
    })
    .map((link) => {
      return {
        label: link.label || link.entity,
        icon: "i-lucide-link",
        slot: link.entity,
        value: link.entity,
        linkEntity: link.entity,
        fkField: link.fk_field,
        count: linkedCounts.value[link.entity] || 0,
        permissions: link.permissions || {
          can_read: true,
          can_create: true,
          can_update: true,
          can_delete: true,
        },
      };
    });
});

const tabs = computed(() => {
  const items: any[] = [
    {
      label: "Details",
      value: "details",
    },
  ];

  // For new records, only show Details tab
  if (isNew.value) {
    return items;
  }

  // Add related entity tabs
  items.push(
    ...relatedTabs.value.map((tab) => ({
      label: tab.label,
      value: tab.value,
      linkEntity: tab.linkEntity,
      fkField: tab.fkField,
      count: tab.count,
    })),
  );

  // Add Attachments tab LAST if enabled
  if (allowAttachments.value && !isNew.value) {
    items.push({
      label: "Attachments",
      value: "attachments",
      count: attachmentCount.value || 0,
    });
  }

  return items;
});

const availableTabValues = computed(() => {
  return new Set((tabs.value || []).map((t: any) => String(t.value)));
});

watch(
  () => route.query.tab,
  (tab) => {
    if (
      typeof tab === "string" &&
      tab.length &&
      !availableTabValues.value.has(tab)
    ) {
      const nextQuery = { ...route.query };
      delete nextQuery.tab;
      router.replace({ path: route.path, query: nextQuery, hash: route.hash });
    }
  },
  { immediate: true },
);

// Watch for tab changes to lazy-load related tab data
watch(
  activeTab,
  async (newTab) => {
    if (newTab === "details" || isNew.value) return;

    // Lazy-load attachments when tab is first activated
    if (newTab === "attachments") {
      if (attachments.value.length === 0 && !attachmentsLoading.value) {
        await loadAttachments();
      }
      return;
    }

    // Find the related tab that matches and ensure metadata is loaded
    const relatedTab = relatedTabs.value.find((t) => t.value === newTab);
    if (relatedTab && !relatedMeta.value[relatedTab.linkEntity]) {
      try {
        const metaRes = await getEntityMeta(relatedTab.linkEntity);
        relatedMeta.value[relatedTab.linkEntity] = metaRes.data;
      } catch (err) {
        console.error(
          `Failed to load metadata for ${relatedTab.linkEntity}`,
          err,
        );
      }
    }
  },
  { immediate: true },
);

const headerMenuItems = computed(() => {
  if (isNew.value) return [];
  const items: any[] = [
    {
      label: "Print",
      icon: "i-lucide-printer",
      onSelect: () => openPrintPreview(entityName.value, recordId.value),
    },
    {
      label: "Export",
      icon: "i-lucide-download",
      onSelect: async () => {
        try {
          const blob = await exportEntity(entityName.value);
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement("a");
          link.href = url;
          link.download = `${entityName.value}_${recordId.value}_${new Date().toISOString().split("T")[0]}.xlsx`;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          window.URL.revokeObjectURL(url);
        } catch (error: any) {
          toast.add({
            title: error.message,
            color: "error",
            type: "foreground",
          });
        }
      },
    },
  ];

  if (canEdit.value) {
    items.push({
      label: "Duplicate",
      icon: "i-lucide-copy",
      onSelect: async () => {
        // Copy all fields except system fields and unique fields
        const duplicateData = { ...formData.value };
        delete duplicateData.id;
        delete duplicateData.created_at;
        delete duplicateData.updated_at;

        // Clear unique fields that would cause constraint violations
        const uniqueFields =
          entityMeta.value?.fields?.filter((f: FieldMeta) => f.unique) || [];
        for (const field of uniqueFields) {
          delete duplicateData[field.name];
        }

        // Reset workflow state to initial
        if (workflowMeta.value?.enabled && workflowMeta.value?.initial_state) {
          duplicateData.workflow_state = workflowMeta.value.initial_state;
        }

        // Store duplicate data and navigate to /new form
        sessionStorage.setItem(
          `duplicate_${entityName.value}`,
          JSON.stringify(duplicateData),
        );
        router.push(`/${entityName.value}/new?duplicate=true`);
      },
    });
  }

  if (canDelete.value) {
    items.push({
      label: "Delete",
      icon: "i-lucide-trash-2",
      onSelect: async () => {
        handleDelete();
      },
    });
  }

  return [items];
});

// Load related entity metadata
const loadRelated = async () => {
  if (!entityMeta.value?.links || isNew.value) return;

  // Load metadata for each related entity
  for (const link of entityMeta.value.links) {
    if (link?.entity && !relatedMeta.value[link.entity]) {
      try {
        const metaRes = await getEntityMeta(link.entity);
        relatedMeta.value[link.entity] = metaRes.data;
      } catch (err) {
        console.error(`Failed to load metadata for ${link.entity}`, err);
      }
    }
  }
};

const getFkFieldForRelatedEntity = (linkEntity: string): string | null => {
  const links = entityMeta.value?.links || [];
  const link = links.find((l: any) => l?.entity === linkEntity);
  return link?.fk_field || null;
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

    // Load metadata for inline child entities (in parallel)
    const children = metaRes.data?.children || [];
    if (children.length) {
      await Promise.all(
        children.map(async (child: any) => {
          if (childEntityMeta.value[child.entity]) return;
          try {
            const childMetaRes = await getEntityMeta(child.entity);
            childEntityMeta.value[child.entity] = childMetaRes.data;
          } catch (err) {
            console.error(`Failed to load child meta for ${child.entity}`, err);
          }
        }),
      );
    }
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
    dataLoading.value = true;
    error.value = "";

    if (isNew.value) {
      if (!entityMeta.value) return;
      const defaults: Record<string, any> = {};
      entityMeta.value?.fields?.forEach((field: FieldMeta) => {
        if (field.default !== undefined && field.default !== null) {
          defaults[field.name] = field.default;
        }
      });

      // Set initial workflow state for new records
      if (workflowMeta.value?.enabled && workflowMeta.value?.initial_state) {
        defaults.workflow_state = workflowMeta.value.initial_state;
      }

      // Fetch server-side prefill values (e.g. date_requested = today)
      try {
        const prefillRes = await getEntityPrefill(entityName.value);
        if (prefillRes?.status === "success" && prefillRes.data) {
          Object.assign(defaults, prefillRes.data);
        }
      } catch {
        // Prefill is best-effort; ignore errors
      }

      // Check for duplicate data in sessionStorage
      if (route.query.duplicate === "true") {
        const duplicateKey = `duplicate_${entityName.value}`;
        const duplicateDataStr = sessionStorage.getItem(duplicateKey);
        if (duplicateDataStr) {
          try {
            const duplicateData = JSON.parse(duplicateDataStr);
            formData.value = { ...defaults, ...duplicateData };
            sessionStorage.removeItem(duplicateKey);
          } catch {
            formData.value = defaults;
          }
        } else {
          formData.value = defaults;
        }
      } else {
        formData.value = defaults;
      }
      isEditMode.value = true;
    } else {
      // Fire detail + attachments in parallel
      const detailPromise = getEntityDetail(entityName.value, recordId.value);
      const attachPromise = allowAttachments.value
        ? loadAttachments()
        : Promise.resolve();

      const detailRes = await detailPromise;
      formData.value = { ...detailRes.data };
      originalData.value = { ...detailRes.data };
      linkedCounts.value = (detailRes as any).linked_counts || {};
      linkTitles.value = (detailRes as any)._link_titles || {};

      // Load workflow transitions separately so the form can render immediately
      workflowActions.value = [];
      if (workflowMeta.value?.enabled) {
        workflowLoading.value = true;
        const currentState = formData.value?.workflow_state
          ? String(formData.value.workflow_state)
          : null;
        getWorkflowTransitions(entityName.value, currentState)
          .then((wfRes) => {
            if (wfRes.status === "success") {
              workflowActions.value = (wfRes.data || []) as any;
            }
          })
          .catch(() => {
            workflowActions.value = [];
          })
          .finally(() => {
            workflowLoading.value = false;
          });
      } else {
        workflowLoading.value = false;
      }

      isEditMode.value = route.query.edit === "true";

      // Ensure attachment load is complete
      await attachPromise;
    }
  } catch (err: any) {
    error.value = err.message || "Failed to load data";
    console.error(err);
  } finally {
    dataLoading.value = false;
  }
};

const handleSave = async () => {
  if (saving.value) return;
  try {
    saving.value = true;
    error.value = "";
    fieldErrors.value = {};

    // Collect child data from all grids
    const children: Record<string, { rows: any[]; deleted_ids: string[] }> = {};
    const dirtyGrids = Object.entries(childGridRefs.value).filter(
      ([entity]) => childGridDirty.value[entity],
    );
    for (const [childEntity, gridRef] of dirtyGrids) {
      if (gridRef?.getChildData && gridRef?.getDeletedIds) {
        children[childEntity] = {
          rows: gridRef.getChildData(),
          deleted_ids: gridRef.getDeletedIds(),
        };
      }
    }

    const action = isNew.value ? "create" : "update";
    const response = await postEntityAction(entityName.value, {
      action,
      id: isNew.value ? undefined : recordId.value,
      data: formData.value,
      children: Object.keys(children).length > 0 ? children : undefined,
    });

    if (response.status === "success") {
      // Mark child grids as saved
      for (const [childEntity, gridRef] of dirtyGrids) {
        if (gridRef?.markAsSaved) {
          gridRef.markAsSaved();
        }
      }

      const backendMessage =
        response.message || `${entityName.value} ${action}d`;
      toast.add({
        title: backendMessage,
        color: "success",
        type: "foreground",
      });

      // Invalidate caches for this entity so lists refresh
      const cache = useCacheStore();
      cache.invalidatePrefix(`entity:options:${entityName.value}`);
      cache.invalidatePrefix(`meta:entity:v2:${entityName.value}`);

      if (isNew.value && response.data?.id) {
        router.replace(`/${entityName.value}/${response.data.id}`);
      } else {
        isEditMode.value = false;
        originalData.value = { ...formData.value };
      }
    } else {
      error.value = response.message || "Save failed";
      if (response.errors) {
        fieldErrors.value = response.errors as Record<string, string>;
        const errorMessages = Object.entries(response.errors)
          .map(([field, msg]) => `${field}: ${msg}`)
          .join(", ");
        error.value += `: ${errorMessages}`;
      }
    }
  } catch (err: any) {
    error.value = err.message || "Save failed";
  } finally {
    saving.value = false;
  }
};

const handleCancel = () => {
  if (isNew.value) {
    router.push(`/${entityName.value}`);
  } else {
    formData.value = { ...originalData.value };
    isEditMode.value = false;
  }
};

const handleDelete = () => {
  const itemName =
    formData.value?.[entityMeta.value?.title_field || "name"] ||
    `ID: ${recordId.value}`;

  (async () => {
    const confirmed = await deleteDialog({
      entityName: entityMeta.value?.label || "Record",
      itemName,
    });
    if (!confirmed) return;

    const response = await postEntityAction(entityName.value, {
      action: "delete",
      id: recordId.value,
    });

    if (response.status === "success") {
      const cache = useCacheStore();
      cache.invalidatePrefix(`entity:options:${entityName.value}`);
      if (response.message) {
        toast.add({
          title: response.message,
          color: "success",
          type: "foreground",
        });
      }
      router.push(`/${entityName.value}`);
    } else {
      throw new Error(response.message || "Delete failed");
    }
  })().catch((err: any) => {
    if (err?.message) {
      toast.add({
        title: err.message,
        color: "error",
        type: "foreground",
      });
    }
  });
};

const handleWorkflowAction = async (action: WorkflowAction) => {
  try {
    saving.value = true;
    const response = await postWorkflowAction(
      entityName.value,
      recordId.value,
      action.name,
    );

    if (response.status === "success") {
      if (response.message) {
        toast.add({
          title: response.message,
          color: "success",
          type: "foreground",
        });
      }
      await loadData();
    } else {
      if (response.message) {
        toast.add({
          title: response.message,
          color: "error",
          type: "foreground",
        });
      }
    }
  } catch (err: any) {
    if (err?.message) {
      toast.add({ title: err.message, color: "error", type: "foreground" });
    }
  } finally {
    saving.value = false;
  }
};

// Dirty-form detection (includes child grid changes)
const anyChildGridDirty = computed(() =>
  Object.values(childGridDirty.value).some(Boolean),
);

const isDirty = computed(() => {
  if (isNew.value) {
    return Object.values(formData.value).some(
      (v) => v !== null && v !== undefined && v !== "",
    );
  }
  const formDirty =
    JSON.stringify(formData.value) !== JSON.stringify(originalData.value);
  return formDirty || anyChildGridDirty.value;
});

// Navigation guard — warn before leaving with unsaved changes
onBeforeRouteLeave((_to, _from, next) => {
  if (isDirty.value && isEditMode.value && !saving.value) {
    confirmDialog({
      title: "Unsaved Changes",
      description: "You have unsaved changes. Are you sure you want to leave?",
      confirmLabel: "Leave",
      confirmColor: "error",
    }).then((confirmed) => next(confirmed));
  } else {
    next();
  }
});

watch(saving, (isSaving) => {
  if (isSaving) {
    savingOverlay.open();
  } else {
    savingOverlay.close();
  }
});

// Also guard browser close / refresh
if (import.meta.client) {
  const beforeUnload = (e: BeforeUnloadEvent) => {
    if (isDirty.value && isEditMode.value && !saving.value) {
      e.preventDefault();
      e.returnValue = "";
    }
  };
  onMounted(() => window.addEventListener("beforeunload", beforeUnload));
  onUnmounted(() => window.removeEventListener("beforeunload", beforeUnload));
}

// Field-level errors from backend
const fieldErrors = ref<Record<string, string>>({});

const clearFieldError = (fieldName: string) => {
  if (fieldErrors.value[fieldName]) {
    const { [fieldName]: _removed, ...rest } = fieldErrors.value;
    fieldErrors.value = rest;
  }
};

const validateForm = () => {
  const errors: { name: string; message: string }[] = [];

  for (const field of editableFields.value) {
    const isRequired =
      fieldStates.value[field.name]?.required ?? field.required;
    if (!isRequired) continue;

    const value = formData.value[field.name];
    const isEmptyString = typeof value === "string" && value.trim() === "";
    if (value === null || value === undefined || isEmptyString) {
      errors.push({
        name: field.name,
        message: `${field.label} is required`,
      });
    }
  }

  return errors;
};

// Keyboard shortcuts
const onKeydown = (e: KeyboardEvent) => {
  // Ctrl+S / Cmd+S — save
  if ((e.ctrlKey || e.metaKey) && e.key === "s") {
    e.preventDefault();
    if (isEditMode.value && !saving.value) handleSave();
  }
  // Escape — cancel edit
  if (e.key === "Escape" && isEditMode.value && !isNew.value) {
    handleCancel();
  }
};

if (import.meta.client) {
  onMounted(() => window.addEventListener("keydown", onKeydown));
  onUnmounted(() => {
    window.removeEventListener("keydown", onKeydown);
    savingOverlay.close();
  });
}

watch(
  [entityName, recordId],
  async () => {
    fieldErrors.value = {};
    entityMeta.value = null;
    permissions.value = null;
    metaLoading.value = true;
    permissionsLoading.value = true;
    error.value = "";
    // Load metadata first (loadData depends on entityMeta for new records)
    await loadMetadata();
    // Load data (related tab metadata is lazy-loaded when tab is clicked)
    await loadData();
  },
  { immediate: true },
);

definePageMeta({
  middleware: "auth" as any,
});
</script>

<template>
  <div class="h-full min-h-0 flex flex-col gap-6 px-3 py-3">
    <!-- Header -->
    <div class="flex items-center gap-2">
      <UButton
        variant="ghost"
        icon="i-lucide-arrow-left"
        @click="router.go(-1)"
      />
      <div class="flex-1 flex items-center gap-2">
        <h1 class="text-2xl font-bold mr-2">
          {{
            isNew
              ? "New"
              : formData[entityMeta?.title_field || "id"] ||
                recordId ||
                entityName
          }}
        </h1>

        <div>
          <USkeleton
            v-if="showWorkflowButtonSkeleton"
            class="h-8 w-28 rounded-md"
          />
          <UDropdownMenu
            v-else-if="showWorkflowButton && workflowMenuItems.length"
            :items="workflowMenuItems"
          >
            <UButton
              variant="outline"
              size="md"
              :disabled="saving"
              :loading="workflowLoading"
            >
              {{ currentWorkflowStateLabel || "Workflow" }}
            </UButton>
          </UDropdownMenu>
          <UButton
            v-else-if="showWorkflowButton"
            variant="outline"
            size="md"
            :disabled="saving"
            :loading="workflowLoading"
          >
            {{ currentWorkflowStateLabel || "Workflow" }}
          </UButton>
          <!-- Read-only state badge for entities where show_actions is false -->
          <UBadge v-else-if="showWorkflowBadge" variant="subtle" size="md">
            {{
              currentWorkflowStateLabel ||
              String(formData.workflow_state)
                .replace(/_/g, " ")
                .replace(/\b\w/g, (c) => c.toUpperCase())
            }}
          </UBadge>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex gap-2">
        <!-- Document Actions -->
        <UDropdownMenu
          v-if="!isEditMode && visibleDocumentActions.length > 0"
          :items="
            visibleDocumentActions.map((a) => ({
              label: a.label,
              onSelect: () => handleDocumentAction(a),
            }))
          "
        >
          <UButton
            trailing-icon="i-lucide-chevron-down"
            variant="outline"
            size="md"
            :disabled="saving || loading"
          >
            Actions
          </UButton>
        </UDropdownMenu>

        <template v-if="isEditMode">
          <UFieldGroup>
            <UButton :loading="saving" @click="handleSave">
              {{ isNew ? "Create" : "Save" }}
            </UButton>
            <UButton
              variant="outline"
              icon="i-lucide-x"
              :disabled="saving"
              @click="handleCancel"
            />
          </UFieldGroup>
        </template>
        <template v-else>
          <div class="flex gap-2">
            <div class="flex justify-end">
              <USkeleton v-if="permissionsLoading" class="h-9 w-28" />
              <UButton
                v-else
                icon="i-lucide-pencil"
                @click="isEditMode = true"
                size="md"
                :disabled="!canEdit"
              >
                Edit
              </UButton>
            </div>
            <UDropdownMenu
              v-if="headerMenuItems.length"
              :items="headerMenuItems"
            >
              <UButton
                icon="i-lucide-ellipsis-vertical"
                variant="outline"
                size="md"
                :disabled="saving || loading"
              />
            </UDropdownMenu>
          </div>
        </template>
      </div>
    </div>

    <!-- Error Alert -->
    <UAlert
      v-if="error"
      color="error"
      icon="i-lucide-alert-circle"
      :close-button="{ icon: 'i-lucide-x', onClick: () => (error = '') }"
    >
      <template #title>Error</template>
      <template #description>{{ error }}</template>
    </UAlert>

    <!-- Loading State - Skeleton -->
    <div v-if="loading" class="space-y-6">
      <!-- Tabs skeleton -->
      <div class="mt-3">
        <div class="flex gap-4 ml-4 mb-3">
          <USkeleton v-for="i in 4" :key="i" class="h-4 w-24" />
        </div>
        <USeparator />
      </div>

      <!-- Form skeleton -->
      <div class="space-y-6 mt-3">
        <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div v-for="i in 8" :key="i" class="space-y-2">
            <USkeleton class="h-4 w-24" />
            <USkeleton class="h-8 w-full" />
          </div>
        </div>
      </div>
    </div>

    <UTabs
      v-else-if="!metaLoading && entityMeta"
      v-model="activeTab"
      :items="tabs"
      :unmount-on-hide="true"
      class="w-full flex-1 min-h-0 flex flex-col"
      :ui="{
        root: 'flex flex-col min-h-0',
        list: 'shrink-0 overflow-x-auto',
        trigger: 'shrink-0 min-w-fit',
        label: 'whitespace-nowrap overflow-visible',
        content: 'flex-1 min-h-0 flex flex-col',
      }"
      size="md"
      variant="link"
    >
      <template #default="{ item }">
        <div class="flex items-center gap-2">
          <span>{{ item.label }}</span>
          <UBadge
            v-if="item.count && item.count > 0"
            size="sm"
            variant="solid"
            color="primary"
            class="rounded-full w-5 justify-center font-bold"
          >
            {{ item.count }}
          </UBadge>
        </div>
      </template>
      <template #content="{ item }">
        <!-- Details Tab -->
        <div
          v-if="item.value === 'details'"
          class="flex-1 min-h-0 flex flex-col overflow-hidden"
        >
          <div class="flex-1 min-h-0 overflow-y-auto pb-8 space-y-6">
            <UForm
              :state="formData"
              :validate="validateForm"
              class="space-y-6 mt-2"
              @submit.prevent="handleSave"
            >
              <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div
                  v-for="field in editableFields"
                  :key="field.name"
                  class="space-y-2"
                >
                  <UFormField
                    :label="field.label"
                    :required="
                      !!(fieldStates[field.name]?.required ?? field.required)
                    "
                    :name="field.name"
                    :error="fieldErrors[field.name]"
                  >
                    <EntityFieldRenderer
                      :field="field"
                      v-model="formData[field.name]"
                      :loading="fetchFromLoading[field.name] === true"
                      :record-id="isNew ? undefined : recordId"
                      :disabled="
                        !isEditMode ||
                        field.readonly ||
                        (!isFormEditable && !isNew) ||
                        fieldStates[field.name]?.editable === false
                      "
                      :link-options="linkOptions"
                      :link-titles="linkTitles"
                      :on-load-link-options="loadLinkOptionsForField"
                      :entity-name="entityName"
                      :form-state="formData"
                      :link-field-permissions="
                        entityMeta?.link_field_permissions || {}
                      "
                      @update:model-value="clearFieldError(field.name)"
                    />
                  </UFormField>
                </div>
              </div>
            </UForm>

            <!-- Inline Child Tables (rendered in the form, not as tabs) -->
            <div v-if="!isNew && entityMeta?.children?.length" class="mt-6">
              <USeparator label="Line Items" />
              <div v-for="child in entityMeta.children" :key="child.entity">
                <div class="min-h-0">
                  <EntityChildDataGrid
                    :ref="
                      (el: any) => {
                        if (el) childGridRefs[child.entity] = el;
                      }
                    "
                    :parent-entity="entityName"
                    :parent-id="recordId"
                    :child-entity="child.entity"
                    :fk-field="child.fk_field"
                    :child-meta="childEntityMeta[child.entity] || null"
                    :editable="isEditMode"
                    :can-add="isEditMode && canAddChildren"
                    :can-delete="isEditMode && canEdit"
                    @dirty-change="
                      (dirty: boolean) => {
                        childGridDirty[child.entity] = dirty;
                      }
                    "
                    @loading-change="
                      (isLoading: boolean) =>
                        handleChildGridLoading(isLoading, child.entity)
                    "
                    @save-complete="() => loadData()"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Attachments Tab -->
        <div
          v-else-if="item.value === 'attachments'"
          class="border rounded-lg border-accented mt-4 flex-1 min-h-0 flex flex-col overflow-hidden"
        >
          <!-- Toolbar -->
          <div
            class="flex items-center justify-between gap-2 p-4 border-b border-accented"
          >
            <div class="flex items-center gap-2">
              <UButton
                icon="i-lucide-upload"
                size="md"
                :loading="attachmentUploading"
                :disabled="attachmentUploading"
                @click="attachmentFileInput?.click()"
              >
                Upload File
              </UButton>
              <input
                ref="attachmentFileInput"
                type="file"
                multiple
                class="hidden"
                @change="handleAttachmentUpload"
              />
              <UButton
                icon="i-lucide-refresh-cw"
                variant="outline"
                size="md"
                :loading="attachmentsLoading"
                @click="loadAttachments"
              />
            </div>
            <span class="text-sm text-muted">
              {{ attachmentCount }}
              /
              {{ entityMeta?.attachment_config?.max_attachments || 10 }}
              files
            </span>
          </div>

          <!-- Attachment List -->
          <div
            v-if="attachmentsLoading"
            class="flex-1 min-h-0 flex justify-center py-8 overflow-y-auto pb-6"
          >
            <UIcon
              name="i-lucide-loader-2"
              class="animate-spin h-6 w-6 text-primary"
            />
          </div>

          <div
            v-else-if="attachments.length === 0"
            class="flex-1 min-h-0 text-center py-12 text-muted-foreground overflow-y-auto pb-6"
          >
            <UIcon name="i-lucide-paperclip" class="h-8 w-8 mx-auto mb-2" />
            <p class="text-sm">No attachments yet</p>
            <p class="text-xs mt-1">Click "Upload File" to add attachments</p>
          </div>

          <div
            v-else
            class="flex-1 min-h-0 divide-y divide-accented overflow-y-auto pb-6"
          >
            <div
              v-for="att in attachments"
              :key="att.id"
              class="flex items-center justify-between p-4 hover:bg-muted/50 transition-colors"
            >
              <div class="flex items-center gap-3 min-w-0 flex-1">
                <UIcon
                  :name="
                    att.mime_type?.startsWith('image/')
                      ? 'i-lucide-image'
                      : att.mime_type === 'application/pdf'
                        ? 'i-lucide-file-text'
                        : 'i-lucide-file'
                  "
                  class="h-5 w-5 text-muted-foreground shrink-0"
                />
                <div class="min-w-0">
                  <div class="font-medium text-sm truncate">
                    {{ att.file_name }}
                  </div>
                  <div class="text-xs text-muted-foreground">
                    {{ formatFileSize(att.file_size) }}
                    <span v-if="att.uploaded_by">
                      · by {{ att.uploaded_by }}
                    </span>
                    <span v-if="att.created_at">
                      ·
                      {{
                        new Date(att.created_at).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })
                      }}
                    </span>
                  </div>
                </div>
              </div>
              <div class="flex items-center gap-1 shrink-0">
                <UButton
                  icon="i-lucide-download"
                  variant="ghost"
                  size="xs"
                  @click="handleDownloadAttachment(att)"
                />
                <UButton
                  icon="i-lucide-trash-2"
                  variant="ghost"
                  size="xs"
                  color="error"
                  @click="handleDeleteAttachment(att)"
                />
              </div>
            </div>
          </div>
        </div>

        <!-- Related Tab Panel -->
        <div
          v-else
          class="mt-4 flex-1 min-h-0 flex flex-col overflow-y-auto px-1 pb-6"
        >
          <EntityRelatedDataGrid
            :ref="
              (el: any) => {
                if (el) relatedGridRefs[(item as any).linkEntity] = el;
              }
            "
            :parent-entity="entityName"
            :parent-id="recordId"
            :child-entity="(item as any).linkEntity"
            :fk-field="(item as any).fkField"
            :child-meta="relatedMeta[(item as any).linkEntity] || null"
            :editable="getLinkPermissions((item as any).linkEntity).can_update"
            :can-add="getLinkPermissions((item as any).linkEntity).can_create"
            :can-delete="
              getLinkPermissions((item as any).linkEntity).can_delete
            "
          />
        </div>
      </template>
    </UTabs>
  </div>

  <!-- Serial Number Modal: shown after confirm_receipt for serialized items -->
  <SerialNumberModal
    :open="serialModalOpen"
    :inventory-ids="serialModalInventoryIds"
    :receipt-id="serialModalReceiptId"
    :entity-name="entityName"
    @close="serialModalOpen = false"
    @submitted="onSerialNumbersSubmitted"
  />

  <!-- Print Preview Modal -->
  <UModal
    v-model:open="showPrintPreview"
    :title="`${entityMeta?.label || entityName} — Print Preview`"
    :ui="{
      content: 'max-w-4xl w-full max-h-screen flex flex-col',
      body: 'flex-1 min-h-0 overflow-hidden',
      footer: 'shrink-0',
    }"
    scrollable
  >
    <template #body>
      <div
        class="h-full max-h-[calc(100vh-12rem)] overflow-y-auto overflow-x-hidden bg-[#e5e7eb] p-4 rounded"
      >
        <div v-if="printPreviewHtml" class="flex justify-center min-w-0">
          <div class="w-full max-w-[816px] bg-white shadow-md">
            <div
              style="
                position: relative;
                width: 100%;
                padding-top: calc(11 / 8.5 * 100%);
              "
            >
              <iframe
                ref="previewIframe"
                :srcdoc="printPreviewHtml"
                sandbox="allow-scripts allow-same-origin"
                class="border-0 block"
                style="
                  position: absolute;
                  top: 0;
                  left: 0;
                  width: 100%;
                  height: 100%;
                "
                @load="resizeIframe"
              />
            </div>
          </div>
        </div>
        <div v-else class="flex items-center justify-center py-16">
          <UIcon
            name="i-lucide-loader-2"
            class="animate-spin text-2xl text-gray-400"
          />
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton variant="outline" @click="showPrintPreview = false">
          Close
        </UButton>
        <UButton
          icon="i-lucide-printer"
          variant="soft"
          @click="printFromPreview"
        >
          Print
        </UButton>
        <UButton
          icon="i-lucide-file-down"
          color="primary"
          :loading="printLoading"
          @click="downloadPdf(entityName, recordId)"
        >
          Download PDF
        </UButton>
      </div>
    </template>
  </UModal>
</template>
