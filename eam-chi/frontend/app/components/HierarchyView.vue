<script setup lang="ts">
import type { TreeItem } from "@nuxt/ui";

interface HierarchyNode {
  id: string;
  label: string;
  entity: string;
  data: Record<string, any>;
  children: HierarchyNode[];
}

const props = defineProps<{
  data: HierarchyNode[];
  rootLabel: string;
  loading: boolean;
}>();

const emit = defineEmits<{
  select: [node: HierarchyNode];
}>();

const router = useRouter();

const entityIcons: Record<string, string> = {
  organization: "i-lucide-building-2",
  site: "i-lucide-map-pin",
  department: "i-lucide-users",
};

const entityColors: Record<string, string> = {
  organization: "text-primary",
  site: "text-emerald-500",
  department: "text-amber-500",
};

function buildTreeItems(nodes: HierarchyNode[]): TreeItem[] {
  return nodes.map((node) => ({
    label: node.label || node.id,
    icon: entityIcons[node.entity] || "i-lucide-folder",
    id: node.id,
    _entity: node.entity,
    defaultExpanded: true,
    children:
      node.children?.length > 0 ? buildTreeItems(node.children) : undefined,
  }));
}

const treeItems = computed<TreeItem[]>(() => {
  if (!props.data?.length) return [];
  return buildTreeItems(props.data);
});

const nodeMap = computed(() => {
  const map = new Map<string, HierarchyNode>();
  function walk(nodes: HierarchyNode[]) {
    for (const n of nodes) {
      map.set(n.id, n);
      if (n.children?.length) walk(n.children);
    }
  }
  walk(props.data || []);
  return map;
});

function handleSelect(item: TreeItem) {
  const node = nodeMap.value.get(item.id as string);
  if (node) {
    router.push(`/${node.entity}/${node.id}`);
  }
}

function countNodes(nodes: HierarchyNode[]): { [entity: string]: number } {
  const counts: Record<string, number> = {};
  function walk(list: HierarchyNode[]) {
    for (const n of list) {
      counts[n.entity] = (counts[n.entity] || 0) + 1;
      if (n.children?.length) walk(n.children);
    }
  }
  walk(nodes);
  return counts;
}

const stats = computed(() => countNodes(props.data || []));
</script>

<template>
  <div class="h-full min-h-0 flex flex-col gap-4">
    <!-- Stats bar -->
    <div
      v-if="!loading && data?.length"
      class="flex items-center gap-4 text-sm text-muted-foreground"
    >
      <div
        v-for="(count, entity) in stats"
        :key="entity"
        class="flex items-center gap-1.5"
      >
        <UIcon
          :name="entityIcons[entity as string] || 'i-lucide-folder'"
          :class="entityColors[entity as string] || 'text-muted-foreground'"
          class="w-4 h-4"
        />
        <span class="capitalize">{{ entity.toString().replace(/_/g, ' ') }}</span>
        <UBadge variant="subtle" size="sm">{{ count }}</UBadge>
      </div>
    </div>

    <div v-if="loading" class="space-y-3">
      <USkeleton class="h-10 w-full" />
      <USkeleton class="h-10 w-11/12" />
      <USkeleton class="h-10 w-10/12" />
      <USkeleton class="h-10 w-9/12" />
    </div>

    <div
      v-else-if="treeItems.length === 0"
      class="text-center py-12 rounded-lg border border-muted"
    >
      <UIcon
        name="i-lucide-inbox"
        class="h-12 w-12 mx-auto text-muted-foreground mb-4"
      />
      <h3 class="text-lg font-medium mb-2">No hierarchy data</h3>
      <p class="text-muted-foreground">
        Create an {{ rootLabel }} to build the hierarchy.
      </p>
    </div>

    <div
      v-else
      class="flex-1 min-h-0 rounded-lg border border-muted p-4 overflow-y-auto"
    >
      <UTree :items="treeItems" @select="handleSelect" />
    </div>
  </div>
</template>
