<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";
import { useBrandingSettings } from "~/composables/useBrandingSettings";

const authStore = useAuthStore();
const { branding } = useBrandingSettings();
const { getMeta } = useApi();

const entities = ref<any[]>([]);
const loading = ref(true);

const moduleIcons: Record<string, string> = {
  core: "i-lucide-settings",
  core_eam: "i-lucide-building-2",
  asset_management: "i-lucide-box",
  maintenance_mgmt: "i-lucide-wrench",
  work_mgmt: "i-lucide-clipboard-list",
  purchasing_stores: "i-lucide-shopping-cart",
};

const formatLabel = (str: string) =>
  str
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");

const getModuleIcon = (mod: string) => moduleIcons[mod] || "i-lucide-folder";

const loadEntities = async () => {
  try {
    const response = await getMeta();
    entities.value = (response.data || []).filter((e: any) => e.in_sidebar);
  } catch (err) {
    console.error("Failed to load entities:", err);
  } finally {
    loading.value = false;
  }
};

const groupedEntities = computed(() => {
  const groups: Record<string, any[]> = {};
  entities.value.forEach((e) => {
    const mod = e.module || "Other";
    if (!groups[mod]) groups[mod] = [];
    groups[mod].push(e);
  });
  return groups;
});

const adminLinks = [
  {
    label: "Permissions",
    icon: "i-lucide-shield",
    to: "/admin/permissions",
    description: "Manage role-based access control",
  },
  {
    label: "Workflows",
    icon: "i-lucide-git-branch",
    to: "/workflow",
    description: "Configure state machines",
  },
  {
    label: "Users",
    icon: "i-lucide-users",
    to: "/admin",
    description: "Manage user accounts",
  },
  {
    label: "Model Editor",
    icon: "i-lucide-database",
    to: "/model-editor",
    description: "Edit entity metadata",
  },
  {
    label: "Settings",
    icon: "i-lucide-cog",
    to: "/settings",
    description: "Branding & system config",
  },
  {
    label: "Import & Export",
    icon: "i-lucide-arrow-up-down",
    to: "/import-export",
    description: "Bulk data operations",
  },
];

onMounted(loadEntities);

definePageMeta({
  title: "Home",
  middleware: "auth" as any,
});
</script>

<template>
  <div class="space-y-8 px-3 py-3">
    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center py-20">
      <UIcon
        name="i-lucide-loader-2"
        class="animate-spin h-8 w-8 text-primary"
      />
    </div>

    <template v-else>
      <!-- Welcome header -->
      <div class="flex items-start justify-between">
        <div>
          <h1 class="text-3xl font-bold">
            Welcome back, {{ authStore.displayName }}
          </h1>
          <p class="text-muted-foreground mt-1">
            {{ branding.organization_name || "EAM System" }}
            <span v-if="branding.description">
              — {{ branding.description }}</span
            >
          </p>
        </div>
        <UButton
          to="/profile"
          variant="ghost"
          icon="i-lucide-user-circle"
          size="lg"
        />
      </div>

      <!-- Quick Create -->
      <div v-if="entities.length" class="space-y-3">
        <h2 class="text-lg font-semibold">Quick Create</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
          <UButton
            v-for="entity in entities.slice(0, 5)"
            :key="entity.name"
            :to="`/${entity.name}/new`"
            variant="outline"
            class="h-auto py-3 flex-col gap-1.5"
          >
            <UIcon name="i-lucide-plus-circle" class="h-5 w-5 text-primary" />
            <span class="text-sm">{{ entity.label }}</span>
          </UButton>
        </div>
      </div>

      <!-- Modules -->
      <div class="space-y-3">
        <h2 class="text-lg font-semibold">Modules</h2>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div
            v-for="(moduleEntities, moduleName) in groupedEntities"
            :key="moduleName"
            class="border border-accented rounded-lg bg-card"
          >
            <div class="p-4 border-b border-accented flex items-center gap-2">
              <UIcon
                :name="getModuleIcon(moduleName)"
                class="h-5 w-5 text-primary"
              />
              <h3 class="font-semibold text-sm">
                {{ formatLabel(moduleName) }}
              </h3>
              <UBadge
                :label="String(moduleEntities.length)"
                size="sm"
                variant="subtle"
                color="neutral"
                class="ml-auto"
              />
            </div>
            <div class="p-2">
              <NuxtLink
                v-for="entity in moduleEntities"
                :key="entity.name"
                :to="`/${entity.name}`"
                class="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted/60 transition-colors group"
              >
                <UIcon
                  name="i-lucide-file-text"
                  class="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors"
                />
                <span class="text-sm">{{ entity.label }}</span>
                <UIcon
                  name="i-lucide-chevron-right"
                  class="h-3.5 w-3.5 text-muted-foreground ml-auto opacity-0 group-hover:opacity-100 transition-opacity"
                />
              </NuxtLink>
            </div>
          </div>
        </div>
      </div>

      <!-- Admin Section -->
      <div v-if="authStore.isSuperuser" class="space-y-3">
        <h2 class="text-lg font-semibold">Administration</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          <NuxtLink
            v-for="item in adminLinks"
            :key="item.to"
            :to="item.to"
            class="flex items-start gap-3 p-4 border border-accented rounded-lg bg-card hover:bg-muted/50 transition-colors group"
          >
            <div class="p-2 bg-primary/10 rounded-lg shrink-0">
              <UIcon :name="item.icon" class="h-5 w-5 text-primary" />
            </div>
            <div>
              <p
                class="font-medium text-sm group-hover:text-primary transition-colors"
              >
                {{ item.label }}
              </p>
              <p class="text-xs text-muted-foreground mt-0.5">
                {{ item.description }}
              </p>
            </div>
          </NuxtLink>
        </div>
      </div>
    </template>
  </div>
</template>
