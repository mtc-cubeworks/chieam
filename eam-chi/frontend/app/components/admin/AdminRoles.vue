<script setup lang="ts">
import { h, resolveComponent } from "vue";
import { getPaginationRowModel } from "@tanstack/vue-table";
import type { TableColumn } from "@nuxt/ui";
import { z } from "zod";
import type { FormError, FormSubmitEvent } from "@nuxt/ui";
import { useDeleteModalStore } from "~/stores/deleteModal";

const UButton = resolveComponent("UButton");
const UBadge = resolveComponent("UBadge");
const UIcon = resolveComponent("UIcon");
const USlideover = resolveComponent("USlideover");

const api = useApi();
const toast = useToast();

const deleteModalStore = useDeleteModalStore();

const table = useTemplateRef<{ tableApi?: any }>("table");

// Data
const roles = ref<any[]>([]);
const loading = ref(true);
const error = ref("");
const roleMetadata = ref<any>(null);

const pagination = ref({
  page: 1,
  pageSize: 10,
  total: 0,
});

const tablePagination = computed({
  get: () => ({
    pageIndex: Math.max(0, (pagination.value.page || 1) - 1),
    pageSize: pagination.value.pageSize,
  }),
  set: (v: { pageIndex: number; pageSize: number }) => {
    const nextPageSize = v.pageSize ?? pagination.value.pageSize;
    const nextPage = (v.pageIndex ?? 0) + 1;
    const pageSizeChanged = nextPageSize !== pagination.value.pageSize;

    pagination.value.pageSize = nextPageSize;
    pagination.value.page = pageSizeChanged ? 1 : nextPage;
  },
});

// Modal state
const showRoleModal = ref(false);
const editingRole = ref<any>(null);
const isModalLoading = ref(false);
const formRef = ref<any>(null);

// Zod schema for role validation
const roleSchema = computed(() => {
  if (editingRole.value) {
    // Update mode - all fields optional
    return z.object({
      name: z.string().min(1, "Role name is required").optional(),
      description: z.string().optional(),
      is_active: z.boolean().optional(),
    });
  } else {
    // Create mode - name is required
    return z.object({
      name: z.string().min(1, "Role name is required"),
      description: z.string().optional(),
      is_active: z.boolean().optional(),
    });
  }
});

type RoleSchema = z.output<typeof roleSchema.value>;

const state = reactive<Partial<RoleSchema>>({
  name: "",
  description: "",
  is_active: true,
});

// Columns definition
const roleColumns: TableColumn<any>[] = [
  {
    accessorKey: "name",
    header: "Name",
  },
  {
    accessorKey: "description",
    header: "Description",
  },
  {
    accessorKey: "is_active",
    header: "Status",
    cell: ({ row }) =>
      h(
        UBadge,
        {
          color: row.original.is_active ? "success" : "error",
          variant: "subtle",
          size: "md",
        },
        () => (row.original.is_active ? "Active" : "Inactive"),
      ),
  },
  {
    id: "actions",
    header: "",
    cell: ({ row }) =>
      h("div", { class: "flex items-center gap-2" }, [
        h(UButton, {
          variant: "ghost",
          size: "xs",
          icon: "i-lucide-edit",
          onClick: () => openEditModal(row.original),
          disabled: row.original.name === "SystemManager",
        }),
        h(UButton, {
          variant: "ghost",
          size: "xs",
          icon: "i-lucide-trash-2",
          color: "error",
          onClick: () => openDeleteModal(row.original),
          disabled: row.original.name === "SystemManager",
        }),
      ]),
  },
];

// Methods
const loadRoles = async () => {
  try {
    loading.value = true;
    const [rolesRes, metaRes] = await Promise.all([
      api.getAdminRoles(),
      api.getAdminRoleMeta(),
    ]);
    roles.value = rolesRes.data || [];
    pagination.value.total = roles.value.length;
    roleMetadata.value = metaRes.data;
  } catch (err: any) {
    error.value = err.message || "Failed to load data";
    toast.add({ title: "Failed to load data", color: "error" });
  } finally {
    loading.value = false;
  }
};

watch([() => pagination.value.page, () => pagination.value.pageSize], () => {
  // Client-side pagination only (roles are fetched all at once)
});

const openCreateModal = () => {
  editingRole.value = null;
  state.name = "";
  state.description = "";
  state.is_active = true;
  showRoleModal.value = true;
  nextTick(() => {
    formRef.value?.clear();
  });
};

const openEditModal = (role: any) => {
  editingRole.value = role;
  state.name = role.name;
  state.description = role.description || "";
  state.is_active = role.is_active;
  showRoleModal.value = true;
  nextTick(() => {
    formRef.value?.clear();
  });
};

const openDeleteModal = (role: any) => {
  deleteModalStore.open({
    entityName: "Role",
    itemName: role.name,
    itemId: role.id,
    onConfirm: async () => {
      const response = await api.deleteRole(role.id);
      if (response.status === "success") {
        toast.add({ title: response.message, color: "success" });
        await loadRoles();
      } else {
        throw new Error(response.message || "Delete failed");
      }
    },
  });
};

async function onSubmit(event: FormSubmitEvent<RoleSchema>) {
  try {
    isModalLoading.value = true;
    const roleData = { ...event.data };

    if (editingRole.value) {
      const response = await api.updateRole(
        editingRole.value.id,
        roleData as any,
      );
      if (response.status === "success") {
        toast.add({ title: response.message, color: "success" });
        showRoleModal.value = false;
        await loadRoles();
      } else {
        // Handle backend validation errors
        if (response.data?.errors) {
          const errors: FormError[] = [];
          Object.keys(response.data.errors).forEach((field) => {
            if (field !== "_form") {
              errors.push({
                name: field,
                message: response.data.errors[field],
              });
            }
          });
          formRef.value?.setErrors(errors);
        } else {
          toast.add({ title: response.message, color: "error" });
        }
      }
    } else {
      const response = await api.createRole(roleData as any);
      if (response.status === "success") {
        toast.add({ title: response.message, color: "success" });
        showRoleModal.value = false;
        await loadRoles();
      } else {
        // Handle backend validation errors
        if (response.data?.errors) {
          const errors: FormError[] = [];
          Object.keys(response.data.errors).forEach((field) => {
            if (field !== "_form") {
              errors.push({
                name: field,
                message: response.data.errors[field],
              });
            }
          });
          formRef.value?.setErrors(errors);
        } else {
          toast.add({ title: response.message, color: "error" });
        }
      }
    }
  } catch (err: any) {
    toast.add({ title: "Failed to save role", color: "error" });
  } finally {
    isModalLoading.value = false;
  }
}

// Load data on mount
onMounted(() => {
  loadRoles();
});
</script>

<template>
  <div class="space-y-4">
    <!-- Header -->
    <div class="flex justify-between items-center">
      <h2 class="text-xl font-semibold">Roles</h2>
      <UButton @click="openCreateModal" icon="i-lucide-plus">
        Add Role
      </UButton>
    </div>

    <div class="border border-accented rounded-lg space-y-4">
      <!-- Loading state -->
      <div v-if="loading" class="flex items-center justify-center py-12">
        <UIcon
          name="i-lucide-loader-2"
          class="animate-spin h-8 w-8 text-primary"
        />
      </div>

      <!-- Roles Table -->
      <div v-else-if="roles.length > 0">
        <UTable
          ref="table"
          v-model:pagination="tablePagination"
          :data="roles"
          :columns="roleColumns"
          :pagination-options="{
            getPaginationRowModel: getPaginationRowModel(),
          }"
        />

        <div class="flex justify-end border-t border-accented py-3.5 px-4">
          <UPagination
            :page="(table?.tableApi?.getState().pagination.pageIndex || 0) + 1"
            :items-per-page="table?.tableApi?.getState().pagination.pageSize"
            :total="pagination.total"
            @update:page="(p) => (pagination.page = p)"
          />
        </div>
      </div>

      <!-- Empty state -->
      <div
        v-else
        class="text-center py-24 border border-dashed border-accented rounded-lg bg-muted/10"
      >
        <UIcon
          name="i-lucide-shield"
          class="h-12 w-12 text-muted-foreground mx-auto mb-4"
        />
        <p class="text-muted-foreground font-medium text-sm">No roles found</p>
      </div>
    </div>

    <!-- Role Create/Edit Modal -->
    <UModal
      v-model:open="showRoleModal"
      :title="editingRole ? 'Edit Role' : 'Create Role'"
      :ui="{ footer: 'justify-end' }"
      class="w-[400px]"
    >
      <template #body>
        <UForm
          ref="formRef"
          :schema="roleSchema"
          :state="state"
          class="space-y-4"
          @submit="onSubmit"
        >
          <UFormField label="Name" name="name" required>
            <UInput
              v-model="state.name"
              placeholder="Enter role name"
              :disabled="editingRole?.name === 'SystemManager'"
              class="w-full"
            />
          </UFormField>

          <UFormField label="Description" name="description">
            <UTextarea
              v-model="state.description"
              placeholder="Enter role description"
              :rows="3"
              class="w-full"
            />
          </UFormField>

          <UFormField label="Active" name="is_active">
            <UCheckbox v-model="state.is_active" label="Role is active" />
          </UFormField>
        </UForm>
      </template>

      <template #footer="{ close }">
        <UButton
          label="Cancel"
          color="neutral"
          variant="outline"
          @click="close"
        />
        <UButton
          :loading="isModalLoading"
          :label="editingRole ? 'Update' : 'Create'"
          color="neutral"
          type="submit"
          @click="formRef?.submit()"
        />
      </template>
    </UModal>
  </div>
</template>
