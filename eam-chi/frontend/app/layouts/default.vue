<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";
import { useAuthStore } from "~/stores/auth";
import type { RouteLocationMatched } from "vue-router";
import { useBrandingSettings } from "~/composables/useBrandingSettings";

const route = useRoute();
const authStore = useAuthStore();
const { logout } = useAuth();
const { bootInfo } = useBootInfo();
const { branding, refreshBrandingSettings } = useBrandingSettings();

const isLogin = computed(() => route.path === "/login");

// Sidebar state
const isCollapsed = ref(false);

// Use boot info for sidebar entities
const sidebarEntities = computed(() => {
  return bootInfo.value?.sidebar?.entities || [];
});

const sidebarNavigation = computed(() => {
  return bootInfo.value?.sidebar?.navigation || [];
});

const formatLabel = (value: string) =>
  value.replace(/_/g, " ").replace(/\b\w/g, (m: string) => m.toUpperCase());

type SidebarNavigationItem = NavigationMenuItem;
type SidebarNavigationGroup = SidebarNavigationItem[];

const isDefined = <T,>(value: T | null | undefined): value is T =>
  value != null;

const moduleNavigationGroups = computed(() => {
  return sidebarNavigation.value
    .map((moduleConfig) => {
      const items = moduleConfig.items
        .map((item) => {
          if (item.type === "entity") {
            return {
              label: item.label,
              icon: item.icon,
              to: item.to,
            } satisfies SidebarNavigationItem;
          }

          return {
            label: item.label,
            icon: item.icon,
            children: item.children.map((child) => ({
              label: child.label,
              icon: child.icon,
              to: child.to,
            })),
            defaultOpen: item.defaultOpen ?? true,
          } satisfies SidebarNavigationItem;
        })
        .filter(isDefined);

      if (!items.length) return null;

      return [
        {
          label: moduleConfig.label,
          type: "label",
          slot: `${moduleConfig.key}-label`,
        },
        ...items,
      ] satisfies SidebarNavigationGroup;
    })
    .filter(isDefined);
});

const brandingTitle = computed(
  () => branding.value.organization_name || "CubeEAM",
);

const brandingDescription = computed(
  () => branding.value.description || "Asset Management",
);

const brandingLogoUrl = computed(() => branding.value.logo_url || null);

const navigationItems = computed(() => {
  const baseItems = [
    [
      {
        label: "Navigation",
        type: "label",
        slot: "navigation-label" as const,
      },
      {
        label: "Home",
        icon: "i-lucide-home",
        to: "/",
      },
      {
        label: "Dashboard",
        icon: "i-lucide-layout-dashboard",
        to: "/dashboard",
        slot: "dashboard" as const,
      },
      {
        label: "Calendar",
        icon: "i-lucide-calendar",
        to: "/calendar",
        slot: "calendar" as const,
      },
      {
        label: "Reports",
        icon: "i-lucide-file-bar-chart",
        to: "/reports",
        slot: "reports" as const,
      },
    ],
  ];

  const adminItems = authStore.isSuperuser
    ? [
        [
          {
            label: "Settings",
            type: "label",
            slot: "settings-label" as const,
          },
          {
            label: "General",
            icon: "i-lucide-cog",
            to: "/settings",
          },
          {
            label: "Admin",
            icon: "i-lucide-shield",
            to: "/admin",
          },
          {
            label: "Workflow",
            icon: "i-lucide-git-branch",
            to: "/workflow",
          },
          {
            label: "Model Editor",
            icon: "i-lucide-database",
            to: "/model-editor",
          },
          {
            label: "Import & Export",
            icon: "i-lucide-arrow-up-down",
            to: "/import-export",
          },
        ],
      ]
    : [];

  return [...baseItems, ...moduleNavigationGroups.value, ...adminItems];
});

const getEntityLabel = (name: string) =>
  sidebarEntities.value.find((m) => m.name === name)?.label;

const getMetaLabel = (record?: RouteLocationMatched) => {
  const meta = record?.meta as
    | { breadcrumb?: string | ((r: typeof route) => string); title?: string }
    | undefined;
  if (!meta) return "";
  if (typeof meta.breadcrumb === "function") return meta.breadcrumb(route);
  if (meta.breadcrumb) return String(meta.breadcrumb);
  if (record?.path?.includes(":")) return "";
  return meta.title ? String(meta.title) : "";
};

const getCrumbLabel = (segment: string, record?: RouteLocationMatched) => {
  const metaLabel = getMetaLabel(record);
  if (metaLabel) return metaLabel;
  if (record?.path?.includes(":entity")) {
    const entityName = String(route.params.entity || segment);
    return getEntityLabel(entityName) || formatLabel(entityName);
  }
  if (record?.path?.includes(":id") && segment === "new") return "New";
  return getEntityLabel(segment) || formatLabel(segment);
};

const crumbs = computed(() => {
  const raw = (route.path || "").split("?")[0];
  const parts = raw?.split("/").filter(Boolean) || [];
  const matched = route.matched.filter((record) => record.path !== "/");

  return parts.map((seg, idx) => ({
    key: seg,
    label: getCrumbLabel(seg, matched[idx]),
    href: "/" + parts.slice(0, idx + 1).join("/"),
  }));
});

const { notifications, unreadCount, markRead, markAllRead } =
  useNotificationCenter();

// Toggle sidebar collapse
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value;
  if (import.meta.client) {
    localStorage.setItem("sidebar_collapsed", isCollapsed.value.toString());
  }
};

// Restore sidebar state from localStorage
onMounted(() => {
  refreshBrandingSettings();
  if (import.meta.client) {
    const stored = localStorage.getItem("sidebar_collapsed");
    if (stored !== null) {
      isCollapsed.value = stored === "true";
    }
  }
});
</script>

<template>
  <div v-if="isLogin" class="w-full">
    <slot />
  </div>

  <div v-else class="min-h-screen flex overflow-hidden">
    <!-- App Layout with Sidebar -->
    <!-- Sidebar -->
    <aside
      :class="[
        'bg-card h-screen flex flex-col flex-shrink-0 sticky border-r border-accented top-0 transition-[width] duration-300 ease-in-out overflow-hidden',
        isCollapsed ? 'w-18' : 'w-64',
      ]"
    >
      <!-- Header with logo -->
      <div class="p-4 flex items-center gap-2 min-w-[256px]">
        <img
          v-if="brandingLogoUrl"
          :src="brandingLogoUrl"
          alt="Organization logo"
          class="w-10 h-10 rounded-md object-contain shrink-0"
        />
        <div
          v-else
          class="w-10 h-10 flex items-center justify-center rounded-md bg-primary/10 text-primary shrink-0"
        >
          <svg
            class="w-6 h-6"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <rect x="3" y="3" width="18" height="18" rx="2" />
            <path d="M9 11h6M9 15h6" />
          </svg>
        </div>

        <div
          class="leading-tight transition-opacity duration-300"
          :class="isCollapsed ? 'opacity-0' : 'opacity-100'"
        >
          <h1 class="text-sm font-bold whitespace-nowrap truncate">
            {{ brandingTitle }}
          </h1>
          <p class="text-xs text-muted-foreground whitespace-nowrap">
            {{ brandingDescription }}
          </p>
        </div>
      </div>

      <!-- Navigation -->
      <div class="flex-1 overflow-y-auto p-2">
        <UNavigationMenu
          :collapsed="isCollapsed"
          orientation="vertical"
          :items="navigationItems"
          :tooltip="true"
          :popover="true"
          :ui="{
            root: 'data-[collapsed=true]:flex data-[collapsed=true]:flex-col data-[collapsed=true]:items-center',
            item: 'transition-all duration-300',
            label: [
              'transition-opacity duration-300',
              isCollapsed ? 'opacity-0' : 'opacity-100',
            ],
          }"
        >
          <template #navigation-label-trailing>
            <UBadge label="MENU" color="neutral" variant="soft" size="sm" />
          </template>
          <template #calendar-trailing>
            <UBadge label="BETA" color="neutral" variant="outline" size="sm" />
          </template>
          <template #reports-trailing>
            <UBadge label="BETA" color="neutral" variant="outline" size="sm" />
          </template>
          <template #settings-label-trailing>
            <UBadge label="ADMIN" color="neutral" variant="soft" size="sm" />
          </template>
        </UNavigationMenu>
      </div>

      <!-- User section -->
      <div class="p-4 border-t border-accented">
        <UDropdownMenu
          :items="[
            [
              {
                label: 'Profile',
                icon: 'i-lucide-user',
                to: '/profile',
              },
              {
                label: 'Logout',
                icon: 'i-lucide-log-out',
                onSelect: logout,
              },
            ],
          ]"
          :popper="{ placement: 'top-start' }"
        >
          <button
            class="w-full flex items-center gap-2 rounded-md hover:bg-muted p-1.5 min-w-[224px]"
          >
            <UAvatar size="sm" :alt="authStore.displayName" class="shrink-0" />

            <div
              class="flex-1 min-w-0 text-left transition-opacity duration-300"
              :class="isCollapsed ? 'opacity-0' : 'opacity-100'"
            >
              <p class="text-sm font-medium truncate">
                {{ authStore.displayName }}
              </p>
              <p class="text-xs text-muted-foreground truncate">
                {{ authStore.userRoles[0] || "User" }}
              </p>
            </div>
          </button>
        </UDropdownMenu>
      </div>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col min-w-0 h-screen">
      <!-- Header -->
      <header
        class="h-16 px-4 flex items-center justify-between sticky border-b border-accented top-0 z-10 shrink-0"
      >
        <!-- Breadcrumbs with collapse button -->
        <div class="flex items-center space-x-2">
          <UButton
            variant="ghost"
            size="sm"
            icon="i-lucide-menu"
            @click="toggleSidebar"
            class="mr-2"
          />
          <UBreadcrumb
            :items="[
              { label: 'Home', to: '/' },
              ...crumbs.map((c) => ({ label: c.label, to: c.href })),
            ]"
            separator-icon="i-lucide-chevron-right"
          />
        </div>

        <!-- Notifications -->
        <UPopover>
          <div class="relative">
            <UButton variant="outline" icon="i-lucide-bell" size="sm" />
            <span
              v-if="unreadCount > 0"
              class="absolute -top-1 -right-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold text-white"
            >
              {{ unreadCount > 9 ? "9+" : unreadCount }}
            </span>
          </div>

          <template #content>
            <div class="w-80 p-3 space-y-3">
              <div class="flex items-center justify-between">
                <p class="text-sm font-semibold">Notifications</p>
                <UButton
                  v-if="unreadCount > 0"
                  variant="link"
                  size="xs"
                  @click="markAllRead"
                >
                  Mark all read
                </UButton>
              </div>
              <div
                v-if="notifications.length"
                class="space-y-2 max-h-64 overflow-y-auto"
              >
                <div
                  v-for="note in notifications.slice(0, 20)"
                  :key="note.id"
                  class="rounded-md border border-accented p-2 cursor-pointer transition-colors"
                  :class="note.read ? 'opacity-60' : 'bg-primary/5'"
                  @click="markRead(note.id)"
                >
                  <p class="text-sm font-medium">{{ note.title }}</p>
                  <p
                    v-if="note.description"
                    class="text-xs text-muted-foreground"
                  >
                    {{ note.description }}
                  </p>
                </div>
              </div>
              <p v-else class="text-xs text-muted-foreground text-center py-4">
                No notifications
              </p>
            </div>
          </template>
        </UPopover>
      </header>

      <!-- Page content -->
      <main class="flex-1 p-4 overflow-y-auto min-h-0">
        <slot />
      </main>
    </div>
  </div>
</template>
