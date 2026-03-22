<script setup lang="ts">
// Import components
import AdminUsers from "~/components/admin/AdminUsers.vue";
import AdminRoles from "~/components/admin/AdminRoles.vue";
import AdminPermissions from "~/components/admin/AdminPermissions.vue";

const authStore = useAuthStore();

// Active tab state
const activeTab = ref("users");

// Initialize auth store on mount
onMounted(() => {
  authStore.initFromStorage();
});

definePageMeta({ middleware: "auth" as any });
</script>

<template>
  <div class="space-y-6 px-3 py-3">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-foreground">Admin Panel</h1>
        <p class="text-muted-foreground text-sm">
          Manage users, roles, and permissions
        </p>
      </div>
    </div>

    <UTabs
      v-model="activeTab"
      :items="[
        { value: 'users', slot: 'users', label: 'Users' },
        { value: 'roles', slot: 'roles', label: 'Roles' },
        {
          value: 'permissions',
          slot: 'permissions',
          label: 'Role Permissions',
        },
      ]"
      class="w-full"
      size="md"
      variant="link"
    >
      <template #users>
        <div class="pt-4" v-if="activeTab === 'users'">
          <AdminUsers />
        </div>
      </template>

      <template #roles>
        <div class="pt-4" v-if="activeTab === 'roles'">
          <AdminRoles />
        </div>
      </template>

      <template #permissions>
        <div class="pt-4" v-if="activeTab === 'permissions'">
          <AdminPermissions />
        </div>
      </template>

      <template #states>
        <div class="pt-4" v-if="activeTab === 'states'">
          <AdminWorkflowStates />
        </div>
      </template>
    </UTabs>
  </div>
</template>
